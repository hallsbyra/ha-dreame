"""Home Assistant side of reconciliation: observe, decide, apply, audit and log."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime
import logging

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .audit import async_call_robot_service, record_activity
from .const import VACUUM_DOMAIN
from .dispatch_executor import async_dispatch_current_room
from .queue_core import (
    DispatchTracking,
    QueueItem,
    complete_current_room,
    current_item,
    external_takeover,
)
from .reconcile_core import Decision, Observation, decide
from .runtime import HaDreameRuntimeData

_LOGGER = logging.getLogger(__name__)
COMMAND_INTENT_DISPATCH_CURRENT_ROOM = "dispatch_current_room"
COMMAND_INTENT_RESUME_CURRENT_ROOM = "resume_current_room"


@dataclass(frozen=True, slots=True)
class ReconcileEvaluation:
    """One observation and, while a room awaits completion, the decision about it."""

    observation: Observation
    item: QueueItem | None = None
    tracking: DispatchTracking | None = None
    seconds_since_command: float | None = None
    decision: Decision | None = None


def evaluate_reconcile(
    hass: HomeAssistant,
    runtime_data: HaDreameRuntimeData,
    *,
    task_status_override: str | None = None,
) -> ReconcileEvaluation:
    """Observe the robot and decide about the awaited room without changing anything."""
    observation = runtime_data.observe(hass, task_status_override=task_status_override)
    item = runtime_data.awaited_item()
    tracking = runtime_data.queue_state.dispatch
    if item is None or tracking is None:
        return ReconcileEvaluation(observation)
    seconds = max(0.0, (datetime.now(UTC) - tracking.last_command_at).total_seconds())
    return ReconcileEvaluation(
        observation,
        item,
        tracking,
        seconds,
        decide(observation, item, tracking, seconds),
    )


async def async_reconcile(
    hass: HomeAssistant,
    runtime_data: HaDreameRuntimeData,
) -> ReconcileEvaluation:
    """Run one reconcile pass under the runtime operation lock."""
    async with runtime_data.operation_lock:
        if runtime_data.unload_requested.is_set():
            raise HomeAssistantError("HA Dreame runtime is unloading")
        return await async_reconcile_under_lock(hass, runtime_data)


async def async_reconcile_under_lock(
    hass: HomeAssistant,
    runtime_data: HaDreameRuntimeData,
    *,
    task_status_override: str | None = None,
) -> ReconcileEvaluation:
    """Run one reconcile pass while the caller owns the runtime operation lock."""
    evaluation = evaluate_reconcile(
        hass,
        runtime_data,
        task_status_override=task_status_override,
    )
    if evaluation.decision is None:
        return evaluation
    assert evaluation.item is not None and evaluation.tracking is not None
    decision = evaluation.decision
    command_intent = await async_apply_decision(hass, runtime_data, decision)
    if (
        decision.tracking.active_room_confirmed_since_dispatch
        and not evaluation.tracking.active_room_confirmed_since_dispatch
    ):
        observation = evaluation.observation
        record_activity(
            runtime_data,
            "active_room_confirmation",
            "confirmed",
            context=Context(),
            source="robot_observation",
            room_id=evaluation.item.room_id,
            item_id=evaluation.item.item_id,
            reason=(
                f"observed_room_id={observation.observed_room_id};"
                f"vacuum_state={observation.vacuum_state};task_status={observation.task_status}"
            ),
        )
    _log_reconcile_outcome(runtime_data, evaluation, decision, command_intent)
    return evaluation


async def async_apply_decision(
    hass: HomeAssistant,
    runtime_data: HaDreameRuntimeData,
    decision: Decision,
) -> str | None:
    """Apply a decision about the current room and return the command intent it sent."""
    queue_state = runtime_data.queue_state
    if decision.action == "hold":
        if decision.tracking != queue_state.dispatch:
            runtime_data.set_queue_state(replace(queue_state, dispatch=decision.tracking))
        return None

    if decision.action == "fail":
        assert decision.fail_reason is not None
        runtime_data.set_queue_state(
            external_takeover(queue_state, reason=decision.fail_reason, blocked=decision.blocked)
        )
        return None

    next_state = (
        complete_current_room(queue_state) if decision.action == "complete" else queue_state
    )
    if next_state.current_item_id is None:
        runtime_data.set_queue_state(next_state)
        return None

    command_intent = (
        COMMAND_INTENT_RESUME_CURRENT_ROOM
        if decision.action == "resume"
        else COMMAND_INTENT_DISPATCH_CURRENT_ROOM
    )
    item = current_item(queue_state)
    assert item is not None
    record_activity(
        runtime_data,
        command_intent,
        "decision",
        context=Context(),
        source="reconcile",
        room_id=item.room_id,
        reason=",".join(decision.reasons),
    )
    if decision.action == "resume":
        await async_call_robot_service(
            hass,
            runtime_data,
            VACUUM_DOMAIN,
            "start",
            {ATTR_ENTITY_ID: runtime_data.vacuum_entity_id},
        )
        runtime_data.set_queue_state(
            replace(
                queue_state,
                dispatch=replace(decision.tracking, last_command_at=datetime.now(UTC)),
            )
        )
    else:
        retry_count = decision.tracking.dispatch_retry_count if decision.action == "retry" else 0
        await async_dispatch_current_room(hass, runtime_data, next_state, retry_count)
    return command_intent


def _log_reconcile_outcome(
    runtime_data: HaDreameRuntimeData,
    evaluation: ReconcileEvaluation,
    decision: Decision,
    command_intent: str | None,
) -> None:
    """Log reconcile outcomes that did or explained something, without tick noise."""
    tracking_changed = decision.tracking != evaluation.tracking
    if decision.action == "hold" and not tracking_changed and not decision.reasons:
        return

    queue_state = runtime_data.queue_state
    logger = _LOGGER.info
    if decision.action == "fail":
        action, logger = queue_state.run_state, _LOGGER.warning
    elif decision.action == "complete":
        action = "complete_queue" if queue_state.run_state == "completed" else "complete_room"
    elif decision.action == "retry":
        action = "retry_dispatch"
    elif decision.action == "resume":
        action = "resume_room"
    else:
        action = "update_tracking" if tracking_changed else "hold"
        logger = _LOGGER.debug

    item = evaluation.item
    observation = evaluation.observation
    progress = observation.cleaning_progress
    logger(
        (
            "HA Dreame reconcile action=%s vacuum=%s run_id=%s item_id=%s "
            "expected_room_id=%s expected_room_name=%s observed_room_id=%s "
            "observed_room_name=%s progress=%s command_intent=%s terminal_state=%s "
            "reasons=%s"
        ),
        action,
        runtime_data.vacuum_entity_id,
        queue_state.run_id,
        queue_state.current_item_id,
        item.room_id if item else None,
        item.room_name if item else None,
        observation.observed_room_id,
        observation.observed_room_name,
        "-" if progress is None else progress,
        command_intent,
        queue_state.run_state,
        ",".join(decision.reasons) or "-",
    )

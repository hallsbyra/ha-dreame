"""Shared runtime reconcile evaluation and application helpers."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime
import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .queue_core import QueueError
from .runtime import HaDreameRuntimeData
from .runtime_observation import build_runtime_reconcile_observation
from .runtime_reconcile import RuntimeReconcileResult, apply_reconcile_decision
from .runtime_reconcile_executor import async_apply_runtime_reconcile_result
from .runtime_reconcile_observation import (
    RuntimeReconcileEvaluation,
    RuntimeReconcileObservation,
    evaluate_runtime_reconcile_observation,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RuntimeReconcileApplyOutcome:
    """Inspectable result from one runtime reconcile apply pass."""

    applied_result: RuntimeReconcileResult
    evaluation: RuntimeReconcileEvaluation
    observation: RuntimeReconcileObservation


def evaluate_runtime_reconcile(
    hass: HomeAssistant,
    runtime_data: HaDreameRuntimeData,
    *,
    task_status_override: str | None = None,
) -> tuple[RuntimeReconcileObservation, RuntimeReconcileEvaluation]:
    """Build and evaluate one runtime reconcile observation."""
    observation = build_runtime_reconcile_observation(
        hass,
        vacuum_entity_id=runtime_data.vacuum_entity_id,
        entity_ids=runtime_data.observation_entity_ids,
    )
    if task_status_override is not None:
        observation = replace(observation, task_status=task_status_override)
    evaluation = evaluate_runtime_reconcile_observation(
        runtime_data.queue_state,
        runtime_data.run_tracking,
        observation,
        now=datetime.now(UTC),
    )

    return observation, evaluation


async def async_evaluate_and_apply_runtime_reconcile(
    hass: HomeAssistant,
    runtime_data: HaDreameRuntimeData,
) -> RuntimeReconcileApplyOutcome:
    """Evaluate and apply one runtime reconcile pass."""
    async with runtime_data.operation_lock:
        if runtime_data.unload_requested.is_set():
            raise HomeAssistantError("HA Dreame runtime is unloading")
        return await async_evaluate_and_apply_runtime_reconcile_under_lock(
            hass,
            runtime_data,
        )


async def async_evaluate_and_apply_runtime_reconcile_under_lock(
    hass: HomeAssistant,
    runtime_data: HaDreameRuntimeData,
    *,
    task_status_override: str | None = None,
) -> RuntimeReconcileApplyOutcome:
    """Evaluate and apply while the caller owns the runtime operation lock."""
    observation, evaluation = evaluate_runtime_reconcile(
        hass,
        runtime_data,
        task_status_override=task_status_override,
    )
    try:
        result = apply_reconcile_decision(
            runtime_data.queue_state,
            runtime_data.run_tracking,
            evaluation.decision,
        )
    except QueueError as err:
        raise HomeAssistantError(str(err)) from err

    applied_result = await async_apply_runtime_reconcile_result(
        hass,
        runtime_data,
        result,
    )
    _log_reconcile_outcome(runtime_data, evaluation, applied_result)
    return RuntimeReconcileApplyOutcome(
        applied_result=applied_result,
        evaluation=evaluation,
        observation=observation,
    )


def _log_reconcile_outcome(
    runtime_data: HaDreameRuntimeData,
    evaluation: RuntimeReconcileEvaluation,
    result: RuntimeReconcileResult,
) -> None:
    """Log non-noop reconcile outcomes without spamming normal ticks."""
    decision = evaluation.decision
    if not _should_log_reconcile_outcome(evaluation, result):
        return

    action = _reconcile_log_action(evaluation, result)
    logger = _LOGGER.warning if decision.mark_out_of_sync_reason else _LOGGER.debug
    if (
        decision.complete_current_room
        or decision.retry_current_room
        or decision.resume_current_room
    ):
        logger = _LOGGER.info

    logger(
        (
            "HA Dreame reconcile action=%s vacuum=%s run_id=%s item_id=%s "
            "expected_room_id=%s expected_room_name=%s observed_room_id=%s "
            "observed_room_name=%s progress=%s command_intent=%s terminal_state=%s "
            "reasons=%s"
        ),
        action,
        runtime_data.vacuum_entity_id,
        result.queue_state.run_id,
        result.queue_state.current_item_id,
        evaluation.expected_room_id,
        evaluation.expected_room_name,
        evaluation.observed_room_id,
        evaluation.observed_room_name,
        _first_event_progress(decision.event_reasons),
        result.command_intent,
        result.queue_state.run_state,
        ",".join(decision.event_reasons) or "-",
    )


def _should_log_reconcile_outcome(
    evaluation: RuntimeReconcileEvaluation,
    result: RuntimeReconcileResult,
) -> bool:
    decision = evaluation.decision
    return bool(
        decision.event_reasons
        or decision.complete_current_room
        or decision.retry_current_room
        or decision.resume_current_room
        or decision.mark_out_of_sync_reason
        or decision.set_active_room_confirmed_since_dispatch
        or decision.set_task_status_cleared_since_dispatch
        or decision.set_post_run_maintenance_seen
        or decision.reset_dispatch_retry_count
        or result.command_intent
    )


def _reconcile_log_action(
    evaluation: RuntimeReconcileEvaluation,
    result: RuntimeReconcileResult,
) -> str:
    decision = evaluation.decision
    if decision.mark_out_of_sync_reason:
        return result.queue_state.run_state
    if decision.complete_current_room:
        return "complete_queue" if result.queue_state.run_state == "completed" else "complete_room"
    if decision.retry_current_room:
        return "retry_dispatch"
    if decision.resume_current_room:
        return "resume_room"
    if (
        decision.set_active_room_confirmed_since_dispatch
        or decision.set_task_status_cleared_since_dispatch
        or decision.set_post_run_maintenance_seen
        or decision.reset_dispatch_retry_count
    ):
        return "update_tracking"
    return "hold"


def _first_event_progress(event_reasons: tuple[str, ...]) -> str:
    for reason in event_reasons:
        for part in str(reason).split(":"):
            if part.startswith("progress_"):
                return part.removeprefix("progress_")
    return "-"

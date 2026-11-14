"""Home Assistant boundary for applying runtime reconcile results."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import VACUUM_DOMAIN
from .dispatch_executor import async_execute_dispatch_plan, observed_cleaning_mode
from .audit import async_call_robot_service
from .dispatch_plan import build_room_dispatch_plan
from .queue_core import QueueError, QueueState, current_item
from .runtime import HaDreameRuntimeData
from .runtime_reconcile import COMMAND_INTENT_DISPATCH_CURRENT_ROOM, RuntimeReconcileResult
from .runtime_state import QueueRunTracking


async def async_apply_runtime_reconcile_result(
    hass: HomeAssistant,
    runtime_data: HaDreameRuntimeData,
    result: RuntimeReconcileResult,
) -> RuntimeReconcileResult:
    """Apply one reconcile result to runtime data and execute explicit intents."""
    if result.command_intent is None:
        _commit_runtime_state(runtime_data, result.queue_state, result.run_tracking)
        return result

    if result.command_intent == COMMAND_INTENT_DISPATCH_CURRENT_ROOM:
        committed_result = await _async_dispatch_current_room_intent(
            hass,
            runtime_data,
            result,
        )
        _commit_runtime_state(
            runtime_data,
            committed_result.queue_state,
            committed_result.run_tracking,
        )
        return committed_result

    committed_result = await _async_resume_current_room_intent(hass, runtime_data, result)
    _commit_runtime_state(
        runtime_data,
        committed_result.queue_state,
        committed_result.run_tracking,
    )
    return committed_result


async def _async_dispatch_current_room_intent(
    hass: HomeAssistant,
    runtime_data: HaDreameRuntimeData,
    result: RuntimeReconcileResult,
) -> RuntimeReconcileResult:
    # Dispatch intents always target the current running room of an active run.
    item = current_item(result.queue_state)
    assert item is not None

    run_tracking = _new_dispatched_run_tracking(result)
    try:
        plan = build_room_dispatch_plan(
            item,
            vacuum_entity_id=runtime_data.vacuum_entity_id,
            current_cleaning_mode=observed_cleaning_mode(hass, runtime_data.vacuum_entity_id),
            retry_count=run_tracking.dispatch_retry_count,
        )
    except QueueError as err:
        raise HomeAssistantError(str(err)) from err

    # Service handlers and state observers can run synchronously while the
    # command is in flight. Publish the post-transition queue before sending
    # the command so they cannot attribute fresh robot activity to the room
    # that just completed. A rejected command restores the prior state.
    previous_queue_state = runtime_data.queue_state
    previous_run_tracking = runtime_data.run_tracking
    _commit_runtime_state(runtime_data, result.queue_state, run_tracking)
    try:
        await async_execute_dispatch_plan(hass, runtime_data, plan)
    except Exception:
        _commit_runtime_state(runtime_data, previous_queue_state, previous_run_tracking)
        raise
    return replace(result, run_tracking=run_tracking)


async def _async_resume_current_room_intent(
    hass: HomeAssistant,
    runtime_data: HaDreameRuntimeData,
    result: RuntimeReconcileResult,
) -> RuntimeReconcileResult:
    # Resume intents are only produced for the tracked current room.
    assert result.run_tracking is not None

    await async_call_robot_service(
        hass,
        runtime_data,
        VACUUM_DOMAIN,
        "start",
        {ATTR_ENTITY_ID: runtime_data.vacuum_entity_id},
    )
    return replace(
        result,
        run_tracking=replace(
            result.run_tracking,
            last_command_at=datetime.now(UTC),
        ),
    )


def _new_dispatched_run_tracking(result: RuntimeReconcileResult) -> QueueRunTracking:
    assert result.queue_state.run_id is not None and result.command_item_id is not None
    dispatch_retry_count = 0
    if result.run_tracking is not None:
        dispatch_retry_count = result.run_tracking.dispatch_retry_count

    return QueueRunTracking(
        run_id=result.queue_state.run_id,
        current_item_id=result.command_item_id,
        last_command_at=datetime.now(UTC),
        dispatch_retry_count=dispatch_retry_count,
    )


def _commit_runtime_state(
    runtime_data: HaDreameRuntimeData,
    queue_state: QueueState,
    run_tracking: QueueRunTracking | None,
) -> None:
    runtime_data.set_queue_state(queue_state)
    runtime_data.set_run_tracking(run_tracking)

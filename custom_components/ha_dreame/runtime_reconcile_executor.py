"""Home Assistant boundary for applying runtime reconcile results."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import VACUUM_DOMAIN
from .dispatch_executor import async_execute_dispatch_plan
from .dispatch_plan import build_room_dispatch_plan
from .queue_core import QueueError, QueueState, current_item
from .runtime import HaDreameRuntimeData
from .runtime_reconcile import (
    COMMAND_INTENT_DISPATCH_CURRENT_ROOM,
    COMMAND_INTENT_RESUME_CURRENT_ROOM,
    RuntimeReconcileResult,
)
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

    if result.command_intent == COMMAND_INTENT_RESUME_CURRENT_ROOM:
        committed_result = await _async_resume_current_room_intent(
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

    raise HomeAssistantError(
        f"Unsupported runtime reconcile command intent: {result.command_intent}"
    )


async def _async_dispatch_current_room_intent(
    hass: HomeAssistant,
    runtime_data: HaDreameRuntimeData,
    result: RuntimeReconcileResult,
) -> RuntimeReconcileResult:
    item = current_item(result.queue_state)
    if item is None:
        raise HomeAssistantError("Runtime reconcile dispatch requires a current room")
    if item.item_id != result.command_item_id:
        raise HomeAssistantError("Runtime reconcile dispatch item does not match current room")

    run_tracking = _new_dispatched_run_tracking(result)
    try:
        plan = build_room_dispatch_plan(
            item,
            vacuum_entity_id=runtime_data.vacuum_entity_id,
            retry_count=run_tracking.dispatch_retry_count,
        )
    except QueueError as err:
        raise HomeAssistantError(str(err)) from err

    await async_execute_dispatch_plan(
        hass,
        plan,
        commands_enabled=runtime_data.commands_enabled,
    )
    return replace(result, run_tracking=run_tracking)


async def _async_resume_current_room_intent(
    hass: HomeAssistant,
    runtime_data: HaDreameRuntimeData,
    result: RuntimeReconcileResult,
) -> RuntimeReconcileResult:
    if not runtime_data.commands_enabled:
        raise HomeAssistantError("HA Dreame robot commands are disabled")
    if result.queue_state.run_id is None or result.command_item_id is None:
        raise HomeAssistantError("Runtime reconcile resume requires an active run")
    if result.queue_state.current_item_id != result.command_item_id:
        raise HomeAssistantError("Runtime reconcile resume item does not match current room")
    if (
        result.run_tracking is None
        or result.run_tracking.run_id != result.queue_state.run_id
        or result.run_tracking.current_item_id != result.command_item_id
    ):
        raise HomeAssistantError("Runtime reconcile resume requires matching run tracking")

    await hass.services.async_call(
        VACUUM_DOMAIN,
        "start",
        {ATTR_ENTITY_ID: runtime_data.vacuum_entity_id},
        blocking=True,
    )
    return replace(
        result,
        run_tracking=replace(
            result.run_tracking,
            last_command_at=datetime.now(UTC).isoformat(),
        ),
    )


def _new_dispatched_run_tracking(result: RuntimeReconcileResult) -> QueueRunTracking:
    if result.queue_state.run_id is None or result.command_item_id is None:
        raise HomeAssistantError("Runtime reconcile dispatch requires an active run")

    dispatch_retry_count = 0
    if (
        result.run_tracking is not None
        and result.run_tracking.run_id == result.queue_state.run_id
        and result.run_tracking.current_item_id == result.command_item_id
    ):
        dispatch_retry_count = result.run_tracking.dispatch_retry_count

    return QueueRunTracking(
        run_id=result.queue_state.run_id,
        current_item_id=result.command_item_id,
        last_command_at=datetime.now(UTC).isoformat(),
        dispatch_retry_count=dispatch_retry_count,
    )


def _commit_runtime_state(
    runtime_data: HaDreameRuntimeData,
    queue_state: QueueState,
    run_tracking: QueueRunTracking | None,
) -> None:
    runtime_data.set_queue_state(queue_state)
    runtime_data.set_run_tracking(run_tracking)

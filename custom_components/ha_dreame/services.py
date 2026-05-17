"""Service handlers for HA Dreame."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import voluptuous as vol

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import HomeAssistantError

from .const import (
    ATTR_ACTIVE_ROOM_MISMATCH_STREAK,
    ATTR_COMPLETED_ITEMS,
    ATTR_CURRENT_ITEM_ID,
    ATTR_DISPATCH_RETRY_COUNT,
    ATTR_LAST_COMMAND_AT,
    ATTR_PENDING_ITEMS,
    ATTR_QUEUE_ITEMS,
    ATTR_RUN_ID,
    ATTR_RUN_TRACKING,
    ATTR_RUNNING_ITEMS,
    ATTR_TASK_STATUS_CLEARED_SINCE_DISPATCH,
    ATTR_TOTAL_ITEMS,
    CONF_ALLOW_ROBOT_COMMANDS,
    CONF_CONFIG_ENTRY_ID,
    CONF_ITEM_ID,
    CONF_NEW_POSITION,
    CONF_OVERRIDES,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_VACUUM_ENTITY_ID,
    DOMAIN,
    SERVICE_ADD_QUEUE_ROOM,
    SERVICE_APPLY_RECONCILE,
    SERVICE_CANCEL_QUEUE,
    SERVICE_CLEAR_PENDING_QUEUE,
    SERVICE_EVALUATE_RECONCILE,
    SERVICE_GET_RUNTIME_STATUS,
    SERVICE_MOVE_QUEUE_ITEM,
    SERVICE_REMOVE_QUEUE_ITEM,
    SERVICE_SKIP_CURRENT_ROOM,
    SERVICE_START_QUEUE,
    SERVICE_UPDATE_QUEUE_ITEM_OVERRIDES,
    VACUUM_DOMAIN,
)
from .dispatch_executor import async_execute_dispatch_plan
from .dispatch_plan import build_room_dispatch_plan
from .queue_core import (
    QueueError,
    QueueState,
    add_room,
    cancel_run,
    clear_pending,
    current_item,
    move_item,
    remove_item,
    skip_current_room,
    start_run,
    update_item_overrides,
)
from .queue_snapshot import count_queue_items, queue_item_snapshots
from .runtime_observation import build_runtime_reconcile_observation
from .runtime_reconcile import RuntimeReconcileResult, apply_reconcile_decision
from .runtime_reconcile_executor import async_apply_runtime_reconcile_result
from .runtime_reconcile_observation import (
    RuntimeReconcileEvaluation,
    RuntimeReconcileObservation,
    evaluate_runtime_reconcile_observation,
)
from .runtime_state import QueueRunTracking

ADD_QUEUE_ROOM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CONFIG_ENTRY_ID): str,
        vol.Required(CONF_ROOM_ID): vol.Coerce(int),
        vol.Required(CONF_ROOM_NAME): vol.All(str, vol.Length(min=1)),
    }
)
APPLY_RECONCILE_SCHEMA = vol.Schema({vol.Required(CONF_CONFIG_ENTRY_ID): str})
CANCEL_QUEUE_SCHEMA = vol.Schema({vol.Required(CONF_CONFIG_ENTRY_ID): str})
CLEAR_PENDING_QUEUE_SCHEMA = vol.Schema({vol.Required(CONF_CONFIG_ENTRY_ID): str})
EVALUATE_RECONCILE_SCHEMA = vol.Schema({vol.Required(CONF_CONFIG_ENTRY_ID): str})
GET_RUNTIME_STATUS_SCHEMA = vol.Schema({vol.Required(CONF_CONFIG_ENTRY_ID): str})
MOVE_QUEUE_ITEM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CONFIG_ENTRY_ID): str,
        vol.Required(CONF_ITEM_ID): vol.All(str, vol.Length(min=1)),
        vol.Required(CONF_NEW_POSITION): vol.Coerce(int),
    }
)
REMOVE_QUEUE_ITEM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CONFIG_ENTRY_ID): str,
        vol.Required(CONF_ITEM_ID): vol.All(str, vol.Length(min=1)),
    }
)
SKIP_CURRENT_ROOM_SCHEMA = vol.Schema({vol.Required(CONF_CONFIG_ENTRY_ID): str})
START_QUEUE_SCHEMA = vol.Schema({vol.Required(CONF_CONFIG_ENTRY_ID): str})
UPDATE_QUEUE_ITEM_OVERRIDES_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CONFIG_ENTRY_ID): str,
        vol.Required(CONF_ITEM_ID): vol.All(str, vol.Length(min=1)),
        vol.Required(CONF_OVERRIDES): dict,
    }
)


def async_register_services(hass: HomeAssistant) -> None:
    """Register HA Dreame services."""
    if not hass.services.has_service(DOMAIN, SERVICE_ADD_QUEUE_ROOM):

        async def _async_add_queue_room(call: ServiceCall) -> ServiceResponse:
            return _add_queue_room_response(
                hass,
                call.data[CONF_CONFIG_ENTRY_ID],
                room_id=call.data[CONF_ROOM_ID],
                room_name=call.data[CONF_ROOM_NAME],
            )

        hass.services.async_register(
            DOMAIN,
            SERVICE_ADD_QUEUE_ROOM,
            _async_add_queue_room,
            schema=ADD_QUEUE_ROOM_SCHEMA,
            supports_response=SupportsResponse.OPTIONAL,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_APPLY_RECONCILE):

        async def _async_apply_reconcile(call: ServiceCall) -> ServiceResponse:
            return await _async_apply_reconcile_response(
                hass,
                call.data[CONF_CONFIG_ENTRY_ID],
            )

        hass.services.async_register(
            DOMAIN,
            SERVICE_APPLY_RECONCILE,
            _async_apply_reconcile,
            schema=APPLY_RECONCILE_SCHEMA,
            supports_response=SupportsResponse.OPTIONAL,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_CANCEL_QUEUE):

        async def _async_cancel_queue(call: ServiceCall) -> ServiceResponse:
            return await _async_cancel_queue_response(
                hass,
                call.data[CONF_CONFIG_ENTRY_ID],
            )

        hass.services.async_register(
            DOMAIN,
            SERVICE_CANCEL_QUEUE,
            _async_cancel_queue,
            schema=CANCEL_QUEUE_SCHEMA,
            supports_response=SupportsResponse.OPTIONAL,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_CLEAR_PENDING_QUEUE):

        async def _async_clear_pending_queue(call: ServiceCall) -> ServiceResponse:
            return _clear_pending_queue_response(
                hass,
                call.data[CONF_CONFIG_ENTRY_ID],
            )

        hass.services.async_register(
            DOMAIN,
            SERVICE_CLEAR_PENDING_QUEUE,
            _async_clear_pending_queue,
            schema=CLEAR_PENDING_QUEUE_SCHEMA,
            supports_response=SupportsResponse.OPTIONAL,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_GET_RUNTIME_STATUS):

        async def _async_get_runtime_status(call: ServiceCall) -> ServiceResponse:
            return _runtime_status_response(hass, call.data[CONF_CONFIG_ENTRY_ID])

        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_RUNTIME_STATUS,
            _async_get_runtime_status,
            schema=GET_RUNTIME_STATUS_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_EVALUATE_RECONCILE):

        async def _async_evaluate_reconcile(call: ServiceCall) -> ServiceResponse:
            return _evaluate_reconcile_response(
                hass,
                call.data[CONF_CONFIG_ENTRY_ID],
            )

        hass.services.async_register(
            DOMAIN,
            SERVICE_EVALUATE_RECONCILE,
            _async_evaluate_reconcile,
            schema=EVALUATE_RECONCILE_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_REMOVE_QUEUE_ITEM):

        async def _async_remove_queue_item(call: ServiceCall) -> ServiceResponse:
            return _remove_queue_item_response(
                hass,
                call.data[CONF_CONFIG_ENTRY_ID],
                item_id=call.data[CONF_ITEM_ID],
            )

        hass.services.async_register(
            DOMAIN,
            SERVICE_REMOVE_QUEUE_ITEM,
            _async_remove_queue_item,
            schema=REMOVE_QUEUE_ITEM_SCHEMA,
            supports_response=SupportsResponse.OPTIONAL,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_MOVE_QUEUE_ITEM):

        async def _async_move_queue_item(call: ServiceCall) -> ServiceResponse:
            return _move_queue_item_response(
                hass,
                call.data[CONF_CONFIG_ENTRY_ID],
                item_id=call.data[CONF_ITEM_ID],
                new_position=call.data[CONF_NEW_POSITION],
            )

        hass.services.async_register(
            DOMAIN,
            SERVICE_MOVE_QUEUE_ITEM,
            _async_move_queue_item,
            schema=MOVE_QUEUE_ITEM_SCHEMA,
            supports_response=SupportsResponse.OPTIONAL,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_SKIP_CURRENT_ROOM):

        async def _async_skip_current_room(call: ServiceCall) -> ServiceResponse:
            return await _async_skip_current_room_response(
                hass,
                call.data[CONF_CONFIG_ENTRY_ID],
            )

        hass.services.async_register(
            DOMAIN,
            SERVICE_SKIP_CURRENT_ROOM,
            _async_skip_current_room,
            schema=SKIP_CURRENT_ROOM_SCHEMA,
            supports_response=SupportsResponse.OPTIONAL,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_START_QUEUE):

        async def _async_start_queue(call: ServiceCall) -> ServiceResponse:
            return await _async_start_queue_response(
                hass,
                call.data[CONF_CONFIG_ENTRY_ID],
            )

        hass.services.async_register(
            DOMAIN,
            SERVICE_START_QUEUE,
            _async_start_queue,
            schema=START_QUEUE_SCHEMA,
            supports_response=SupportsResponse.OPTIONAL,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_UPDATE_QUEUE_ITEM_OVERRIDES):

        async def _async_update_queue_item_overrides(
            call: ServiceCall,
        ) -> ServiceResponse:
            return _update_queue_item_overrides_response(
                hass,
                call.data[CONF_CONFIG_ENTRY_ID],
                item_id=call.data[CONF_ITEM_ID],
                overrides=call.data[CONF_OVERRIDES],
            )

        hass.services.async_register(
            DOMAIN,
            SERVICE_UPDATE_QUEUE_ITEM_OVERRIDES,
            _async_update_queue_item_overrides,
            schema=UPDATE_QUEUE_ITEM_OVERRIDES_SCHEMA,
            supports_response=SupportsResponse.OPTIONAL,
        )


def async_remove_services(hass: HomeAssistant) -> None:
    """Remove all HA Dreame services."""
    hass.services.async_remove(DOMAIN, SERVICE_ADD_QUEUE_ROOM)
    hass.services.async_remove(DOMAIN, SERVICE_APPLY_RECONCILE)
    hass.services.async_remove(DOMAIN, SERVICE_CANCEL_QUEUE)
    hass.services.async_remove(DOMAIN, SERVICE_CLEAR_PENDING_QUEUE)
    hass.services.async_remove(DOMAIN, SERVICE_EVALUATE_RECONCILE)
    hass.services.async_remove(DOMAIN, SERVICE_GET_RUNTIME_STATUS)
    hass.services.async_remove(DOMAIN, SERVICE_MOVE_QUEUE_ITEM)
    hass.services.async_remove(DOMAIN, SERVICE_REMOVE_QUEUE_ITEM)
    hass.services.async_remove(DOMAIN, SERVICE_SKIP_CURRENT_ROOM)
    hass.services.async_remove(DOMAIN, SERVICE_START_QUEUE)
    hass.services.async_remove(DOMAIN, SERVICE_UPDATE_QUEUE_ITEM_OVERRIDES)


def _runtime_entry(hass: HomeAssistant, config_entry_id: str) -> ConfigEntry:
    """Return a loaded HA Dreame entry for service handling."""
    entry = hass.data.get(DOMAIN, {}).get(config_entry_id)
    if entry is None or not hasattr(entry, "runtime_data"):
        raise HomeAssistantError(f"HA Dreame entry is not loaded: {config_entry_id}")
    return entry


def _add_queue_room_response(
    hass: HomeAssistant,
    config_entry_id: str,
    *,
    room_id: int,
    room_name: str,
) -> dict[str, Any]:
    """Append one room to the runtime queue and return a queue snapshot."""
    entry = _runtime_entry(hass, config_entry_id)
    runtime_data = entry.runtime_data

    try:
        queue_state = add_room(
            runtime_data.queue_state,
            room_id=room_id,
            room_name=room_name,
        )
    except QueueError as err:
        raise HomeAssistantError(str(err)) from err

    runtime_data.set_queue_state(queue_state)
    return _queue_status_response(entry)


def _clear_pending_queue_response(
    hass: HomeAssistant,
    config_entry_id: str,
) -> dict[str, Any]:
    """Clear pending queue items and return a queue snapshot."""
    entry = _runtime_entry(hass, config_entry_id)
    runtime_data = entry.runtime_data

    try:
        queue_state = clear_pending(runtime_data.queue_state)
    except QueueError as err:
        raise HomeAssistantError(str(err)) from err

    runtime_data.set_queue_state(queue_state)
    return _queue_status_response(entry)


async def _async_apply_reconcile_response(
    hass: HomeAssistant,
    config_entry_id: str,
) -> dict[str, Any]:
    """Evaluate and apply one manual runtime reconcile decision."""
    entry = _runtime_entry(hass, config_entry_id)
    runtime_data = entry.runtime_data

    if not runtime_data.commands_enabled:
        raise HomeAssistantError("HA Dreame robot commands are disabled")

    observation, evaluation = _runtime_reconcile_evaluation(hass, runtime_data)
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
    return {
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        "applied": _reconcile_result_response(applied_result),
        "decision": _reconcile_decision_response(evaluation),
        "evaluation": _reconcile_evaluation_response(evaluation),
        "observation": _reconcile_observation_response(observation),
        "queue": _queue_status_response(entry),
    }


async def _async_cancel_queue_response(
    hass: HomeAssistant,
    config_entry_id: str,
) -> dict[str, Any]:
    """Cancel the runtime queue and send the robot back to base."""
    entry = _runtime_entry(hass, config_entry_id)
    runtime_data = entry.runtime_data

    if not runtime_data.commands_enabled:
        raise HomeAssistantError("HA Dreame robot commands are disabled")

    await hass.services.async_call(
        VACUUM_DOMAIN,
        "return_to_base",
        {ATTR_ENTITY_ID: runtime_data.vacuum_entity_id},
        blocking=True,
    )

    try:
        queue_state = cancel_run(runtime_data.queue_state, reason="canceled_by_user")
    except QueueError as err:
        raise HomeAssistantError(str(err)) from err

    runtime_data.set_queue_state(queue_state)
    runtime_data.set_run_tracking(None)
    return _queue_status_response(entry)


async def _async_skip_current_room_response(
    hass: HomeAssistant,
    config_entry_id: str,
) -> dict[str, Any]:
    """Skip the current room and continue or finish the runtime queue."""
    entry = _runtime_entry(hass, config_entry_id)
    runtime_data = entry.runtime_data

    if not runtime_data.commands_enabled:
        raise HomeAssistantError("HA Dreame robot commands are disabled")

    try:
        queue_state = skip_current_room(runtime_data.queue_state, reason="skip_pressed")
        item = current_item(queue_state)
        plan = (
            build_room_dispatch_plan(
                item,
                vacuum_entity_id=runtime_data.vacuum_entity_id,
            )
            if item is not None
            else None
        )
    except QueueError as err:
        raise HomeAssistantError(str(err)) from err

    if queue_state.run_state == "running":
        await hass.services.async_call(
            VACUUM_DOMAIN,
            "stop",
            {ATTR_ENTITY_ID: runtime_data.vacuum_entity_id},
            blocking=True,
        )
        if plan is None:
            raise HomeAssistantError("No next room to dispatch")
        await async_execute_dispatch_plan(
            hass,
            plan,
            commands_enabled=runtime_data.commands_enabled,
        )
        runtime_data.set_queue_state(queue_state)
        runtime_data.set_run_tracking(_new_run_tracking(queue_state))
        return _queue_status_response(entry)

    await hass.services.async_call(
        VACUUM_DOMAIN,
        "return_to_base",
        {ATTR_ENTITY_ID: runtime_data.vacuum_entity_id},
        blocking=True,
    )
    runtime_data.set_queue_state(queue_state)
    runtime_data.set_run_tracking(None)
    return _queue_status_response(entry)


def _remove_queue_item_response(
    hass: HomeAssistant,
    config_entry_id: str,
    *,
    item_id: str,
) -> dict[str, Any]:
    """Remove one pending queue item and return a queue snapshot."""
    entry = _runtime_entry(hass, config_entry_id)
    runtime_data = entry.runtime_data

    try:
        queue_state = remove_item(runtime_data.queue_state, item_id=item_id)
    except QueueError as err:
        raise HomeAssistantError(str(err)) from err

    runtime_data.set_queue_state(queue_state)
    return _queue_status_response(entry)


def _move_queue_item_response(
    hass: HomeAssistant,
    config_entry_id: str,
    *,
    item_id: str,
    new_position: int,
) -> dict[str, Any]:
    """Move one pending queue item and return a queue snapshot."""
    entry = _runtime_entry(hass, config_entry_id)
    runtime_data = entry.runtime_data

    try:
        queue_state = move_item(
            runtime_data.queue_state,
            item_id=item_id,
            new_position=new_position,
        )
    except QueueError as err:
        raise HomeAssistantError(str(err)) from err

    runtime_data.set_queue_state(queue_state)
    return _queue_status_response(entry)


def _update_queue_item_overrides_response(
    hass: HomeAssistant,
    config_entry_id: str,
    *,
    item_id: str,
    overrides: dict[str, Any],
) -> dict[str, Any]:
    """Update one pending queue item's overrides and return a queue snapshot."""
    entry = _runtime_entry(hass, config_entry_id)
    runtime_data = entry.runtime_data

    try:
        queue_state = update_item_overrides(
            runtime_data.queue_state,
            item_id=item_id,
            overrides=overrides,
        )
    except QueueError as err:
        raise HomeAssistantError(str(err)) from err

    runtime_data.set_queue_state(queue_state)
    return _queue_status_response(entry)


async def _async_start_queue_response(
    hass: HomeAssistant,
    config_entry_id: str,
) -> dict[str, Any]:
    """Start queue execution and dispatch the first pending room."""
    entry = _runtime_entry(hass, config_entry_id)
    runtime_data = entry.runtime_data

    if not runtime_data.commands_enabled:
        raise HomeAssistantError("HA Dreame robot commands are disabled")

    try:
        queue_state = start_run(runtime_data.queue_state)
        item = current_item(queue_state)
        if item is None:
            raise HomeAssistantError("No current room to dispatch")
        plan = build_room_dispatch_plan(
            item,
            vacuum_entity_id=runtime_data.vacuum_entity_id,
        )
    except QueueError as err:
        raise HomeAssistantError(str(err)) from err

    await async_execute_dispatch_plan(
        hass,
        plan,
        commands_enabled=runtime_data.commands_enabled,
    )

    runtime_data.set_queue_state(queue_state)
    runtime_data.set_run_tracking(_new_run_tracking(queue_state))
    return _queue_status_response(entry)


def _runtime_status_response(hass: HomeAssistant, config_entry_id: str) -> dict[str, Any]:
    """Return read-only runtime status for one HA Dreame entry."""
    entry = _runtime_entry(hass, config_entry_id)

    runtime_data = entry.runtime_data
    return {
        CONF_ALLOW_ROBOT_COMMANDS: runtime_data.commands_enabled,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        ATTR_RUN_TRACKING: _run_tracking_response(runtime_data.run_tracking),
        CONF_VACUUM_ENTITY_ID: runtime_data.vacuum_entity_id,
    }


def _evaluate_reconcile_response(hass: HomeAssistant, config_entry_id: str) -> dict[str, Any]:
    """Return a read-only runtime reconcile observation and decision."""
    entry = _runtime_entry(hass, config_entry_id)
    observation, evaluation = _runtime_reconcile_evaluation(hass, entry.runtime_data)

    return {
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        "decision": _reconcile_decision_response(evaluation),
        "evaluation": _reconcile_evaluation_response(evaluation),
        "observation": _reconcile_observation_response(observation),
    }


def _runtime_reconcile_evaluation(
    hass: HomeAssistant,
    runtime_data: Any,
) -> tuple[RuntimeReconcileObservation, RuntimeReconcileEvaluation]:
    """Build and evaluate one runtime reconcile observation."""
    observation = build_runtime_reconcile_observation(
        hass,
        vacuum_entity_id=runtime_data.vacuum_entity_id,
        entity_ids=runtime_data.observation_entity_ids,
    )
    evaluation = evaluate_runtime_reconcile_observation(
        runtime_data.queue_state,
        runtime_data.run_tracking,
        observation,
        now=datetime.now(UTC),
    )

    return observation, evaluation


def _reconcile_observation_response(
    observation: RuntimeReconcileObservation,
) -> dict[str, Any]:
    """Return a serializable reconcile observation snapshot."""
    return {
        "cleaning_progress": observation.cleaning_progress,
        "dock_prep_resume_ready": observation.dock_prep_resume_ready,
        "force_retry_after_recovery": observation.force_retry_after_recovery,
        "is_dock_prep_paused": observation.is_dock_prep_paused,
        "is_dock_prep_state": observation.is_dock_prep_state,
        "is_mop_maintenance_state": observation.is_mop_maintenance_state,
        "is_returning_state": observation.is_returning_state,
        "observed_room_id": observation.observed_room_id,
        "observed_room_name": observation.observed_room_name,
        "pause_waiting_seen": observation.pause_waiting_seen,
        "task_status": observation.task_status,
        "vacuum_error_code": observation.vacuum_error_code,
        "vacuum_state": observation.vacuum_state,
    }


def _reconcile_evaluation_response(
    evaluation: RuntimeReconcileEvaluation,
) -> dict[str, Any]:
    """Return serializable reconcile evaluation metadata."""
    return {
        "awaiting_completion_event": evaluation.awaiting_completion_event,
        "expected_room_id": evaluation.expected_room_id,
        "expected_room_name": evaluation.expected_room_name,
        "observed_room_id": evaluation.observed_room_id,
        "observed_room_name": evaluation.observed_room_name,
        "seconds_since_last_command": evaluation.seconds_since_last_command,
    }


def _reconcile_decision_response(
    evaluation: RuntimeReconcileEvaluation,
) -> dict[str, Any]:
    """Return a serializable reconcile decision snapshot."""
    decision = evaluation.decision
    return {
        "complete_current_room": decision.complete_current_room,
        "event_reasons": list(decision.event_reasons),
        "mark_out_of_sync_reason": decision.mark_out_of_sync_reason,
        "reset_dispatch_retry_count": decision.reset_dispatch_retry_count,
        "resume_current_room": decision.resume_current_room,
        "retry_current_room": decision.retry_current_room,
        "set_task_status_cleared_since_dispatch": decision.set_task_status_cleared_since_dispatch,
    }


def _reconcile_result_response(result: RuntimeReconcileResult) -> dict[str, Any]:
    """Return a serializable applied reconcile result snapshot."""
    return {
        "command_intent": result.command_intent,
        "command_item_id": result.command_item_id,
        "event_reasons": list(result.event_reasons),
    }


def _queue_status_response(entry: ConfigEntry) -> dict[str, Any]:
    """Return a compact runtime queue status response."""
    queue_state = entry.runtime_data.queue_state
    return {
        ATTR_COMPLETED_ITEMS: count_queue_items(queue_state, "completed"),
        ATTR_PENDING_ITEMS: count_queue_items(queue_state, "pending"),
        ATTR_QUEUE_ITEMS: queue_item_snapshots(queue_state),
        ATTR_RUNNING_ITEMS: count_queue_items(queue_state, "running"),
        ATTR_TOTAL_ITEMS: len(queue_state.items),
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        "run_state": queue_state.run_state,
    }


def _new_run_tracking(queue_state: QueueState) -> QueueRunTracking:
    """Build run tracking for a queue state that has just been dispatched."""
    if queue_state.run_id is None or queue_state.current_item_id is None:
        raise HomeAssistantError("Queue run tracking requires an active run")

    return QueueRunTracking(
        run_id=queue_state.run_id,
        current_item_id=queue_state.current_item_id,
        last_command_at=datetime.now(UTC).isoformat(),
    )


def _run_tracking_response(run_tracking: QueueRunTracking | None) -> dict[str, Any] | None:
    """Return a serializable runtime run tracking snapshot."""
    if run_tracking is None:
        return None

    return {
        ATTR_ACTIVE_ROOM_MISMATCH_STREAK: run_tracking.active_room_mismatch_streak,
        ATTR_CURRENT_ITEM_ID: run_tracking.current_item_id,
        ATTR_DISPATCH_RETRY_COUNT: run_tracking.dispatch_retry_count,
        ATTR_LAST_COMMAND_AT: run_tracking.last_command_at,
        ATTR_RUN_ID: run_tracking.run_id,
        ATTR_TASK_STATUS_CLEARED_SINCE_DISPATCH: (run_tracking.task_status_cleared_since_dispatch),
    }

"""Service handlers for HA Dreame."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable, Mapping
from contextlib import asynccontextmanager
from dataclasses import asdict, replace
from datetime import UTC, datetime
import logging
from typing import Any, NamedTuple

import voluptuous as vol

from homeassistant.const import ATTR_ENTITY_ID, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import HomeAssistantError

from .const import (
    ATTR_ACTIVE_ROOM_CONFIRMED_SINCE_DISPATCH,
    ATTR_COMPLETED_ITEMS,
    ATTR_CURRENT_ITEM_ID,
    ATTR_DISPATCH_RETRY_COUNT,
    ATTR_LAST_COMMAND_AT,
    ATTR_PENDING_ITEMS,
    ATTR_POST_RUN_MAINTENANCE_SEEN,
    ATTR_QUEUE_ITEMS,
    ATTR_RUN_ID,
    ATTR_RUN_TRACKING,
    ATTR_RUNNING_ITEMS,
    ATTR_TASK_STATUS_CLEARED_SINCE_DISPATCH,
    ATTR_TOTAL_ITEMS,
    CONF_ALLOW_ROBOT_COMMANDS,
    CONF_CONFIG_ENTRY_ID,
    CONF_FIELD,
    CONF_ITEM_ID,
    CONF_NEW_POSITION,
    CONF_OVERRIDES,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_VALUE,
    CONF_VACUUM_ENTITY_ID,
    DOMAIN,
    SERVICE_ADD_QUEUE_ROOM,
    SERVICE_CANCEL_QUEUE,
    SERVICE_CLEAR_PENDING_QUEUE,
    SERVICE_EVALUATE_RECONCILE,
    SERVICE_GET_CONTROL_READINESS,
    SERVICE_GET_RUNTIME_STATUS,
    SERVICE_MOVE_QUEUE_ITEM,
    SERVICE_REMOVE_QUEUE_ITEM,
    SERVICE_RESUME_QUEUE,
    SERVICE_SKIP_CURRENT_ROOM,
    SERVICE_START_QUEUE,
    SERVICE_UPDATE_QUEUE_ITEM_OVERRIDES,
    SERVICE_UPDATE_RUNNING_OVERRIDE,
    VACUUM_DOMAIN,
    companion_entity_id,
)
from .dispatch_executor import async_dispatch_current_room, current_room_dispatch_plan
from .audit import async_call_robot_service, service_audit
from .queue_core import (
    DispatchTracking,
    QueueError,
    QueueState,
    add_room,
    cancel_run,
    clear_pending,
    current_item,
    external_takeover,
    move_item,
    remove_item,
    skip_current_room,
    start_run,
    update_item_overrides,
)
from .queue_snapshot import count_queue_items, queue_item_snapshots
from .runtime import HaDreameRuntimeData
from .reconcile import ReconcileEvaluation, evaluate_reconcile
from .reconcile_core import Observation, is_meaningful_error
from .runtime_observation import normalize_signal

_LOGGER = logging.getLogger(__name__)

ENTRY_SCHEMA = vol.Schema({vol.Required(CONF_CONFIG_ENTRY_ID): str})
ADD_QUEUE_ROOM_SCHEMA = ENTRY_SCHEMA.extend(
    {
        vol.Required(CONF_ROOM_ID): vol.Coerce(int),
        vol.Required(CONF_ROOM_NAME): vol.All(str, vol.Length(min=1)),
    }
)
ITEM_SCHEMA = ENTRY_SCHEMA.extend({vol.Required(CONF_ITEM_ID): vol.All(str, vol.Length(min=1))})
MOVE_QUEUE_ITEM_SCHEMA = ITEM_SCHEMA.extend({vol.Required(CONF_NEW_POSITION): vol.Coerce(int)})
UPDATE_QUEUE_ITEM_OVERRIDES_SCHEMA = ITEM_SCHEMA.extend({vol.Required(CONF_OVERRIDES): dict})
RUNNING_OVERRIDE_SUCTION_OPTIONS = {
    0: "quiet",
    1: "standard",
    2: "strong",
    3: "turbo",
}
RUNNING_OVERRIDE_WATER_VALUES = {
    1: 8,
    2: 16,
    3: 24,
}
RUNNING_OVERRIDE_FIELDS = ("suction_level", "water_volume")
UPDATE_RUNNING_OVERRIDE_SCHEMA = ENTRY_SCHEMA.extend(
    {
        vol.Required(CONF_FIELD): vol.In(RUNNING_OVERRIDE_FIELDS),
        vol.Required(CONF_VALUE): vol.Coerce(int),
    }
)


ServiceHandler = Callable[
    [HomeAssistant, ConfigEntry, Mapping[str, Any]], Awaitable[dict[str, Any]]
]


class _Service(NamedTuple):
    """One HA Dreame service.

    Read-only services answer without the operation lock and audit trail. All others
    serialize queue mutations and robot commands per entry and are audited.
    """

    handler: ServiceHandler
    schema: vol.Schema = ENTRY_SCHEMA
    read_only: bool = False


def async_register_services(hass: HomeAssistant) -> None:
    """Register HA Dreame services."""
    for name, service in SERVICES.items():
        if hass.services.has_service(DOMAIN, name):
            continue

        async def _async_handle(call: ServiceCall, service: _Service = service) -> ServiceResponse:
            entry = _runtime_entry(hass, call.data[CONF_CONFIG_ENTRY_ID])
            if service.read_only:
                return await service.handler(hass, entry, call.data)
            async with _async_runtime_operation(hass, entry, call):
                return await service.handler(hass, entry, call.data)

        hass.services.async_register(
            DOMAIN,
            name,
            _async_handle,
            schema=service.schema,
            supports_response=(
                SupportsResponse.ONLY if service.read_only else SupportsResponse.OPTIONAL
            ),
        )


def async_remove_services(hass: HomeAssistant) -> None:
    """Remove all HA Dreame services."""
    for name in SERVICES:
        hass.services.async_remove(DOMAIN, name)


def _require_commands(runtime_data: HaDreameRuntimeData) -> None:
    """Reject a command handler before it changes queue state without the robot."""
    if not runtime_data.commands_enabled:
        raise HomeAssistantError("HA Dreame robot commands are disabled")


def _runtime_entry(hass: HomeAssistant, config_entry_id: str) -> ConfigEntry:
    """Return a loaded HA Dreame entry for service handling."""
    entry = hass.data.get(DOMAIN, {}).get(config_entry_id)
    if entry is None or not hasattr(entry, "runtime_data"):
        raise HomeAssistantError(f"HA Dreame entry is not loaded: {config_entry_id}")
    return entry


@asynccontextmanager
async def _async_runtime_operation(
    hass: HomeAssistant,
    entry: ConfigEntry,
    call: ServiceCall,
) -> AsyncIterator[None]:
    """Serialize one queue mutation or robot command for a loaded entry."""
    runtime_data = entry.runtime_data
    async with runtime_data.operation_lock:
        if (
            hass.data.get(DOMAIN, {}).get(entry.entry_id) is not entry
            or getattr(entry, "runtime_data", None) is not runtime_data
            or runtime_data.unload_requested.is_set()
        ):
            raise HomeAssistantError(f"HA Dreame entry is not loaded: {entry.entry_id}")
        with service_audit(runtime_data, call):
            yield


def _mutate_queue(
    runtime_data: HaDreameRuntimeData,
    mutation: Callable[..., QueueState],
    **kwargs: Any,
) -> None:
    """Apply one pure queue transition to the runtime queue."""
    try:
        runtime_data.set_queue_state(mutation(runtime_data.queue_state, **kwargs))
    except QueueError as err:
        raise HomeAssistantError(str(err)) from err


def _queue_mutation(mutation: Callable[..., QueueState], *fields: str) -> ServiceHandler:
    """Return a handler that applies a queue transition with call fields as arguments."""

    async def _async_handle(
        hass: HomeAssistant, entry: ConfigEntry, data: Mapping[str, Any]
    ) -> dict[str, Any]:
        _mutate_queue(entry.runtime_data, mutation, **{field: data[field] for field in fields})
        return _queue_status_response(entry)

    return _async_handle


async def _async_cancel_queue(
    hass: HomeAssistant, entry: ConfigEntry, data: Mapping[str, Any]
) -> dict[str, Any]:
    """Cancel the runtime queue and send the robot back to base."""
    runtime_data = entry.runtime_data

    _require_commands(runtime_data)

    if runtime_data.queue_state.run_state == "waiting_for_tanks":
        runtime_data.set_queue_state(cancel_run(runtime_data.queue_state))
        return _queue_status_response(entry)

    await async_call_robot_service(
        hass,
        runtime_data,
        VACUUM_DOMAIN,
        "stop",
        {ATTR_ENTITY_ID: runtime_data.vacuum_entity_id},
    )
    await async_call_robot_service(
        hass,
        runtime_data,
        VACUUM_DOMAIN,
        "return_to_base",
        {ATTR_ENTITY_ID: runtime_data.vacuum_entity_id},
    )

    try:
        queue_state = cancel_run(runtime_data.queue_state, reason="canceled_by_user")
    except QueueError as err:
        raise HomeAssistantError(str(err)) from err

    runtime_data.set_queue_state(queue_state)
    return _queue_status_response(entry)


async def _async_skip_current_room(
    hass: HomeAssistant, entry: ConfigEntry, data: Mapping[str, Any]
) -> dict[str, Any]:
    """Skip the current room and continue or finish the runtime queue."""
    runtime_data = entry.runtime_data

    try:
        queue_state = skip_current_room(runtime_data.queue_state, reason="skip_pressed")
    except QueueError as err:
        raise HomeAssistantError(str(err)) from err
    plan = (
        current_room_dispatch_plan(hass, runtime_data, queue_state)
        if queue_state.run_state == "running"
        else None
    )

    # Stop the skipped room first, before the next dispatch or, as cancel does, before
    # docking: a bare dock command is ignored during dock preparation.
    await async_call_robot_service(
        hass,
        runtime_data,
        VACUUM_DOMAIN,
        "stop",
        {ATTR_ENTITY_ID: runtime_data.vacuum_entity_id},
    )
    if plan is not None:
        await async_dispatch_current_room(hass, runtime_data, queue_state, plan=plan)
        return _queue_status_response(entry)

    await async_call_robot_service(
        hass,
        runtime_data,
        VACUUM_DOMAIN,
        "return_to_base",
        {ATTR_ENTITY_ID: runtime_data.vacuum_entity_id},
    )
    runtime_data.set_queue_state(queue_state)
    return _queue_status_response(entry)


async def _async_resume_queue(
    hass: HomeAssistant, entry: ConfigEntry, data: Mapping[str, Any]
) -> dict[str, Any]:
    """Resume an interrupted active queue run through the vacuum start command."""
    runtime_data = entry.runtime_data

    if runtime_data.queue_state.run_state != "running":
        raise HomeAssistantError("Queue is not running")

    dispatch = runtime_data.queue_state.dispatch
    if dispatch is None:
        raise HomeAssistantError("Queue run tracking is not active")

    observation = runtime_data.observe(hass)
    robot_status = _robot_status_response(observation)
    if observation.water_tank_block_reason:
        raise HomeAssistantError(observation.water_tank_block_reason)
    if not robot_status["interrupted"]:
        raise HomeAssistantError("Robot is not waiting for user action")

    await async_call_robot_service(
        hass,
        runtime_data,
        VACUUM_DOMAIN,
        "start",
        {ATTR_ENTITY_ID: runtime_data.vacuum_entity_id},
    )
    runtime_data.set_queue_state(
        replace(
            runtime_data.queue_state,
            dispatch=replace(
                dispatch,
                dispatch_retry_count=0,
                last_command_at=datetime.now(UTC),
                post_run_maintenance_seen=False,
            ),
        )
    )
    return {
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        CONF_VACUUM_ENTITY_ID: runtime_data.vacuum_entity_id,
        "resumed": True,
        "robot_status": robot_status,
    }


async def _async_update_running_override(
    hass: HomeAssistant, entry: ConfigEntry, data: Mapping[str, Any]
) -> dict[str, Any]:
    """Update a live running override through command-gated companion entities."""
    runtime_data = entry.runtime_data
    field, value = data[CONF_FIELD], data[CONF_VALUE]

    if runtime_data.queue_state.run_state != "running":
        raise HomeAssistantError("Queue is not running")

    entity_id, domain, service, service_data = _running_override_service_call(
        runtime_data.vacuum_entity_id,
        field=field,
        value=value,
    )
    if hass.states.get(entity_id) is None:
        raise HomeAssistantError(f"Running override entity is not available: {entity_id}")

    await async_call_robot_service(hass, runtime_data, domain, service, service_data)
    return {
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        CONF_FIELD: field,
        CONF_VALUE: value,
        ATTR_ENTITY_ID: entity_id,
    }


async def _async_start_queue(
    hass: HomeAssistant,
    entry: ConfigEntry,
    data: Mapping[str, Any] | None = None,
    observation: Observation | None = None,
) -> dict[str, Any]:
    """Start queue execution and dispatch the first pending room."""
    runtime_data: HaDreameRuntimeData = entry.runtime_data

    _require_commands(runtime_data)

    if observation is None:
        observation = runtime_data.observe(hass)
    if observation.task_status and normalize_signal(observation.task_status) != "completed":
        raise HomeAssistantError("Cannot start queue while a previous robot task is still active")
    try:
        queue_state = start_run(runtime_data.queue_state)
    except QueueError as err:
        raise HomeAssistantError(str(err)) from err
    # Validate the room's profile before accepting a deferred start.
    plan = current_room_dispatch_plan(hass, runtime_data, queue_state)

    if observation.water_tank_block_reason:
        if not _entity_available(hass, runtime_data.vacuum_entity_id):
            raise HomeAssistantError("Robot is unavailable")
        runtime_data.set_queue_state(
            replace(runtime_data.queue_state, run_state="waiting_for_tanks")
        )
        return _queue_status_response(entry)

    await async_dispatch_current_room(hass, runtime_data, queue_state, plan=plan)
    item = current_item(queue_state)
    assert item is not None
    _LOGGER.info(
        ("HA Dreame queue started vacuum=%s run_id=%s item_id=%s room_id=%s room_name=%s"),
        runtime_data.vacuum_entity_id,
        queue_state.run_id,
        item.item_id,
        item.room_id,
        item.room_name,
    )
    return _queue_status_response(entry)


async def async_start_waiting_queue(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Release a tank-blocked start once, under the caller's operation lock."""
    runtime_data = entry.runtime_data
    if runtime_data.queue_state.run_state != "waiting_for_tanks":
        return
    observation = runtime_data.observe(hass)
    if (
        observation.water_tank_block_reason
        or normalize_signal(observation.vacuum_state)
        in {"", "unknown", "unavailable", "error", "paused", "cleaning", "returning"}
        or observation.robot_paused
        or normalize_signal(observation.task_status) != "completed"
        or is_meaningful_error(normalize_signal(observation.vacuum_error_code))
    ):
        return
    # Disarm before dispatch: a service failure must not create an invisible retry loop.
    runtime_data.set_queue_state(replace(runtime_data.queue_state, run_state="idle"))
    try:
        await _async_start_queue(hass, entry, observation=observation)
    except Exception:
        runtime_data.set_queue_state(
            external_takeover(runtime_data.queue_state, reason="deferred_start_dispatch_failed")
        )
        raise


def _running_override_service_call(
    vacuum_entity_id: str,
    *,
    field: str,
    value: int,
) -> tuple[str, str, str, dict[str, Any]]:
    """Return the companion entity service call for one running override."""
    if field == "suction_level":
        option = RUNNING_OVERRIDE_SUCTION_OPTIONS.get(value)
        if option is None:
            raise HomeAssistantError("Invalid running override suction_level value")
        entity_id = companion_entity_id(vacuum_entity_id, "select", "suction_level")
        return (
            entity_id,
            "select",
            "select_option",
            {ATTR_ENTITY_ID: entity_id, "option": option},
        )

    if field == "water_volume":
        wetness = RUNNING_OVERRIDE_WATER_VALUES.get(value)
        if wetness is None:
            raise HomeAssistantError("Invalid running override water_volume value")
        entity_id = companion_entity_id(vacuum_entity_id, "number", "wetness_level")
        return (
            entity_id,
            "number",
            "set_value",
            {ATTR_ENTITY_ID: entity_id, CONF_VALUE: wetness},
        )

    raise HomeAssistantError(f"Invalid running override field: {field}")


async def _async_control_readiness(
    hass: HomeAssistant, entry: ConfigEntry, data: Mapping[str, Any]
) -> dict[str, Any]:
    """Return a read-only manual control preflight snapshot."""
    runtime_data = entry.runtime_data
    queue_state = runtime_data.queue_state
    pending_items = count_queue_items(queue_state, "pending")
    running_items = count_queue_items(queue_state, "running")
    vacuum_available = _entity_available(hass, runtime_data.vacuum_entity_id)
    companion_entities = _running_override_companion_entities(
        hass,
        runtime_data.vacuum_entity_id,
    )
    running_override_ready = queue_state.run_state == "running" and all(
        entity["available"] for entity in companion_entities.values()
    )
    robot_status = _robot_status_response(runtime_data.observe(hass))
    available_actions: list[str] = []
    blocking_reasons: list[str] = []

    if not vacuum_available:
        blocking_reasons.append("vacuum_entity_unavailable")
    if not runtime_data.commands_enabled:
        blocking_reasons.append("robot_commands_disabled")

    can_offer_command_actions = runtime_data.commands_enabled and vacuum_available
    tank_block = any(
        reason.endswith("_tank_not_ready") for reason in robot_status["interruption_reasons"]
    )
    if tank_block:
        blocking_reasons.extend(
            reason
            for reason in robot_status["interruption_reasons"]
            if reason.endswith("_tank_not_ready")
        )
    if queue_state.run_state == "idle":
        if can_offer_command_actions and pending_items > 0:
            available_actions.append(SERVICE_START_QUEUE)
        elif pending_items == 0:
            blocking_reasons.append("queue_has_no_pending_items")
    elif queue_state.run_state == "waiting_for_tanks":
        available_actions.append(SERVICE_CANCEL_QUEUE)
    elif queue_state.run_state == "running":
        if can_offer_command_actions:
            if robot_status["interrupted"]:
                if not tank_block:
                    available_actions.append(SERVICE_RESUME_QUEUE)
                available_actions.append(SERVICE_CANCEL_QUEUE)
            else:
                available_actions.extend([SERVICE_CANCEL_QUEUE, SERVICE_SKIP_CURRENT_ROOM])
            if running_override_ready and not robot_status["interrupted"]:
                available_actions.append(SERVICE_UPDATE_RUNNING_OVERRIDE)
        if not running_override_ready and not robot_status["interrupted"]:
            blocking_reasons.append("running_override_entities_unavailable")
    elif can_offer_command_actions:
        blocking_reasons.append("queue_state_not_actionable")

    return {
        CONF_ALLOW_ROBOT_COMMANDS: runtime_data.commands_enabled,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        CONF_VACUUM_ENTITY_ID: runtime_data.vacuum_entity_id,
        ATTR_PENDING_ITEMS: pending_items,
        ATTR_RUNNING_ITEMS: running_items,
        "available_actions": available_actions,
        "blocking_reasons": blocking_reasons,
        "companion_entities": companion_entities,
        "queue_run_state": queue_state.run_state,
        "ready_for_control_window": bool(available_actions),
        "ready_for_read_only_observation": vacuum_available,
        "robot_status": robot_status,
        "running_override_ready": running_override_ready,
        "vacuum_available": vacuum_available,
    }


def _running_override_companion_entities(
    hass: HomeAssistant,
    vacuum_entity_id: str,
) -> dict[str, dict[str, Any]]:
    """Return readiness for companion entities used by running overrides."""
    suction_entity_id, *_ = _running_override_service_call(
        vacuum_entity_id,
        field="suction_level",
        value=0,
    )
    water_entity_id, *_ = _running_override_service_call(
        vacuum_entity_id,
        field="water_volume",
        value=1,
    )

    return {
        "suction_level": _companion_entity_response(hass, suction_entity_id),
        "water_volume": _companion_entity_response(hass, water_entity_id),
    }


def _companion_entity_response(
    hass: HomeAssistant,
    entity_id: str,
) -> dict[str, Any]:
    """Return a compact companion entity readiness response."""
    return {
        "available": _entity_available(hass, entity_id),
        "entity_id": entity_id,
    }


def _entity_available(hass: HomeAssistant, entity_id: str) -> bool:
    """Return whether an entity exists with a usable current state."""
    state = hass.states.get(entity_id)
    return state is not None and state.state not in {STATE_UNAVAILABLE, STATE_UNKNOWN}


async def _async_runtime_status(
    hass: HomeAssistant, entry: ConfigEntry, data: Mapping[str, Any]
) -> dict[str, Any]:
    """Return read-only runtime status for one HA Dreame entry."""

    runtime_data = entry.runtime_data
    return {
        CONF_ALLOW_ROBOT_COMMANDS: runtime_data.commands_enabled,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        ATTR_RUN_TRACKING: _run_tracking_response(runtime_data.queue_state),
        "recent_activity": list(runtime_data.recent_activity),
        "robot_status": _robot_status_response(runtime_data.observe(hass)),
        CONF_VACUUM_ENTITY_ID: runtime_data.vacuum_entity_id,
    }


def _robot_status_response(observation: Observation) -> dict[str, Any]:
    """Return robot interruption status derived from read-only companion entities."""
    vacuum_state = normalize_signal(observation.vacuum_state)
    task_status = normalize_signal(observation.task_status)
    error_code = normalize_signal(observation.vacuum_error_code)

    interruption_reasons: list[str] = []
    if vacuum_state == "paused":
        interruption_reasons.append("vacuum_paused")
    elif observation.robot_paused:
        interruption_reasons.append("robot_paused")
    if observation.water_tank_block_reason:
        interruption_reasons.append(observation.water_tank_block_reason)
    if task_status.endswith("_paused"):
        interruption_reasons.append("task_status_paused")
    interruption_context = bool(interruption_reasons) or vacuum_state == "error"
    if vacuum_state == "error":
        interruption_reasons.append(
            f"vacuum_error:{error_code}" if is_meaningful_error(error_code) else "vacuum_error"
        )
    elif interruption_context and is_meaningful_error(error_code):
        interruption_reasons.append(f"vacuum_error:{error_code}")

    return {
        "error_code": error_code,
        "interruption_reasons": interruption_reasons,
        "interrupted": bool(interruption_reasons),
        "task_status": task_status,
        "vacuum_state": vacuum_state,
    }


async def _async_evaluate_reconcile(
    hass: HomeAssistant, entry: ConfigEntry, data: Mapping[str, Any]
) -> dict[str, Any]:
    """Return a read-only runtime reconcile observation and decision."""
    return _reconcile_response(entry, evaluate_reconcile(hass, entry.runtime_data))


def _reconcile_response(entry: ConfigEntry, evaluation: ReconcileEvaluation) -> dict[str, Any]:
    """Return a serializable debug snapshot of one reconcile evaluation."""
    decision = evaluation.decision
    item = evaluation.item
    return {
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        "decision": (
            None
            if decision is None
            else {**asdict(decision), "tracking": _dispatch_response(decision.tracking)}
        ),
        "evaluation": {
            "awaiting_completion_event": decision is not None,
            "expected_room_id": item.room_id if item else None,
            "expected_room_name": item.room_name if item else None,
            "seconds_since_last_command": evaluation.seconds_since_command,
        },
        "observation": asdict(evaluation.observation),
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


def _run_tracking_response(queue_state: QueueState) -> dict[str, Any] | None:
    """Return a serializable snapshot of the current room's dispatch tracking."""
    if queue_state.dispatch is None:
        return None
    return {
        **_dispatch_response(queue_state.dispatch),
        ATTR_CURRENT_ITEM_ID: queue_state.current_item_id,
        ATTR_RUN_ID: queue_state.run_id,
    }


def _dispatch_response(dispatch: DispatchTracking) -> dict[str, Any]:
    """Return serializable dispatch tracking fields."""
    return {
        ATTR_ACTIVE_ROOM_CONFIRMED_SINCE_DISPATCH: dispatch.active_room_confirmed_since_dispatch,
        ATTR_DISPATCH_RETRY_COUNT: dispatch.dispatch_retry_count,
        ATTR_LAST_COMMAND_AT: dispatch.last_command_at.isoformat(),
        ATTR_POST_RUN_MAINTENANCE_SEEN: dispatch.post_run_maintenance_seen,
        ATTR_TASK_STATUS_CLEARED_SINCE_DISPATCH: dispatch.task_status_cleared_since_dispatch,
    }


SERVICES: dict[str, _Service] = {
    SERVICE_ADD_QUEUE_ROOM: _Service(
        _queue_mutation(add_room, CONF_ROOM_ID, CONF_ROOM_NAME), ADD_QUEUE_ROOM_SCHEMA
    ),
    SERVICE_CANCEL_QUEUE: _Service(_async_cancel_queue),
    SERVICE_CLEAR_PENDING_QUEUE: _Service(_queue_mutation(clear_pending)),
    SERVICE_EVALUATE_RECONCILE: _Service(_async_evaluate_reconcile, read_only=True),
    SERVICE_GET_CONTROL_READINESS: _Service(_async_control_readiness, read_only=True),
    SERVICE_GET_RUNTIME_STATUS: _Service(_async_runtime_status, read_only=True),
    SERVICE_MOVE_QUEUE_ITEM: _Service(
        _queue_mutation(move_item, CONF_ITEM_ID, CONF_NEW_POSITION), MOVE_QUEUE_ITEM_SCHEMA
    ),
    SERVICE_REMOVE_QUEUE_ITEM: _Service(_queue_mutation(remove_item, CONF_ITEM_ID), ITEM_SCHEMA),
    SERVICE_RESUME_QUEUE: _Service(_async_resume_queue),
    SERVICE_SKIP_CURRENT_ROOM: _Service(_async_skip_current_room),
    SERVICE_START_QUEUE: _Service(_async_start_queue),
    SERVICE_UPDATE_QUEUE_ITEM_OVERRIDES: _Service(
        _queue_mutation(update_item_overrides, CONF_ITEM_ID, CONF_OVERRIDES),
        UPDATE_QUEUE_ITEM_OVERRIDES_SCHEMA,
    ),
    SERVICE_UPDATE_RUNNING_OVERRIDE: _Service(
        _async_update_running_override, UPDATE_RUNNING_OVERRIDE_SCHEMA
    ),
}

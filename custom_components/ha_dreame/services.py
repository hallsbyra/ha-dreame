"""Service handlers for HA Dreame."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import HomeAssistantError

from .const import (
    ATTR_COMPLETED_ITEMS,
    ATTR_PENDING_ITEMS,
    ATTR_QUEUE_ITEMS,
    ATTR_RUNNING_ITEMS,
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
    SERVICE_CLEAR_PENDING_QUEUE,
    SERVICE_GET_RUNTIME_STATUS,
    SERVICE_MOVE_QUEUE_ITEM,
    SERVICE_REMOVE_QUEUE_ITEM,
    SERVICE_START_QUEUE,
    SERVICE_UPDATE_QUEUE_ITEM_OVERRIDES,
)
from .dispatch_executor import async_execute_dispatch_plan
from .dispatch_plan import build_room_dispatch_plan
from .queue_core import (
    QueueError,
    add_room,
    clear_pending,
    current_item,
    move_item,
    remove_item,
    start_run,
    update_item_overrides,
)
from .queue_snapshot import count_queue_items, queue_item_snapshots

ADD_QUEUE_ROOM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CONFIG_ENTRY_ID): str,
        vol.Required(CONF_ROOM_ID): vol.Coerce(int),
        vol.Required(CONF_ROOM_NAME): vol.All(str, vol.Length(min=1)),
    }
)
CLEAR_PENDING_QUEUE_SCHEMA = vol.Schema({vol.Required(CONF_CONFIG_ENTRY_ID): str})
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
    hass.services.async_remove(DOMAIN, SERVICE_CLEAR_PENDING_QUEUE)
    hass.services.async_remove(DOMAIN, SERVICE_GET_RUNTIME_STATUS)
    hass.services.async_remove(DOMAIN, SERVICE_MOVE_QUEUE_ITEM)
    hass.services.async_remove(DOMAIN, SERVICE_REMOVE_QUEUE_ITEM)
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
    return _queue_status_response(entry)


def _runtime_status_response(hass: HomeAssistant, config_entry_id: str) -> dict[str, Any]:
    """Return read-only runtime status for one HA Dreame entry."""
    entry = _runtime_entry(hass, config_entry_id)

    runtime_data = entry.runtime_data
    return {
        CONF_ALLOW_ROBOT_COMMANDS: runtime_data.commands_enabled,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        CONF_VACUUM_ENTITY_ID: runtime_data.vacuum_entity_id,
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

"""HA Dreame integration scaffold."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import ConfigEntryError, HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    ATTR_COMPLETED_ITEMS,
    ATTR_PENDING_ITEMS,
    ATTR_QUEUE_ITEMS,
    ATTR_RUNNING_ITEMS,
    ATTR_TOTAL_ITEMS,
    CONF_ALLOW_ROBOT_COMMANDS,
    CONF_CONFIG_ENTRY_ID,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_VACUUM_ENTITY_ID,
    DOMAIN,
    DREAME_VACUUM_DOMAIN,
    SERVICE_ADD_QUEUE_ROOM,
    SERVICE_GET_RUNTIME_STATUS,
    VACUUM_DOMAIN,
)
from .queue_core import QueueError, QueueState, add_room, new_state
from .queue_snapshot import count_queue_items, queue_item_snapshots
from .runtime import HaDreameRuntimeData

_LOGGER = logging.getLogger(__name__)

ADD_QUEUE_ROOM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CONFIG_ENTRY_ID): str,
        vol.Required(CONF_ROOM_ID): vol.Coerce(int),
        vol.Required(CONF_ROOM_NAME): vol.All(str, vol.Length(min=1)),
    }
)
GET_RUNTIME_STATUS_SCHEMA = vol.Schema({vol.Required(CONF_CONFIG_ENTRY_ID): str})
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration from YAML."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    runtime_data = _build_runtime_data(hass, entry)

    hass.data.setdefault(DOMAIN, {})
    _async_register_services(hass)
    entry.runtime_data = runtime_data
    hass.data[DOMAIN][entry.entry_id] = entry
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.info(
        "Loaded %s config entry %s for %s",
        DOMAIN,
        entry.entry_id,
        runtime_data.vacuum_entity_id,
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unload_ok:
        return False

    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if hasattr(entry, "runtime_data"):
        del entry.runtime_data
    if not hass.data.get(DOMAIN):
        hass.services.async_remove(DOMAIN, SERVICE_ADD_QUEUE_ROOM)
        hass.services.async_remove(DOMAIN, SERVICE_GET_RUNTIME_STATUS)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload a config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


def _async_register_services(hass: HomeAssistant) -> None:
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


def _build_runtime_data(hass: HomeAssistant, entry: ConfigEntry) -> HaDreameRuntimeData:
    """Build validated runtime data for a config entry."""
    vacuum_entity_id = entry.data.get(CONF_VACUUM_ENTITY_ID)

    if not isinstance(vacuum_entity_id, str) or not vacuum_entity_id:
        raise ConfigEntryError("Config entry is missing a Dreame vacuum entity id")

    domain = vacuum_entity_id.split(".", maxsplit=1)[0]
    if domain != VACUUM_DOMAIN:
        raise ConfigEntryError(f"Configured Dreame entity is not a vacuum: {vacuum_entity_id}")

    registry_entry = er.async_get(hass).async_get(vacuum_entity_id)
    if registry_entry is None:
        raise ConfigEntryError(f"Configured Dreame vacuum does not exist: {vacuum_entity_id}")

    if registry_entry.platform != DREAME_VACUUM_DOMAIN:
        raise ConfigEntryError(f"Configured vacuum is not from Dreame: {vacuum_entity_id}")

    return HaDreameRuntimeData(
        commands_enabled=entry.options.get(CONF_ALLOW_ROBOT_COMMANDS) is True,
        queue_coordinator=_build_queue_coordinator(hass, entry),
        vacuum_entity_id=vacuum_entity_id,
    )


def _build_queue_coordinator(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> DataUpdateCoordinator[QueueState]:
    """Build the runtime queue state coordinator for a config entry."""
    coordinator = DataUpdateCoordinator[QueueState](
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{entry.entry_id}_queue",
    )
    coordinator.async_set_updated_data(new_state())
    return coordinator

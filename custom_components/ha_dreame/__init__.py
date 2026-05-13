"""HA Dreame integration scaffold."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import ConfigEntryError, HomeAssistantError
from homeassistant.helpers import entity_registry as er

from .const import (
    CONF_ALLOW_ROBOT_COMMANDS,
    CONF_CONFIG_ENTRY_ID,
    CONF_VACUUM_ENTITY_ID,
    DOMAIN,
    DREAME_VACUUM_DOMAIN,
    SERVICE_GET_RUNTIME_STATUS,
    VACUUM_DOMAIN,
)
from .runtime import HaDreameRuntimeData

_LOGGER = logging.getLogger(__name__)

GET_RUNTIME_STATUS_SCHEMA = vol.Schema({vol.Required(CONF_CONFIG_ENTRY_ID): str})


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
    _LOGGER.info(
        "Loaded %s config entry %s for %s",
        DOMAIN,
        entry.entry_id,
        runtime_data.vacuum_entity_id,
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if hasattr(entry, "runtime_data"):
        del entry.runtime_data
    if not hass.data.get(DOMAIN):
        hass.services.async_remove(DOMAIN, SERVICE_GET_RUNTIME_STATUS)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload a config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


def _async_register_services(hass: HomeAssistant) -> None:
    """Register HA Dreame services."""
    if hass.services.has_service(DOMAIN, SERVICE_GET_RUNTIME_STATUS):
        return

    async def _async_get_runtime_status(call: ServiceCall) -> ServiceResponse:
        return _runtime_status_response(hass, call.data[CONF_CONFIG_ENTRY_ID])

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_RUNTIME_STATUS,
        _async_get_runtime_status,
        schema=GET_RUNTIME_STATUS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )


def _runtime_status_response(hass: HomeAssistant, config_entry_id: str) -> dict[str, Any]:
    """Return read-only runtime status for one HA Dreame entry."""
    entry = hass.data.get(DOMAIN, {}).get(config_entry_id)
    if entry is None or not hasattr(entry, "runtime_data"):
        raise HomeAssistantError(f"HA Dreame entry is not loaded: {config_entry_id}")

    runtime_data = entry.runtime_data
    return {
        CONF_ALLOW_ROBOT_COMMANDS: runtime_data.commands_enabled,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        CONF_VACUUM_ENTITY_ID: runtime_data.vacuum_entity_id,
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
        vacuum_entity_id=vacuum_entity_id,
    )

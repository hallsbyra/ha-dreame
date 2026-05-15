"""HA Dreame integration scaffold."""

from __future__ import annotations

import logging

from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_ALLOW_ROBOT_COMMANDS,
    CONF_VACUUM_ENTITY_ID,
    DOMAIN,
    DREAME_VACUUM_DOMAIN,
    VACUUM_DOMAIN,
)
from .queue_core import QueueState, new_state
from .runtime import HaDreameRuntimeData
from .services import async_register_services, async_remove_services

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration from YAML."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    runtime_data = _build_runtime_data(hass, entry)

    hass.data.setdefault(DOMAIN, {})
    async_register_services(hass)
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
        async_remove_services(hass)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload a config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


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

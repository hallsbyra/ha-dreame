"""HA Dreame integration scaffold."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_VACUUM_ENTITY_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration from YAML."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "status": "configured",
        CONF_VACUUM_ENTITY_ID: entry.data[CONF_VACUUM_ENTITY_ID],
    }
    _LOGGER.info(
        "Loaded %s config entry %s for %s",
        DOMAIN,
        entry.entry_id,
        entry.data[CONF_VACUUM_ENTITY_ID],
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True

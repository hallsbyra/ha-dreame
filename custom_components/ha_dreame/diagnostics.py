"""Diagnostics support for HA Dreame."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_ALLOW_ROBOT_COMMANDS, CONF_VACUUM_ENTITY_ID
from .runtime import HaDreameRuntimeData


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    runtime_data = getattr(entry, "runtime_data", None)
    vacuum_entity_id = _diagnostic_vacuum_entity_id(entry, runtime_data)
    commands_enabled = _diagnostic_commands_enabled(entry, runtime_data)

    return {
        "entry": {
            "data": {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
            "domain": entry.domain,
            "entry_id": entry.entry_id,
            "options": {CONF_ALLOW_ROBOT_COMMANDS: commands_enabled},
            "title": entry.title,
        },
        "runtime": {
            CONF_ALLOW_ROBOT_COMMANDS: commands_enabled,
            CONF_VACUUM_ENTITY_ID: vacuum_entity_id,
            "loaded": isinstance(runtime_data, HaDreameRuntimeData),
        },
    }


def _diagnostic_commands_enabled(
    entry: ConfigEntry,
    runtime_data: object,
) -> bool:
    """Return the effective command gate state for diagnostics."""
    if isinstance(runtime_data, HaDreameRuntimeData):
        return runtime_data.commands_enabled

    return entry.options.get(CONF_ALLOW_ROBOT_COMMANDS) is True


def _diagnostic_vacuum_entity_id(
    entry: ConfigEntry,
    runtime_data: object,
) -> str | None:
    """Return the selected vacuum entity id for diagnostics."""
    if isinstance(runtime_data, HaDreameRuntimeData):
        return runtime_data.vacuum_entity_id

    vacuum_entity_id = entry.data.get(CONF_VACUUM_ENTITY_ID)
    if isinstance(vacuum_entity_id, str):
        return vacuum_entity_id

    return None

"""Tests for HA Dreame diagnostics."""

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_dreame.const import (
    CONF_ALLOW_ROBOT_COMMANDS,
    CONF_VACUUM_ENTITY_ID,
    DOMAIN,
    DREAME_VACUUM_DOMAIN,
)
from custom_components.ha_dreame.diagnostics import async_get_config_entry_diagnostics

pytestmark = pytest.mark.usefixtures("mock_dreame_vacuum_dependency")


def _register_vacuum(
    hass: HomeAssistant,
    *,
    unique_id: str = "robot-1",
    suggested_object_id: str = "dreame_robot",
) -> str:
    registry = er.async_get(hass)
    entry = registry.async_get_or_create(
        "vacuum",
        DREAME_VACUUM_DOMAIN,
        unique_id,
        suggested_object_id=suggested_object_id,
    )
    return entry.entity_id


async def test_config_entry_diagnostics_report_runtime_status(
    hass: HomeAssistant,
) -> None:
    """Test diagnostics expose public-safe runtime status."""
    vacuum_entity_id = _register_vacuum(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Dreame Robot",
        data={
            CONF_VACUUM_ENTITY_ID: vacuum_entity_id,
            "future_secret": "do-not-include",
        },
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    diagnostics = await async_get_config_entry_diagnostics(hass, entry)

    assert diagnostics == {
        "entry": {
            "data": {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
            "domain": DOMAIN,
            "entry_id": entry.entry_id,
            "options": {CONF_ALLOW_ROBOT_COMMANDS: False},
            "title": "Dreame Robot",
        },
        "runtime": {
            CONF_ALLOW_ROBOT_COMMANDS: False,
            CONF_VACUUM_ENTITY_ID: vacuum_entity_id,
            "loaded": True,
        },
    }
    assert "future_secret" not in str(diagnostics)
    assert "do-not-include" not in str(diagnostics)


async def test_config_entry_diagnostics_report_enabled_command_gate(
    hass: HomeAssistant,
) -> None:
    """Test diagnostics expose the effective command gate."""
    vacuum_entity_id = _register_vacuum(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Dreame Robot",
        data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    diagnostics = await async_get_config_entry_diagnostics(hass, entry)

    assert diagnostics["entry"]["options"] == {CONF_ALLOW_ROBOT_COMMANDS: True}
    assert diagnostics["runtime"][CONF_ALLOW_ROBOT_COMMANDS] is True


async def test_config_entry_diagnostics_handle_unloaded_entry(
    hass: HomeAssistant,
) -> None:
    """Test diagnostics still describe an unloaded entry without runtime data."""
    vacuum_entity_id = _register_vacuum(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Dreame Robot",
        data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )
    entry.add_to_hass(hass)

    diagnostics = await async_get_config_entry_diagnostics(hass, entry)

    assert diagnostics["entry"]["data"] == {CONF_VACUUM_ENTITY_ID: vacuum_entity_id}
    assert diagnostics["runtime"] == {
        CONF_ALLOW_ROBOT_COMMANDS: False,
        CONF_VACUUM_ENTITY_ID: vacuum_entity_id,
        "loaded": False,
    }

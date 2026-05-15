"""Tests for HA Dreame integration setup."""

import pytest

from homeassistant.core import HomeAssistant

from custom_components.ha_dreame.const import (
    CONF_ALLOW_ROBOT_COMMANDS,
    CONF_VACUUM_ENTITY_ID,
    DOMAIN,
    DREAME_VACUUM_DOMAIN,
)
from custom_components.ha_dreame.queue_core import QueueState, add_room
from custom_components.ha_dreame.runtime import HaDreameRuntimeData, QueueRunTracking

from .helpers import mock_entry, register_entity

pytestmark = pytest.mark.usefixtures("mock_dreame_vacuum_dependency")


async def test_setup_entry_attaches_runtime_data(hass: HomeAssistant) -> None:
    """Test that a config entry exposes typed runtime data."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert isinstance(entry.runtime_data, HaDreameRuntimeData)
    assert entry.runtime_data.vacuum_entity_id == vacuum_entity_id
    assert entry.runtime_data.commands_enabled is False
    assert isinstance(entry.runtime_data.queue_state, QueueState)
    assert entry.runtime_data.queue_state.run_state == "idle"
    assert entry.runtime_data.queue_state.items == ()
    assert entry.runtime_data.run_tracking is None
    assert hass.data[DOMAIN][entry.entry_id] is entry


async def test_runtime_data_updates_queue_state(
    hass: HomeAssistant,
) -> None:
    """Test runtime data exposes an updateable queue state surface."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    updated_state = add_room(
        entry.runtime_data.queue_state,
        room_id=1,
        room_name="Room 1",
    )
    entry.runtime_data.set_queue_state(updated_state)
    await hass.async_block_till_done()

    assert entry.runtime_data.queue_state == updated_state


async def test_runtime_data_updates_run_tracking(
    hass: HomeAssistant,
) -> None:
    """Test runtime data exposes an updateable run tracking surface."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    run_tracking = QueueRunTracking(
        run_id="run-1",
        current_item_id="item-1",
        last_command_at="2026-05-15T18:00:00+00:00",
    )
    entry.runtime_data.set_run_tracking(run_tracking)
    await hass.async_block_till_done()

    assert entry.runtime_data.run_tracking == run_tracking

    entry.runtime_data.set_run_tracking(None)
    await hass.async_block_till_done()

    assert entry.runtime_data.run_tracking is None


async def test_setup_entry_reads_enabled_command_gate_from_options(
    hass: HomeAssistant,
) -> None:
    """Test that runtime data reflects explicit command enablement."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.runtime_data.commands_enabled is True


async def test_options_update_reloads_runtime_data_when_enabling_commands(
    hass: HomeAssistant,
) -> None:
    """Test enabling commands through options refreshes runtime data."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.runtime_data.commands_enabled is False

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    await hass.async_block_till_done()

    assert result["type"] == "create_entry"
    assert entry.runtime_data.commands_enabled is True
    assert hass.data[DOMAIN][entry.entry_id] is entry


async def test_options_update_reloads_runtime_data_when_disabling_commands(
    hass: HomeAssistant,
) -> None:
    """Test disabling commands through options refreshes runtime data."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.runtime_data.commands_enabled is True

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {CONF_ALLOW_ROBOT_COMMANDS: False},
    )
    await hass.async_block_till_done()

    assert result["type"] == "create_entry"
    assert entry.runtime_data.commands_enabled is False
    assert hass.data[DOMAIN][entry.entry_id] is entry


async def test_unload_entry_clears_runtime_data(hass: HomeAssistant) -> None:
    """Test that unloading clears runtime state."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert not hasattr(entry, "runtime_data")
    assert entry.entry_id not in hass.data[DOMAIN]


@pytest.mark.parametrize(
    ("data", "entity_id", "platform"),
    [
        pytest.param({}, None, DREAME_VACUUM_DOMAIN, id="missing-config-data"),
        pytest.param(
            {CONF_VACUUM_ENTITY_ID: "vacuum.missing"},
            None,
            DREAME_VACUUM_DOMAIN,
            id="missing-registry-entry",
        ),
        pytest.param(
            {CONF_VACUUM_ENTITY_ID: "sensor.dreame_robot"},
            "sensor.dreame_robot",
            DREAME_VACUUM_DOMAIN,
            id="non-vacuum-domain",
        ),
        pytest.param(
            {CONF_VACUUM_ENTITY_ID: "vacuum.other_robot"},
            "vacuum.other_robot",
            "other_vacuum",
            id="non-dreame-platform",
        ),
    ],
)
async def test_setup_entry_rejects_invalid_stored_vacuum(
    hass: HomeAssistant,
    data: dict[str, str],
    entity_id: str | None,
    platform: str,
) -> None:
    """Test invalid stored dependency references fail setup."""
    if entity_id is not None:
        register_entity(hass, entity_id, platform=platform)
    entry = mock_entry(data)
    entry.add_to_hass(hass)

    assert not await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert not hasattr(entry, "runtime_data")
    assert entry.entry_id not in hass.data.get(DOMAIN, {})

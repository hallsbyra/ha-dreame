"""Tests for HA Dreame integration setup."""

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_dreame.const import (
    ATTR_COMPLETED_ITEMS,
    ATTR_PENDING_ITEMS,
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
    TITLE,
)
from custom_components.ha_dreame.queue_core import QueueState, add_room
from custom_components.ha_dreame.runtime import HaDreameRuntimeData

pytestmark = pytest.mark.usefixtures("mock_dreame_vacuum_dependency")


def _register_entity(
    hass: HomeAssistant,
    entity_id: str,
    *,
    platform: str = DREAME_VACUUM_DOMAIN,
    unique_id: str = "robot-1",
) -> str:
    """Register an entity and return its entity id."""
    domain, object_id = entity_id.split(".", maxsplit=1)
    registry = er.async_get(hass)
    entry = registry.async_get_or_create(
        domain,
        platform,
        unique_id,
        suggested_object_id=object_id,
    )
    return entry.entity_id


def _mock_entry(
    data: dict[str, str],
    *,
    options: dict[str, bool] | None = None,
) -> MockConfigEntry:
    return MockConfigEntry(domain=DOMAIN, title=TITLE, data=data, options=options)


async def _call_runtime_status_service(
    hass: HomeAssistant,
    config_entry_id: str,
) -> dict[str, object]:
    """Call the runtime status service and return its response."""
    return await hass.services.async_call(
        DOMAIN,
        SERVICE_GET_RUNTIME_STATUS,
        {CONF_CONFIG_ENTRY_ID: config_entry_id},
        blocking=True,
        return_response=True,
    )


async def _call_add_queue_room_service(
    hass: HomeAssistant,
    config_entry_id: str,
    *,
    room_id: int = 1,
    room_name: str = "Room 1",
) -> dict[str, object]:
    """Call the add queue room service and return its response."""
    return await hass.services.async_call(
        DOMAIN,
        SERVICE_ADD_QUEUE_ROOM,
        {
            CONF_CONFIG_ENTRY_ID: config_entry_id,
            CONF_ROOM_ID: room_id,
            CONF_ROOM_NAME: room_name,
        },
        blocking=True,
        return_response=True,
    )


async def test_setup_entry_attaches_runtime_data(hass: HomeAssistant) -> None:
    """Test that a config entry exposes typed runtime data."""
    vacuum_entity_id = _register_entity(hass, "vacuum.dreame_robot")
    entry = _mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert isinstance(entry.runtime_data, HaDreameRuntimeData)
    assert entry.runtime_data.vacuum_entity_id == vacuum_entity_id
    assert entry.runtime_data.commands_enabled is False
    assert isinstance(entry.runtime_data.queue_state, QueueState)
    assert entry.runtime_data.queue_state.run_state == "idle"
    assert entry.runtime_data.queue_state.items == ()
    assert hass.data[DOMAIN][entry.entry_id] is entry


async def test_runtime_data_updates_queue_state(
    hass: HomeAssistant,
) -> None:
    """Test runtime data exposes an updateable queue state surface."""
    vacuum_entity_id = _register_entity(hass, "vacuum.dreame_robot")
    entry = _mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
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


async def test_setup_entry_registers_runtime_status_service(
    hass: HomeAssistant,
) -> None:
    """Test setup registers the read-only runtime status service."""
    vacuum_entity_id = _register_entity(hass, "vacuum.dreame_robot")
    entry = _mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service(DOMAIN, SERVICE_GET_RUNTIME_STATUS)


async def test_setup_entry_registers_add_queue_room_service(
    hass: HomeAssistant,
) -> None:
    """Test setup registers the internal add queue room service."""
    vacuum_entity_id = _register_entity(hass, "vacuum.dreame_robot")
    entry = _mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service(DOMAIN, SERVICE_ADD_QUEUE_ROOM)


async def test_add_queue_room_service_updates_runtime_queue_state(
    hass: HomeAssistant,
) -> None:
    """Test the add queue room service appends a pending queue item."""
    vacuum_entity_id = _register_entity(hass, "vacuum.dreame_robot")
    entry = _mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    response = await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=42,
        room_name="Room 42",
    )

    queue_state = entry.runtime_data.queue_state
    assert queue_state.run_state == "idle"
    assert len(queue_state.items) == 1
    assert queue_state.items[0].room_id == 42
    assert queue_state.items[0].room_name == "Room 42"
    assert queue_state.items[0].status == "pending"
    assert response == {
        ATTR_COMPLETED_ITEMS: 0,
        ATTR_PENDING_ITEMS: 1,
        ATTR_RUNNING_ITEMS: 0,
        ATTR_TOTAL_ITEMS: 1,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        "run_state": "idle",
    }


async def test_add_queue_room_service_rejects_unknown_entry(
    hass: HomeAssistant,
) -> None:
    """Test the add queue room service rejects unknown config entry ids."""
    vacuum_entity_id = _register_entity(hass, "vacuum.dreame_robot")
    entry = _mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(HomeAssistantError):
        await _call_add_queue_room_service(hass, "missing-entry")


async def test_runtime_status_service_returns_entry_runtime_data(
    hass: HomeAssistant,
) -> None:
    """Test the read-only runtime status service response."""
    vacuum_entity_id = _register_entity(hass, "vacuum.dreame_robot")
    entry = _mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert await _call_runtime_status_service(hass, entry.entry_id) == {
        CONF_ALLOW_ROBOT_COMMANDS: True,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        CONF_VACUUM_ENTITY_ID: vacuum_entity_id,
    }


async def test_runtime_status_service_reflects_reloaded_command_gate(
    hass: HomeAssistant,
) -> None:
    """Test the service reports command gate changes after options reload."""
    vacuum_entity_id = _register_entity(hass, "vacuum.dreame_robot")
    entry = _mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    await hass.config_entries.options.async_configure(
        result["flow_id"],
        {CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    await hass.async_block_till_done()

    assert await _call_runtime_status_service(hass, entry.entry_id) == {
        CONF_ALLOW_ROBOT_COMMANDS: True,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        CONF_VACUUM_ENTITY_ID: vacuum_entity_id,
    }


async def test_runtime_status_service_rejects_unknown_entry(
    hass: HomeAssistant,
) -> None:
    """Test the service rejects unknown config entry ids."""
    vacuum_entity_id = _register_entity(hass, "vacuum.dreame_robot")
    entry = _mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(HomeAssistantError):
        await _call_runtime_status_service(hass, "missing-entry")


async def test_setup_entry_reads_enabled_command_gate_from_options(
    hass: HomeAssistant,
) -> None:
    """Test that runtime data reflects explicit command enablement."""
    vacuum_entity_id = _register_entity(hass, "vacuum.dreame_robot")
    entry = _mock_entry(
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
    vacuum_entity_id = _register_entity(hass, "vacuum.dreame_robot")
    entry = _mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
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
    vacuum_entity_id = _register_entity(hass, "vacuum.dreame_robot")
    entry = _mock_entry(
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
    vacuum_entity_id = _register_entity(hass, "vacuum.dreame_robot")
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=TITLE,
        data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert not hasattr(entry, "runtime_data")
    assert entry.entry_id not in hass.data[DOMAIN]


async def test_unload_last_entry_removes_runtime_status_service(
    hass: HomeAssistant,
) -> None:
    """Test unloading the last entry removes the read-only service."""
    vacuum_entity_id = _register_entity(hass, "vacuum.dreame_robot")
    entry = _mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert hass.services.has_service(DOMAIN, SERVICE_GET_RUNTIME_STATUS)

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert not hass.services.has_service(DOMAIN, SERVICE_GET_RUNTIME_STATUS)
    assert not hass.services.has_service(DOMAIN, SERVICE_ADD_QUEUE_ROOM)


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
        _register_entity(hass, entity_id, platform=platform)
    entry = _mock_entry(data)
    entry.add_to_hass(hass)

    assert not await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert not hasattr(entry, "runtime_data")
    assert entry.entry_id not in hass.data.get(DOMAIN, {})

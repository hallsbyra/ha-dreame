"""Tests for HA Dreame sensor entities."""

import pytest

from homeassistant.const import ATTR_FRIENDLY_NAME, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_dreame.const import (
    ATTR_COMPLETED_ITEMS,
    ATTR_ITEM_ID,
    ATTR_OVERRIDES,
    ATTR_PENDING_ITEMS,
    ATTR_QUEUE_ITEMS,
    ATTR_RESULT,
    ATTR_RUNNING_ITEMS,
    ATTR_STATUS,
    ATTR_TOTAL_ITEMS,
    CONF_CONFIG_ENTRY_ID,
    CONF_ITEM_ID,
    CONF_NEW_POSITION,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_VACUUM_ENTITY_ID,
    DOMAIN,
    DREAME_VACUUM_DOMAIN,
    SERVICE_ADD_QUEUE_ROOM,
    SERVICE_MOVE_QUEUE_ITEM,
    SERVICE_REMOVE_QUEUE_ITEM,
    SENSOR_QUEUE_STATUS,
    TITLE,
)
from custom_components.ha_dreame.queue_core import add_room, start_run

pytestmark = pytest.mark.usefixtures("mock_dreame_vacuum_dependency")


def _register_vacuum(hass: HomeAssistant, entity_id: str = "vacuum.dreame_robot") -> str:
    """Register a Dreame vacuum and return its entity id."""
    domain, object_id = entity_id.split(".", maxsplit=1)
    registry = er.async_get(hass)
    entry = registry.async_get_or_create(
        domain,
        DREAME_VACUUM_DOMAIN,
        "robot-1",
        suggested_object_id=object_id,
    )
    return entry.entity_id


async def test_queue_status_sensor_exposes_initial_queue_state(
    hass: HomeAssistant,
) -> None:
    """Test the queue status sensor exposes the initial empty queue state."""
    vacuum_entity_id = _register_vacuum(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=TITLE,
        data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.ha_dreame_queue_status")

    assert state is not None
    assert state.state == "idle"
    assert state.attributes[ATTR_FRIENDLY_NAME] == "HA Dreame Queue Status"
    assert state.attributes[CONF_VACUUM_ENTITY_ID] == vacuum_entity_id
    assert state.attributes[ATTR_PENDING_ITEMS] == 0
    assert state.attributes[ATTR_RUNNING_ITEMS] == 0
    assert state.attributes[ATTR_COMPLETED_ITEMS] == 0
    assert state.attributes[ATTR_TOTAL_ITEMS] == 0
    assert state.attributes[ATTR_QUEUE_ITEMS] == []


async def test_queue_status_sensor_has_stable_unique_id(
    hass: HomeAssistant,
) -> None:
    """Test the queue status sensor unique id is based on the config entry."""
    vacuum_entity_id = _register_vacuum(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=TITLE,
        data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    registry_entry = er.async_get(hass).async_get("sensor.ha_dreame_queue_status")

    assert registry_entry is not None
    assert registry_entry.config_entry_id == entry.entry_id
    assert registry_entry.platform == DOMAIN
    assert registry_entry.unique_id == f"{entry.entry_id}_{SENSOR_QUEUE_STATUS}"


async def test_queue_status_sensor_updates_when_runtime_queue_state_changes(
    hass: HomeAssistant,
) -> None:
    """Test the queue status sensor reacts to runtime queue state updates."""
    vacuum_entity_id = _register_vacuum(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=TITLE,
        data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    queued_state = add_room(
        entry.runtime_data.queue_state,
        room_id=1,
        room_name="Room 1",
    )
    running_state = start_run(queued_state)
    entry.runtime_data.set_queue_state(running_state)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.ha_dreame_queue_status")

    assert state.state == "running"
    assert state.attributes[ATTR_PENDING_ITEMS] == 0
    assert state.attributes[ATTR_RUNNING_ITEMS] == 1
    assert state.attributes[ATTR_COMPLETED_ITEMS] == 0
    assert state.attributes[ATTR_TOTAL_ITEMS] == 1
    assert state.attributes[ATTR_QUEUE_ITEMS] == [
        {
            ATTR_ITEM_ID: running_state.items[0].item_id,
            ATTR_OVERRIDES: {},
            ATTR_RESULT: None,
            ATTR_STATUS: "running",
            CONF_ROOM_ID: 1,
            CONF_ROOM_NAME: "Room 1",
        }
    ]


async def test_queue_status_sensor_updates_when_add_queue_room_service_runs(
    hass: HomeAssistant,
) -> None:
    """Test the queue status sensor reacts to the add queue room service."""
    vacuum_entity_id = _register_vacuum(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=TITLE,
        data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await hass.services.async_call(
        DOMAIN,
        SERVICE_ADD_QUEUE_ROOM,
        {
            CONF_CONFIG_ENTRY_ID: entry.entry_id,
            CONF_ROOM_ID: 7,
            CONF_ROOM_NAME: "Room 7",
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    state = hass.states.get("sensor.ha_dreame_queue_status")

    assert state.state == "idle"
    assert state.attributes[ATTR_PENDING_ITEMS] == 1
    assert state.attributes[ATTR_RUNNING_ITEMS] == 0
    assert state.attributes[ATTR_COMPLETED_ITEMS] == 0
    assert state.attributes[ATTR_TOTAL_ITEMS] == 1
    assert state.attributes[ATTR_QUEUE_ITEMS][0][CONF_ROOM_ID] == 7
    assert state.attributes[ATTR_QUEUE_ITEMS][0][CONF_ROOM_NAME] == "Room 7"
    assert state.attributes[ATTR_QUEUE_ITEMS][0][ATTR_STATUS] == "pending"
    assert state.attributes[ATTR_QUEUE_ITEMS][0][ATTR_ITEM_ID]


async def test_queue_status_sensor_updates_when_remove_queue_item_service_runs(
    hass: HomeAssistant,
) -> None:
    """Test the queue status sensor reacts to the remove queue item service."""
    vacuum_entity_id = _register_vacuum(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=TITLE,
        data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await hass.services.async_call(
        DOMAIN,
        SERVICE_ADD_QUEUE_ROOM,
        {
            CONF_CONFIG_ENTRY_ID: entry.entry_id,
            CONF_ROOM_ID: 7,
            CONF_ROOM_NAME: "Room 7",
        },
        blocking=True,
    )
    await hass.services.async_call(
        DOMAIN,
        SERVICE_ADD_QUEUE_ROOM,
        {
            CONF_CONFIG_ENTRY_ID: entry.entry_id,
            CONF_ROOM_ID: 8,
            CONF_ROOM_NAME: "Room 8",
        },
        blocking=True,
    )
    removed_item_id = entry.runtime_data.queue_state.items[0].item_id

    await hass.services.async_call(
        DOMAIN,
        SERVICE_REMOVE_QUEUE_ITEM,
        {
            CONF_CONFIG_ENTRY_ID: entry.entry_id,
            CONF_ITEM_ID: removed_item_id,
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    state = hass.states.get("sensor.ha_dreame_queue_status")

    assert state.state == "idle"
    assert state.attributes[ATTR_PENDING_ITEMS] == 1
    assert state.attributes[ATTR_RUNNING_ITEMS] == 0
    assert state.attributes[ATTR_COMPLETED_ITEMS] == 0
    assert state.attributes[ATTR_TOTAL_ITEMS] == 1
    assert state.attributes[ATTR_QUEUE_ITEMS][0][CONF_ROOM_ID] == 8
    assert state.attributes[ATTR_QUEUE_ITEMS][0][CONF_ROOM_NAME] == "Room 8"


async def test_queue_status_sensor_updates_when_move_queue_item_service_runs(
    hass: HomeAssistant,
) -> None:
    """Test the queue status sensor reacts to the move queue item service."""
    vacuum_entity_id = _register_vacuum(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=TITLE,
        data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    for room_id, room_name in ((7, "Room 7"), (8, "Room 8"), (9, "Room 9")):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_ADD_QUEUE_ROOM,
            {
                CONF_CONFIG_ENTRY_ID: entry.entry_id,
                CONF_ROOM_ID: room_id,
                CONF_ROOM_NAME: room_name,
            },
            blocking=True,
        )

    moved_item_id = entry.runtime_data.queue_state.items[0].item_id
    await hass.services.async_call(
        DOMAIN,
        SERVICE_MOVE_QUEUE_ITEM,
        {
            CONF_CONFIG_ENTRY_ID: entry.entry_id,
            CONF_ITEM_ID: moved_item_id,
            CONF_NEW_POSITION: 2,
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    state = hass.states.get("sensor.ha_dreame_queue_status")

    assert state.state == "idle"
    assert state.attributes[ATTR_PENDING_ITEMS] == 3
    assert state.attributes[ATTR_RUNNING_ITEMS] == 0
    assert state.attributes[ATTR_COMPLETED_ITEMS] == 0
    assert state.attributes[ATTR_TOTAL_ITEMS] == 3
    assert [item[CONF_ROOM_NAME] for item in state.attributes[ATTR_QUEUE_ITEMS]] == [
        "Room 8",
        "Room 9",
        "Room 7",
    ]


async def test_unload_entry_marks_queue_status_sensor_unavailable(
    hass: HomeAssistant,
) -> None:
    """Test unloading an entry marks its queue status sensor unavailable."""
    vacuum_entity_id = _register_vacuum(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=TITLE,
        data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert hass.states.get("sensor.ha_dreame_queue_status") is not None

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get("sensor.ha_dreame_queue_status").state == STATE_UNAVAILABLE

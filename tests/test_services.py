"""Tests for HA Dreame services."""

from datetime import datetime
import logging

import pytest

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from _pytest.logging import LogCaptureFixture

from custom_components.ha_dreame.const import (
    ATTR_ACTIVE_ROOM_MISMATCH_STREAK,
    ATTR_COMPLETED_ITEMS,
    ATTR_CURRENT_ITEM_ID,
    ATTR_DISPATCH_RETRY_COUNT,
    ATTR_ITEM_ID,
    ATTR_LAST_COMMAND_AT,
    ATTR_OVERRIDES,
    ATTR_PENDING_ITEMS,
    ATTR_QUEUE_ITEMS,
    ATTR_RESULT,
    ATTR_RUN_ID,
    ATTR_RUN_TRACKING,
    ATTR_RUNNING_ITEMS,
    ATTR_STATUS,
    ATTR_TASK_STATUS_CLEARED_SINCE_DISPATCH,
    ATTR_TOTAL_ITEMS,
    CONF_ALLOW_ROBOT_COMMANDS,
    CONF_AUTO_RECONCILE_ENABLED,
    CONF_CONFIG_ENTRY_ID,
    CONF_FIELD,
    CONF_ITEM_ID,
    CONF_NEW_POSITION,
    CONF_OVERRIDES,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_VALUE,
    CONF_VACUUM_ENTITY_ID,
    DOMAIN,
    DREAME_VACUUM_DOMAIN,
    SERVICE_ADD_QUEUE_ROOM,
    SERVICE_CANCEL_QUEUE,
    SERVICE_CLEAR_PENDING_QUEUE,
    SERVICE_GET_CONTROL_READINESS,
    SERVICE_GET_RUNTIME_STATUS,
    SERVICE_MOVE_QUEUE_ITEM,
    SERVICE_REMOVE_QUEUE_ITEM,
    SERVICE_RESUME_QUEUE,
    SERVICE_SKIP_CURRENT_ROOM,
    SERVICE_START_QUEUE,
    SERVICE_UPDATE_QUEUE_ITEM_OVERRIDES,
    SERVICE_UPDATE_RUNNING_OVERRIDE,
)
from custom_components.ha_dreame.queue_core import start_run
from custom_components.ha_dreame.runtime_state import QueueRunTracking

from .helpers import mock_entry, register_entity

pytestmark = pytest.mark.usefixtures("mock_dreame_vacuum_dependency")


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


async def _call_control_readiness_service(
    hass: HomeAssistant,
    config_entry_id: str,
) -> dict[str, object]:
    """Call the control readiness service and return its response."""
    return await hass.services.async_call(
        DOMAIN,
        SERVICE_GET_CONTROL_READINESS,
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


async def _call_remove_queue_item_service(
    hass: HomeAssistant,
    config_entry_id: str,
    *,
    item_id: str = "item-1",
) -> dict[str, object]:
    """Call the remove queue item service and return its response."""
    return await hass.services.async_call(
        DOMAIN,
        SERVICE_REMOVE_QUEUE_ITEM,
        {
            CONF_CONFIG_ENTRY_ID: config_entry_id,
            CONF_ITEM_ID: item_id,
        },
        blocking=True,
        return_response=True,
    )


async def _call_move_queue_item_service(
    hass: HomeAssistant,
    config_entry_id: str,
    *,
    item_id: str = "item-1",
    new_position: int = 0,
) -> dict[str, object]:
    """Call the move queue item service and return its response."""
    return await hass.services.async_call(
        DOMAIN,
        SERVICE_MOVE_QUEUE_ITEM,
        {
            CONF_CONFIG_ENTRY_ID: config_entry_id,
            CONF_ITEM_ID: item_id,
            CONF_NEW_POSITION: new_position,
        },
        blocking=True,
        return_response=True,
    )


async def _call_clear_pending_queue_service(
    hass: HomeAssistant,
    config_entry_id: str,
) -> dict[str, object]:
    """Call the clear pending queue service and return its response."""
    return await hass.services.async_call(
        DOMAIN,
        SERVICE_CLEAR_PENDING_QUEUE,
        {CONF_CONFIG_ENTRY_ID: config_entry_id},
        blocking=True,
        return_response=True,
    )


async def _call_cancel_queue_service(
    hass: HomeAssistant,
    config_entry_id: str,
) -> dict[str, object]:
    """Call the cancel queue service and return its response."""
    return await hass.services.async_call(
        DOMAIN,
        SERVICE_CANCEL_QUEUE,
        {CONF_CONFIG_ENTRY_ID: config_entry_id},
        blocking=True,
        return_response=True,
    )


async def _call_skip_current_room_service(
    hass: HomeAssistant,
    config_entry_id: str,
) -> dict[str, object]:
    """Call the skip current room service and return its response."""
    return await hass.services.async_call(
        DOMAIN,
        SERVICE_SKIP_CURRENT_ROOM,
        {CONF_CONFIG_ENTRY_ID: config_entry_id},
        blocking=True,
        return_response=True,
    )


async def _call_resume_queue_service(
    hass: HomeAssistant,
    config_entry_id: str,
) -> dict[str, object]:
    """Call the resume queue service and return its response."""
    return await hass.services.async_call(
        DOMAIN,
        SERVICE_RESUME_QUEUE,
        {CONF_CONFIG_ENTRY_ID: config_entry_id},
        blocking=True,
        return_response=True,
    )


async def _call_update_queue_item_overrides_service(
    hass: HomeAssistant,
    config_entry_id: str,
    *,
    item_id: str = "item-1",
    overrides: dict[str, object] | None = None,
) -> dict[str, object]:
    """Call the update queue item overrides service and return its response."""
    return await hass.services.async_call(
        DOMAIN,
        SERVICE_UPDATE_QUEUE_ITEM_OVERRIDES,
        {
            CONF_CONFIG_ENTRY_ID: config_entry_id,
            CONF_ITEM_ID: item_id,
            CONF_OVERRIDES: overrides or {},
        },
        blocking=True,
        return_response=True,
    )


async def _call_update_running_override_service(
    hass: HomeAssistant,
    config_entry_id: str,
    *,
    field: str = "suction_level",
    value: int = 1,
) -> dict[str, object]:
    """Call the update running override service and return its response."""
    return await hass.services.async_call(
        DOMAIN,
        SERVICE_UPDATE_RUNNING_OVERRIDE,
        {
            CONF_CONFIG_ENTRY_ID: config_entry_id,
            CONF_FIELD: field,
            CONF_VALUE: value,
        },
        blocking=True,
        return_response=True,
    )


async def _call_start_queue_service(
    hass: HomeAssistant,
    config_entry_id: str,
) -> dict[str, object]:
    """Call the start queue service and return its response."""
    return await hass.services.async_call(
        DOMAIN,
        SERVICE_START_QUEUE,
        {CONF_CONFIG_ENTRY_ID: config_entry_id},
        blocking=True,
        return_response=True,
    )


async def test_setup_entry_registers_runtime_status_service(
    hass: HomeAssistant,
) -> None:
    """Test setup registers the read-only runtime status service."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service(DOMAIN, SERVICE_GET_RUNTIME_STATUS)


async def test_setup_entry_registers_control_readiness_service(
    hass: HomeAssistant,
) -> None:
    """Test setup registers the read-only control readiness service."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service(DOMAIN, SERVICE_GET_CONTROL_READINESS)


async def test_setup_entry_registers_add_queue_room_service(
    hass: HomeAssistant,
) -> None:
    """Test setup registers the internal add queue room service."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service(DOMAIN, SERVICE_ADD_QUEUE_ROOM)


async def test_setup_entry_registers_remove_queue_item_service(
    hass: HomeAssistant,
) -> None:
    """Test setup registers the internal remove queue item service."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service(DOMAIN, SERVICE_REMOVE_QUEUE_ITEM)


async def test_setup_entry_registers_move_queue_item_service(
    hass: HomeAssistant,
) -> None:
    """Test setup registers the internal move queue item service."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service(DOMAIN, SERVICE_MOVE_QUEUE_ITEM)


async def test_setup_entry_registers_clear_pending_queue_service(
    hass: HomeAssistant,
) -> None:
    """Test setup registers the internal clear pending queue service."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service(DOMAIN, SERVICE_CLEAR_PENDING_QUEUE)


async def test_setup_entry_registers_cancel_queue_service(
    hass: HomeAssistant,
) -> None:
    """Test setup registers the command-gated cancel queue service."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service(DOMAIN, SERVICE_CANCEL_QUEUE)


async def test_setup_entry_registers_skip_current_room_service(
    hass: HomeAssistant,
) -> None:
    """Test setup registers the command-gated skip current room service."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service(DOMAIN, SERVICE_SKIP_CURRENT_ROOM)


async def test_setup_entry_registers_resume_queue_service(
    hass: HomeAssistant,
) -> None:
    """Test setup registers the command-gated resume queue service."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service(DOMAIN, SERVICE_RESUME_QUEUE)


async def test_setup_entry_registers_update_queue_item_overrides_service(
    hass: HomeAssistant,
) -> None:
    """Test setup registers the internal queue item overrides service."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service(DOMAIN, SERVICE_UPDATE_QUEUE_ITEM_OVERRIDES)


async def test_setup_entry_registers_start_queue_service(
    hass: HomeAssistant,
) -> None:
    """Test setup registers the command-gated start queue service."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service(DOMAIN, SERVICE_START_QUEUE)


async def test_setup_entry_registers_update_running_override_service(
    hass: HomeAssistant,
) -> None:
    """Test setup registers the command-gated running override service."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service(DOMAIN, SERVICE_UPDATE_RUNNING_OVERRIDE)


async def test_add_queue_room_service_updates_runtime_queue_state(
    hass: HomeAssistant,
) -> None:
    """Test the add queue room service appends a pending queue item."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
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
    item = queue_state.items[0]
    assert response == {
        ATTR_COMPLETED_ITEMS: 0,
        ATTR_PENDING_ITEMS: 1,
        ATTR_QUEUE_ITEMS: [
            {
                ATTR_ITEM_ID: item.item_id,
                ATTR_OVERRIDES: {},
                ATTR_RESULT: None,
                ATTR_STATUS: "pending",
                CONF_ROOM_ID: 42,
                CONF_ROOM_NAME: "Room 42",
            }
        ],
        ATTR_RUNNING_ITEMS: 0,
        ATTR_TOTAL_ITEMS: 1,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        "run_state": "idle",
    }


async def test_add_queue_room_service_rejects_unknown_entry(
    hass: HomeAssistant,
) -> None:
    """Test the add queue room service rejects unknown config entry ids."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(HomeAssistantError):
        await _call_add_queue_room_service(hass, "missing-entry")


async def test_remove_queue_item_service_updates_runtime_queue_state(
    hass: HomeAssistant,
) -> None:
    """Test the remove queue item service removes a pending queue item."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=1,
        room_name="Room 1",
    )
    add_response = await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=2,
        room_name="Room 2",
    )
    removed_item_id = add_response[ATTR_QUEUE_ITEMS][0][ATTR_ITEM_ID]

    response = await _call_remove_queue_item_service(
        hass,
        entry.entry_id,
        item_id=removed_item_id,
    )

    queue_state = entry.runtime_data.queue_state
    remaining_item = queue_state.items[0]
    assert [item.room_name for item in queue_state.items] == ["Room 2"]
    assert response == {
        ATTR_COMPLETED_ITEMS: 0,
        ATTR_PENDING_ITEMS: 1,
        ATTR_QUEUE_ITEMS: [
            {
                ATTR_ITEM_ID: remaining_item.item_id,
                ATTR_OVERRIDES: {},
                ATTR_RESULT: None,
                ATTR_STATUS: "pending",
                CONF_ROOM_ID: 2,
                CONF_ROOM_NAME: "Room 2",
            }
        ],
        ATTR_RUNNING_ITEMS: 0,
        ATTR_TOTAL_ITEMS: 1,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        "run_state": "idle",
    }


async def test_remove_queue_item_service_rejects_unknown_entry_and_missing_item(
    hass: HomeAssistant,
) -> None:
    """Test the remove queue item service rejects invalid requests."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(HomeAssistantError):
        await _call_remove_queue_item_service(hass, "missing-entry")

    with pytest.raises(HomeAssistantError):
        await _call_remove_queue_item_service(hass, entry.entry_id, item_id="missing-item")


async def test_move_queue_item_service_updates_runtime_queue_order(
    hass: HomeAssistant,
) -> None:
    """Test the move queue item service reorders pending queue items."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=1,
        room_name="Room 1",
    )
    await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=2,
        room_name="Room 2",
    )
    await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=3,
        room_name="Room 3",
    )
    moved_item_id = entry.runtime_data.queue_state.items[0].item_id

    response = await _call_move_queue_item_service(
        hass,
        entry.entry_id,
        item_id=moved_item_id,
        new_position=2,
    )

    queue_state = entry.runtime_data.queue_state
    assert [item.room_name for item in queue_state.items] == [
        "Room 2",
        "Room 3",
        "Room 1",
    ]
    assert response[ATTR_PENDING_ITEMS] == 3
    assert response[ATTR_RUNNING_ITEMS] == 0
    assert response[ATTR_COMPLETED_ITEMS] == 0
    assert response[ATTR_TOTAL_ITEMS] == 3
    assert response[CONF_CONFIG_ENTRY_ID] == entry.entry_id
    assert response["run_state"] == "idle"
    assert [item[ATTR_ITEM_ID] for item in response[ATTR_QUEUE_ITEMS]] == [
        item.item_id for item in queue_state.items
    ]
    assert [item[CONF_ROOM_NAME] for item in response[ATTR_QUEUE_ITEMS]] == [
        "Room 2",
        "Room 3",
        "Room 1",
    ]


async def test_move_queue_item_service_rejects_unknown_entry_and_invalid_move(
    hass: HomeAssistant,
) -> None:
    """Test the move queue item service rejects invalid requests."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    add_response = await _call_add_queue_room_service(hass, entry.entry_id)
    item_id = add_response[ATTR_QUEUE_ITEMS][0][ATTR_ITEM_ID]

    with pytest.raises(HomeAssistantError):
        await _call_move_queue_item_service(hass, "missing-entry")

    with pytest.raises(HomeAssistantError):
        await _call_move_queue_item_service(hass, entry.entry_id, item_id="missing-item")

    with pytest.raises(HomeAssistantError):
        await _call_move_queue_item_service(
            hass,
            entry.entry_id,
            item_id=item_id,
            new_position=1,
        )


async def test_clear_pending_queue_service_updates_runtime_queue_state(
    hass: HomeAssistant,
) -> None:
    """Test the clear pending queue service removes pending queue items."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=1,
        room_name="Room 1",
    )
    await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=2,
        room_name="Room 2",
    )

    response = await _call_clear_pending_queue_service(hass, entry.entry_id)

    assert entry.runtime_data.queue_state.run_state == "idle"
    assert entry.runtime_data.queue_state.items == ()
    assert response == {
        ATTR_COMPLETED_ITEMS: 0,
        ATTR_PENDING_ITEMS: 0,
        ATTR_QUEUE_ITEMS: [],
        ATTR_RUNNING_ITEMS: 0,
        ATTR_TOTAL_ITEMS: 0,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        "run_state": "idle",
    }


async def test_clear_pending_queue_service_rejects_unknown_entry(
    hass: HomeAssistant,
) -> None:
    """Test the clear pending queue service rejects unknown config entry ids."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(HomeAssistantError):
        await _call_clear_pending_queue_service(hass, "missing-entry")


async def test_update_queue_item_overrides_service_updates_runtime_queue_state(
    hass: HomeAssistant,
) -> None:
    """Test the update overrides service replaces pending item overrides."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    add_response = await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=7,
        room_name="Room 7",
    )
    item_id = add_response[ATTR_QUEUE_ITEMS][0][ATTR_ITEM_ID]
    overrides = {
        "cleaning_mode": "mop",
        "repeats": 2,
        "suction_level": "turbo",
        "water_level": "high",
    }

    response = await _call_update_queue_item_overrides_service(
        hass,
        entry.entry_id,
        item_id=item_id,
        overrides=overrides,
    )

    queue_state = entry.runtime_data.queue_state
    assert queue_state.items[0].overrides == overrides
    assert response == {
        ATTR_COMPLETED_ITEMS: 0,
        ATTR_PENDING_ITEMS: 1,
        ATTR_QUEUE_ITEMS: [
            {
                ATTR_ITEM_ID: item_id,
                ATTR_OVERRIDES: overrides,
                ATTR_RESULT: None,
                ATTR_STATUS: "pending",
                CONF_ROOM_ID: 7,
                CONF_ROOM_NAME: "Room 7",
            }
        ],
        ATTR_RUNNING_ITEMS: 0,
        ATTR_TOTAL_ITEMS: 1,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        "run_state": "idle",
    }


async def test_update_queue_item_overrides_service_rejects_invalid_requests(
    hass: HomeAssistant,
) -> None:
    """Test the update overrides service rejects invalid requests."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    add_response = await _call_add_queue_room_service(hass, entry.entry_id)
    item_id = add_response[ATTR_QUEUE_ITEMS][0][ATTR_ITEM_ID]

    with pytest.raises(HomeAssistantError):
        await _call_update_queue_item_overrides_service(hass, "missing-entry")

    with pytest.raises(HomeAssistantError):
        await _call_update_queue_item_overrides_service(
            hass,
            entry.entry_id,
            item_id="missing-item",
        )

    entry.runtime_data.set_queue_state(start_run(entry.runtime_data.queue_state))

    with pytest.raises(HomeAssistantError):
        await _call_update_queue_item_overrides_service(
            hass,
            entry.entry_id,
            item_id=item_id,
            overrides={"repeats": 2},
        )


async def test_start_queue_service_rejects_disabled_command_gate_without_dispatch(
    hass: HomeAssistant,
) -> None:
    """Test disabled command gate prevents start and dispatch."""
    calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=7,
        room_name="Room 7",
    )

    with pytest.raises(HomeAssistantError, match="robot commands are disabled"):
        await _call_start_queue_service(hass, entry.entry_id)

    assert calls == []
    queue_state = entry.runtime_data.queue_state
    assert entry.runtime_data.run_tracking is None
    assert queue_state.run_state == "idle"
    assert queue_state.items[0].status == "pending"
    assert queue_state.current_item_id is None


async def test_start_queue_service_rejects_empty_queue(
    hass: HomeAssistant,
) -> None:
    """Test the start queue service rejects empty queues."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(HomeAssistantError, match="Queue is empty"):
        await _call_start_queue_service(hass, entry.entry_id)

    assert entry.runtime_data.queue_state.run_state == "idle"
    assert entry.runtime_data.queue_state.items == ()
    assert entry.runtime_data.run_tracking is None


async def test_start_queue_service_dispatches_first_room_and_updates_runtime_state(
    hass: HomeAssistant,
    caplog: LogCaptureFixture,
) -> None:
    """Test start queue dispatches the first pending room and marks it running."""
    calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    caplog.set_level(logging.INFO, "custom_components.ha_dreame.services")
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=7,
        room_name="Room 7",
    )

    response = await _call_start_queue_service(hass, entry.entry_id)

    queue_state = entry.runtime_data.queue_state
    running_item = queue_state.items[0]
    assert calls == [{"entity_id": vacuum_entity_id, "segments": [7]}]
    assert queue_state.run_state == "running"
    assert queue_state.current_item_id == running_item.item_id
    assert running_item.status == "running"
    run_tracking = entry.runtime_data.run_tracking
    assert run_tracking is not None
    assert run_tracking.run_id == queue_state.run_id
    assert run_tracking.current_item_id == running_item.item_id
    assert run_tracking.dispatch_retry_count == 0
    assert run_tracking.task_status_cleared_since_dispatch is False
    assert run_tracking.active_room_mismatch_streak == 0
    datetime.fromisoformat(run_tracking.last_command_at)
    assert response == {
        ATTR_COMPLETED_ITEMS: 0,
        ATTR_PENDING_ITEMS: 0,
        ATTR_QUEUE_ITEMS: [
            {
                ATTR_ITEM_ID: running_item.item_id,
                ATTR_OVERRIDES: {},
                ATTR_RESULT: None,
                ATTR_STATUS: "running",
                CONF_ROOM_ID: 7,
                CONF_ROOM_NAME: "Room 7",
            }
        ],
        ATTR_RUNNING_ITEMS: 1,
        ATTR_TOTAL_ITEMS: 1,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        "run_state": "running",
    }

    runtime_status = await _call_runtime_status_service(hass, entry.entry_id)
    assert runtime_status[ATTR_RUN_TRACKING] == {
        ATTR_ACTIVE_ROOM_MISMATCH_STREAK: 0,
        ATTR_CURRENT_ITEM_ID: running_item.item_id,
        ATTR_DISPATCH_RETRY_COUNT: 0,
        ATTR_LAST_COMMAND_AT: run_tracking.last_command_at,
        ATTR_RUN_ID: queue_state.run_id,
        ATTR_TASK_STATUS_CLEARED_SINCE_DISPATCH: False,
    }
    assert any(
        record.levelno == logging.INFO
        and "HA Dreame queue started" in record.message
        and "room_id=7" in record.message
        for record in caplog.records
    )


async def test_start_queue_service_leaves_queue_idle_when_dispatch_fails(
    hass: HomeAssistant,
) -> None:
    """Test dispatch failures do not mark the queue as running."""
    calls: list[dict[str, object]] = []

    async def _raise_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))
        raise HomeAssistantError("dispatch failed")

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _raise_clean_segment,
    )
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=7,
        room_name="Room 7",
    )

    with pytest.raises(HomeAssistantError, match="dispatch failed"):
        await _call_start_queue_service(hass, entry.entry_id)

    assert calls == [{"entity_id": vacuum_entity_id, "segments": [7]}]
    queue_state = entry.runtime_data.queue_state
    assert queue_state.run_state == "idle"
    assert queue_state.current_item_id is None
    assert queue_state.items[0].status == "pending"
    assert entry.runtime_data.run_tracking is None


async def test_update_running_override_rejects_disabled_command_gate_without_dispatch(
    hass: HomeAssistant,
) -> None:
    """Test disabled command gate prevents running override commands."""
    calls: list[dict[str, object]] = []

    async def _record_select_option(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register("select", "select_option", _record_select_option)
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(hass, entry.entry_id)
    entry.runtime_data.set_queue_state(start_run(entry.runtime_data.queue_state))
    hass.states.async_set("select.dreame_robot_suction_level", "quiet")

    with pytest.raises(HomeAssistantError, match="robot commands are disabled"):
        await _call_update_running_override_service(
            hass,
            entry.entry_id,
            field="suction_level",
            value=1,
        )

    assert calls == []


async def test_update_running_override_rejects_idle_queue_without_dispatch(
    hass: HomeAssistant,
) -> None:
    """Test running override commands are only accepted for active runs."""
    calls: list[dict[str, object]] = []

    async def _record_select_option(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register("select", "select_option", _record_select_option)
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    hass.states.async_set("select.dreame_robot_suction_level", "quiet")

    with pytest.raises(HomeAssistantError, match="Queue is not running"):
        await _call_update_running_override_service(
            hass,
            entry.entry_id,
            field="suction_level",
            value=1,
        )

    assert calls == []


async def test_update_running_suction_override_calls_companion_select(
    hass: HomeAssistant,
) -> None:
    """Test running suction overrides dispatch to the vacuum companion select."""
    calls: list[dict[str, object]] = []

    async def _record_select_option(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register("select", "select_option", _record_select_option)
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(hass, entry.entry_id)
    queue_state = start_run(entry.runtime_data.queue_state)
    entry.runtime_data.set_queue_state(queue_state)
    hass.states.async_set("select.dreame_robot_suction_level", "quiet")

    response = await _call_update_running_override_service(
        hass,
        entry.entry_id,
        field="suction_level",
        value=3,
    )

    assert calls == [
        {
            "entity_id": "select.dreame_robot_suction_level",
            "option": "turbo",
        }
    ]
    assert entry.runtime_data.queue_state == queue_state
    assert response == {
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        CONF_FIELD: "suction_level",
        CONF_VALUE: 3,
        "entity_id": "select.dreame_robot_suction_level",
    }


async def test_update_running_water_override_calls_companion_number(
    hass: HomeAssistant,
) -> None:
    """Test running water overrides dispatch to the vacuum wetness number."""
    calls: list[dict[str, object]] = []

    async def _record_set_value(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register("number", "set_value", _record_set_value)
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(hass, entry.entry_id)
    queue_state = start_run(entry.runtime_data.queue_state)
    entry.runtime_data.set_queue_state(queue_state)
    hass.states.async_set("number.dreame_robot_wetness_level", "8")

    response = await _call_update_running_override_service(
        hass,
        entry.entry_id,
        field="water_volume",
        value=2,
    )

    assert calls == [
        {
            "entity_id": "number.dreame_robot_wetness_level",
            "value": 16,
        }
    ]
    assert entry.runtime_data.queue_state == queue_state
    assert response == {
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        CONF_FIELD: "water_volume",
        CONF_VALUE: 2,
        "entity_id": "number.dreame_robot_wetness_level",
    }


async def test_update_running_override_rejects_invalid_values_without_dispatch(
    hass: HomeAssistant,
) -> None:
    """Test invalid running override values fail before companion service calls."""
    calls: list[dict[str, object]] = []

    async def _record_select_option(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register("select", "select_option", _record_select_option)
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(hass, entry.entry_id)
    entry.runtime_data.set_queue_state(start_run(entry.runtime_data.queue_state))
    hass.states.async_set("select.dreame_robot_suction_level", "quiet")

    with pytest.raises(HomeAssistantError, match="Invalid running override"):
        await _call_update_running_override_service(
            hass,
            entry.entry_id,
            field="suction_level",
            value=4,
        )

    assert calls == []


async def test_cancel_queue_service_rejects_disabled_command_gate_without_dispatch(
    hass: HomeAssistant,
) -> None:
    """Test disabled command gate prevents cancel commands and state mutation."""
    calls: list[dict[str, object]] = []

    async def _record_return_to_base(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register("vacuum", "return_to_base", _record_return_to_base)
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(hass, entry.entry_id)
    queue_state = start_run(entry.runtime_data.queue_state)
    entry.runtime_data.set_queue_state(queue_state)
    run_tracking = QueueRunTracking(
        run_id=queue_state.run_id,
        current_item_id=queue_state.current_item_id,
        last_command_at="2026-01-01T00:00:00+00:00",
    )
    entry.runtime_data.set_run_tracking(run_tracking)

    with pytest.raises(HomeAssistantError, match="robot commands are disabled"):
        await _call_cancel_queue_service(hass, entry.entry_id)

    assert calls == []
    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking == run_tracking


async def test_cancel_queue_service_returns_vacuum_to_base_and_cancels_run(
    hass: HomeAssistant,
) -> None:
    """Test cancel queue sends the robot home and clears active runtime state."""
    clean_calls: list[dict[str, object]] = []
    dock_calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        clean_calls.append(dict(call.data))

    async def _record_return_to_base(call: ServiceCall) -> None:
        dock_calls.append(dict(call.data))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    hass.services.async_register("vacuum", "return_to_base", _record_return_to_base)
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=7,
        room_name="Room 7",
    )
    await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=8,
        room_name="Room 8",
    )
    await _call_start_queue_service(hass, entry.entry_id)

    response = await _call_cancel_queue_service(hass, entry.entry_id)

    queue_state = entry.runtime_data.queue_state
    assert clean_calls == [{"entity_id": vacuum_entity_id, "segments": [7]}]
    assert dock_calls == [{"entity_id": vacuum_entity_id}]
    assert queue_state.run_state == "canceled"
    assert queue_state.current_item_id is None
    assert [item.status for item in queue_state.items] == ["canceled", "canceled"]
    assert [item.result for item in queue_state.items] == [
        "canceled_by_user",
        "canceled_by_user",
    ]
    assert entry.runtime_data.run_tracking is None
    assert response == {
        ATTR_COMPLETED_ITEMS: 0,
        ATTR_PENDING_ITEMS: 0,
        ATTR_QUEUE_ITEMS: [
            {
                ATTR_ITEM_ID: queue_state.items[0].item_id,
                ATTR_OVERRIDES: {},
                ATTR_RESULT: "canceled_by_user",
                ATTR_STATUS: "canceled",
                CONF_ROOM_ID: 7,
                CONF_ROOM_NAME: "Room 7",
            },
            {
                ATTR_ITEM_ID: queue_state.items[1].item_id,
                ATTR_OVERRIDES: {},
                ATTR_RESULT: "canceled_by_user",
                ATTR_STATUS: "canceled",
                CONF_ROOM_ID: 8,
                CONF_ROOM_NAME: "Room 8",
            },
        ],
        ATTR_RUNNING_ITEMS: 0,
        ATTR_TOTAL_ITEMS: 2,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        "run_state": "canceled",
    }


async def test_cancel_queue_service_preserves_runtime_state_when_dock_command_fails(
    hass: HomeAssistant,
) -> None:
    """Test failed cancel commands leave runtime state unchanged."""
    clean_calls: list[dict[str, object]] = []
    dock_calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        clean_calls.append(dict(call.data))

    async def _raise_return_to_base(call: ServiceCall) -> None:
        dock_calls.append(dict(call.data))
        raise HomeAssistantError("dock command failed")

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    hass.services.async_register("vacuum", "return_to_base", _raise_return_to_base)
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(hass, entry.entry_id)
    await _call_start_queue_service(hass, entry.entry_id)
    queue_state = entry.runtime_data.queue_state
    run_tracking = entry.runtime_data.run_tracking

    with pytest.raises(HomeAssistantError, match="dock command failed"):
        await _call_cancel_queue_service(hass, entry.entry_id)

    assert clean_calls == [{"entity_id": vacuum_entity_id, "segments": [1]}]
    assert dock_calls == [{"entity_id": vacuum_entity_id}]
    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking == run_tracking


async def test_resume_queue_service_rejects_disabled_command_gate_without_dispatch(
    hass: HomeAssistant,
) -> None:
    """Test disabled command gate prevents resume commands and state mutation."""
    start_calls: list[dict[str, object]] = []

    async def _record_start(call: ServiceCall) -> None:
        start_calls.append(dict(call.data))

    hass.services.async_register("vacuum", "start", _record_start)
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(hass, entry.entry_id)
    queue_state = start_run(entry.runtime_data.queue_state)
    entry.runtime_data.set_queue_state(queue_state)
    run_tracking = QueueRunTracking(
        run_id=queue_state.run_id,
        current_item_id=queue_state.current_item_id,
        last_command_at="2026-01-01T00:00:00+00:00",
    )
    entry.runtime_data.set_run_tracking(run_tracking)
    hass.states.async_set(vacuum_entity_id, "paused")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning_paused")

    with pytest.raises(HomeAssistantError, match="robot commands are disabled"):
        await _call_resume_queue_service(hass, entry.entry_id)

    assert start_calls == []
    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking == run_tracking


async def test_resume_queue_service_rejects_non_running_queue_without_dispatch(
    hass: HomeAssistant,
) -> None:
    """Test resume requires an active queue run."""
    start_calls: list[dict[str, object]] = []

    async def _record_start(call: ServiceCall) -> None:
        start_calls.append(dict(call.data))

    hass.services.async_register("vacuum", "start", _record_start)
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    hass.states.async_set(vacuum_entity_id, "paused")

    with pytest.raises(HomeAssistantError, match="Queue is not running"):
        await _call_resume_queue_service(hass, entry.entry_id)

    assert start_calls == []


async def test_resume_queue_service_rejects_active_robot_without_dispatch(
    hass: HomeAssistant,
) -> None:
    """Test resume is only available for paused or user-action error states."""
    start_calls: list[dict[str, object]] = []

    async def _record_start(call: ServiceCall) -> None:
        start_calls.append(dict(call.data))

    hass.services.async_register("vacuum", "start", _record_start)
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(hass, entry.entry_id)
    queue_state = start_run(entry.runtime_data.queue_state)
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(
        QueueRunTracking(
            run_id=queue_state.run_id,
            current_item_id=queue_state.current_item_id,
            last_command_at="2026-01-01T00:00:00+00:00",
        )
    )
    hass.states.async_set(vacuum_entity_id, "cleaning")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    hass.states.async_set("sensor.dreame_robot_error", "mop_removed")

    with pytest.raises(HomeAssistantError, match="Robot is not waiting"):
        await _call_resume_queue_service(hass, entry.entry_id)

    assert start_calls == []
    assert entry.runtime_data.queue_state == queue_state


async def test_resume_queue_service_starts_interrupted_robot_and_refreshes_tracking(
    hass: HomeAssistant,
) -> None:
    """Test resume calls vacuum.start and refreshes tracking after an interruption."""
    start_calls: list[dict[str, object]] = []

    async def _record_start(call: ServiceCall) -> None:
        start_calls.append(dict(call.data))

    hass.services.async_register("vacuum", "start", _record_start)
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(hass, entry.entry_id)
    queue_state = start_run(entry.runtime_data.queue_state)
    entry.runtime_data.set_queue_state(queue_state)
    run_tracking = QueueRunTracking(
        run_id=queue_state.run_id,
        current_item_id=queue_state.current_item_id,
        last_command_at="2026-01-01T00:00:00+00:00",
        dispatch_retry_count=2,
    )
    entry.runtime_data.set_run_tracking(run_tracking)
    hass.states.async_set(vacuum_entity_id, "error")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    hass.states.async_set("sensor.dreame_robot_error", "mop_removed")

    response = await _call_resume_queue_service(hass, entry.entry_id)

    refreshed_tracking = entry.runtime_data.run_tracking
    assert start_calls == [{"entity_id": vacuum_entity_id}]
    assert entry.runtime_data.queue_state == queue_state
    assert refreshed_tracking is not None
    assert refreshed_tracking.run_id == run_tracking.run_id
    assert refreshed_tracking.current_item_id == run_tracking.current_item_id
    assert refreshed_tracking.dispatch_retry_count == 0
    assert refreshed_tracking.last_command_at != run_tracking.last_command_at
    assert response == {
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        CONF_VACUUM_ENTITY_ID: vacuum_entity_id,
        "resumed": True,
        "robot_status": {
            "error_code": "mop_removed",
            "interruption_reasons": ["vacuum_error:mop_removed"],
            "interrupted": True,
            "task_status": "room_cleaning",
            "vacuum_state": "error",
        },
    }


async def test_skip_current_room_service_rejects_disabled_command_gate_without_dispatch(
    hass: HomeAssistant,
) -> None:
    """Test disabled command gate prevents skip commands and state mutation."""
    stop_calls: list[dict[str, object]] = []

    async def _record_stop(call: ServiceCall) -> None:
        stop_calls.append(dict(call.data))

    hass.services.async_register("vacuum", "stop", _record_stop)
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(hass, entry.entry_id)
    await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=2,
        room_name="Room 2",
    )
    queue_state = start_run(entry.runtime_data.queue_state)
    entry.runtime_data.set_queue_state(queue_state)
    run_tracking = QueueRunTracking(
        run_id=queue_state.run_id,
        current_item_id=queue_state.current_item_id,
        last_command_at="2026-01-01T00:00:00+00:00",
    )
    entry.runtime_data.set_run_tracking(run_tracking)

    with pytest.raises(HomeAssistantError, match="robot commands are disabled"):
        await _call_skip_current_room_service(hass, entry.entry_id)

    assert stop_calls == []
    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking == run_tracking


async def test_skip_current_room_service_rejects_non_running_queue_without_dispatch(
    hass: HomeAssistant,
) -> None:
    """Test skip current room rejects idle queues before robot commands."""
    stop_calls: list[dict[str, object]] = []

    async def _record_stop(call: ServiceCall) -> None:
        stop_calls.append(dict(call.data))

    hass.services.async_register("vacuum", "stop", _record_stop)
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(hass, entry.entry_id)

    with pytest.raises(HomeAssistantError, match="Queue is not running"):
        await _call_skip_current_room_service(hass, entry.entry_id)

    assert stop_calls == []
    assert entry.runtime_data.queue_state.run_state == "idle"
    assert entry.runtime_data.run_tracking is None


async def test_skip_current_room_service_advances_and_dispatches_next_room(
    hass: HomeAssistant,
) -> None:
    """Test skipping with pending work dispatches the next queue room."""
    clean_calls: list[dict[str, object]] = []
    stop_calls: list[dict[str, object]] = []
    dock_calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        clean_calls.append(dict(call.data))

    async def _record_stop(call: ServiceCall) -> None:
        stop_calls.append(dict(call.data))

    async def _record_return_to_base(call: ServiceCall) -> None:
        dock_calls.append(dict(call.data))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    hass.services.async_register("vacuum", "stop", _record_stop)
    hass.services.async_register("vacuum", "return_to_base", _record_return_to_base)
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=7,
        room_name="Room 7",
    )
    await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=8,
        room_name="Room 8",
    )
    await _call_start_queue_service(hass, entry.entry_id)
    first_item_id = entry.runtime_data.queue_state.items[0].item_id

    response = await _call_skip_current_room_service(hass, entry.entry_id)

    queue_state = entry.runtime_data.queue_state
    next_item = queue_state.items[1]
    assert clean_calls == [
        {"entity_id": vacuum_entity_id, "segments": [7]},
        {"entity_id": vacuum_entity_id, "segments": [8]},
    ]
    assert stop_calls == [{"entity_id": vacuum_entity_id}]
    assert dock_calls == []
    assert queue_state.run_state == "running"
    assert queue_state.current_item_id == next_item.item_id
    assert [item.status for item in queue_state.items] == ["skipped", "running"]
    assert queue_state.items[0].result == "skip_pressed"
    run_tracking = entry.runtime_data.run_tracking
    assert run_tracking is not None
    assert run_tracking.run_id == queue_state.run_id
    assert run_tracking.current_item_id == next_item.item_id
    assert run_tracking.dispatch_retry_count == 0
    assert run_tracking.task_status_cleared_since_dispatch is False
    datetime.fromisoformat(run_tracking.last_command_at)
    assert response == {
        ATTR_COMPLETED_ITEMS: 0,
        ATTR_PENDING_ITEMS: 0,
        ATTR_QUEUE_ITEMS: [
            {
                ATTR_ITEM_ID: first_item_id,
                ATTR_OVERRIDES: {},
                ATTR_RESULT: "skip_pressed",
                ATTR_STATUS: "skipped",
                CONF_ROOM_ID: 7,
                CONF_ROOM_NAME: "Room 7",
            },
            {
                ATTR_ITEM_ID: next_item.item_id,
                ATTR_OVERRIDES: {},
                ATTR_RESULT: None,
                ATTR_STATUS: "running",
                CONF_ROOM_ID: 8,
                CONF_ROOM_NAME: "Room 8",
            },
        ],
        ATTR_RUNNING_ITEMS: 1,
        ATTR_TOTAL_ITEMS: 2,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        "run_state": "running",
    }


async def test_skip_current_room_service_sends_final_skipped_room_home(
    hass: HomeAssistant,
) -> None:
    """Test skipping the final running room sends the robot home."""
    clean_calls: list[dict[str, object]] = []
    dock_calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        clean_calls.append(dict(call.data))

    async def _record_return_to_base(call: ServiceCall) -> None:
        dock_calls.append(dict(call.data))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    hass.services.async_register("vacuum", "return_to_base", _record_return_to_base)
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=7,
        room_name="Room 7",
    )
    await _call_start_queue_service(hass, entry.entry_id)

    response = await _call_skip_current_room_service(hass, entry.entry_id)

    queue_state = entry.runtime_data.queue_state
    skipped_item = queue_state.items[0]
    assert clean_calls == [{"entity_id": vacuum_entity_id, "segments": [7]}]
    assert dock_calls == [{"entity_id": vacuum_entity_id}]
    assert queue_state.run_state == "completed"
    assert queue_state.current_item_id is None
    assert skipped_item.status == "skipped"
    assert skipped_item.result == "skip_pressed"
    assert entry.runtime_data.run_tracking is None
    assert response == {
        ATTR_COMPLETED_ITEMS: 0,
        ATTR_PENDING_ITEMS: 0,
        ATTR_QUEUE_ITEMS: [
            {
                ATTR_ITEM_ID: skipped_item.item_id,
                ATTR_OVERRIDES: {},
                ATTR_RESULT: "skip_pressed",
                ATTR_STATUS: "skipped",
                CONF_ROOM_ID: 7,
                CONF_ROOM_NAME: "Room 7",
            }
        ],
        ATTR_RUNNING_ITEMS: 0,
        ATTR_TOTAL_ITEMS: 1,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        "run_state": "completed",
    }


async def test_skip_current_room_service_preserves_runtime_state_when_stop_fails(
    hass: HomeAssistant,
) -> None:
    """Test stop failures leave runtime state unchanged while skipping."""
    clean_calls: list[dict[str, object]] = []
    stop_calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        clean_calls.append(dict(call.data))

    async def _raise_stop(call: ServiceCall) -> None:
        stop_calls.append(dict(call.data))
        raise HomeAssistantError("stop failed")

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    hass.services.async_register("vacuum", "stop", _raise_stop)
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await _call_add_queue_room_service(hass, entry.entry_id)
    await _call_add_queue_room_service(
        hass,
        entry.entry_id,
        room_id=2,
        room_name="Room 2",
    )
    await _call_start_queue_service(hass, entry.entry_id)
    queue_state = entry.runtime_data.queue_state
    run_tracking = entry.runtime_data.run_tracking

    with pytest.raises(HomeAssistantError, match="stop failed"):
        await _call_skip_current_room_service(hass, entry.entry_id)

    assert clean_calls == [{"entity_id": vacuum_entity_id, "segments": [1]}]
    assert stop_calls == [{"entity_id": vacuum_entity_id}]
    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking == run_tracking


async def test_runtime_status_service_returns_entry_runtime_data(
    hass: HomeAssistant,
) -> None:
    """Test the read-only runtime status service response."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert await _call_runtime_status_service(hass, entry.entry_id) == {
        CONF_ALLOW_ROBOT_COMMANDS: True,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        ATTR_RUN_TRACKING: None,
        "robot_status": {
            "error_code": "",
            "interruption_reasons": [],
            "interrupted": False,
            "task_status": "",
            "vacuum_state": "",
        },
        CONF_VACUUM_ENTITY_ID: vacuum_entity_id,
    }


async def test_runtime_status_service_reflects_reloaded_command_gate(
    hass: HomeAssistant,
) -> None:
    """Test the service reports command gate changes after options reload."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
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
        ATTR_RUN_TRACKING: None,
        "robot_status": {
            "error_code": "",
            "interruption_reasons": [],
            "interrupted": False,
            "task_status": "",
            "vacuum_state": "",
        },
        CONF_VACUUM_ENTITY_ID: vacuum_entity_id,
    }


async def test_runtime_status_service_rejects_unknown_entry(
    hass: HomeAssistant,
) -> None:
    """Test the service rejects unknown config entry ids."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(HomeAssistantError):
        await _call_runtime_status_service(hass, "missing-entry")


async def test_control_readiness_reports_read_only_safe_default(
    hass: HomeAssistant,
) -> None:
    """Test control readiness reports safe default state before manual testing."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    hass.states.async_set(vacuum_entity_id, "docked")

    assert await _call_control_readiness_service(hass, entry.entry_id) == {
        CONF_ALLOW_ROBOT_COMMANDS: False,
        CONF_AUTO_RECONCILE_ENABLED: False,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        CONF_VACUUM_ENTITY_ID: vacuum_entity_id,
        ATTR_PENDING_ITEMS: 0,
        ATTR_RUNNING_ITEMS: 0,
        "available_actions": [],
        "blocking_reasons": [
            "robot_commands_disabled",
            "queue_has_no_pending_items",
        ],
        "companion_entities": {
            "suction_level": {
                "available": False,
                "entity_id": "select.dreame_robot_suction_level",
            },
            "water_volume": {
                "available": False,
                "entity_id": "number.dreame_robot_wetness_level",
            },
        },
        "queue_run_state": "idle",
        "ready_for_control_window": False,
        "ready_for_read_only_observation": True,
        "robot_status": {
            "error_code": "",
            "interruption_reasons": [],
            "interrupted": False,
            "task_status": "",
            "vacuum_state": "docked",
        },
        "running_override_ready": False,
        "vacuum_available": True,
    }


async def test_control_readiness_reports_start_queue_ready(
    hass: HomeAssistant,
) -> None:
    """Test control readiness reports start readiness for a pending queue."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    hass.states.async_set(vacuum_entity_id, "docked")
    await _call_add_queue_room_service(hass, entry.entry_id)

    response = await _call_control_readiness_service(hass, entry.entry_id)

    assert response["ready_for_read_only_observation"] is True
    assert response["ready_for_control_window"] is True
    assert response["queue_run_state"] == "idle"
    assert response[ATTR_PENDING_ITEMS] == 1
    assert response["available_actions"] == [SERVICE_START_QUEUE]
    assert response["blocking_reasons"] == []


async def test_control_readiness_reports_running_override_ready(
    hass: HomeAssistant,
) -> None:
    """Test control readiness reports live override companion readiness."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={
            CONF_ALLOW_ROBOT_COMMANDS: True,
            CONF_AUTO_RECONCILE_ENABLED: True,
        },
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    hass.states.async_set(vacuum_entity_id, "cleaning")
    hass.states.async_set("select.dreame_robot_suction_level", "quiet")
    hass.states.async_set("number.dreame_robot_wetness_level", "8")
    await _call_add_queue_room_service(hass, entry.entry_id)
    entry.runtime_data.set_queue_state(start_run(entry.runtime_data.queue_state))

    assert await _call_control_readiness_service(hass, entry.entry_id) == {
        CONF_ALLOW_ROBOT_COMMANDS: True,
        CONF_AUTO_RECONCILE_ENABLED: True,
        CONF_CONFIG_ENTRY_ID: entry.entry_id,
        CONF_VACUUM_ENTITY_ID: vacuum_entity_id,
        ATTR_PENDING_ITEMS: 0,
        ATTR_RUNNING_ITEMS: 1,
        "available_actions": [
            SERVICE_CANCEL_QUEUE,
            SERVICE_SKIP_CURRENT_ROOM,
            SERVICE_UPDATE_RUNNING_OVERRIDE,
        ],
        "blocking_reasons": [],
        "companion_entities": {
            "suction_level": {
                "available": True,
                "entity_id": "select.dreame_robot_suction_level",
            },
            "water_volume": {
                "available": True,
                "entity_id": "number.dreame_robot_wetness_level",
            },
        },
        "queue_run_state": "running",
        "ready_for_control_window": True,
        "ready_for_read_only_observation": True,
        "robot_status": {
            "error_code": "",
            "interruption_reasons": [],
            "interrupted": False,
            "task_status": "",
            "vacuum_state": "cleaning",
        },
        "running_override_ready": True,
        "vacuum_available": True,
    }


async def test_control_readiness_reports_resume_for_interrupted_running_queue(
    hass: HomeAssistant,
) -> None:
    """Test control readiness exposes Continue/End actions for interrupted runs."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    hass.states.async_set(vacuum_entity_id, "paused")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning_paused")
    hass.states.async_set("sensor.dreame_robot_error", "slippery_floor")
    await _call_add_queue_room_service(hass, entry.entry_id)
    entry.runtime_data.set_queue_state(start_run(entry.runtime_data.queue_state))

    response = await _call_control_readiness_service(hass, entry.entry_id)

    assert response["available_actions"] == [
        SERVICE_RESUME_QUEUE,
        SERVICE_CANCEL_QUEUE,
    ]
    assert response["ready_for_control_window"] is True
    assert response["robot_status"] == {
        "error_code": "slippery_floor",
        "interruption_reasons": [
            "vacuum_paused",
            "task_status_paused",
            "vacuum_error:slippery_floor",
        ],
        "interrupted": True,
        "task_status": "room_cleaning_paused",
        "vacuum_state": "paused",
    }


async def test_control_readiness_reports_missing_running_override_entities(
    hass: HomeAssistant,
) -> None:
    """Test running control readiness keeps cancel and skip separate from overrides."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: True},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    hass.states.async_set(vacuum_entity_id, "cleaning")
    await _call_add_queue_room_service(hass, entry.entry_id)
    entry.runtime_data.set_queue_state(start_run(entry.runtime_data.queue_state))

    response = await _call_control_readiness_service(hass, entry.entry_id)

    assert response["ready_for_control_window"] is True
    assert response["available_actions"] == [
        SERVICE_CANCEL_QUEUE,
        SERVICE_SKIP_CURRENT_ROOM,
    ]
    assert response["running_override_ready"] is False
    assert response["blocking_reasons"] == [
        "running_override_entities_unavailable",
    ]


async def test_control_readiness_service_rejects_unknown_entry(
    hass: HomeAssistant,
) -> None:
    """Test control readiness rejects unknown config entry ids."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(HomeAssistantError):
        await _call_control_readiness_service(hass, "missing-entry")


async def test_unload_last_entry_removes_runtime_status_service(
    hass: HomeAssistant,
) -> None:
    """Test unloading the last entry removes the read-only service."""
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert hass.services.has_service(DOMAIN, SERVICE_CLEAR_PENDING_QUEUE)
    assert hass.services.has_service(DOMAIN, SERVICE_CANCEL_QUEUE)
    assert hass.services.has_service(DOMAIN, SERVICE_GET_CONTROL_READINESS)
    assert hass.services.has_service(DOMAIN, SERVICE_GET_RUNTIME_STATUS)
    assert hass.services.has_service(DOMAIN, SERVICE_MOVE_QUEUE_ITEM)
    assert hass.services.has_service(DOMAIN, SERVICE_REMOVE_QUEUE_ITEM)
    assert hass.services.has_service(DOMAIN, SERVICE_RESUME_QUEUE)
    assert hass.services.has_service(DOMAIN, SERVICE_SKIP_CURRENT_ROOM)
    assert hass.services.has_service(DOMAIN, SERVICE_START_QUEUE)
    assert hass.services.has_service(DOMAIN, SERVICE_UPDATE_QUEUE_ITEM_OVERRIDES)
    assert hass.services.has_service(DOMAIN, SERVICE_UPDATE_RUNNING_OVERRIDE)

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert not hass.services.has_service(DOMAIN, SERVICE_GET_RUNTIME_STATUS)
    assert not hass.services.has_service(DOMAIN, SERVICE_ADD_QUEUE_ROOM)
    assert not hass.services.has_service(DOMAIN, SERVICE_CANCEL_QUEUE)
    assert not hass.services.has_service(DOMAIN, SERVICE_CLEAR_PENDING_QUEUE)
    assert not hass.services.has_service(DOMAIN, SERVICE_GET_CONTROL_READINESS)
    assert not hass.services.has_service(DOMAIN, SERVICE_MOVE_QUEUE_ITEM)
    assert not hass.services.has_service(DOMAIN, SERVICE_REMOVE_QUEUE_ITEM)
    assert not hass.services.has_service(DOMAIN, SERVICE_RESUME_QUEUE)
    assert not hass.services.has_service(DOMAIN, SERVICE_SKIP_CURRENT_ROOM)
    assert not hass.services.has_service(DOMAIN, SERVICE_START_QUEUE)
    assert not hass.services.has_service(DOMAIN, SERVICE_UPDATE_QUEUE_ITEM_OVERRIDES)
    assert not hass.services.has_service(DOMAIN, SERVICE_UPDATE_RUNNING_OVERRIDE)

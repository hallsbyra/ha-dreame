"""Tests for HA Dreame services."""

from datetime import datetime

import pytest

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

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
    CONF_CONFIG_ENTRY_ID,
    CONF_ITEM_ID,
    CONF_NEW_POSITION,
    CONF_OVERRIDES,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_VACUUM_ENTITY_ID,
    DOMAIN,
    DREAME_VACUUM_DOMAIN,
    SERVICE_ADD_QUEUE_ROOM,
    SERVICE_CLEAR_PENDING_QUEUE,
    SERVICE_GET_RUNTIME_STATUS,
    SERVICE_MOVE_QUEUE_ITEM,
    SERVICE_REMOVE_QUEUE_ITEM,
    SERVICE_START_QUEUE,
    SERVICE_UPDATE_QUEUE_ITEM_OVERRIDES,
)
from custom_components.ha_dreame.queue_core import start_run

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
    assert hass.services.has_service(DOMAIN, SERVICE_GET_RUNTIME_STATUS)
    assert hass.services.has_service(DOMAIN, SERVICE_MOVE_QUEUE_ITEM)
    assert hass.services.has_service(DOMAIN, SERVICE_REMOVE_QUEUE_ITEM)
    assert hass.services.has_service(DOMAIN, SERVICE_START_QUEUE)
    assert hass.services.has_service(DOMAIN, SERVICE_UPDATE_QUEUE_ITEM_OVERRIDES)

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert not hass.services.has_service(DOMAIN, SERVICE_GET_RUNTIME_STATUS)
    assert not hass.services.has_service(DOMAIN, SERVICE_ADD_QUEUE_ROOM)
    assert not hass.services.has_service(DOMAIN, SERVICE_CLEAR_PENDING_QUEUE)
    assert not hass.services.has_service(DOMAIN, SERVICE_MOVE_QUEUE_ITEM)
    assert not hass.services.has_service(DOMAIN, SERVICE_REMOVE_QUEUE_ITEM)
    assert not hass.services.has_service(DOMAIN, SERVICE_START_QUEUE)
    assert not hass.services.has_service(DOMAIN, SERVICE_UPDATE_QUEUE_ITEM_OVERRIDES)

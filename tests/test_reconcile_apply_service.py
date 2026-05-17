"""Tests for the manual reconcile apply service."""

import pytest

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from custom_components.ha_dreame.const import (
    ATTR_COMPLETED_ITEMS,
    ATTR_PENDING_ITEMS,
    ATTR_RUNNING_ITEMS,
    CONF_ALLOW_ROBOT_COMMANDS,
    CONF_CONFIG_ENTRY_ID,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_VACUUM_ENTITY_ID,
    DOMAIN,
    DREAME_VACUUM_DOMAIN,
    SERVICE_APPLY_RECONCILE,
)
from custom_components.ha_dreame.queue_core import QueueState, add_room, start_run
from custom_components.ha_dreame.runtime_state import QueueRunTracking

from .helpers import mock_entry, register_entity

pytestmark = pytest.mark.usefixtures("mock_dreame_vacuum_dependency")


async def _setup_loaded_entry(
    hass: HomeAssistant,
    *,
    commands_enabled: bool = True,
) -> tuple[str, object]:
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: commands_enabled},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return vacuum_entity_id, entry


async def _call_apply_reconcile_service(
    hass: HomeAssistant,
    config_entry_id: str,
) -> dict[str, object]:
    return await hass.services.async_call(
        DOMAIN,
        SERVICE_APPLY_RECONCILE,
        {CONF_CONFIG_ENTRY_ID: config_entry_id},
        blocking=True,
        return_response=True,
    )


def _running_state() -> QueueState:
    state = add_room(QueueState(), room_id=1, room_name="Kitchen")
    state = add_room(state, room_id=2, room_name="Hall")
    return start_run(state)


def _tracking(state: QueueState, **overrides: object) -> QueueRunTracking:
    assert state.run_id is not None
    assert state.current_item_id is not None
    values = {
        "run_id": state.run_id,
        "current_item_id": state.current_item_id,
        "last_command_at": "2000-01-01T00:00:00+00:00",
    }
    values.update(overrides)
    return QueueRunTracking(**values)


def _set_current_room(hass: HomeAssistant, room_id: int, room_name: str) -> None:
    hass.states.async_set(
        "sensor.dreame_robot_current_room",
        room_name,
        {CONF_ROOM_ID: str(room_id), CONF_ROOM_NAME: room_name},
    )


async def test_setup_entry_registers_apply_reconcile_service(
    hass: HomeAssistant,
) -> None:
    """Test setup registers the manual reconcile apply service."""
    await _setup_loaded_entry(hass)

    assert hass.services.has_service(DOMAIN, SERVICE_APPLY_RECONCILE)


async def test_unload_entry_removes_apply_reconcile_service(
    hass: HomeAssistant,
) -> None:
    """Test unload removes the manual reconcile apply service."""
    _, entry = await _setup_loaded_entry(hass)

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert not hass.services.has_service(DOMAIN, SERVICE_APPLY_RECONCILE)


async def test_apply_reconcile_rejects_unknown_entry(
    hass: HomeAssistant,
) -> None:
    """Test unknown entries raise Home Assistant service errors."""
    await _setup_loaded_entry(hass)

    with pytest.raises(HomeAssistantError, match="not loaded"):
        await _call_apply_reconcile_service(hass, "missing-entry")


async def test_apply_reconcile_rejects_disabled_command_gate_without_mutating(
    hass: HomeAssistant,
) -> None:
    """Test disabled command gate prevents reconcile application."""
    calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    vacuum_entity_id, entry = await _setup_loaded_entry(hass, commands_enabled=False)
    queue_state = _running_state()
    run_tracking = _tracking(queue_state, task_status_cleared_since_dispatch=True)
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(run_tracking)
    hass.states.async_set(vacuum_entity_id, "idle")
    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    _set_current_room(hass, 1, "Kitchen")

    with pytest.raises(HomeAssistantError, match="robot commands are disabled"):
        await _call_apply_reconcile_service(hass, entry.entry_id)

    assert calls == []
    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking == run_tracking


async def test_apply_reconcile_noop_returns_observation_without_mutating(
    hass: HomeAssistant,
) -> None:
    """Test no-op reconcile decisions return inspectable data only."""
    vacuum_entity_id, entry = await _setup_loaded_entry(hass)
    hass.states.async_set(vacuum_entity_id, "cleaning")

    response = await _call_apply_reconcile_service(hass, entry.entry_id)

    assert response[CONF_CONFIG_ENTRY_ID] == entry.entry_id
    assert response["observation"]["vacuum_state"] == "cleaning"
    assert response["evaluation"]["awaiting_completion_event"] is False
    assert response["decision"]["event_reasons"] == []
    assert response["applied"] == {
        "command_intent": None,
        "command_item_id": None,
        "event_reasons": [],
    }
    assert response["queue"]["run_state"] == "idle"
    assert entry.runtime_data.queue_state == QueueState()
    assert entry.runtime_data.run_tracking is None


async def test_apply_reconcile_updates_tracking_only_decision_without_robot_calls(
    hass: HomeAssistant,
) -> None:
    """Test tracking-only decisions update run tracking and do not call robot services."""
    calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    vacuum_entity_id, entry = await _setup_loaded_entry(hass)
    queue_state = _running_state()
    run_tracking = _tracking(queue_state, task_status_cleared_since_dispatch=False)
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(run_tracking)
    hass.states.async_set(vacuum_entity_id, "cleaning")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    _set_current_room(hass, 1, "Kitchen")

    response = await _call_apply_reconcile_service(hass, entry.entry_id)

    assert calls == []
    assert response["decision"]["set_task_status_cleared_since_dispatch"] is True
    assert response["applied"]["command_intent"] is None
    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking is not None
    assert entry.runtime_data.run_tracking.task_status_cleared_since_dispatch is True


async def test_apply_reconcile_completion_dispatches_next_room(
    hass: HomeAssistant,
) -> None:
    """Test completion decisions dispatch the next room and update runtime state."""
    calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    vacuum_entity_id, entry = await _setup_loaded_entry(hass)
    queue_state = _running_state()
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(
        _tracking(queue_state, task_status_cleared_since_dispatch=True)
    )
    hass.states.async_set(vacuum_entity_id, "idle")
    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    _set_current_room(hass, 1, "Kitchen")

    response = await _call_apply_reconcile_service(hass, entry.entry_id)

    next_item = entry.runtime_data.queue_state.items[1]
    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert response["decision"]["complete_current_room"] is True
    assert response["applied"] == {
        "command_intent": "dispatch_current_room",
        "command_item_id": next_item.item_id,
        "event_reasons": ["task_status_completed"],
    }
    assert response["queue"][ATTR_COMPLETED_ITEMS] == 1
    assert response["queue"][ATTR_RUNNING_ITEMS] == 1
    assert response["queue"][ATTR_PENDING_ITEMS] == 0
    assert entry.runtime_data.queue_state.run_state == "running"
    assert entry.runtime_data.queue_state.current_item_id == next_item.item_id
    assert entry.runtime_data.run_tracking is not None
    assert entry.runtime_data.run_tracking.current_item_id == next_item.item_id


async def test_apply_reconcile_dispatch_failure_preserves_runtime_state(
    hass: HomeAssistant,
) -> None:
    """Test dispatch failures leave runtime state unchanged."""
    calls: list[dict[str, object]] = []

    async def _raise_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))
        raise HomeAssistantError("dispatch failed")

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _raise_clean_segment,
    )
    vacuum_entity_id, entry = await _setup_loaded_entry(hass)
    queue_state = _running_state()
    run_tracking = _tracking(queue_state, task_status_cleared_since_dispatch=True)
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(run_tracking)
    hass.states.async_set(vacuum_entity_id, "idle")
    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    _set_current_room(hass, 1, "Kitchen")

    with pytest.raises(HomeAssistantError, match="dispatch failed"):
        await _call_apply_reconcile_service(hass, entry.entry_id)

    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking == run_tracking


async def test_apply_reconcile_resume_intent_errors_without_mutating(
    hass: HomeAssistant,
) -> None:
    """Test unsupported resume intents surface an error and preserve state."""
    vacuum_entity_id, entry = await _setup_loaded_entry(hass)
    queue_state = _running_state()
    run_tracking = _tracking(queue_state)
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(run_tracking)
    hass.states.async_set(vacuum_entity_id, "cleaning")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    hass.states.async_set("sensor.dreame_robot_state", "washing_paused")
    hass.states.async_set("sensor.dreame_robot_clean_water_tank_status", "installed")
    _set_current_room(hass, 1, "Kitchen")

    with pytest.raises(HomeAssistantError, match="Resume reconcile intent is not wired"):
        await _call_apply_reconcile_service(hass, entry.entry_id)

    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking == run_tracking

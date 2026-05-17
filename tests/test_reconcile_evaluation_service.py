"""Tests for the read-only reconcile evaluation service."""

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from custom_components.ha_dreame.const import (
    CONF_CONFIG_ENTRY_ID,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_VACUUM_ENTITY_ID,
    DOMAIN,
    SERVICE_EVALUATE_RECONCILE,
)
from custom_components.ha_dreame.queue_core import QueueState, add_room, start_run
from custom_components.ha_dreame.runtime_state import QueueRunTracking

from .helpers import mock_entry, register_entity


async def _setup_loaded_entry(hass: HomeAssistant) -> tuple[str, object]:
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({CONF_VACUUM_ENTITY_ID: vacuum_entity_id})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return vacuum_entity_id, entry


async def _call_evaluate_reconcile_service(
    hass: HomeAssistant,
    config_entry_id: str,
) -> dict[str, object]:
    return await hass.services.async_call(
        DOMAIN,
        SERVICE_EVALUATE_RECONCILE,
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
        "task_status_cleared_since_dispatch": True,
    }
    values.update(overrides)
    return QueueRunTracking(**values)


async def test_setup_entry_registers_evaluate_reconcile_service(
    hass: HomeAssistant,
    mock_dreame_vacuum_dependency: None,
) -> None:
    """Test setup registers the read-only reconcile evaluation service."""
    await _setup_loaded_entry(hass)

    assert hass.services.has_service(DOMAIN, SERVICE_EVALUATE_RECONCILE)


async def test_unload_entry_removes_evaluate_reconcile_service(
    hass: HomeAssistant,
    mock_dreame_vacuum_dependency: None,
) -> None:
    """Test unload removes the read-only reconcile evaluation service."""
    _, entry = await _setup_loaded_entry(hass)

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert not hass.services.has_service(DOMAIN, SERVICE_EVALUATE_RECONCILE)


async def test_evaluate_reconcile_rejects_unknown_entry(
    hass: HomeAssistant,
    mock_dreame_vacuum_dependency: None,
) -> None:
    """Test unknown entries raise Home Assistant service errors."""
    await _setup_loaded_entry(hass)

    try:
        await _call_evaluate_reconcile_service(hass, "missing-entry")
    except HomeAssistantError as err:
        assert "not loaded" in str(err)
    else:
        raise AssertionError("Expected HomeAssistantError")


async def test_evaluate_reconcile_returns_noop_for_idle_queue(
    hass: HomeAssistant,
    mock_dreame_vacuum_dependency: None,
) -> None:
    """Test idle queues return safe observation data and no-op decisions."""
    vacuum_entity_id, entry = await _setup_loaded_entry(hass)
    hass.states.async_set(vacuum_entity_id, "cleaning")

    response = await _call_evaluate_reconcile_service(hass, entry.entry_id)

    assert response[CONF_CONFIG_ENTRY_ID] == entry.entry_id
    assert response["observation"]["vacuum_state"] == "cleaning"
    assert response["observation"]["task_status"] == ""
    assert response["evaluation"]["awaiting_completion_event"] is False
    assert response["evaluation"]["expected_room_id"] is None
    assert response["decision"] == {
        "complete_current_room": False,
        "retry_current_room": False,
        "resume_current_room": False,
        "mark_out_of_sync_reason": None,
        "set_task_status_cleared_since_dispatch": False,
        "reset_dispatch_retry_count": False,
        "event_reasons": [],
    }
    assert entry.runtime_data.queue_state == QueueState()
    assert entry.runtime_data.run_tracking is None


async def test_evaluate_reconcile_returns_decision_for_running_queue(
    hass: HomeAssistant,
    mock_dreame_vacuum_dependency: None,
) -> None:
    """Test running queues return expected room metadata and decision fields."""
    vacuum_entity_id, entry = await _setup_loaded_entry(hass)
    queue_state = _running_state()
    run_tracking = _tracking(queue_state)
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(run_tracking)
    hass.states.async_set(vacuum_entity_id, "idle")
    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    hass.states.async_set(
        "sensor.dreame_robot_current_room",
        "Kitchen",
        {CONF_ROOM_ID: "1", CONF_ROOM_NAME: "Kitchen"},
    )

    response = await _call_evaluate_reconcile_service(hass, entry.entry_id)

    assert response["observation"]["task_status"] == "completed"
    assert response["observation"]["observed_room_id"] == 1
    assert response["evaluation"]["awaiting_completion_event"] is True
    assert response["evaluation"]["expected_room_id"] == 1
    assert response["evaluation"]["expected_room_name"] == "Kitchen"
    assert response["decision"]["complete_current_room"] is True
    assert response["decision"]["event_reasons"] == ["task_status_completed"]
    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking == run_tracking


async def test_evaluate_reconcile_does_not_call_vacuum_services(
    hass: HomeAssistant,
    mock_dreame_vacuum_dependency: None,
) -> None:
    """Test reconcile evaluation is read-only and does not issue robot commands."""
    vacuum_entity_id, entry = await _setup_loaded_entry(hass)
    queue_state = _running_state()
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(_tracking(queue_state, dispatch_retry_count=1))
    hass.states.async_set(vacuum_entity_id, "idle")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")

    calls: list[ServiceCall] = []

    async def _record_call(call: ServiceCall) -> None:
        calls.append(call)

    hass.services.async_register("vacuum", "return_to_base", _record_call)
    hass.services.async_register("vacuum", "send_command", _record_call)
    hass.services.async_register("vacuum", "stop", _record_call)

    response = await _call_evaluate_reconcile_service(hass, entry.entry_id)

    assert response["decision"]["retry_current_room"] is True
    assert calls == []
    assert entry.runtime_data.queue_state == queue_state

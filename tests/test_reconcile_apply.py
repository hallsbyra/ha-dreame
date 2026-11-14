"""Tests for applying one reconcile decision to the runtime queue."""

from dataclasses import replace

from datetime import datetime

import pytest

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from custom_components.ha_dreame.const import (
    CONF_ALLOW_ROBOT_COMMANDS,
    CONF_CURRENT_ROOM_ENTITY_ID,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_TASK_STATUS_ENTITY_ID,
    CONF_VACUUM_ENTITY_ID,
    DOMAIN,
    DREAME_VACUUM_DOMAIN,
)
from custom_components.ha_dreame.queue_core import QueueState, add_room, start_run
from custom_components.ha_dreame.reconcile import ReconcileEvaluation, async_reconcile_under_lock
from custom_components.ha_dreame.queue_core import DispatchTracking

from .helpers import mock_entry, register_entity, set_dispatch, without_dispatch

pytestmark = pytest.mark.usefixtures("mock_dreame_vacuum_dependency")


async def _setup_loaded_entry(
    hass: HomeAssistant,
    *,
    commands_enabled: bool = True,
    options: dict[str, object] | None = None,
) -> tuple[str, object]:
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: commands_enabled, **(options or {})},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return vacuum_entity_id, entry


async def _reconcile(hass: HomeAssistant, entry) -> ReconcileEvaluation:
    """Run one reconcile pass the way the automatic tick does."""
    runtime_data = entry.runtime_data
    async with runtime_data.operation_lock:
        return await async_reconcile_under_lock(hass, runtime_data)


def _running_state() -> QueueState:
    state = add_room(QueueState(), room_id=1, room_name="Kitchen")
    state = add_room(state, room_id=2, room_name="Hall")
    return start_run(state)


def _tracking(state: QueueState, **overrides: object) -> DispatchTracking:
    values = {
        "last_command_at": datetime.fromisoformat("2000-01-01T00:00:00+00:00"),
    }
    values.update(overrides)
    return DispatchTracking(**values)


def _record(hass: HomeAssistant, domain: str, service: str, *, error: str | None = None):
    calls: list[dict[str, object]] = []

    async def _handle(call: ServiceCall) -> None:
        calls.append(dict(call.data))
        if error is not None:
            raise HomeAssistantError(error)

    hass.services.async_register(domain, service, _handle)
    return calls


def _set_current_room(hass: HomeAssistant, room_id: int, room_name: str) -> None:
    hass.states.async_set(
        "sensor.dreame_robot_current_room",
        room_name,
        {CONF_ROOM_ID: str(room_id), CONF_ROOM_NAME: room_name},
    )


async def test_manual_apply_reconcile_service_is_not_registered(
    hass: HomeAssistant,
) -> None:
    """Test reconciliation is automatic only; manual stepping is no longer a service."""
    await _setup_loaded_entry(hass)

    assert not hass.services.has_service(DOMAIN, "apply_reconcile")


async def test_reconcile_without_awaited_room_returns_observation_without_mutating(
    hass: HomeAssistant,
) -> None:
    """Test an idle queue only returns an inspectable observation."""
    vacuum_entity_id, entry = await _setup_loaded_entry(hass)
    hass.states.async_set(vacuum_entity_id, "cleaning")

    evaluation = await _reconcile(hass, entry)

    assert evaluation.observation.vacuum_state == "cleaning"
    assert evaluation.decision is None
    assert entry.runtime_data.queue_state == QueueState()


async def test_reconcile_updates_tracking_only_decision_without_robot_calls(
    hass: HomeAssistant,
) -> None:
    """Test tracking-only decisions update run tracking and do not call robot services."""
    calls = _record(hass, DREAME_VACUUM_DOMAIN, "vacuum_clean_segment")
    vacuum_entity_id, entry = await _setup_loaded_entry(hass)
    hass.states.async_set(vacuum_entity_id, "cleaning")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    _set_current_room(hass, 1, "Kitchen")
    queue_state = _running_state()
    queue_state = replace(
        queue_state, dispatch=_tracking(queue_state, task_status_cleared_since_dispatch=False)
    )
    entry.runtime_data.set_queue_state(queue_state)

    evaluation = await _reconcile(hass, entry)

    assert calls == []
    assert evaluation.decision is not None
    assert evaluation.decision.action == "hold"
    assert without_dispatch(entry.runtime_data.queue_state) == without_dispatch(queue_state)
    assert entry.runtime_data.queue_state.dispatch is not None
    assert entry.runtime_data.queue_state.dispatch.task_status_cleared_since_dispatch is True


async def test_reconcile_completion_dispatches_next_room(
    hass: HomeAssistant,
) -> None:
    """Test completion decisions dispatch the next room and update runtime state."""
    calls = _record(hass, DREAME_VACUUM_DOMAIN, "vacuum_clean_segment")
    vacuum_entity_id, entry = await _setup_loaded_entry(hass)
    hass.states.async_set(vacuum_entity_id, "idle")
    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    _set_current_room(hass, 1, "Kitchen")
    queue_state = _running_state()
    entry.runtime_data.set_queue_state(queue_state)
    set_dispatch(
        entry.runtime_data, _tracking(queue_state, task_status_cleared_since_dispatch=True)
    )

    evaluation = await _reconcile(hass, entry)

    next_item = entry.runtime_data.queue_state.items[1]
    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert evaluation.decision is not None
    assert evaluation.decision.action == "complete"
    assert evaluation.decision.reasons == ("task_status_completed",)
    assert [item.status for item in entry.runtime_data.queue_state.items] == [
        "completed",
        "running",
    ]
    assert entry.runtime_data.queue_state.run_state == "running"
    assert entry.runtime_data.queue_state.current_item_id == next_item.item_id
    assert entry.runtime_data.queue_state.dispatch is not None


async def test_reconcile_uses_configured_observation_entities(
    hass: HomeAssistant,
) -> None:
    """Test reconciliation observes configured companion entities."""
    calls = _record(hass, DREAME_VACUUM_DOMAIN, "vacuum_clean_segment")
    vacuum_entity_id, entry = await _setup_loaded_entry(
        hass,
        options={
            CONF_TASK_STATUS_ENTITY_ID: "sensor.robot_custom_task_status",
            CONF_CURRENT_ROOM_ENTITY_ID: "sensor.robot_custom_current_room",
        },
    )
    hass.states.async_set(vacuum_entity_id, "idle")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    _set_current_room(hass, 99, "Wrong room")
    hass.states.async_set("sensor.robot_custom_task_status", "completed")
    hass.states.async_set(
        "sensor.robot_custom_current_room",
        "Kitchen",
        {CONF_ROOM_ID: "1", CONF_ROOM_NAME: "Kitchen"},
    )
    queue_state = _running_state()
    entry.runtime_data.set_queue_state(queue_state)
    set_dispatch(
        entry.runtime_data, _tracking(queue_state, task_status_cleared_since_dispatch=True)
    )

    evaluation = await _reconcile(hass, entry)

    next_item = entry.runtime_data.queue_state.items[1]
    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert evaluation.observation.task_status == "completed"
    assert evaluation.observation.observed_room_id == 1
    assert evaluation.decision is not None
    assert evaluation.decision.action == "complete"
    assert entry.runtime_data.queue_state.current_item_id == next_item.item_id


async def test_reconcile_dispatch_failure_preserves_runtime_state(
    hass: HomeAssistant,
) -> None:
    """Test dispatch failures leave runtime state unchanged."""
    calls = _record(hass, DREAME_VACUUM_DOMAIN, "vacuum_clean_segment", error="dispatch failed")
    vacuum_entity_id, entry = await _setup_loaded_entry(hass)
    hass.states.async_set(vacuum_entity_id, "idle")
    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    _set_current_room(hass, 1, "Kitchen")
    queue_state = _running_state()
    run_tracking = _tracking(queue_state, task_status_cleared_since_dispatch=True)
    queue_state = replace(queue_state, dispatch=run_tracking)
    entry.runtime_data.set_queue_state(queue_state)

    with pytest.raises(HomeAssistantError, match="dispatch failed"):
        await _reconcile(hass, entry)

    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.queue_state.dispatch == run_tracking


async def test_reconcile_resume_intent_calls_vacuum_start(
    hass: HomeAssistant,
) -> None:
    """Test resume observations call vacuum.start and update run tracking."""
    calls = _record(hass, "vacuum", "start")
    vacuum_entity_id, entry = await _setup_loaded_entry(hass)
    hass.states.async_set(vacuum_entity_id, "cleaning")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    hass.states.async_set("sensor.dreame_robot_state", "washing_paused")
    hass.states.async_set("sensor.dreame_robot_clean_water_tank_status", "installed")
    _set_current_room(hass, 1, "Kitchen")
    queue_state = _running_state()
    run_tracking = _tracking(queue_state)
    queue_state = replace(queue_state, dispatch=run_tracking)
    entry.runtime_data.set_queue_state(queue_state)

    evaluation = await _reconcile(hass, entry)

    assert calls == [{"entity_id": vacuum_entity_id}]
    assert evaluation.decision is not None
    assert evaluation.decision.action == "resume"
    assert evaluation.decision.reasons == (
        "task_status_cleared_after_dispatch",
        "dock_prep_paused_resume_requested",
    )
    assert without_dispatch(entry.runtime_data.queue_state) == without_dispatch(queue_state)
    assert entry.runtime_data.queue_state.dispatch is not None
    assert entry.runtime_data.queue_state.current_item_id == queue_state.current_item_id
    assert entry.runtime_data.queue_state.dispatch.task_status_cleared_since_dispatch is True
    assert entry.runtime_data.queue_state.dispatch.last_command_at != run_tracking.last_command_at

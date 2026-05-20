"""Tests for disabled-by-default automatic runtime reconciliation."""

from datetime import timedelta

import pytest

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.ha_dreame import AUTO_RECONCILE_INTERVAL
from custom_components.ha_dreame.const import (
    CONF_ALLOW_ROBOT_COMMANDS,
    CONF_AUTO_RECONCILE_ENABLED,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_VACUUM_ENTITY_ID,
    DREAME_VACUUM_DOMAIN,
)
from custom_components.ha_dreame.queue_core import QueueState, add_room, start_run
from custom_components.ha_dreame.runtime_state import QueueRunTracking

from .helpers import mock_entry, register_entity

pytestmark = pytest.mark.usefixtures("mock_dreame_vacuum_dependency")


async def _setup_loaded_entry(
    hass: HomeAssistant,
    *,
    commands_enabled: bool = False,
    auto_reconcile_enabled: bool = False,
) -> tuple[str, object]:
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={
            CONF_ALLOW_ROBOT_COMMANDS: commands_enabled,
            CONF_AUTO_RECONCILE_ENABLED: auto_reconcile_enabled,
        },
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return vacuum_entity_id, entry


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


async def _fire_auto_reconcile_interval(hass: HomeAssistant) -> None:
    async_fire_time_changed(
        hass,
        dt_util.utcnow() + AUTO_RECONCILE_INTERVAL + timedelta(seconds=1),
    )
    await hass.async_block_till_done()
    await hass.async_block_till_done()


async def test_auto_reconcile_does_not_run_when_disabled(
    hass: HomeAssistant,
) -> None:
    """Test automatic reconcile is disabled by default."""
    vacuum_entity_id, entry = await _setup_loaded_entry(
        hass,
        commands_enabled=True,
        auto_reconcile_enabled=False,
    )
    queue_state = _running_state()
    run_tracking = _tracking(queue_state, task_status_cleared_since_dispatch=False)
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(run_tracking)
    hass.states.async_set(vacuum_entity_id, "cleaning")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    _set_current_room(hass, 1, "Kitchen")

    await _fire_auto_reconcile_interval(hass)

    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking == run_tracking


async def test_auto_reconcile_does_not_run_when_commands_disabled(
    hass: HomeAssistant,
) -> None:
    """Test automatic reconcile also requires the command gate."""
    calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    vacuum_entity_id, entry = await _setup_loaded_entry(
        hass,
        commands_enabled=False,
        auto_reconcile_enabled=True,
    )
    queue_state = _running_state()
    run_tracking = _tracking(queue_state, task_status_cleared_since_dispatch=True)
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(run_tracking)
    hass.states.async_set(vacuum_entity_id, "idle")
    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    _set_current_room(hass, 1, "Kitchen")

    await _fire_auto_reconcile_interval(hass)

    assert calls == []
    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking == run_tracking


async def test_auto_reconcile_applies_tracking_only_decision(
    hass: HomeAssistant,
) -> None:
    """Test enabled automatic reconcile applies tracking-only decisions."""
    vacuum_entity_id, entry = await _setup_loaded_entry(
        hass,
        commands_enabled=True,
        auto_reconcile_enabled=True,
    )
    queue_state = _running_state()
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(
        _tracking(queue_state, task_status_cleared_since_dispatch=False)
    )
    hass.states.async_set(vacuum_entity_id, "cleaning")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    _set_current_room(hass, 1, "Kitchen")

    await _fire_auto_reconcile_interval(hass)

    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking is not None
    assert entry.runtime_data.run_tracking.task_status_cleared_since_dispatch is True


async def test_auto_reconcile_dispatches_next_room_after_completion(
    hass: HomeAssistant,
) -> None:
    """Test enabled automatic reconcile can dispatch the next room."""
    calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    vacuum_entity_id, entry = await _setup_loaded_entry(
        hass,
        commands_enabled=True,
        auto_reconcile_enabled=True,
    )
    queue_state = _running_state()
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(
        _tracking(queue_state, task_status_cleared_since_dispatch=True)
    )
    hass.states.async_set(vacuum_entity_id, "idle")
    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    _set_current_room(hass, 1, "Kitchen")

    await _fire_auto_reconcile_interval(hass)

    next_item = entry.runtime_data.queue_state.items[1]
    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert entry.runtime_data.queue_state.current_item_id == next_item.item_id
    assert entry.runtime_data.run_tracking is not None
    assert entry.runtime_data.run_tracking.current_item_id == next_item.item_id


async def test_auto_reconcile_dispatch_failure_preserves_runtime_state(
    hass: HomeAssistant,
) -> None:
    """Test interval dispatch failures leave runtime state unchanged."""
    calls: list[dict[str, object]] = []

    async def _raise_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))
        raise RuntimeError("dispatch failed")

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _raise_clean_segment,
    )
    vacuum_entity_id, entry = await _setup_loaded_entry(
        hass,
        commands_enabled=True,
        auto_reconcile_enabled=True,
    )
    queue_state = _running_state()
    run_tracking = _tracking(queue_state, task_status_cleared_since_dispatch=True)
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(run_tracking)
    hass.states.async_set(vacuum_entity_id, "idle")
    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    _set_current_room(hass, 1, "Kitchen")

    await _fire_auto_reconcile_interval(hass)

    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking == run_tracking


async def test_auto_reconcile_resumes_current_room_when_ready(
    hass: HomeAssistant,
) -> None:
    """Test enabled automatic reconcile resumes dock-prep pauses."""
    calls: list[dict[str, object]] = []

    async def _record_start(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register("vacuum", "start", _record_start)
    vacuum_entity_id, entry = await _setup_loaded_entry(
        hass,
        commands_enabled=True,
        auto_reconcile_enabled=True,
    )
    queue_state = _running_state()
    run_tracking = _tracking(queue_state)
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(run_tracking)
    hass.states.async_set(vacuum_entity_id, "cleaning")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    hass.states.async_set("sensor.dreame_robot_state", "washing_paused")
    hass.states.async_set("sensor.dreame_robot_clean_water_tank_status", "installed")
    _set_current_room(hass, 1, "Kitchen")

    await _fire_auto_reconcile_interval(hass)

    assert calls == [{"entity_id": vacuum_entity_id}]
    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking is not None
    assert entry.runtime_data.run_tracking.current_item_id == queue_state.current_item_id
    assert entry.runtime_data.run_tracking.task_status_cleared_since_dispatch is True
    assert entry.runtime_data.run_tracking.last_command_at != run_tracking.last_command_at

"""Tests for disabled-by-default automatic runtime reconciliation."""

import asyncio
from datetime import timedelta
import logging

import pytest

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed
from _pytest.logging import LogCaptureFixture

from custom_components.ha_dreame import AUTO_RECONCILE_INTERVAL
from custom_components.ha_dreame.const import (
    CONF_ALLOW_ROBOT_COMMANDS,
    CONF_AUTO_RECONCILE_ENABLED,
    CONF_CONFIG_ENTRY_ID,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_TASK_STATUS_ENTITY_ID,
    CONF_VACUUM_ENTITY_ID,
    DOMAIN,
    DREAME_VACUUM_DOMAIN,
    SERVICE_CANCEL_QUEUE,
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
    extra_options: dict[str, object] | None = None,
) -> tuple[str, object]:
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    options = {
        CONF_ALLOW_ROBOT_COMMANDS: commands_enabled,
        CONF_AUTO_RECONCILE_ENABLED: auto_reconcile_enabled,
    }
    options.update(extra_options or {})
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options=options,
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


async def _fire_auto_reconcile_at(hass: HomeAssistant, when) -> None:
    async_fire_time_changed(hass, when)
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


async def test_auto_reconcile_logs_late_room_mismatch_as_debug_hold(
    hass: HomeAssistant,
    caplog: LogCaptureFixture,
) -> None:
    """Test ignored late room flips are diagnostic debug, not normal log noise."""
    caplog.set_level(
        logging.DEBUG,
        "custom_components.ha_dreame.runtime_reconcile_runner",
    )
    vacuum_entity_id, entry = await _setup_loaded_entry(
        hass,
        commands_enabled=True,
        auto_reconcile_enabled=True,
    )
    queue_state = _running_state()
    run_tracking = _tracking(
        queue_state,
        task_status_cleared_since_dispatch=True,
    )
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(run_tracking)
    hass.states.async_set(vacuum_entity_id, "cleaning")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    hass.states.async_set("sensor.dreame_robot_cleaning_progress", "95")
    _set_current_room(hass, 7, "Hall")

    await _fire_auto_reconcile_interval(hass)

    assert entry.runtime_data.run_tracking == run_tracking
    assert any(
        record.levelno == logging.DEBUG
        and record.name == "custom_components.ha_dreame.runtime_reconcile_runner"
        and "action=hold" in record.message
        and "active_room_mismatch_waiting_near_completion" in record.message
        for record in caplog.records
    )
    assert not any(
        record.name == "custom_components.ha_dreame.runtime_reconcile_runner"
        and record.levelno >= logging.INFO
        for record in caplog.records
    )


async def test_auto_reconcile_logs_retry_dispatch_as_info(
    hass: HomeAssistant,
    caplog: LogCaptureFixture,
) -> None:
    """Test redispatch decisions are visible without enabling debug logging."""
    calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    caplog.set_level(
        logging.INFO,
        "custom_components.ha_dreame.runtime_reconcile_runner",
    )
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
        _tracking(
            queue_state,
            task_status_cleared_since_dispatch=True,
        )
    )
    hass.states.async_set(vacuum_entity_id, "cleaning")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    hass.states.async_set("sensor.dreame_robot_cleaning_progress", "20")
    _set_current_room(hass, 7, "Hall")

    await _fire_auto_reconcile_interval(hass)

    assert calls == [{"entity_id": vacuum_entity_id, "segments": [1]}]
    assert any(
        record.levelno == logging.INFO
        and record.name == "custom_components.ha_dreame.runtime_reconcile_runner"
        and "action=retry_dispatch" in record.message
        and "active_room_mismatch_retry:1:expected_1:observed_7" in record.message
        for record in caplog.records
    )


async def test_auto_reconcile_logs_terminal_problem_as_warning(
    hass: HomeAssistant,
    caplog: LogCaptureFixture,
) -> None:
    """Test terminal reconcile problem states are warning-level events."""
    caplog.set_level(
        logging.WARNING,
        "custom_components.ha_dreame.runtime_reconcile_runner",
    )
    vacuum_entity_id, entry = await _setup_loaded_entry(
        hass,
        commands_enabled=True,
        auto_reconcile_enabled=True,
    )
    queue_state = _running_state()
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(
        _tracking(
            queue_state,
            dispatch_retry_count=2,
            task_status_cleared_since_dispatch=True,
        )
    )
    hass.states.async_set(vacuum_entity_id, "idle")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    _set_current_room(hass, 7, "Hall")

    await _fire_auto_reconcile_interval(hass)

    assert entry.runtime_data.queue_state.run_state == "out_of_sync"
    assert entry.runtime_data.run_tracking is None
    assert any(
        record.levelno == logging.WARNING
        and record.name == "custom_components.ha_dreame.runtime_reconcile_runner"
        and "action=out_of_sync" in record.message
        and "dispatch_retry_exhausted" in record.message
        for record in caplog.records
    )


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
    hass.states.async_set(vacuum_entity_id, "idle")
    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    _set_current_room(hass, 1, "Kitchen")
    await hass.async_block_till_done()

    queue_state = _running_state()
    run_tracking = _tracking(queue_state, task_status_cleared_since_dispatch=True)
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(run_tracking)

    await _fire_auto_reconcile_interval(hass)

    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking == run_tracking


async def test_task_status_attribute_update_does_not_repeat_failed_dispatch(
    hass: HomeAssistant,
) -> None:
    """Test same-state attribute updates cannot replay a failed completion dispatch."""
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
    hass.states.async_set(vacuum_entity_id, "docked")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    _set_current_room(hass, 1, "Kitchen")
    await hass.async_block_till_done()

    queue_state = _running_state()
    run_tracking = _tracking(queue_state, task_status_cleared_since_dispatch=True)
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(run_tracking)

    hass.states.async_set(
        "sensor.dreame_robot_task_status",
        "completed",
        {"sequence": 1},
    )
    await hass.async_block_till_done()
    await hass.async_block_till_done()

    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking == run_tracking

    hass.states.async_set(
        "sensor.dreame_robot_task_status",
        "completed",
        {"sequence": 2},
    )
    await hass.async_block_till_done()

    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking == run_tracking


async def test_auto_reconcile_survives_unavailable_run_and_short_completion_pulse(
    hass: HomeAssistant,
) -> None:
    """Test outages and post-run settling cannot hide a brief completion event."""
    segment_calls: list[dict[str, object]] = []
    resume_calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        segment_calls.append(dict(call.data))

    async def _record_start(call: ServiceCall) -> None:
        resume_calls.append(dict(call.data))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    hass.services.async_register("vacuum", "start", _record_start)
    vacuum_entity_id, entry = await _setup_loaded_entry(
        hass,
        commands_enabled=True,
        auto_reconcile_enabled=True,
    )
    queue_state = _running_state()
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(
        _tracking(
            queue_state,
            dispatch_retry_count=1,
            task_status_cleared_since_dispatch=True,
        )
    )
    _set_current_room(hass, 1, "Kitchen")

    next_tick = dt_util.utcnow()

    hass.states.async_set(vacuum_entity_id, "unavailable")
    hass.states.async_set("sensor.dreame_robot_task_status", "unavailable")
    next_tick += AUTO_RECONCILE_INTERVAL + timedelta(seconds=1)
    await _fire_auto_reconcile_at(hass, next_tick)

    assert segment_calls == []
    assert resume_calls == []
    assert entry.runtime_data.queue_state.run_state == "running"
    assert entry.runtime_data.run_tracking is not None
    assert entry.runtime_data.run_tracking.dispatch_retry_count == 1

    hass.states.async_set(vacuum_entity_id, "cleaning")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    hass.states.async_set("sensor.dreame_robot_state", "sweeping_and_mopping")
    next_tick += AUTO_RECONCILE_INTERVAL + timedelta(seconds=1)
    await _fire_auto_reconcile_at(hass, next_tick)

    assert segment_calls == []
    assert resume_calls == []
    assert entry.runtime_data.run_tracking is not None
    assert entry.runtime_data.run_tracking.dispatch_retry_count == 0

    hass.states.async_set(
        vacuum_entity_id,
        "docked",
        {"paused": True, "running": False},
    )
    hass.states.async_set("sensor.dreame_robot_state", "auto_emptying")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    hass.states.async_set("sensor.dreame_robot_clean_water_tank_status", "installed")
    next_tick += AUTO_RECONCILE_INTERVAL + timedelta(seconds=1)
    await _fire_auto_reconcile_at(hass, next_tick)

    assert segment_calls == []
    assert resume_calls == []
    assert entry.runtime_data.queue_state.run_state == "running"
    assert entry.runtime_data.run_tracking is not None
    assert entry.runtime_data.run_tracking.post_run_maintenance_seen is True

    hass.states.async_set("sensor.dreame_robot_state", "idle")
    next_tick += AUTO_RECONCILE_INTERVAL + timedelta(seconds=1)
    await _fire_auto_reconcile_at(hass, next_tick)

    assert segment_calls == []
    assert resume_calls == []
    assert entry.runtime_data.queue_state.run_state == "running"
    assert entry.runtime_data.run_tracking is not None
    assert entry.runtime_data.run_tracking.post_run_maintenance_seen is True

    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    hass.states.async_set("sensor.dreame_robot_task_status", "unavailable")
    await hass.async_block_till_done()
    await hass.async_block_till_done()

    assert segment_calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert resume_calls == []
    assert entry.runtime_data.queue_state.items[0].status == "completed"
    assert entry.runtime_data.queue_state.items[1].status == "running"


async def test_prior_room_auto_emptying_is_not_bound_to_new_queue_item(
    hass: HomeAssistant,
) -> None:
    """Test lingering maintenance cannot permanently block a newly dispatched room."""
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
        _tracking(
            queue_state,
            active_room_confirmed_since_dispatch=True,
            task_status_cleared_since_dispatch=True,
        )
    )
    hass.states.async_set(vacuum_entity_id, "docked")
    hass.states.async_set("sensor.dreame_robot_state", "auto_emptying")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    _set_current_room(hass, 1, "Kitchen")
    await hass.async_block_till_done()

    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    await hass.async_block_till_done()
    await hass.async_block_till_done()

    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert entry.runtime_data.queue_state.items[1].status == "running"
    assert entry.runtime_data.run_tracking is not None
    assert entry.runtime_data.run_tracking.active_room_confirmed_since_dispatch is False

    await _fire_auto_reconcile_interval(hass)

    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert entry.runtime_data.queue_state.run_state == "running"
    assert entry.runtime_data.run_tracking is not None
    assert entry.runtime_data.run_tracking.post_run_maintenance_seen is False


async def test_auto_reconcile_captures_full_task_lifecycle_between_intervals(
    hass: HomeAssistant,
) -> None:
    """Test an active-to-completed pulse works without an earlier interval tick."""
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
    hass.states.async_set(vacuum_entity_id, "cleaning")
    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    _set_current_room(hass, 1, "Kitchen")
    await hass.async_block_till_done()

    queue_state = _running_state()
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(
        _tracking(queue_state, task_status_cleared_since_dispatch=False)
    )

    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    hass.states.async_set("sensor.dreame_robot_task_status", "unavailable")
    await hass.async_block_till_done()
    await hass.async_block_till_done()

    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert entry.runtime_data.queue_state.items[0].status == "completed"
    assert entry.runtime_data.queue_state.items[1].status == "running"


async def test_auto_reconcile_latches_completion_while_operation_lock_is_held(
    hass: HomeAssistant,
) -> None:
    """Test a completion event remains valid while another operation owns the lock."""
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
    hass.states.async_set(vacuum_entity_id, "docked")
    _set_current_room(hass, 1, "Kitchen")

    await entry.runtime_data.operation_lock.acquire()
    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    hass.states.async_set("sensor.dreame_robot_task_status", "unavailable")
    await asyncio.sleep(0)
    entry.runtime_data.operation_lock.release()
    await hass.async_block_till_done()
    await hass.async_block_till_done()

    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert entry.runtime_data.queue_state.items[0].status == "completed"
    assert entry.runtime_data.queue_state.items[1].status == "running"


async def test_auto_reconcile_listens_to_explicit_task_status_entity(
    hass: HomeAssistant,
) -> None:
    """Test completion latching follows an explicitly configured task sensor."""
    calls: list[dict[str, object]] = []
    task_status_entity_id = "sensor.robot_task_lifecycle"

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
        extra_options={CONF_TASK_STATUS_ENTITY_ID: task_status_entity_id},
    )
    queue_state = _running_state()
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(
        _tracking(queue_state, task_status_cleared_since_dispatch=True)
    )
    hass.states.async_set(vacuum_entity_id, "docked")
    _set_current_room(hass, 1, "Kitchen")

    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    await hass.async_block_till_done()
    assert calls == []

    hass.states.async_set(task_status_entity_id, "completed")
    hass.states.async_set(task_status_entity_id, "unavailable")
    await hass.async_block_till_done()
    await hass.async_block_till_done()

    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]


async def test_queued_task_status_reconcile_stops_when_entry_unloads(
    hass: HomeAssistant,
) -> None:
    """Test an event waiting on the lock cannot command after entry unload."""
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
    hass.states.async_set(vacuum_entity_id, "docked")
    _set_current_room(hass, 1, "Kitchen")

    runtime_data = entry.runtime_data
    await runtime_data.operation_lock.acquire()
    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    await asyncio.sleep(0)

    unload_task = asyncio.create_task(hass.config_entries.async_unload(entry.entry_id))
    for _ in range(10):
        if runtime_data.unload_requested.is_set():
            break
        await asyncio.sleep(0)
    assert runtime_data.unload_requested.is_set()
    assert unload_task.done() is False

    runtime_data.operation_lock.release()
    assert await unload_task is True
    await hass.async_block_till_done()

    assert calls == []


async def test_auto_reconcile_serializes_completion_event_with_interval(
    hass: HomeAssistant,
) -> None:
    """Test simultaneous reconcile triggers dispatch the next room exactly once."""
    calls: list[dict[str, object]] = []
    first_dispatch_started = asyncio.Event()
    release_first_dispatch = asyncio.Event()

    async def _record_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))
        if len(calls) == 1:
            first_dispatch_started.set()
            await release_first_dispatch.wait()

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
    hass.states.async_set(vacuum_entity_id, "cleaning")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    _set_current_room(hass, 1, "Kitchen")
    await hass.async_block_till_done()

    queue_state = _running_state()
    entry.runtime_data.set_queue_state(queue_state)
    entry.runtime_data.set_run_tracking(
        _tracking(queue_state, task_status_cleared_since_dispatch=True)
    )

    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    await asyncio.wait_for(first_dispatch_started.wait(), timeout=1)

    async_fire_time_changed(
        hass,
        dt_util.utcnow() + AUTO_RECONCILE_INTERVAL + timedelta(seconds=1),
    )
    for _ in range(5):
        await asyncio.sleep(0)

    release_first_dispatch.set()
    await hass.async_block_till_done()
    await hass.async_block_till_done()

    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert entry.runtime_data.queue_state.items[0].status == "completed"
    assert entry.runtime_data.queue_state.items[1].status == "running"


async def test_cancel_waits_for_inflight_reconcile_and_cannot_be_overwritten(
    hass: HomeAssistant,
) -> None:
    """Test cancel uses the same operation lock as completion dispatch."""
    segment_calls: list[dict[str, object]] = []
    return_calls: list[dict[str, object]] = []
    dispatch_started = asyncio.Event()
    release_dispatch = asyncio.Event()

    async def _record_clean_segment(call: ServiceCall) -> None:
        segment_calls.append(dict(call.data))
        dispatch_started.set()
        await release_dispatch.wait()

    async def _record_return_to_base(call: ServiceCall) -> None:
        return_calls.append(dict(call.data))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    hass.services.async_register("vacuum", "return_to_base", _record_return_to_base)
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
    hass.states.async_set(vacuum_entity_id, "docked")
    _set_current_room(hass, 1, "Kitchen")

    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    await asyncio.wait_for(dispatch_started.wait(), timeout=1)

    cancel_task = asyncio.create_task(
        hass.services.async_call(
            DOMAIN,
            SERVICE_CANCEL_QUEUE,
            {CONF_CONFIG_ENTRY_ID: entry.entry_id},
            blocking=True,
            return_response=True,
        )
    )
    await asyncio.sleep(0)
    assert cancel_task.done() is False

    release_dispatch.set()
    await cancel_task
    await hass.async_block_till_done()

    assert segment_calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert return_calls == [{"entity_id": vacuum_entity_id}]
    assert entry.runtime_data.queue_state.run_state == "canceled"
    assert all(item.status != "running" for item in entry.runtime_data.queue_state.items)
    assert entry.runtime_data.run_tracking is None


async def test_completion_waiting_behind_cancel_cannot_resurrect_queue(
    hass: HomeAssistant,
) -> None:
    """Test stale completion work is discarded after cancel changes the active run."""
    segment_calls: list[dict[str, object]] = []
    return_calls: list[dict[str, object]] = []
    cancel_started = asyncio.Event()
    release_cancel = asyncio.Event()

    async def _record_clean_segment(call: ServiceCall) -> None:
        segment_calls.append(dict(call.data))

    async def _hold_return_to_base(call: ServiceCall) -> None:
        return_calls.append(dict(call.data))
        cancel_started.set()
        await release_cancel.wait()

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    hass.services.async_register("vacuum", "return_to_base", _hold_return_to_base)
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
    hass.states.async_set(vacuum_entity_id, "cleaning")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    _set_current_room(hass, 1, "Kitchen")
    await hass.async_block_till_done()

    cancel_task = asyncio.create_task(
        hass.services.async_call(
            DOMAIN,
            SERVICE_CANCEL_QUEUE,
            {CONF_CONFIG_ENTRY_ID: entry.entry_id},
            blocking=True,
            return_response=True,
        )
    )
    await asyncio.wait_for(cancel_started.wait(), timeout=1)

    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    await asyncio.sleep(0)
    release_cancel.set()
    await cancel_task
    await hass.async_block_till_done()
    await hass.async_block_till_done()

    assert segment_calls == []
    assert return_calls == [{"entity_id": vacuum_entity_id}]
    assert entry.runtime_data.queue_state.run_state == "canceled"
    assert all(item.status != "running" for item in entry.runtime_data.queue_state.items)
    assert entry.runtime_data.run_tracking is None


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


async def test_auto_reconcile_resumes_after_transient_low_water_pause(
    hass: HomeAssistant,
) -> None:
    """Test refill recovery survives a dock-pause state pulse between polls."""
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
    hass.states.async_set(
        vacuum_entity_id,
        "cleaning",
        {
            "paused": True,
            "running": False,
            "washing": True,
        },
    )
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    hass.states.async_set("sensor.dreame_robot_state", "washing_paused")
    hass.states.async_set("sensor.dreame_robot_self_wash_base_status", "paused")
    hass.states.async_set("sensor.dreame_robot_clean_water_tank_status", "low_water")
    hass.states.async_set("sensor.dreame_robot_error", "water_tank_dry")
    _set_current_room(hass, 1, "Kitchen")

    # The short pause pulse disappears before the next reconcile tick, while
    # the vacuum's durable attributes still say that the dock task is paused.
    hass.states.async_set("sensor.dreame_robot_state", "washing")
    hass.states.async_set("sensor.dreame_robot_self_wash_base_status", "washing")
    hass.states.async_set("sensor.dreame_robot_clean_water_tank_status", "installed")
    hass.states.async_set("sensor.dreame_robot_error", "no_error")

    await _fire_auto_reconcile_interval(hass)

    assert calls == [{"entity_id": vacuum_entity_id}]
    assert entry.runtime_data.queue_state == queue_state
    assert entry.runtime_data.run_tracking is not None
    assert entry.runtime_data.run_tracking.current_item_id == queue_state.current_item_id
    assert entry.runtime_data.run_tracking.task_status_cleared_since_dispatch is True
    assert entry.runtime_data.run_tracking.last_command_at != run_tracking.last_command_at

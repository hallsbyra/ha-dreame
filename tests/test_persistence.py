"""The queue survives Home Assistant restarts and integration reloads."""

from dataclasses import replace
from datetime import datetime, timedelta
import logging
from typing import Any

import pytest

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed
from _pytest.logging import LogCaptureFixture

from custom_components.ha_dreame import AUTO_RECONCILE_INTERVAL
from custom_components.ha_dreame.const import DOMAIN
from custom_components.ha_dreame.queue_core import (
    DispatchTracking,
    QueueState,
    add_room,
    queue_state_to_dict,
    start_run,
)

from .helpers import mock_entry, register_entity

pytestmark = pytest.mark.usefixtures("mock_dreame_vacuum_dependency")

TRACKING = DispatchTracking(
    last_command_at=datetime.fromisoformat("2026-11-01T08:00:00+00:00"),
    dispatch_retry_count=1,
    active_room_confirmed_since_dispatch=True,
    task_status_cleared_since_dispatch=True,
)


def _running_queue() -> QueueState:
    state = add_room(QueueState(), room_id=1, room_name="Kitchen", overrides={"repeats": 2})
    state = add_room(state, room_id=2, room_name="Hall")
    return replace(start_run(state), dispatch=TRACKING)


def _entry(hass: HomeAssistant, *, commands: bool = True):
    vacuum = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({"vacuum_entity_id": vacuum}, options={"allow_robot_commands": commands})
    entry.add_to_hass(hass)
    return entry


def _store_key(entry) -> str:
    return f"{DOMAIN}.{entry.entry_id}"


def _seed(hass_storage: dict[str, Any], entry, data: object) -> None:
    hass_storage[_store_key(entry)] = {
        "version": 1,
        "minor_version": 1,
        "key": _store_key(entry),
        "data": data,
    }


async def _setup(hass: HomeAssistant, entry) -> None:
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


def _record(hass: HomeAssistant, domain: str, service: str) -> list[dict[str, object]]:
    calls: list[dict[str, object]] = []

    async def _handle(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register(domain, service, _handle)
    return calls


async def test_setup_restores_a_running_queue_with_its_dispatch_tracking(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    entry = _entry(hass)
    saved = _running_queue()
    _seed(hass_storage, entry, queue_state_to_dict(saved))

    await _setup(hass, entry)

    assert entry.runtime_data.queue_state == saved
    state = hass.states.get("sensor.ha_dreame_queue_status")
    assert state is not None
    assert state.state == "running"
    assert [item["status"] for item in state.attributes["queue_items"]] == ["running", "pending"]


async def test_restored_run_continues_reconciling_from_the_observed_robot(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    """A room the robot finished while HA was down completes and the next room dispatches."""
    calls = _record(hass, "dreame_vacuum", "vacuum_clean_segment")
    entry = _entry(hass)
    _seed(hass_storage, entry, queue_state_to_dict(_running_queue()))
    hass.states.async_set("vacuum.dreame_robot", "docked")
    hass.states.async_set("sensor.dreame_robot_task_status", "completed")

    await _setup(hass, entry)
    async_fire_time_changed(hass, dt_util.utcnow() + AUTO_RECONCILE_INTERVAL + timedelta(seconds=1))
    await hass.async_block_till_done()

    assert calls == [{"entity_id": "vacuum.dreame_robot", "segments": [2], "repeats": 2}]
    assert [item.status for item in entry.runtime_data.queue_state.items] == [
        "completed",
        "running",
    ]


async def test_restored_waiting_start_is_released_when_the_tanks_are_ready(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    calls = _record(hass, "dreame_vacuum", "vacuum_clean_segment")
    entry = _entry(hass)
    waiting = replace(
        add_room(QueueState(), room_id=6, room_name="Room 6"), run_state="waiting_for_tanks"
    )
    _seed(hass_storage, entry, queue_state_to_dict(waiting))
    hass.states.async_set("vacuum.dreame_robot", "docked")
    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    hass.states.async_set("sensor.dreame_robot_clean_water_tank_status", "installed")

    await _setup(hass, entry)
    assert entry.runtime_data.queue_state.run_state == "waiting_for_tanks"
    async_fire_time_changed(hass, dt_util.utcnow() + AUTO_RECONCILE_INTERVAL + timedelta(seconds=1))
    await hass.async_block_till_done()

    assert calls == [{"entity_id": "vacuum.dreame_robot", "segments": [6]}]
    assert entry.runtime_data.queue_state.run_state == "running"


async def test_queue_changes_are_saved_after_a_short_delay(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    entry = _entry(hass, commands=False)
    await _setup(hass, entry)

    await hass.services.async_call(
        DOMAIN,
        "add_queue_room",
        {"config_entry_id": entry.entry_id, "room_id": 3, "room_name": "Office"},
        blocking=True,
    )
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=30))
    await hass.async_block_till_done()

    stored = hass_storage[_store_key(entry)]
    assert stored["version"] == 1
    assert stored["data"] == queue_state_to_dict(entry.runtime_data.queue_state)
    assert [item["room_name"] for item in stored["data"]["items"]] == ["Office"]


async def test_unload_flushes_the_latest_queue_and_reload_restores_it(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    entry = _entry(hass, commands=False)
    await _setup(hass, entry)
    await hass.services.async_call(
        DOMAIN,
        "add_queue_room",
        {"config_entry_id": entry.entry_id, "room_id": 3, "room_name": "Office"},
        blocking=True,
    )
    queue_state = entry.runtime_data.queue_state

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert hass_storage[_store_key(entry)]["data"] == queue_state_to_dict(queue_state)

    await _setup(hass, entry)
    assert entry.runtime_data.queue_state == queue_state


async def test_options_change_keeps_the_queue(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    entry = _entry(hass, commands=False)
    await _setup(hass, entry)
    await hass.services.async_call(
        DOMAIN,
        "add_queue_room",
        {"config_entry_id": entry.entry_id, "room_id": 3, "room_name": "Office"},
        blocking=True,
    )
    queue_state = entry.runtime_data.queue_state

    hass.config_entries.async_update_entry(entry, options={"allow_robot_commands": True})
    await hass.async_block_till_done()

    assert entry.runtime_data.commands_enabled is True
    assert entry.runtime_data.queue_state == queue_state


@pytest.mark.parametrize(
    "data",
    [
        {"run_state": "exploded", "items": []},
        {"items": [{"item_id": "a"}]},
        "not a queue",
    ],
)
async def test_invalid_stored_queue_starts_empty_with_a_warning(
    hass: HomeAssistant,
    hass_storage: dict[str, Any],
    caplog: LogCaptureFixture,
    data: object,
) -> None:
    entry = _entry(hass)
    _seed(hass_storage, entry, data)
    caplog.set_level(logging.WARNING)

    await _setup(hass, entry)

    assert entry.runtime_data.queue_state == QueueState()
    assert "Ignoring unreadable stored HA Dreame queue" in caplog.text


async def test_unreadable_store_starts_empty_with_a_warning(
    hass: HomeAssistant,
    hass_storage: dict[str, Any],
    caplog: LogCaptureFixture,
) -> None:
    """A store written by a newer major version cannot be read here."""
    entry = _entry(hass)
    hass_storage[_store_key(entry)] = {
        "version": 2,
        "minor_version": 1,
        "key": _store_key(entry),
        "data": queue_state_to_dict(_running_queue()),
    }
    caplog.set_level(logging.WARNING)

    await _setup(hass, entry)

    assert entry.runtime_data.queue_state == QueueState()
    assert "Ignoring unreadable stored HA Dreame queue" in caplog.text


async def test_removing_the_entry_removes_its_stored_queue(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    entry = _entry(hass, commands=False)
    await _setup(hass, entry)
    await hass.services.async_call(
        DOMAIN,
        "add_queue_room",
        {"config_entry_id": entry.entry_id, "room_id": 3, "room_name": "Office"},
        blocking=True,
    )
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert _store_key(entry) in hass_storage

    await hass.config_entries.async_remove(entry.entry_id)
    await hass.async_block_till_done()

    assert _store_key(entry) not in hass_storage

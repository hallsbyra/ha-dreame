"""A tank-blocked Start is an explicit, cancellable, one-shot request."""

import pytest
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from custom_components.ha_dreame import _async_auto_reconcile_tick
from custom_components.ha_dreame.const import DOMAIN
from .helpers import mock_entry, register_entity

pytestmark = pytest.mark.usefixtures("mock_dreame_vacuum_dependency")


async def setup_waiting_robot(hass: HomeAssistant, *, auto: bool = True):
    vacuum = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({"vacuum_entity_id": vacuum}, options={
        "allow_robot_commands": True, "auto_reconcile_enabled": auto})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    hass.states.async_set(vacuum, "docked")
    hass.states.async_set("sensor.dreame_robot_task_status", "completed")
    hass.states.async_set("sensor.dreame_robot_clean_water_tank_status", "low_water")
    hass.states.async_set("sensor.dreame_robot_dirty_water_tank_status", "installed")
    calls = []

    async def record(call: ServiceCall):
        calls.append(call)

    hass.services.async_register("dreame_vacuum", "vacuum_clean_segment", record)
    await hass.services.async_call(DOMAIN, "add_queue_room", {
        "config_entry_id": entry.entry_id, "room_id": 6, "room_name": "Room 6"}, blocking=True)
    return entry, calls


async def command(hass, entry, service, **data):
    return await hass.services.async_call(DOMAIN, service,
        {"config_entry_id": entry.entry_id, **data}, blocking=True, return_response=True)


async def test_tank_wait_starts_once_only_after_both_tanks_recover(hass: HomeAssistant):
    entry, calls = await setup_waiting_robot(hass)
    await command(hass, entry, "start_queue")
    await command(hass, entry, "start_queue")
    assert entry.runtime_data.queue_state.run_state == "waiting_for_tanks"
    assert entry.runtime_data.queue_state.items[0].status == "pending"
    assert not calls
    hass.states.async_set("sensor.dreame_robot_clean_water_tank_status", "installed")
    hass.states.async_set("sensor.dreame_robot_dirty_water_tank_status", "not_installed_or_full")
    await _async_auto_reconcile_tick(hass, entry)
    assert not calls
    hass.states.async_set("sensor.dreame_robot_dirty_water_tank_status", "installed")
    await _async_auto_reconcile_tick(hass, entry)
    await _async_auto_reconcile_tick(hass, entry)
    assert len(calls) == 1
    assert calls[0].data["segments"] == [6]
    assert entry.runtime_data.queue_state.run_state == "running"


@pytest.mark.parametrize("cancel", ["cancel_queue", "clear_pending_queue", "remove_queue_item"])
async def test_cancelled_tank_wait_cannot_start_later_added_room(hass: HomeAssistant, cancel: str):
    entry, calls = await setup_waiting_robot(hass)
    await command(hass, entry, "start_queue")
    item_id = entry.runtime_data.queue_state.items[0].item_id
    await command(hass, entry, cancel, **({"item_id": item_id} if cancel == "remove_queue_item" else {}))
    hass.states.async_set("sensor.dreame_robot_clean_water_tank_status", "installed")
    await command(hass, entry, "add_queue_room", room_id=7, room_name="Room 7")
    await _async_auto_reconcile_tick(hass, entry)
    assert not calls
    assert entry.runtime_data.queue_state.run_state == "idle"


async def test_refill_without_a_start_request_does_not_dispatch(hass: HomeAssistant):
    entry, calls = await setup_waiting_robot(hass)
    hass.states.async_set("sensor.dreame_robot_clean_water_tank_status", "installed")
    await _async_auto_reconcile_tick(hass, entry)
    assert not calls
    assert entry.runtime_data.queue_state.run_state == "idle"


async def test_tank_wait_requires_automatic_reconcile(hass: HomeAssistant):
    entry, calls = await setup_waiting_robot(hass, auto=False)
    with pytest.raises(HomeAssistantError, match="automatic reconciliation"):
        await command(hass, entry, "start_queue")
    assert not calls
    assert entry.runtime_data.queue_state.run_state == "idle"


@pytest.mark.parametrize("obstacle", ["unavailable", "paused", "other_task"])
async def test_tank_wait_does_not_override_other_robot_states(hass: HomeAssistant, obstacle: str):
    entry, calls = await setup_waiting_robot(hass)
    await command(hass, entry, "start_queue")
    hass.states.async_set("sensor.dreame_robot_clean_water_tank_status", "installed")
    if obstacle == "other_task":
        hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    elif obstacle == "paused":
        hass.states.async_set("sensor.dreame_robot_status", "paused")
    else:
        hass.states.async_set("vacuum.dreame_robot", "unavailable")
    await _async_auto_reconcile_tick(hass, entry)
    assert not calls


async def test_failed_deferred_dispatch_does_not_retry_indefinitely(hass: HomeAssistant):
    entry, calls = await setup_waiting_robot(hass)
    await command(hass, entry, "start_queue")

    async def fail(call: ServiceCall):
        calls.append(call)
        raise HomeAssistantError("Dispatch failed")

    hass.services.async_register("dreame_vacuum", "vacuum_clean_segment", fail)
    hass.states.async_set("sensor.dreame_robot_clean_water_tank_status", "installed")
    await _async_auto_reconcile_tick(hass, entry)
    await _async_auto_reconcile_tick(hass, entry)
    assert len(calls) == 1
    assert entry.runtime_data.queue_state.run_state != "waiting_for_tanks"

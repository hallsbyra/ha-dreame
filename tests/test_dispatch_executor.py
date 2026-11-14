"""Tests for the shared command-gated room dispatch."""

import pytest

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from custom_components.ha_dreame.const import DREAME_VACUUM_DOMAIN
from custom_components.ha_dreame.dispatch_executor import async_dispatch_current_room
from custom_components.ha_dreame.queue_core import add_room, new_state, start_run
from custom_components.ha_dreame.runtime import HaDreameRuntimeData

from .helpers import mock_entry, register_entity, without_dispatch

pytestmark = pytest.mark.usefixtures("mock_dreame_vacuum_dependency")


async def _runtime(hass: HomeAssistant, *, commands_enabled: bool = True) -> HaDreameRuntimeData:
    vacuum_entity_id = register_entity(hass, "vacuum.robot")
    entry = mock_entry(
        {"vacuum_entity_id": vacuum_entity_id},
        options={"allow_robot_commands": commands_enabled},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    # A robot left in mop-only mode needs a mode switch before the segment command.
    hass.states.async_set("select.robot_cleaning_mode", "mopping")
    return entry.runtime_data


def _next_state():
    return start_run(add_room(new_state(), room_id=7, room_name="Room 7"))


async def test_dispatch_rejects_disabled_command_gate_and_restores_state(
    hass: HomeAssistant,
) -> None:
    """Test the disabled command gate prevents every planned call."""
    calls: list[ServiceCall] = []

    async def _record_call(call: ServiceCall) -> None:
        calls.append(call)

    hass.services.async_register("select", "select_option", _record_call)
    hass.services.async_register(DREAME_VACUUM_DOMAIN, "vacuum_clean_segment", _record_call)
    runtime_data = await _runtime(hass, commands_enabled=False)
    previous_state = runtime_data.queue_state

    with pytest.raises(HomeAssistantError, match="robot commands are disabled"):
        await async_dispatch_current_room(hass, runtime_data, _next_state())

    assert calls == []
    assert runtime_data.queue_state == previous_state
    assert runtime_data.queue_state.dispatch is None


async def test_dispatch_publishes_state_then_calls_services_in_order(
    hass: HomeAssistant,
) -> None:
    """Test observers see the dispatched room while planned calls run in order."""
    runtime_data = await _runtime(hass)
    next_state = _next_state()
    calls: list[tuple[str, str, dict[str, object], str | None]] = []

    async def _record_call(call: ServiceCall) -> None:
        calls.append(
            (call.domain, call.service, dict(call.data), runtime_data.queue_state.current_item_id)
        )

    hass.services.async_register("select", "select_option", _record_call)
    hass.services.async_register(DREAME_VACUUM_DOMAIN, "vacuum_clean_segment", _record_call)

    await async_dispatch_current_room(hass, runtime_data, next_state, retry_count=1)

    assert calls == [
        (
            "select",
            "select_option",
            {"entity_id": "select.robot_cleaning_mode", "option": "sweeping_and_mopping"},
            next_state.current_item_id,
        ),
        (
            DREAME_VACUUM_DOMAIN,
            "vacuum_clean_segment",
            {"entity_id": "vacuum.robot", "segments": [7]},
            next_state.current_item_id,
        ),
    ]
    assert without_dispatch(runtime_data.queue_state) == without_dispatch(next_state)
    run_tracking = runtime_data.queue_state.dispatch
    assert run_tracking is not None
    assert runtime_data.queue_state.current_item_id == next_state.current_item_id
    assert run_tracking.dispatch_retry_count == 1
    assert run_tracking.last_command_at.tzinfo is not None


async def test_dispatch_stops_after_service_failure_and_restores_state(
    hass: HomeAssistant,
) -> None:
    """Test a rejected call stops later calls and restores the previous state."""
    calls: list[tuple[str, str]] = []

    async def _raise_call(call: ServiceCall) -> None:
        calls.append((call.domain, call.service))
        raise HomeAssistantError("dispatch failed")

    async def _record_call(call: ServiceCall) -> None:
        calls.append((call.domain, call.service))

    hass.services.async_register("select", "select_option", _raise_call)
    hass.services.async_register(DREAME_VACUUM_DOMAIN, "vacuum_clean_segment", _record_call)
    runtime_data = await _runtime(hass)
    previous_state = runtime_data.queue_state

    with pytest.raises(HomeAssistantError, match="dispatch failed"):
        await async_dispatch_current_room(hass, runtime_data, _next_state())

    assert calls == [("select", "select_option")]
    assert runtime_data.queue_state == previous_state
    assert runtime_data.queue_state.dispatch is None

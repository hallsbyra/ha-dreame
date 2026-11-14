"""Provenance must survive service boundaries without recording arbitrary payloads."""

import pytest
from homeassistant.core import Context, HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from custom_components.ha_dreame.audit import (
    async_call_robot_service,
    automatic_audit,
    service_audit,
)
from custom_components.ha_dreame.const import DOMAIN
from .helpers import mock_entry, register_entity

pytestmark = pytest.mark.usefixtures("mock_dreame_vacuum_dependency")


async def test_audit_correlates_user_automatic_and_external_commands(hass: HomeAssistant) -> None:
    vacuum = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({"vacuum_entity_id": vacuum}, options={"allow_robot_commands": True})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    contexts = []

    async def record(call: ServiceCall) -> None:
        contexts.append(call.context)

    hass.services.async_register("vacuum", "start", record)
    caller = Context(user_id="test-user")
    call = ServiceCall(hass, DOMAIN, "resume_queue", {}, context=caller)
    with service_audit(entry.runtime_data, call):
        await async_call_robot_service(
            hass, entry.runtime_data, "vacuum", "start", {"entity_id": vacuum}
        )
    await hass.async_block_till_done()
    assert contexts[-1] == caller
    events = list(entry.runtime_data.recent_activity)
    assert any(
        e["action"] == "vacuum.start"
        and e["source"] == "ha_dreame.resume_queue"
        and e["context_id"] == caller.id
        and e["outcome"] == "accepted"
        for e in events
    )
    assert not any(e["outcome"] == "observed_request" for e in events)

    with service_audit(entry.runtime_data, call), automatic_audit():
        await async_call_robot_service(
            hass, entry.runtime_data, "vacuum", "start", {"entity_id": vacuum}
        )
    await hass.async_block_till_done()
    assert any(e["source"] == "automatic_reconcile" for e in entry.runtime_data.recent_activity)

    external = Context(parent_id="automation-context")
    await hass.services.async_call(
        "vacuum",
        "start",
        {"entity_id": vacuum, "secret": "do-not-log"},
        blocking=True,
        context=external,
    )
    await hass.async_block_till_done()
    assert any(
        e["source"] == "context_chain"
        and e["parent_id"] == "automation-context"
        and e["outcome"] == "observed_request"
        for e in entry.runtime_data.recent_activity
    )
    assert "do-not-log" not in str(entry.runtime_data.recent_activity)

    await hass.services.async_call(
        "vacuum", "start", {"entity_id": vacuum}, blocking=True, context=external
    )
    await hass.async_block_till_done()
    assert (
        sum(
            e["context_id"] == external.id and e["outcome"] == "observed_request"
            for e in entry.runtime_data.recent_activity
        )
        == 2
    )

    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")
    await hass.async_block_till_done()
    assert any(
        e["source"] == "robot_observation" and e["reason"] == "room_cleaning"
        for e in entry.runtime_data.recent_activity
    )

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    # The listener must not access an unloaded entry on subsequent robot calls.
    await hass.services.async_call("vacuum", "start", {"entity_id": vacuum}, blocking=True)
    await hass.async_block_till_done()


async def test_audit_records_cleaning_mode_switch_before_dispatch(hass: HomeAssistant) -> None:
    """A mode switch targets the select entity but is still a robot command."""
    vacuum = register_entity(hass, "vacuum.dreame_robot")
    hass.states.async_set("select.dreame_robot_cleaning_mode", "mopping")
    entry = mock_entry({"vacuum_entity_id": vacuum}, options={"allow_robot_commands": True})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    async def record(call: ServiceCall) -> None:
        return None

    hass.services.async_register("select", "select_option", record)
    hass.services.async_register("dreame_vacuum", "vacuum_clean_segment", record)
    hass.states.async_set(vacuum, "docked")
    caller = Context(user_id="test-user")
    for service, data in (
        ("add_queue_room", {"room_id": 7, "room_name": "Room 7"}),
        ("start_queue", {}),
    ):
        await hass.services.async_call(
            DOMAIN,
            service,
            {"config_entry_id": entry.entry_id, **data},
            blocking=True,
            context=caller,
        )

    commands = [
        (e["action"], e["outcome"], e["source"], e["context_id"])
        for e in entry.runtime_data.recent_activity
        if e["action"] in {"select.select_option", "dreame_vacuum.vacuum_clean_segment"}
    ]
    assert commands == [
        ("select.select_option", "requested", "ha_dreame.start_queue", caller.id),
        ("select.select_option", "accepted", "ha_dreame.start_queue", caller.id),
        ("dreame_vacuum.vacuum_clean_segment", "requested", "ha_dreame.start_queue", caller.id),
        ("dreame_vacuum.vacuum_clean_segment", "accepted", "ha_dreame.start_queue", caller.id),
    ]


async def test_robot_commands_are_refused_while_commands_are_disabled(hass: HomeAssistant) -> None:
    vacuum = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry({"vacuum_entity_id": vacuum})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    calls = []

    async def record(call: ServiceCall) -> None:
        calls.append(call)

    hass.services.async_register("select", "select_option", record)
    with pytest.raises(HomeAssistantError, match="robot commands are disabled"):
        await async_call_robot_service(
            hass,
            entry.runtime_data,
            "select",
            "select_option",
            {"entity_id": "select.dreame_robot_cleaning_mode", "option": "sweeping"},
        )
    assert calls == []
    assert not entry.runtime_data.recent_activity

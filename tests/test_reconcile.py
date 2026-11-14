"""Tests for applying reconcile decisions in Home Assistant."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from custom_components.ha_dreame.const import (
    CONF_ALLOW_ROBOT_COMMANDS,
    CONF_VACUUM_ENTITY_ID,
    DREAME_VACUUM_DOMAIN,
)
from custom_components.ha_dreame.queue_core import add_room, new_state, start_run
from custom_components.ha_dreame.reconcile import async_apply_decision, evaluate_reconcile
from custom_components.ha_dreame.reconcile_core import Decision
from custom_components.ha_dreame.queue_core import DispatchTracking

from .helpers import mock_entry, register_entity, set_dispatch, without_dispatch

pytestmark = pytest.mark.usefixtures("mock_dreame_vacuum_dependency")


async def _setup_entry(
    hass: HomeAssistant,
    *,
    commands_enabled: bool = True,
) -> tuple[object, str]:
    vacuum_entity_id = register_entity(hass, "vacuum.dreame_robot")
    entry = mock_entry(
        {CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
        options={CONF_ALLOW_ROBOT_COMMANDS: commands_enabled},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry, vacuum_entity_id


def _running_two_room_state():
    state = new_state()
    state = add_room(state, room_id=1, room_name="Kitchen")
    state = add_room(state, room_id=2, room_name="Hall")
    return start_run(state)


def _tracking(state, **overrides: object) -> DispatchTracking:
    values = {
        "last_command_at": datetime.fromisoformat("2026-05-16T09:00:00+00:00"),
    }
    values.update(overrides)
    return DispatchTracking(**values)


async def _running_entry(hass: HomeAssistant, *, commands_enabled: bool = True, **tracking):
    entry, vacuum_entity_id = await _setup_entry(hass, commands_enabled=commands_enabled)
    state = _running_two_room_state()
    run_tracking = _tracking(state, **tracking)
    entry.runtime_data.set_queue_state(state)
    state = replace(state, dispatch=run_tracking)
    entry.runtime_data.set_queue_state(state)
    return entry, vacuum_entity_id, state, run_tracking


async def test_awaited_item_requires_a_dispatched_running_room(
    hass: HomeAssistant,
) -> None:
    """Test only a running room that was dispatched awaits completion."""
    entry, _vacuum_entity_id = await _setup_entry(hass)
    runtime_data = entry.runtime_data
    idle_state = add_room(new_state(), room_id=1, room_name="Kitchen")
    runtime_data.set_queue_state(idle_state)
    assert runtime_data.awaited_item() is None

    state = start_run(idle_state)
    runtime_data.set_queue_state(state)
    assert runtime_data.awaited_item() is None

    set_dispatch(runtime_data, _tracking(state))
    assert runtime_data.awaited_item() == state.items[0]


async def test_evaluate_reconcile_skips_the_decision_without_an_awaited_room(
    hass: HomeAssistant,
) -> None:
    """Test evaluation observes the robot but decides nothing for an idle queue."""
    entry, vacuum_entity_id = await _setup_entry(hass)
    hass.states.async_set(vacuum_entity_id, "cleaning")

    evaluation = evaluate_reconcile(hass, entry.runtime_data)

    assert evaluation.observation.vacuum_state == "cleaning"
    assert evaluation.decision is None
    assert evaluation.seconds_since_command is None


async def test_evaluate_reconcile_measures_time_since_the_last_command(
    hass: HomeAssistant,
) -> None:
    """Test the decision sees how long ago the awaited room was commanded."""
    entry, vacuum_entity_id, state, _ = await _running_entry(
        hass, last_command_at=datetime.now(UTC) - timedelta(seconds=30)
    )
    hass.states.async_set(vacuum_entity_id, "idle")
    hass.states.async_set("sensor.dreame_robot_task_status", "room_cleaning")

    evaluation = evaluate_reconcile(hass, entry.runtime_data)

    assert evaluation.item == state.items[0]
    assert evaluation.seconds_since_command is not None
    assert 30 <= evaluation.seconds_since_command < 40
    assert evaluation.decision is not None
    assert evaluation.decision.action == "retry"


async def test_apply_hold_commits_tracking_only(hass: HomeAssistant) -> None:
    """Test a hold keeps the queue and stores the decision's tracking."""
    entry, _vacuum_entity_id, state, tracking = await _running_entry(
        hass,
        dispatch_retry_count=2,
        task_status_cleared_since_dispatch=False,
    )
    next_tracking = replace(
        tracking, dispatch_retry_count=0, task_status_cleared_since_dispatch=True
    )

    intent = await async_apply_decision(hass, entry.runtime_data, Decision("hold", next_tracking))

    assert intent is None
    assert without_dispatch(entry.runtime_data.queue_state) == without_dispatch(state)
    assert entry.runtime_data.queue_state.dispatch == next_tracking


async def test_apply_complete_dispatches_next_room_visible_to_observers(
    hass: HomeAssistant,
) -> None:
    """Test next-room dispatch exposes the new room to synchronous observers."""
    calls: list[dict[str, object]] = []
    observed_current_items: list[str | None] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))
        observed_current_items.append(entry.runtime_data.queue_state.current_item_id)

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    entry, vacuum_entity_id, state, tracking = await _running_entry(hass)
    next_item = state.items[1]

    intent = await async_apply_decision(hass, entry.runtime_data, Decision("complete", tracking))

    assert intent == "dispatch_current_room"
    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert observed_current_items == [next_item.item_id]
    queue_state = entry.runtime_data.queue_state
    assert [item.status for item in queue_state.items] == ["completed", "running"]
    assert queue_state.current_item_id == next_item.item_id
    run_tracking = entry.runtime_data.queue_state.dispatch
    assert run_tracking is not None
    assert entry.runtime_data.queue_state.current_item_id == next_item.item_id
    assert run_tracking.dispatch_retry_count == 0
    assert run_tracking.task_status_cleared_since_dispatch is False
    assert run_tracking.last_command_at.tzinfo is not None
    assert any(
        event["action"] == "dispatch_current_room"
        and event["outcome"] == "decision"
        and event["source"] == "reconcile"
        and event["room_id"] == 1
        for event in entry.runtime_data.recent_activity
    )


async def test_apply_complete_of_last_room_finishes_queue_without_dispatch(
    hass: HomeAssistant,
) -> None:
    """Test completing the final room ends the run without a robot command."""
    calls: list[ServiceCall] = []

    async def _record(call: ServiceCall) -> None:
        calls.append(call)

    hass.services.async_register(DREAME_VACUUM_DOMAIN, "vacuum_clean_segment", _record)
    entry, _vacuum_entity_id = await _setup_entry(hass)
    state = start_run(add_room(new_state(), room_id=1, room_name="Kitchen"))
    tracking = _tracking(state)
    entry.runtime_data.set_queue_state(state)
    state = replace(state, dispatch=tracking)
    entry.runtime_data.set_queue_state(state)

    intent = await async_apply_decision(hass, entry.runtime_data, Decision("complete", tracking))

    assert intent is None
    assert calls == []
    assert entry.runtime_data.queue_state.run_state == "completed"
    assert entry.runtime_data.queue_state.current_item_id is None
    assert entry.runtime_data.queue_state.dispatch is None


async def test_apply_complete_switches_mode_before_next_room(
    hass: HomeAssistant,
) -> None:
    """Test next-room dispatch restores the queue cleaning mode first."""
    calls: list[str] = []

    async def _record(call: ServiceCall) -> None:
        calls.append(f"{call.domain}.{call.service}:{call.data.get('option', '')}")

    hass.services.async_register(DREAME_VACUUM_DOMAIN, "vacuum_clean_segment", _record)
    hass.services.async_register("select", "select_option", _record)
    entry, _vacuum_entity_id, _state, tracking = await _running_entry(hass)
    hass.states.async_set("select.dreame_robot_cleaning_mode", "sweeping")

    await async_apply_decision(hass, entry.runtime_data, Decision("complete", tracking))

    assert calls == [
        "select.select_option:sweeping_and_mopping",
        f"{DREAME_VACUUM_DOMAIN}.vacuum_clean_segment:",
    ]


async def test_apply_retry_redispatches_with_the_incremented_retry_count(
    hass: HomeAssistant,
) -> None:
    """Test a retry redispatches the same room and keeps its retry accounting."""
    calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    entry, vacuum_entity_id, state, tracking = await _running_entry(
        hass,
        dispatch_retry_count=1,
        task_status_cleared_since_dispatch=True,
    )

    intent = await async_apply_decision(
        hass,
        entry.runtime_data,
        Decision("retry", replace(tracking, dispatch_retry_count=2)),
    )

    assert intent == "dispatch_current_room"
    assert calls == [{"entity_id": vacuum_entity_id, "segments": [1]}]
    assert without_dispatch(entry.runtime_data.queue_state) == without_dispatch(state)
    run_tracking = entry.runtime_data.queue_state.dispatch
    assert run_tracking is not None
    assert run_tracking.dispatch_retry_count == 2
    assert run_tracking.task_status_cleared_since_dispatch is False
    assert run_tracking.last_command_at != tracking.last_command_at


async def test_apply_dispatch_failure_preserves_runtime_state(
    hass: HomeAssistant,
) -> None:
    """Test failed command intents leave runtime state unchanged."""
    calls: list[dict[str, object]] = []

    async def _raise_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))
        raise HomeAssistantError("dispatch failed")

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _raise_clean_segment,
    )
    entry, vacuum_entity_id, state, tracking = await _running_entry(hass)

    with pytest.raises(HomeAssistantError, match="dispatch failed"):
        await async_apply_decision(hass, entry.runtime_data, Decision("complete", tracking))

    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert entry.runtime_data.queue_state == state
    assert entry.runtime_data.queue_state.dispatch == tracking


async def test_apply_retry_honors_disabled_command_gate(
    hass: HomeAssistant,
) -> None:
    """Test dispatch decisions still honor the runtime command gate."""
    calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    entry, _vacuum_entity_id, state, tracking = await _running_entry(hass, commands_enabled=False)

    with pytest.raises(HomeAssistantError, match="robot commands are disabled"):
        await async_apply_decision(
            hass,
            entry.runtime_data,
            Decision("retry", replace(tracking, dispatch_retry_count=1)),
        )

    assert calls == []
    assert entry.runtime_data.queue_state == state
    assert entry.runtime_data.queue_state.dispatch == tracking


@pytest.mark.parametrize(("blocked", "run_state"), [(False, "out_of_sync"), (True, "blocked")])
async def test_apply_fail_ends_the_run_and_clears_tracking(
    hass: HomeAssistant,
    blocked: bool,
    run_state: str,
) -> None:
    """Test a failed run stops, marks its room for review and keeps later rooms."""
    entry, _vacuum_entity_id, _state, tracking = await _running_entry(hass)

    intent = await async_apply_decision(
        hass,
        entry.runtime_data,
        Decision("fail", tracking, fail_reason="dispatch_retry_exhausted", blocked=blocked),
    )

    assert intent is None
    queue_state = entry.runtime_data.queue_state
    assert queue_state.run_state == run_state
    assert queue_state.current_item_id is None
    assert [(item.status, item.result) for item in queue_state.items] == [
        ("needs_attention", "dispatch_retry_exhausted"),
        ("pending", None),
    ]
    assert entry.runtime_data.queue_state.dispatch is None


async def test_apply_resume_calls_vacuum_start_and_commits_tracking(
    hass: HomeAssistant,
) -> None:
    """Test resume decisions call vacuum.start before committing runtime state."""
    calls: list[dict[str, object]] = []

    async def _record_start(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register("vacuum", "start", _record_start)
    entry, vacuum_entity_id, state, tracking = await _running_entry(hass)
    decision_tracking = replace(tracking, task_status_cleared_since_dispatch=True)

    intent = await async_apply_decision(
        hass, entry.runtime_data, Decision("resume", decision_tracking)
    )

    assert intent == "resume_current_room"
    assert calls == [{"entity_id": vacuum_entity_id}]
    assert without_dispatch(entry.runtime_data.queue_state) == without_dispatch(state)
    run_tracking = entry.runtime_data.queue_state.dispatch
    assert run_tracking is not None
    assert entry.runtime_data.queue_state.current_item_id == state.current_item_id
    assert run_tracking.task_status_cleared_since_dispatch is True
    assert run_tracking.last_command_at != tracking.last_command_at
    assert run_tracking.last_command_at.tzinfo is not None


async def test_apply_resume_failure_preserves_runtime_state(
    hass: HomeAssistant,
) -> None:
    """Test failed resume commands leave runtime state unchanged."""
    calls: list[dict[str, object]] = []

    async def _raise_start(call: ServiceCall) -> None:
        calls.append(dict(call.data))
        raise HomeAssistantError("resume failed")

    hass.services.async_register("vacuum", "start", _raise_start)
    entry, vacuum_entity_id, state, tracking = await _running_entry(hass)

    with pytest.raises(HomeAssistantError, match="resume failed"):
        await async_apply_decision(hass, entry.runtime_data, Decision("resume", tracking))

    assert calls == [{"entity_id": vacuum_entity_id}]
    assert entry.runtime_data.queue_state == state
    assert entry.runtime_data.queue_state.dispatch == tracking


async def test_apply_resume_honors_disabled_command_gate(
    hass: HomeAssistant,
) -> None:
    """Test disabled robot commands block resume decisions."""
    calls: list[dict[str, object]] = []

    async def _record_start(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register("vacuum", "start", _record_start)
    entry, _vacuum_entity_id, state, tracking = await _running_entry(hass, commands_enabled=False)

    with pytest.raises(HomeAssistantError, match="robot commands are disabled"):
        await async_apply_decision(hass, entry.runtime_data, Decision("resume", tracking))

    assert calls == []
    assert entry.runtime_data.queue_state == state
    assert entry.runtime_data.queue_state.dispatch == tracking

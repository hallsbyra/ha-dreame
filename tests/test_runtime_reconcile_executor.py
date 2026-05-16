"""Tests for the Home Assistant runtime reconcile executor."""

from datetime import datetime

import pytest

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from custom_components.ha_dreame.const import (
    CONF_ALLOW_ROBOT_COMMANDS,
    CONF_VACUUM_ENTITY_ID,
    DREAME_VACUUM_DOMAIN,
)
from custom_components.ha_dreame.queue_core import (
    ReconcileDecision,
    add_room,
    new_state,
    start_run,
)
from custom_components.ha_dreame.runtime_reconcile import (
    COMMAND_INTENT_RESUME_CURRENT_ROOM,
    RuntimeReconcileResult,
    apply_reconcile_decision,
)
from custom_components.ha_dreame.runtime_reconcile_executor import (
    async_apply_runtime_reconcile_result,
)
from custom_components.ha_dreame.runtime_state import QueueRunTracking

from .helpers import mock_entry, register_entity

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


def _tracking(state, **overrides: object) -> QueueRunTracking:
    assert state.run_id is not None
    assert state.current_item_id is not None
    values = {
        "run_id": state.run_id,
        "current_item_id": state.current_item_id,
        "last_command_at": "2026-05-16T09:00:00+00:00",
    }
    values.update(overrides)
    return QueueRunTracking(**values)


async def test_runtime_reconcile_executor_commits_tracking_only_result(
    hass: HomeAssistant,
) -> None:
    """Test no-command reconcile results update runtime coordinators."""
    entry, _vacuum_entity_id = await _setup_entry(hass)
    state = _running_two_room_state()
    tracking = _tracking(
        state,
        dispatch_retry_count=2,
        task_status_cleared_since_dispatch=False,
    )
    entry.runtime_data.set_queue_state(state)
    entry.runtime_data.set_run_tracking(tracking)

    result = apply_reconcile_decision(
        state,
        tracking,
        ReconcileDecision(
            set_task_status_cleared_since_dispatch=True,
            reset_dispatch_retry_count=True,
        ),
    )

    await async_apply_runtime_reconcile_result(hass, entry.runtime_data, result)

    assert entry.runtime_data.queue_state == result.queue_state
    assert entry.runtime_data.run_tracking == result.run_tracking
    assert entry.runtime_data.run_tracking.dispatch_retry_count == 0
    assert entry.runtime_data.run_tracking.task_status_cleared_since_dispatch is True


async def test_runtime_reconcile_executor_dispatches_next_room_after_completion(
    hass: HomeAssistant,
) -> None:
    """Test next-room command intents dispatch before committing runtime state."""
    calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    entry, vacuum_entity_id = await _setup_entry(hass)
    state = _running_two_room_state()
    tracking = _tracking(state)
    entry.runtime_data.set_queue_state(state)
    entry.runtime_data.set_run_tracking(tracking)

    result = apply_reconcile_decision(
        state,
        tracking,
        ReconcileDecision(complete_current_room=True),
    )

    await async_apply_runtime_reconcile_result(hass, entry.runtime_data, result)

    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert entry.runtime_data.queue_state == result.queue_state
    run_tracking = entry.runtime_data.run_tracking
    assert run_tracking is not None
    assert run_tracking.run_id == result.queue_state.run_id
    assert run_tracking.current_item_id == result.queue_state.current_item_id
    assert run_tracking.dispatch_retry_count == 0
    assert run_tracking.task_status_cleared_since_dispatch is False
    datetime.fromisoformat(run_tracking.last_command_at)


async def test_runtime_reconcile_executor_preserves_retry_count_after_redispatch(
    hass: HomeAssistant,
) -> None:
    """Test retry intents preserve retry accounting after successful dispatch."""
    calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    entry, vacuum_entity_id = await _setup_entry(hass)
    state = _running_two_room_state()
    tracking = _tracking(
        state,
        dispatch_retry_count=1,
        task_status_cleared_since_dispatch=True,
    )
    entry.runtime_data.set_queue_state(state)
    entry.runtime_data.set_run_tracking(tracking)

    result = apply_reconcile_decision(
        state,
        tracking,
        ReconcileDecision(retry_current_room=True),
    )

    await async_apply_runtime_reconcile_result(hass, entry.runtime_data, result)

    assert calls == [{"entity_id": vacuum_entity_id, "segments": [1]}]
    assert entry.runtime_data.queue_state == result.queue_state
    run_tracking = entry.runtime_data.run_tracking
    assert run_tracking is not None
    assert run_tracking.dispatch_retry_count == 2
    assert run_tracking.task_status_cleared_since_dispatch is False
    assert run_tracking.last_command_at != tracking.last_command_at


async def test_runtime_reconcile_executor_dispatch_failure_preserves_runtime_state(
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
    entry, vacuum_entity_id = await _setup_entry(hass)
    state = _running_two_room_state()
    tracking = _tracking(state)
    entry.runtime_data.set_queue_state(state)
    entry.runtime_data.set_run_tracking(tracking)
    result = apply_reconcile_decision(
        state,
        tracking,
        ReconcileDecision(complete_current_room=True),
    )

    with pytest.raises(HomeAssistantError, match="dispatch failed"):
        await async_apply_runtime_reconcile_result(hass, entry.runtime_data, result)

    assert calls == [{"entity_id": vacuum_entity_id, "segments": [2]}]
    assert entry.runtime_data.queue_state == state
    assert entry.runtime_data.run_tracking == tracking


async def test_runtime_reconcile_executor_disabled_gate_preserves_runtime_state(
    hass: HomeAssistant,
) -> None:
    """Test dispatch intents still honor the runtime command gate."""
    calls: list[dict[str, object]] = []

    async def _record_clean_segment(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register(
        DREAME_VACUUM_DOMAIN,
        "vacuum_clean_segment",
        _record_clean_segment,
    )
    entry, _vacuum_entity_id = await _setup_entry(hass, commands_enabled=False)
    state = _running_two_room_state()
    tracking = _tracking(state)
    entry.runtime_data.set_queue_state(state)
    entry.runtime_data.set_run_tracking(tracking)
    result = apply_reconcile_decision(
        state,
        tracking,
        ReconcileDecision(retry_current_room=True),
    )

    with pytest.raises(HomeAssistantError, match="robot commands are disabled"):
        await async_apply_runtime_reconcile_result(hass, entry.runtime_data, result)

    assert calls == []
    assert entry.runtime_data.queue_state == state
    assert entry.runtime_data.run_tracking == tracking


async def test_runtime_reconcile_executor_commits_terminal_result(
    hass: HomeAssistant,
) -> None:
    """Test terminal no-command results update queue state and clear tracking."""
    entry, _vacuum_entity_id = await _setup_entry(hass)
    state = _running_two_room_state()
    tracking = _tracking(state)
    entry.runtime_data.set_queue_state(state)
    entry.runtime_data.set_run_tracking(tracking)
    result = apply_reconcile_decision(
        state,
        tracking,
        ReconcileDecision(mark_out_of_sync_reason="dispatch_retry_exhausted"),
    )

    await async_apply_runtime_reconcile_result(hass, entry.runtime_data, result)

    assert entry.runtime_data.queue_state == result.queue_state
    assert entry.runtime_data.queue_state.run_state == "out_of_sync"
    assert entry.runtime_data.run_tracking is None


async def test_runtime_reconcile_executor_rejects_resume_intent_without_mutating(
    hass: HomeAssistant,
) -> None:
    """Test resume intents stay explicit until a Dreame resume command is chosen."""
    entry, _vacuum_entity_id = await _setup_entry(hass)
    state = _running_two_room_state()
    tracking = _tracking(state)
    entry.runtime_data.set_queue_state(state)
    entry.runtime_data.set_run_tracking(tracking)
    result = RuntimeReconcileResult(
        queue_state=state,
        run_tracking=tracking,
        command_intent=COMMAND_INTENT_RESUME_CURRENT_ROOM,
        command_item_id=state.current_item_id,
    )

    with pytest.raises(HomeAssistantError, match="Resume reconcile intent is not wired"):
        await async_apply_runtime_reconcile_result(hass, entry.runtime_data, result)

    assert entry.runtime_data.queue_state == state
    assert entry.runtime_data.run_tracking == tracking

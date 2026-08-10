"""Tests for the pure HA Dreame queue core."""

import pytest

from custom_components.ha_dreame.queue_core import (
    InvalidOperation,
    ItemNotFound,
    QueueItem,
    QueueState,
    add_room,
    cancel_run,
    clear_pending,
    complete_current_room,
    current_item,
    external_takeover,
    move_item,
    new_state,
    remove_item,
    skip_current_room,
    start_run,
    terminal_run_state_for_reason,
    update_item_overrides,
)


def _seed_three_rooms() -> QueueState:
    state = new_state()
    state = add_room(state, room_id=1, room_name="Kitchen")
    state = add_room(state, room_id=2, room_name="Hall")
    return add_room(state, room_id=3, room_name="Office")


def test_new_state_starts_idle_and_empty() -> None:
    """Test the queue starts idle and empty."""
    state = new_state()

    assert state.run_state == "idle"
    assert state.run_id is None
    assert state.items == ()
    assert state.current_item_id is None
    assert current_item(state) is None


def test_current_item_returns_none_when_id_is_stale() -> None:
    """Test current item lookup tolerates stale state."""
    state = QueueState(
        run_state="running",
        current_item_id="missing",
        items=(
            QueueItem(
                item_id="item-1",
                room_id=1,
                room_name="Kitchen",
                status="running",
            ),
        ),
    )

    assert current_item(state) is None


def test_add_room_appends_pending_item_and_copies_overrides() -> None:
    """Test adding a room appends one pending item."""
    overrides = {"suction_level": "turbo"}

    state = add_room(new_state(), room_id=11, room_name="Living room", overrides=overrides)
    overrides["suction_level"] = "quiet"

    assert len(state.items) == 1
    assert state.items[0].room_id == 11
    assert state.items[0].room_name == "Living room"
    assert state.items[0].status == "pending"
    assert state.items[0].overrides == {"suction_level": "turbo"}


def test_add_room_without_overrides_inherits_previous_room_settings() -> None:
    """Test a new room inherits an independent copy of the preceding settings."""
    state = add_room(
        new_state(),
        room_id=11,
        room_name="Living room",
        overrides={"repeats": 2, "suction_level": 3, "water_volume": 1},
    )

    state = add_room(state, room_id=12, room_name="Dining room")

    assert state.items[1].overrides == state.items[0].overrides
    assert state.items[1].overrides is not state.items[0].overrides


@pytest.mark.parametrize("terminal_state", ["completed", "canceled", "out_of_sync", "blocked"])
def test_add_room_after_terminal_run_starts_fresh_pending_queue(
    terminal_state: str,
) -> None:
    """Test adding a room after a terminal run resets stale queue contents."""
    state = QueueState(
        run_state=terminal_state,
        run_id="run-1",
        current_item_id="item-1",
        items=(
            QueueItem(
                item_id="item-1",
                room_id=1,
                room_name="Kitchen",
                status="completed",
                overrides={"repeats": 3, "water_volume": 1},
            ),
        ),
    )

    state = add_room(state, room_id=7, room_name="Hall")

    assert state.run_state == "idle"
    assert state.run_id is None
    assert state.current_item_id is None
    assert [(item.room_id, item.room_name, item.status) for item in state.items] == [
        (7, "Hall", "pending")
    ]
    assert state.items[0].overrides == {}


def test_start_run_sets_run_state_and_first_room_running() -> None:
    """Test starting a run marks the first pending room as running."""
    state = start_run(_seed_three_rooms())

    assert state.run_state == "running"
    assert state.run_id is not None
    assert state.current_item_id == state.items[0].item_id
    assert current_item(state) == state.items[0]
    assert [item.status for item in state.items] == ["running", "pending", "pending"]


def test_start_run_rejects_invalid_start_states() -> None:
    """Test starting requires a non-running queue with pending rooms."""
    with pytest.raises(InvalidOperation, match="Queue is empty"):
        start_run(new_state())

    running_state = start_run(_seed_three_rooms())
    with pytest.raises(InvalidOperation, match="already running"):
        start_run(running_state)

    completed_only = QueueState(
        items=(QueueItem(item_id="done", room_id=1, room_name="Kitchen", status="completed"),)
    )
    with pytest.raises(InvalidOperation, match="No pending rooms"):
        start_run(completed_only)


def test_complete_current_room_advances_and_completes_run() -> None:
    """Test completing rooms advances through pending items and then completes."""
    state = start_run(_seed_three_rooms())

    state = complete_current_room(state)

    assert state.run_state == "running"
    assert [item.status for item in state.items] == ["completed", "running", "pending"]
    assert state.current_item_id == state.items[1].item_id

    state = complete_current_room(state)
    state = complete_current_room(state)

    assert state.run_state == "completed"
    assert state.current_item_id is None
    assert [item.status for item in state.items] == ["completed", "completed", "completed"]


def test_complete_current_room_requires_consistent_running_context() -> None:
    """Test finishing a room requires a valid running context."""
    with pytest.raises(InvalidOperation, match="Queue is not running"):
        complete_current_room(_seed_three_rooms())

    missing_current = QueueState(run_state="running", items=_seed_three_rooms().items)
    with pytest.raises(InvalidOperation, match="No current room"):
        complete_current_room(missing_current)

    wrong_status = QueueState(
        run_state="running",
        current_item_id="item-1",
        items=(QueueItem(item_id="item-1", room_id=1, room_name="Kitchen"),),
    )
    with pytest.raises(InvalidOperation, match="Current room is not running"):
        complete_current_room(wrong_status)


def test_remove_pending_item_works() -> None:
    """Test pending rooms can be removed."""
    state = _seed_three_rooms()

    state = remove_item(state, item_id=state.items[1].item_id)

    assert [item.room_name for item in state.items] == ["Kitchen", "Office"]


def test_remove_rejects_running_and_terminal_items() -> None:
    """Test only pending items can be removed."""
    state = start_run(_seed_three_rooms())

    with pytest.raises(InvalidOperation, match="currently running"):
        remove_item(state, item_id=state.items[0].item_id)

    state = complete_current_room(state)
    with pytest.raises(InvalidOperation, match="Only pending"):
        remove_item(state, item_id=state.items[0].item_id)

    with pytest.raises(ItemNotFound):
        remove_item(state, item_id="missing")


def test_move_item_before_run_changes_order() -> None:
    """Test pending rooms can be reordered before the run starts."""
    state = _seed_three_rooms()

    state = move_item(state, item_id=state.items[0].item_id, new_position=2)

    assert [item.room_name for item in state.items] == ["Hall", "Office", "Kitchen"]


def test_move_item_during_run_only_reorders_pending_after_running_item() -> None:
    """Test running queues allow reordering only after the current room."""
    state = start_run(_seed_three_rooms())

    state = move_item(state, item_id=state.items[2].item_id, new_position=1)

    assert [item.room_name for item in state.items] == ["Kitchen", "Office", "Hall"]
    assert [item.status for item in state.items] == ["running", "pending", "pending"]


def test_move_item_rejects_invalid_positions_and_items() -> None:
    """Test invalid move requests fail clearly."""
    state = start_run(_seed_three_rooms())

    with pytest.raises(InvalidOperation, match="out of range"):
        move_item(state, item_id=state.items[1].item_id, new_position=3)

    with pytest.raises(InvalidOperation, match="Only pending"):
        move_item(state, item_id=state.items[0].item_id, new_position=1)

    with pytest.raises(InvalidOperation, match="before current"):
        move_item(state, item_id=state.items[1].item_id, new_position=0)

    inconsistent = QueueState(run_state="running", items=_seed_three_rooms().items)
    with pytest.raises(InvalidOperation, match="no running room"):
        move_item(inconsistent, item_id=inconsistent.items[1].item_id, new_position=2)

    with pytest.raises(ItemNotFound):
        move_item(state, item_id="missing", new_position=1)


def test_update_item_overrides_only_allows_pending_items() -> None:
    """Test only pending room overrides can be updated."""
    state = start_run(_seed_three_rooms())

    state = update_item_overrides(
        state,
        item_id=state.items[1].item_id,
        overrides={"repeats": 2},
    )

    assert state.items[1].overrides == {"repeats": 2}

    with pytest.raises(InvalidOperation, match="currently running"):
        update_item_overrides(state, item_id=state.items[0].item_id, overrides={})

    completed_state = complete_current_room(state)
    with pytest.raises(InvalidOperation, match="Only pending"):
        update_item_overrides(
            completed_state, item_id=completed_state.items[0].item_id, overrides={}
        )


def test_clear_pending_keeps_running_item_and_resets_non_running_queue() -> None:
    """Test clear pending preserves active work only while running."""
    state = start_run(_seed_three_rooms())

    running_only = clear_pending(state)

    assert running_only.run_state == "running"
    assert [item.room_name for item in running_only.items] == ["Kitchen"]
    assert running_only.current_item_id == running_only.items[0].item_id

    assert clear_pending(_seed_three_rooms()) == new_state()

    inconsistent = QueueState(run_state="running", items=_seed_three_rooms().items)
    assert clear_pending(inconsistent) == new_state()


def test_skip_current_marks_current_skipped_and_advances() -> None:
    """Test skipping the active room advances to the next pending room."""
    state = start_run(_seed_three_rooms())
    skipped_item_id = state.current_item_id

    state = skip_current_room(state, reason="skip_pressed")

    assert state.run_state == "running"
    assert state.items[0].item_id == skipped_item_id
    assert state.items[0].status == "skipped"
    assert state.items[0].result == "skip_pressed"
    assert state.items[1].status == "running"


def test_cancel_run_marks_non_terminal_items_canceled() -> None:
    """Test cancel preserves terminal item states and cancels the active plan."""
    state = start_run(_seed_three_rooms())
    state = complete_current_room(state)
    state = skip_current_room(state)

    state = cancel_run(state, reason="user_cancel")

    assert state.run_state == "canceled"
    assert state.current_item_id is None
    assert [item.status for item in state.items] == ["completed", "skipped", "canceled"]
    assert state.items[2].result == "user_cancel"


def test_external_takeover_sets_terminal_state_and_cancels_active_plan() -> None:
    """Test external takeover cancels non-terminal queue items."""
    state = start_run(_seed_three_rooms())

    state = external_takeover(state, reason="stopped_from_app")

    assert state.run_state == "out_of_sync"
    assert state.current_item_id is None
    assert [item.status for item in state.items] == ["canceled", "canceled", "canceled"]
    assert all(item.result == "stopped_from_app" for item in state.items)


def test_terminal_run_state_for_reason_handles_route_blocks() -> None:
    """Test route failures map to blocked while other reasons map to out_of_sync."""
    assert terminal_run_state_for_reason("stopped_from_app") == "out_of_sync"
    assert terminal_run_state_for_reason("vacuum_route_error:expected_1:observed_7") == "blocked"

    state = start_run(_seed_three_rooms())
    state = external_takeover(
        state,
        reason="manual_override",
        terminal_state="manual_control",
    )

    assert state.run_state == "manual_control"

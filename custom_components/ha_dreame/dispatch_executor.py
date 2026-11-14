"""Command-gated execution for planned Dreame room dispatches."""

from __future__ import annotations

from datetime import UTC, datetime

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .audit import async_call_robot_service
from .const import companion_entity_id
from .dispatch_plan import DispatchServiceCall, build_room_dispatch_plan
from .queue_core import QueueError, QueueState, current_item
from .runtime import HaDreameRuntimeData
from .runtime_state import QueueRunTracking


def current_room_dispatch_plan(
    hass: HomeAssistant,
    runtime_data: HaDreameRuntimeData,
    state: QueueState,
    retry_count: int = 0,
) -> tuple[DispatchServiceCall, ...]:
    """Plan the dispatch of a state's current room for the robot's observed mode."""
    item = current_item(state)
    if item is None:
        raise HomeAssistantError("No current room to dispatch")
    mode_state = hass.states.get(
        companion_entity_id(runtime_data.vacuum_entity_id, "select", "cleaning_mode")
    )
    try:
        return build_room_dispatch_plan(
            item,
            vacuum_entity_id=runtime_data.vacuum_entity_id,
            current_cleaning_mode=mode_state.state if mode_state is not None else None,
            retry_count=retry_count,
        )
    except QueueError as err:
        raise HomeAssistantError(str(err)) from err


async def async_dispatch_current_room(
    hass: HomeAssistant,
    runtime_data: HaDreameRuntimeData,
    next_state: QueueState,
    retry_count: int = 0,
    *,
    plan: tuple[DispatchServiceCall, ...] | None = None,
) -> None:
    """Publish next_state with fresh run tracking, then dispatch its current room.

    Service handlers and state observers can run synchronously while the command is in
    flight. Publishing first keeps them from attributing fresh robot activity to the room
    that just finished. A rejected command restores the previous queue and tracking.
    Callers that must validate before sending another command pass a plan built earlier.
    """
    if plan is None:
        plan = current_room_dispatch_plan(hass, runtime_data, next_state, retry_count)
    assert next_state.run_id is not None and next_state.current_item_id is not None

    previous_queue_state = runtime_data.queue_state
    previous_run_tracking = runtime_data.run_tracking
    runtime_data.set_queue_state(next_state)
    runtime_data.set_run_tracking(
        QueueRunTracking(
            run_id=next_state.run_id,
            current_item_id=next_state.current_item_id,
            last_command_at=datetime.now(UTC),
            dispatch_retry_count=retry_count,
        )
    )
    try:
        for planned_call in plan:
            await async_call_robot_service(
                hass,
                runtime_data,
                planned_call.domain,
                planned_call.service,
                dict(planned_call.data),
            )
    except Exception:
        runtime_data.set_queue_state(previous_queue_state)
        runtime_data.set_run_tracking(previous_run_tracking)
        raise

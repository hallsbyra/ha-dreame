"""Runtime data for HA Dreame config entries."""

from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .queue_core import QueueItem, QueueState, current_item
from .runtime_observation import RuntimeObservationEntityIds, build_runtime_reconcile_observation
from .reconcile_core import Observation
from .runtime_state import QueueRunTracking


@dataclass(frozen=True, slots=True)
class HaDreameRuntimeData:
    """Runtime data attached to a configured HA Dreame entry."""

    auto_reconcile_enabled: bool
    commands_enabled: bool
    observation_entity_ids: RuntimeObservationEntityIds
    operation_lock: asyncio.Lock
    queue_coordinator: DataUpdateCoordinator[QueueState]
    run_tracking_coordinator: DataUpdateCoordinator[QueueRunTracking | None]
    unload_requested: asyncio.Event
    vacuum_entity_id: str
    recent_activity: deque[dict[str, Any]] = field(default_factory=lambda: deque(maxlen=100))

    def observe(
        self,
        hass: HomeAssistant,
        *,
        task_status_override: str | None = None,
    ) -> Observation:
        """Read one robot observation from this entry's companion entities."""
        return build_runtime_reconcile_observation(
            hass,
            vacuum_entity_id=self.vacuum_entity_id,
            entity_ids=self.observation_entity_ids,
            task_status_override=task_status_override,
        )

    def awaited_item(self) -> QueueItem | None:
        """Return the running room while it awaits completion under matching run tracking."""
        queue_state = self.queue_state
        run_tracking = self.run_tracking
        item = current_item(queue_state)
        if (
            queue_state.run_state != "running"
            or item is None
            or item.status != "running"
            or run_tracking is None
            or run_tracking.run_id != queue_state.run_id
            or run_tracking.current_item_id != item.item_id
        ):
            return None
        return item

    @property
    def queue_state(self) -> QueueState:
        """Return the current runtime queue state."""
        queue_state = self.queue_coordinator.data
        if queue_state is None:
            msg = "HA Dreame queue coordinator has no state"
            raise RuntimeError(msg)
        return queue_state

    def set_queue_state(self, queue_state: QueueState) -> None:
        """Set the current runtime queue state and notify listeners."""
        self.queue_coordinator.async_set_updated_data(queue_state)

    @property
    def run_tracking(self) -> QueueRunTracking | None:
        """Return runtime tracking for the current dispatched queue item."""
        return self.run_tracking_coordinator.data

    def set_run_tracking(self, run_tracking: QueueRunTracking | None) -> None:
        """Set current runtime run tracking and notify listeners."""
        self.run_tracking_coordinator.async_set_updated_data(run_tracking)

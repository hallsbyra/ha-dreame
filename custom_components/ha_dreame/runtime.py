"""Runtime data for HA Dreame config entries."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .queue_core import QueueState
from .runtime_observation import RuntimeObservationEntityIds
from .runtime_state import QueueRunTracking


@dataclass(frozen=True, slots=True)
class HaDreameRuntimeData:
    """Runtime data attached to a configured HA Dreame entry."""

    auto_reconcile_enabled: bool
    commands_enabled: bool
    observation_entity_ids: RuntimeObservationEntityIds
    queue_coordinator: DataUpdateCoordinator[QueueState]
    run_tracking_coordinator: DataUpdateCoordinator[QueueRunTracking | None]
    vacuum_entity_id: str

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

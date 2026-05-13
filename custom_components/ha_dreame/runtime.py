"""Runtime data for HA Dreame config entries."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .queue_core import QueueState


@dataclass(frozen=True, slots=True)
class HaDreameRuntimeData:
    """Runtime data attached to a configured HA Dreame entry."""

    commands_enabled: bool
    queue_coordinator: DataUpdateCoordinator[QueueState]
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

"""Runtime data for HA Dreame config entries."""

from __future__ import annotations

from dataclasses import dataclass

from .queue_core import QueueState


@dataclass(frozen=True, slots=True)
class HaDreameRuntimeData:
    """Runtime data attached to a configured HA Dreame entry."""

    commands_enabled: bool
    queue_state: QueueState
    vacuum_entity_id: str

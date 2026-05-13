"""Runtime data for HA Dreame config entries."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HaDreameRuntimeData:
    """Runtime data attached to a configured HA Dreame entry."""

    commands_enabled: bool
    vacuum_entity_id: str

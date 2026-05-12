"""Pure cleaning profile derivation for HA Dreame queue planning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class InvalidProfile(ValueError):
    """Raised when queue overrides describe an impossible cleaning profile."""


@dataclass(frozen=True)
class CleaningProfile:
    """Resolved cleaning profile values for runtime state and dispatch."""

    cleaning_mode: int
    runtime_suction_level: int | None
    runtime_water_volume: int | None
    dispatch_suction_level: int | None
    dispatch_water_volume: int | None
    custom_suction_level: int
    custom_water_volume: int


def derive_cleaning_profile(effective: dict[str, Any]) -> CleaningProfile:
    """Derive cleaning mode and dispatch values from queue overrides."""
    cleaning_mode = _to_int_or_none(effective.get("cleaning_mode"))
    suction_level = _to_int_or_none(effective.get("suction_level"))
    water_volume = _to_int_or_none(effective.get("water_volume"))

    suction_off = suction_level is not None and suction_level < 0
    water_off = water_volume is not None and water_volume <= 0

    if suction_off and water_off:
        raise InvalidProfile("Both suction and moisture are disabled")

    resolved_mode = _resolve_cleaning_mode(
        cleaning_mode=cleaning_mode,
        suction_level=suction_level,
        water_volume=water_volume,
        suction_off=suction_off,
        water_off=water_off,
    )

    runtime_suction = suction_level if suction_level is not None and suction_level >= 0 else None
    runtime_water = (
        water_volume
        if water_volume is not None and water_volume > 0 and resolved_mode != 0
        else None
    )

    return CleaningProfile(
        cleaning_mode=resolved_mode,
        runtime_suction_level=runtime_suction,
        runtime_water_volume=runtime_water,
        dispatch_suction_level=None if resolved_mode == 1 else runtime_suction,
        dispatch_water_volume=None if resolved_mode == 0 else runtime_water,
        custom_suction_level=runtime_suction if runtime_suction is not None else 0,
        custom_water_volume=runtime_water if runtime_water is not None else 1,
    )


def _resolve_cleaning_mode(
    *,
    cleaning_mode: int | None,
    suction_level: int | None,
    water_volume: int | None,
    suction_off: bool,
    water_off: bool,
) -> int:
    if suction_off:
        return 1
    if water_off:
        return 0
    if cleaning_mode in {0, 1, 2}:
        return int(cleaning_mode)
    if suction_level is not None and water_volume is not None:
        return 2
    if suction_level is not None:
        return 0
    if water_volume is not None:
        return 1
    return 2


def _to_int_or_none(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

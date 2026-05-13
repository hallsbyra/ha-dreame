"""Pure Dreame room dispatch planning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .const import DREAME_VACUUM_DOMAIN
from .profile_core import InvalidProfile, derive_cleaning_profile
from .queue_core import InvalidOperation, QueueItem

ADVANCED_CUSTOM_CLEANING_KEYS = (
    "custom_mopping_route",
    "cleaning_route",
    "wetness_level",
    "mop_temperature",
    "mop_pressure",
)
REMOVED_OVERRIDE_KEYS = {"deep_cleaning"}


@dataclass(frozen=True, slots=True)
class DispatchServiceCall:
    """One planned Home Assistant service call."""

    domain: str
    service: str
    data: dict[str, Any]


@dataclass(frozen=True, slots=True)
class RoomDispatchPlan:
    """Planned command payloads for one queue room."""

    item_id: str
    room_id: int
    room_name: str
    effective_overrides: dict[str, Any]
    service_calls: tuple[DispatchServiceCall, ...]


def build_room_dispatch_plan(
    item: QueueItem,
    *,
    vacuum_entity_id: str,
    defaults: Mapping[str, Any] | None = None,
    retry_count: int = 0,
) -> RoomDispatchPlan:
    """Build planned Dreame service-call payloads for one queue item."""
    effective = _effective_overrides(defaults=defaults, overrides=item.overrides)

    resolved_route = _int_or_none(effective.get("cleaning_route"))
    if resolved_route is None:
        resolved_route = _int_or_none(effective.get("route"))
    if resolved_route is not None:
        effective["cleaning_route"] = resolved_route

    try:
        profile = derive_cleaning_profile(effective)
    except InvalidProfile as err:
        raise InvalidOperation(str(err)) from err

    calls: list[DispatchServiceCall] = []
    has_advanced_override = any(
        effective.get(key) is not None for key in ADVANCED_CUSTOM_CLEANING_KEYS
    )
    repeats = _int_or_none(effective.get("repeats"))

    if has_advanced_override and retry_count == 0:
        if repeats is None:
            raise InvalidOperation("Advanced overrides require repeats")

        custom_payload: dict[str, Any] = {
            "entity_id": vacuum_entity_id,
            "segment_id": [int(item.room_id)],
            "suction_level": [int(profile.custom_suction_level)],
            "water_volume": [int(profile.custom_water_volume)],
            "repeats": [repeats],
        }
        for key in ADVANCED_CUSTOM_CLEANING_KEYS:
            value = _int_or_none(effective.get(key))
            if value is not None:
                custom_payload[key] = [value]

        calls.append(
            DispatchServiceCall(
                domain=DREAME_VACUUM_DOMAIN,
                service="vacuum_set_custom_cleaning",
                data=custom_payload,
            )
        )

    clean_segment_payload: dict[str, Any] = {
        "entity_id": vacuum_entity_id,
        "segments": [int(item.room_id)],
    }
    if repeats is not None:
        clean_segment_payload["repeats"] = repeats
    if profile.dispatch_suction_level is not None:
        clean_segment_payload["suction_level"] = int(profile.dispatch_suction_level)
    if profile.dispatch_water_volume is not None:
        clean_segment_payload["water_volume"] = int(profile.dispatch_water_volume)

    calls.append(
        DispatchServiceCall(
            domain=DREAME_VACUUM_DOMAIN,
            service="vacuum_clean_segment",
            data=clean_segment_payload,
        )
    )

    return RoomDispatchPlan(
        item_id=item.item_id,
        room_id=item.room_id,
        room_name=item.room_name,
        effective_overrides=effective,
        service_calls=tuple(calls),
    )


def _effective_overrides(
    *,
    defaults: Mapping[str, Any] | None,
    overrides: Mapping[str, Any] | None,
) -> dict[str, Any]:
    effective = _non_null_dict(defaults)
    effective.update(_non_null_dict(overrides))
    return effective


def _non_null_dict(raw: Mapping[str, Any] | None) -> dict[str, Any]:
    if raw is None:
        return {}
    return {
        key: value
        for key, value in raw.items()
        if value is not None and key not in REMOVED_OVERRIDE_KEYS
    }


def _int_or_none(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

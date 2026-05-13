"""Tests for pure Dreame room dispatch planning."""

import pytest

from custom_components.ha_dreame.const import DREAME_VACUUM_DOMAIN
from custom_components.ha_dreame.dispatch_plan import (
    DispatchServiceCall,
    build_room_dispatch_plan,
)
from custom_components.ha_dreame.queue_core import InvalidOperation, QueueItem


def test_build_room_dispatch_plan_returns_clean_segment_call() -> None:
    """Test a basic queue item plans exactly one segment clean command."""
    item = QueueItem(item_id="item-1", room_id=7, room_name="Room 7")

    plan = build_room_dispatch_plan(item, vacuum_entity_id="vacuum.robot")

    assert plan.item_id == "item-1"
    assert plan.room_id == 7
    assert plan.room_name == "Room 7"
    assert plan.effective_overrides == {}
    assert plan.service_calls == (
        DispatchServiceCall(
            domain=DREAME_VACUUM_DOMAIN,
            service="vacuum_clean_segment",
            data={
                "entity_id": "vacuum.robot",
                "segments": [7],
            },
        ),
    )


@pytest.mark.parametrize(
    ("overrides", "expected_payload"),
    [
        pytest.param(
            {"cleaning_mode": 0, "suction_level": 3, "water_volume": 2},
            {"suction_level": 3},
            id="vacuum-only",
        ),
        pytest.param(
            {"cleaning_mode": 1, "suction_level": 3, "water_volume": 2},
            {"water_volume": 2},
            id="mop-only",
        ),
        pytest.param(
            {
                "cleaning_mode": 2,
                "repeats": 2,
                "suction_level": 1,
                "water_volume": 3,
            },
            {"repeats": 2, "suction_level": 1, "water_volume": 3},
            id="combined",
        ),
    ],
)
def test_build_room_dispatch_plan_applies_profile_payloads(
    overrides: dict[str, object],
    expected_payload: dict[str, object],
) -> None:
    """Test profile derivation controls segment clean payload fields."""
    item = QueueItem(
        item_id="item-1",
        room_id=7,
        room_name="Room 7",
        overrides=overrides,
    )

    plan = build_room_dispatch_plan(item, vacuum_entity_id="vacuum.robot")

    assert plan.service_calls == (
        DispatchServiceCall(
            domain=DREAME_VACUUM_DOMAIN,
            service="vacuum_clean_segment",
            data={
                "entity_id": "vacuum.robot",
                "segments": [7],
                **expected_payload,
            },
        ),
    )


def test_build_room_dispatch_plan_adds_advanced_custom_cleaning_call() -> None:
    """Test advanced overrides plan a custom-cleaning call before dispatch."""
    item = QueueItem(
        item_id="item-1",
        room_id=7,
        room_name="Room 7",
        overrides={
            "custom_mopping_route": 4,
            "mop_pressure": 2,
            "repeats": 2,
            "suction_level": 3,
            "water_volume": 2,
        },
    )

    plan = build_room_dispatch_plan(item, vacuum_entity_id="vacuum.robot")

    assert plan.service_calls == (
        DispatchServiceCall(
            domain=DREAME_VACUUM_DOMAIN,
            service="vacuum_set_custom_cleaning",
            data={
                "custom_mopping_route": [4],
                "entity_id": "vacuum.robot",
                "mop_pressure": [2],
                "repeats": [2],
                "segment_id": [7],
                "suction_level": [3],
                "water_volume": [2],
            },
        ),
        DispatchServiceCall(
            domain=DREAME_VACUUM_DOMAIN,
            service="vacuum_clean_segment",
            data={
                "entity_id": "vacuum.robot",
                "repeats": 2,
                "segments": [7],
                "suction_level": 3,
                "water_volume": 2,
            },
        ),
    )


def test_build_room_dispatch_plan_requires_repeats_for_advanced_overrides() -> None:
    """Test advanced custom-cleaning overrides require explicit repeats."""
    item = QueueItem(
        item_id="item-1",
        room_id=7,
        room_name="Room 7",
        overrides={"cleaning_route": 3},
    )

    with pytest.raises(InvalidOperation, match="Advanced overrides require repeats"):
        build_room_dispatch_plan(item, vacuum_entity_id="vacuum.robot")


def test_build_room_dispatch_plan_skips_advanced_call_on_retry() -> None:
    """Test retry dispatch does not re-plan custom cleaning updates."""
    item = QueueItem(
        item_id="item-1",
        room_id=7,
        room_name="Room 7",
        overrides={
            "cleaning_route": 3,
            "repeats": 2,
            "suction_level": 3,
            "water_volume": 2,
        },
    )

    plan = build_room_dispatch_plan(
        item,
        vacuum_entity_id="vacuum.robot",
        retry_count=1,
    )

    assert plan.service_calls == (
        DispatchServiceCall(
            domain=DREAME_VACUUM_DOMAIN,
            service="vacuum_clean_segment",
            data={
                "entity_id": "vacuum.robot",
                "repeats": 2,
                "segments": [7],
                "suction_level": 3,
                "water_volume": 2,
            },
        ),
    )


def test_build_room_dispatch_plan_rejects_invalid_profiles() -> None:
    """Test impossible override combinations become queue operation errors."""
    item = QueueItem(
        item_id="item-1",
        room_id=7,
        room_name="Room 7",
        overrides={"suction_level": -1, "water_volume": 0},
    )

    with pytest.raises(InvalidOperation, match="Both suction and moisture are disabled"):
        build_room_dispatch_plan(item, vacuum_entity_id="vacuum.robot")

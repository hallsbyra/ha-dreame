"""Tests for pure cleaning profile derivation."""

import pytest

from custom_components.ha_dreame.profile_core import (
    InvalidProfile,
    derive_cleaning_profile,
)


def test_water_off_derives_vacuum_mode() -> None:
    """Test disabled water derives vacuum-only dispatch values."""
    profile = derive_cleaning_profile(
        {
            "cleaning_mode": 2,
            "suction_level": 2,
            "water_volume": 0,
        }
    )

    assert profile.cleaning_mode == 0
    assert profile.dispatch_suction_level == 2
    assert profile.dispatch_water_volume is None
    assert profile.custom_suction_level == 2
    assert profile.custom_water_volume == 1


def test_suction_off_derives_mop_mode() -> None:
    """Test disabled suction derives mop-only dispatch values."""
    profile = derive_cleaning_profile(
        {
            "cleaning_mode": 2,
            "suction_level": -1,
            "water_volume": 2,
        }
    )

    assert profile.cleaning_mode == 1
    assert profile.dispatch_suction_level is None
    assert profile.dispatch_water_volume == 2
    assert profile.custom_suction_level == 0
    assert profile.custom_water_volume == 2


def test_both_active_derives_combined_mode() -> None:
    """Test active suction and water derive combined cleaning mode by default."""
    profile = derive_cleaning_profile(
        {
            "suction_level": 1,
            "water_volume": 3,
        }
    )

    assert profile.cleaning_mode == 2
    assert profile.dispatch_suction_level == 1
    assert profile.dispatch_water_volume == 3


def test_explicit_vacuum_mode_disables_water_dispatch() -> None:
    """Test explicit vacuum-only mode suppresses water dispatch."""
    profile = derive_cleaning_profile(
        {
            "cleaning_mode": 0,
            "suction_level": 2,
            "water_volume": 3,
        }
    )

    assert profile.cleaning_mode == 0
    assert profile.runtime_suction_level == 2
    assert profile.runtime_water_volume is None
    assert profile.dispatch_suction_level == 2
    assert profile.dispatch_water_volume is None
    assert profile.custom_suction_level == 2
    assert profile.custom_water_volume == 1


def test_suction_only_derives_vacuum_mode() -> None:
    """Test suction without water derives vacuum-only mode."""
    profile = derive_cleaning_profile({"suction_level": 2})

    assert profile.cleaning_mode == 0
    assert profile.dispatch_suction_level == 2
    assert profile.dispatch_water_volume is None


def test_water_only_derives_mop_mode() -> None:
    """Test water without suction derives mop-only mode."""
    profile = derive_cleaning_profile({"water_volume": 2})

    assert profile.cleaning_mode == 1
    assert profile.dispatch_suction_level is None
    assert profile.dispatch_water_volume == 2


def test_missing_overrides_default_to_combined_mode() -> None:
    """Test empty overrides preserve the combined-mode default."""
    profile = derive_cleaning_profile({})

    assert profile.cleaning_mode == 2
    assert profile.dispatch_suction_level is None
    assert profile.dispatch_water_volume is None
    assert profile.custom_suction_level == 0
    assert profile.custom_water_volume == 1


def test_invalid_scalar_values_are_ignored() -> None:
    """Test invalid override scalars are treated as absent values."""
    profile = derive_cleaning_profile(
        {
            "cleaning_mode": "boost",
            "suction_level": "quiet",
            "water_volume": "",
        }
    )

    assert profile.cleaning_mode == 2
    assert profile.dispatch_suction_level is None
    assert profile.dispatch_water_volume is None


def test_both_off_is_invalid() -> None:
    """Test disabling suction and water rejects an impossible profile."""
    with pytest.raises(InvalidProfile):
        derive_cleaning_profile(
            {
                "suction_level": -1,
                "water_volume": 0,
            }
        )

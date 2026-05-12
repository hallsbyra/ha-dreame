"""Shared test fixtures for HA Dreame."""

from collections.abc import Generator

import pytest

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockModule, mock_integration

pytest_plugins = "pytest_homeassistant_custom_component"

DREAME_VACUUM_DOMAIN = "dreame_vacuum"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> Generator[None]:
    """Allow Home Assistant to load integrations from custom_components."""
    yield


async def _async_setup_dreame_vacuum_dependency(
    hass: HomeAssistant,
    config: dict,
) -> bool:
    """Set up the mocked legacy Dreame dependency."""
    return True


@pytest.fixture
def mock_dreame_vacuum_dependency(hass: HomeAssistant) -> None:
    """Register the legacy Dreame integration dependency for HA load tests."""
    mock_integration(
        hass,
        MockModule(
            DREAME_VACUUM_DOMAIN,
            async_setup=_async_setup_dreame_vacuum_dependency,
        ),
    )

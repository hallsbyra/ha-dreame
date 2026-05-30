"""Tests for HA Dreame frontend card packaging."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from custom_components.ha_dreame import (
    FRONTEND_CARD_FILENAME,
    FRONTEND_STATIC_PATH,
    FRONTEND_STATIC_URL_PATH,
    async_setup,
)


def test_frontend_card_asset_is_packaged_inside_integration() -> None:
    """Test the custom card bundle is shipped inside the HACS integration path."""
    assert (FRONTEND_STATIC_PATH / FRONTEND_CARD_FILENAME).is_file()


async def test_async_setup_registers_frontend_static_path(
    hass: HomeAssistant,
    monkeypatch,
    ) -> None:
    """Test setup serves the packaged card bundle from a namespaced static URL."""
    register_static_paths = AsyncMock()
    monkeypatch.setattr(
        hass,
        "http",
        SimpleNamespace(async_register_static_paths=register_static_paths),
    )

    assert await async_setup(hass, {})

    register_static_paths.assert_awaited_once_with(
        [
            StaticPathConfig(
                FRONTEND_STATIC_URL_PATH,
                str(FRONTEND_STATIC_PATH),
                False,
            )
        ]
    )

"""Tests for the HA Dreame config flow."""

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.ha_dreame.const import DOMAIN, TITLE


async def test_user_flow_creates_entry(hass: HomeAssistant) -> None:
    """Test the initial user flow creates the integration entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] is None

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == TITLE
    assert result["data"] == {}


async def test_user_flow_aborts_when_already_configured(hass: HomeAssistant) -> None:
    """Test the config flow allows only one entry while the scaffold has no options."""
    first_result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    first_result = await hass.config_entries.flow.async_configure(first_result["flow_id"], {})

    assert first_result["type"] is FlowResultType.CREATE_ENTRY

    second_result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    second_result = await hass.config_entries.flow.async_configure(second_result["flow_id"], {})

    assert second_result["type"] is FlowResultType.ABORT
    assert second_result["reason"] == "already_configured"

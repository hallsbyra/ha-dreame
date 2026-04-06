"""Config flow for HA Dreame."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, TITLE


class HaDreameConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the scaffold integration."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=f"{TITLE} (Scaffold)", data={})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )

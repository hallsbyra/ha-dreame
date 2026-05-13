"""Config flow for HA Dreame."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import entity_registry as er, selector

from .const import (
    CONF_ALLOW_ROBOT_COMMANDS,
    CONF_VACUUM_ENTITY_ID,
    DOMAIN,
    DREAME_VACUUM_DOMAIN,
    VACUUM_DOMAIN,
)


class HaDreameConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HA Dreame."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return HaDreameOptionsFlow(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            vacuum_entity_id = user_input[CONF_VACUUM_ENTITY_ID]
            errors = self._validate_vacuum_entity(vacuum_entity_id)

            if not errors:
                await self.async_set_unique_id(vacuum_entity_id)
                self._abort_if_unique_id_configured()

                state = self.hass.states.get(vacuum_entity_id)
                title = state.attributes.get("friendly_name") if state else None
                return self.async_create_entry(
                    title=title or vacuum_entity_id,
                    data={CONF_VACUUM_ENTITY_ID: vacuum_entity_id},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_VACUUM_ENTITY_ID): selector.EntitySelector()}
            ),
            errors=errors or None,
        )

    def _validate_vacuum_entity(self, entity_id: str) -> dict[str, str]:
        """Validate that the selected entity is a Dreame vacuum."""
        state = self.hass.states.get(entity_id)

        if state is None:
            return {CONF_VACUUM_ENTITY_ID: "entity_not_found"}

        domain = entity_id.split(".", maxsplit=1)[0]
        if domain != VACUUM_DOMAIN:
            return {CONF_VACUUM_ENTITY_ID: "not_vacuum"}

        registry_entry = er.async_get(self.hass).async_get(entity_id)
        if registry_entry is None or registry_entry.platform != DREAME_VACUUM_DOMAIN:
            return {CONF_VACUUM_ENTITY_ID: "not_dreame_vacuum"}

        return {}


class HaDreameOptionsFlow(config_entries.OptionsFlow):
    """Handle HA Dreame options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={CONF_ALLOW_ROBOT_COMMANDS: user_input[CONF_ALLOW_ROBOT_COMMANDS]},
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_ALLOW_ROBOT_COMMANDS,
                        default=self._config_entry.options.get(CONF_ALLOW_ROBOT_COMMANDS, False),
                    ): bool
                }
            ),
        )

# FILE: custom_components/fwcam/config_flow.py
# File-Version: 0.1.0
# CHANGE HISTORY
# v0.1.0 - Initial creation
# COMMIT TITLE: feat(v0.1.0): add config flow skeleton and options flow handler
# COMMIT DESCRIPTION:
# - Added ConfigFlow for initial setup (user step) and OptionsFlowHandler for runtime options.
# - Implemented basic validation and unique id handling.
# - Prepared placeholders for vehicle mapping UI and notify channel defaults.
# FILE DESCRIPTION:
# Grundgerüst für die Integration‑Konfiguration über die Home Assistant UI. Unterstützt initiale Einrichtung und OptionsFlow (globale Defaults).
# DEPENDENCIES:
# Importiert: homeassistant.config_entries, voluptuous (optional), const.py. Wird verwendet von: __init__.py beim Setup.


from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_FUEL_TYPE, CONF_RADIUS, CONF_NOTIFY_CHANNELS, DEFAULT_FUEL_TYPE, DEFAULT_RADIUS, DEFAULT_NOTIFY_CHANNELS

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_FUEL_TYPE, default=DEFAULT_FUEL_TYPE): str,
        vol.Optional(CONF_RADIUS, default=DEFAULT_RADIUS): int,
        vol.Optional(CONF_NOTIFY_CHANNELS, default=DEFAULT_NOTIFY_CHANNELS): list,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for FWCAM."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)

        # Basic validation placeholder
        # TODO: validate provider API keys if any, validate notify channels
        unique_id = "fwcam_default"  # For single-instance integrations; change if multi-instance supported
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        title = "Fuel Watcher Car Advanced Manager"
        data = {
            CONF_FUEL_TYPE: user_input.get(CONF_FUEL_TYPE, DEFAULT_FUEL_TYPE),
            CONF_RADIUS: user_input.get(CONF_RADIUS, DEFAULT_RADIUS),
            CONF_NOTIFY_CHANNELS: user_input.get(CONF_NOTIFY_CHANNELS, DEFAULT_NOTIFY_CHANNELS),
        }

        return self.async_create_entry(title=title, data=data)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return options flow handler for this integration."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle FWCAM options."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is None:
            current = self.config_entry.options or {}
            schema = vol.Schema(
                {
                    vol.Optional(CONF_FUEL_TYPE, default=current.get(CONF_FUEL_TYPE, DEFAULT_FUEL_TYPE)): str,
                    vol.Optional(CONF_RADIUS, default=current.get(CONF_RADIUS, DEFAULT_RADIUS)): int,
                    vol.Optional(CONF_NOTIFY_CHANNELS, default=current.get(CONF_NOTIFY_CHANNELS, DEFAULT_NOTIFY_CHANNELS)): list,
                }
            )
            return self.async_show_form(step_id="init", data_schema=schema)

        # Save options
        return self.async_create_entry(title="", data=user_input)

# TODO:
# - Add vehicle/device flow for per-vehicle mapping (entity_id_km, entity_id_fuel_level, entity_id_location)
# - Add validation against HA entity registry (check existence of provided entity_ids)
# - Add provider API key step if external providers require authentication

# FILE: custom_components/fwcam/config_flow.py
# File-Version: 0.1.1
# CHANGE HISTORY
# v0.1.0 - Initial creation
# v0.1.1 - Import-safe minimal config flow with logging

from __future__ import annotations

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

_LOGGER = logging.getLogger(__name__)

DOMAIN = "fwcam"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Minimal, import-safe ConfigFlow for FWCAM."""

    VERSION = 1
    # CONNECTION_CLASS intentionally omitted at module level to avoid import-time side effects.

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step. Minimal implementation to avoid import-time issues."""
        try:
            if user_input is None:
                # Show a minimal empty form to avoid importing voluptuous at module import time.
                return self.async_show_form(step_id="user", data_schema={})

            # Basic unique id handling for single-instance integration.
            await self.async_set_unique_id("fwcam_default")
            self._abort_if_unique_id_configured()

            # Save provided user_input as config entry data (validation added later).
            return self.async_create_entry(title="Fuel Watcher Car Advanced Manager", data=user_input or {})
        except Exception as exc:  # pylint: disable=broad-except
            _LOGGER.exception("Error in FWCAM config flow step_user: %s", exc)
            # Use a generic abort reason; logs contain the traceback for debugging.
            return self.async_abort(reason="unknown")

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return options flow handler for this integration."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle FWCAM options in a safe, minimal way."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options. Minimal form to avoid heavy imports at module load."""
        try:
            if user_input is None:
                # Provide an empty form; real schema will be added later.
                return self.async_show_form(step_id="init", data_schema={})
            return self.async_create_entry(title="", data=user_input)
        except Exception as exc:  # pylint: disable=broad-except
            _LOGGER.exception("Error in FWCAM options flow: %s", exc)
            return self.async_abort(reason="unknown")

# FILE: custom_components/fwcam/config_flow.py
# COMMIT TITLE: fix(v0.1.2): provide robust, import-safe config flow with runtime validation
# COMMIT DESCRIPTION:
# - Added an import-safe ConfigFlow implementation that avoids heavy imports at module load.
# - Builds voluptuous schemas at runtime inside steps to prevent import-time failures.
# - Adds detailed debug logging and defensive exception handling to make errors visible in logs.
# - Implements OptionsFlowHandler for runtime options with safe schema construction.
# FILE DESCRIPTION:
#   Config flow and options flow for the FWCAM integration. Designed to be safe to import
#   by Home Assistant (no side effects at module import time) and to provide clear logging
#   for debugging. Validation and optional imports (voluptuous) are performed inside flow
#   methods to avoid ImportError or other exceptions during HA startup.
# DEPENDENCIES:
#   - homeassistant.config_entries
#   - homeassistant.data_entry_flow.FlowResult
#   - runtime import of voluptuous (vol) inside flow methods
#   - runtime import of .const for default values
#   Used by: __init__.py during setup; safe to import at HA startup.

from __future__ import annotations

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

_LOGGER = logging.getLogger(__name__)

DOMAIN = "fwcam"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Fuel Watcher Car Advanced Manager (FWCAM).

    This implementation is intentionally import-safe:
    - Avoids heavy or optional imports at module level.
    - Builds validation schemas inside async steps.
    - Logs exceptions with full tracebacks for easier debugging.
    """

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial configuration step (user)."""
        _LOGGER.debug("FWCAM config_flow: async_step_user called with input: %s", user_input)
        try:
            # Import defaults and voluptuous at runtime to avoid import-time failures.
            from .const import (
                CONF_FUEL_TYPE,
                CONF_RADIUS,
                CONF_NOTIFY_CHANNELS,
                DEFAULT_FUEL_TYPE,
                DEFAULT_RADIUS,
                DEFAULT_NOTIFY_CHANNELS,
            )
            import voluptuous as vol

            schema = vol.Schema(
                {
                    vol.Optional(CONF_FUEL_TYPE, default=DEFAULT_FUEL_TYPE): str,
                    vol.Optional(CONF_RADIUS, default=DEFAULT_RADIUS): int,
                    vol.Optional(CONF_NOTIFY_CHANNELS, default=DEFAULT_NOTIFY_CHANNELS): list,
                }
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            _LOGGER.exception("FWCAM config_flow: failed to build schema: %s", exc)
            # Abort with a generic reason; logs contain the traceback.
            return self.async_abort(reason="unknown")

        try:
            if user_input is None:
                return self.async_show_form(step_id="user", data_schema=schema)

            # Basic unique id handling for single-instance integration.
            await self.async_set_unique_id("fwcam_default")
            self._abort_if_unique_id_configured()

            # Persist the provided configuration (validation already applied by voluptuous)
            data = {
                CONF_FUEL_TYPE: user_input.get(CONF_FUEL_TYPE),
                CONF_RADIUS: user_input.get(CONF_RADIUS),
                CONF_NOTIFY_CHANNELS: user_input.get(CONF_NOTIFY_CHANNELS),
            }

            _LOGGER.debug("FWCAM config_flow: creating entry with data: %s", data)
            return self.async_create_entry(title="Fuel Watcher Car Advanced Manager", data=data)
        except Exception as exc:  # pragma: no cover - defensive logging
            _LOGGER.exception("FWCAM config_flow: unexpected error in async_step_user: %s", exc)
            return self.async_abort(reason="unknown")

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return options flow handler for this integration."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for FWCAM (safe, minimal)."""

    def __init__(self, config_entry):
        self.config_entry = config_entry
        _LOGGER.debug("FWCAM options flow initialized for entry_id=%s", getattr(config_entry, "entry_id", None))

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options. Build schema at runtime to avoid import-time issues."""
        _LOGGER.debug("FWCAM options flow: async_step_init called with input: %s", user_input)
        try:
            from .const import (
                CONF_FUEL_TYPE,
                CONF_RADIUS,
                CONF_NOTIFY_CHANNELS,
                DEFAULT_FUEL_TYPE,
                DEFAULT_RADIUS,
                DEFAULT_NOTIFY_CHANNELS,
            )
            import voluptuous as vol

            current = self.config_entry.options or {}
            schema = vol.Schema(
                {
                    vol.Optional(CONF_FUEL_TYPE, default=current.get(CONF_FUEL_TYPE, DEFAULT_FUEL_TYPE)): str,
                    vol.Optional(CONF_RADIUS, default=current.get(CONF_RADIUS, DEFAULT_RADIUS)): int,
                    vol.Optional(CONF_NOTIFY_CHANNELS, default=current.get(CONF_NOTIFY_CHANNELS, DEFAULT_NOTIFY_CHANNELS)): list,
                }
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            _LOGGER.exception("FWCAM options flow: failed to build schema: %s", exc)
            return self.async_abort(reason="unknown")

        try:
            if user_input is None:
                return self.async_show_form(step_id="init", data_schema=schema)

            _LOGGER.debug("FWCAM options flow: saving options: %s", user_input)
            return self.async_create_entry(title="", data=user_input)
        except Exception as exc:  # pragma: no cover - defensive logging
            _LOGGER.exception("FWCAM options flow: unexpected error while saving options: %s", exc)
            return self.async_abort(reason="unknown")

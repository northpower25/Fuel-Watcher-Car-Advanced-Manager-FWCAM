# FILE: custom_components/fwcam/config_flow.py
# COMMIT TITLE: fix(v0.1.3): add validated config form and safe schema construction
# COMMIT DESCRIPTION:
# - Provide a user-visible config form that collects required GPS and radius values.
# - Build voluptuous schemas at runtime and use hass.config defaults when available.
# - Persist validated data into the config entry so async_setup_entry receives required values.
# - Defensive logging and clear aborts on unexpected errors.
# FILE DESCRIPTION:
#   ConfigFlow for FWCAM: shows a form for latitude, longitude, radius, fuel type and notify channels.
#   Designed to be import-safe and to validate required fields before creating the entry.
# DEPENDENCIES:
#   - runtime import of voluptuous (vol) inside flow methods
#   - homeassistant.config_entries
#   - homeassistant.const for CONF_* constants
#   Used by: __init__.py during setup

from __future__ import annotations

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

_LOGGER = logging.getLogger(__name__)

DOMAIN = "fwcam"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Fuel Watcher Car Advanced Manager (FWCAM)."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step: show form and create entry with validated data."""
        _LOGGER.debug("FWCAM config_flow: async_step_user called with input: %s", user_input)

        try:
            # Import runtime-only dependencies and constants
            from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_RADIUS
            from .const import (
                CONF_FUEL_TYPE,
                CONF_NOTIFY_CHANNELS,
                DEFAULT_FUEL_TYPE,
                DEFAULT_RADIUS,
                DEFAULT_NOTIFY_CHANNELS,
            )
            import voluptuous as vol
        except Exception as exc:  # pragma: no cover - defensive
            _LOGGER.exception("FWCAM config_flow: failed to import runtime dependencies: %s", exc)
            return self.async_abort(reason="unknown")

        # Build schema using hass defaults where available
        try:
            default_lat = float(self.hass.config.latitude) if self.hass.config.latitude is not None else None
            default_lon = float(self.hass.config.longitude) if self.hass.config.longitude is not None else None
        except Exception:
            default_lat = None
            default_lon = None

        schema = vol.Schema(
            {
                vol.Required(CONF_LATITUDE, default=default_lat): float,
                vol.Required(CONF_LONGITUDE, default=default_lon): float,
                vol.Optional(CONF_RADIUS, default=DEFAULT_RADIUS): int,
                vol.Optional(CONF_FUEL_TYPE, default=DEFAULT_FUEL_TYPE): str,
                vol.Optional(CONF_NOTIFY_CHANNELS, default=DEFAULT_NOTIFY_CHANNELS): list,
            }
        )

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=schema)

        # Validate minimal sanity checks
        errors: dict[str, str] = {}
        lat = user_input.get(CONF_LATITUDE)
        lon = user_input.get(CONF_LONGITUDE)
        if lat is None or lon is None:
            errors["base"] = "missing_coordinates"
            return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

        # Unique id for single-instance integration
        try:
            await self.async_set_unique_id("fwcam_default")
            self._abort_if_unique_id_configured()
        except Exception:
            _LOGGER.debug("FWCAM config_flow: unique id handling failed or already configured")

        # Persist validated data
        entry_data = {
            CONF_LATITUDE: float(lat),
            CONF_LONGITUDE: float(lon),
            CONF_RADIUS: int(user_input.get(CONF_RADIUS, DEFAULT_RADIUS)),
            CONF_FUEL_TYPE: user_input.get(CONF_FUEL_TYPE, DEFAULT_FUEL_TYPE),
            CONF_NOTIFY_CHANNELS: user_input.get(CONF_NOTIFY_CHANNELS, DEFAULT_NOTIFY_CHANNELS),
        }

        _LOGGER.debug("FWCAM config_flow: creating entry with data: %s", entry_data)
        return self.async_create_entry(title="Fuel Watcher Car Advanced Manager", data=entry_data)

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
            from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_RADIUS
            from .const import (
                CONF_FUEL_TYPE,
                CONF_NOTIFY_CHANNELS,
                DEFAULT_FUEL_TYPE,
                DEFAULT_RADIUS,
                DEFAULT_NOTIFY_CHANNELS,
            )
            import voluptuous as vol
        except Exception as exc:  # pragma: no cover - defensive
            _LOGGER.exception("FWCAM options flow: failed to import runtime dependencies: %s", exc)
            return self.async_abort(reason="unknown")

        current = self.config_entry.options or {}
        schema = vol.Schema(
            {
                vol.Optional(CONF_LATITUDE, default=current.get(CONF_LATITUDE, self.config_entry.data.get(CONF_LATITUDE))): float,
                vol.Optional(CONF_LONGITUDE, default=current.get(CONF_LONGITUDE, self.config_entry.data.get(CONF_LONGITUDE))): float,
                vol.Optional(CONF_RADIUS, default=current.get(CONF_RADIUS, self.config_entry.data.get(CONF_RADIUS, DEFAULT_RADIUS))): int,
                vol.Optional(CONF_FUEL_TYPE, default=current.get(CONF_FUEL_TYPE, self.config_entry.data.get(CONF_FUEL_TYPE, DEFAULT_FUEL_TYPE))): str,
                vol.Optional(CONF_NOTIFY_CHANNELS, default=current.get(CONF_NOTIFY_CHANNELS, self.config_entry.data.get(CONF_NOTIFY_CHANNELS, DEFAULT_NOTIFY_CHANNELS))): list,
            }
        )

        if user_input is None:
            return self.async_show_form(step_id="init", data_schema=schema)

        _LOGGER.debug("FWCAM options flow: saving options: %s", user_input)
        return self.async_create_entry(title="", data=user_input)

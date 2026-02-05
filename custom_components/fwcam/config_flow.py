# FILE: custom_components/fwcam/config_flow.py

#COMMIT TITLE: fix(v0.1.4): validated config form and safe runtime imports
#COMMIT DESCRIPTION:
#- Show a user form collecting latitude, longitude and radius (with hass defaults).
#- Build voluptuous schemas at runtime to avoid import-time failures.
#- Persist validated data into the config entry.
#- Defensive logging and clear aborts on unexpected errors. 
# FILE DESCRIPTION: ConfigFlow for FWCAM: collects required coordinates and options, validates input and creates a config entry safe for async_setup_entry. 
# DEPENDENCIES:
#- runtime import of voluptuous inside flow methods
#- homeassistant.config_entries and homeassistant.const
#- uses .const for default keys

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
        _LOGGER.debug("FWCAM config_flow: async_step_user called with input: %s", user_input)
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
        except Exception as exc:
            _LOGGER.exception("FWCAM config_flow: failed to import runtime dependencies: %s", exc)
            return self.async_abort(reason="unknown")

        try:
            default_lat = float(self.hass.config.latitude) if self.hass.config.latitude is not None else None
            default_lon = float(self.hass.config.longitude) if self.hass.config.longitude is not None else None
        except Exception:
            default_lat = None
            default_lon = None

        schema = vol.Schema(
            {
                vol.Optional(CONF_LATITUDE, default=default_lat): vol.Coerce(float),
                vol.Optional(CONF_LONGITUDE, default=default_lon): vol.Coerce(float),
                vol.Optional(CONF_RADIUS, default=DEFAULT_RADIUS): vol.Coerce(int),
                vol.Optional(CONF_FUEL_TYPE, default=DEFAULT_FUEL_TYPE): str,
                vol.Optional(CONF_NOTIFY_CHANNELS, default=DEFAULT_NOTIFY_CHANNELS): list,
            }
        )

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=schema)

        errors: dict[str, str] = {}
        lat = user_input.get(CONF_LATITUDE)
        lon = user_input.get(CONF_LONGITUDE)
        
        if lat is None or lon is None:
            errors["base"] = "missing_coordinates"
            return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
        
        try:
            lat = float(lat)
            lon = float(lon)
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                errors["base"] = "invalid_coordinates"
                return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
        except (ValueError, TypeError):
            errors["base"] = "invalid_coordinates"
            return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

        try:
            await self.async_set_unique_id("fwcam_default")
            self._abort_if_unique_id_configured()
        except Exception as exc:
            _LOGGER.debug("FWCAM config_flow: unique id check exception: %s", exc)
            return self.async_abort(reason="already_configured")

        entry_data = {
            CONF_LATITUDE: lat,
            CONF_LONGITUDE: lon,
            CONF_RADIUS: int(user_input.get(CONF_RADIUS, DEFAULT_RADIUS)),
            CONF_FUEL_TYPE: user_input.get(CONF_FUEL_TYPE, DEFAULT_FUEL_TYPE),
            CONF_NOTIFY_CHANNELS: user_input.get(CONF_NOTIFY_CHANNELS, DEFAULT_NOTIFY_CHANNELS),
        }

        _LOGGER.debug("FWCAM config_flow: creating entry with data: %s", entry_data)
        return self.async_create_entry(title="Fuel Watcher Car Advanced Manager", data=entry_data)

    @staticmethod
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry
        _LOGGER.debug("FWCAM options flow initialized for entry_id=%s", getattr(config_entry, "entry_id", None))

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
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
        except Exception as exc:
            _LOGGER.exception("FWCAM options flow: failed to import runtime dependencies: %s", exc)
            return self.async_abort(reason="unknown")

        current = self.config_entry.options or {}
        schema = vol.Schema(
            {
                vol.Optional(CONF_LATITUDE, default=current.get(CONF_LATITUDE, self.config_entry.data.get(CONF_LATITUDE))): vol.Coerce(float),
                vol.Optional(CONF_LONGITUDE, default=current.get(CONF_LONGITUDE, self.config_entry.data.get(CONF_LONGITUDE))): vol.Coerce(float),
                vol.Optional(CONF_RADIUS, default=current.get(CONF_RADIUS, self.config_entry.data.get(CONF_RADIUS, DEFAULT_RADIUS))): vol.Coerce(int),
                vol.Optional(CONF_FUEL_TYPE, default=current.get(CONF_FUEL_TYPE, self.config_entry.data.get(CONF_FUEL_TYPE, DEFAULT_FUEL_TYPE))): str,
                vol.Optional(CONF_NOTIFY_CHANNELS, default=current.get(CONF_NOTIFY_CHANNELS, self.config_entry.data.get(CONF_NOTIFY_CHANNELS, DEFAULT_NOTIFY_CHANNELS))): list,
            }
        )

        if user_input is None:
            return self.async_show_form(step_id="init", data_schema=schema)

        _LOGGER.debug("FWCAM options flow: saving options: %s", user_input)
        return self.async_create_entry(title="", data=user_input)

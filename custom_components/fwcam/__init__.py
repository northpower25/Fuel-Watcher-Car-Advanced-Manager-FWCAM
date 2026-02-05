# FILE: custom_components/fwcam/__init__.py
# COMMIT TITLE: fix(v0.1.3): validate config entry data and fail gracefully on missing values
# COMMIT DESCRIPTION:
# - Validate required config entry fields (latitude, longitude, radius) before creating coordinator.
# - Use hass.config defaults when entry data is missing.
# - Log clear errors and return False instead of raising unhandled exceptions.
# - Keep robust unload handling.
# FILE DESCRIPTION:
#   Integration bootstrap: validates config entry data, creates and registers the DataUpdateCoordinator,
#   forwards platform setup (sensors) and handles unload.
# DEPENDENCIES:
#   Imports: coordinator.FwcamDataUpdateCoordinator, const.DOMAIN, homeassistant.const CONF_*
#   Used by: sensors, providers, config_flow

from __future__ import annotations

import logging
from typing import Final

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_LATITUDE, CONF_LONGITUDE, CONF_RADIUS

from .const import DOMAIN
from .coordinator import FwcamDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: Final = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration via YAML (not supported)."""
    _LOGGER.debug("FWCAM async_setup called (YAML not supported).")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up FWCAM from a config entry with defensive validation."""
    _LOGGER.info("Setting up FWCAM integration (entry_id=%s)", entry.entry_id)
    try:
        # Ensure hass.data structure
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN].setdefault(entry.entry_id, {})

        # Read required values with sensible defaults
        latitude = entry.data.get(CONF_LATITUDE, hass.config.latitude)
        longitude = entry.data.get(CONF_LONGITUDE, hass.config.longitude)
        radius = entry.data.get(CONF_RADIUS, 5)

        # Validate presence of coordinates
        if latitude is None or longitude is None:
            _LOGGER.error(
                "FWCAM async_setup_entry: missing coordinates in config entry (entry_id=%s). "
                "Please reconfigure the integration and provide latitude/longitude.",
                entry.entry_id,
            )
            return False

        # Normalize types
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            radius = int(radius)
        except Exception:
            _LOGGER.exception("FWCAM async_setup_entry: invalid types for latitude/longitude/radius")
            return False

        # Store validated config values for later use by coordinator/providers
        hass.data[DOMAIN][entry.entry_id]["config"] = {
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius,
            **{k: v for k, v in entry.data.items() if k not in (CONF_LATITUDE, CONF_LONGITUDE, CONF_RADIUS)},
        }

        # Create and store coordinator
        coordinator = FwcamDataUpdateCoordinator(hass, entry)
        hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator

        # Start initial refresh (coordinator is robust and returns placeholder snapshot)
        await coordinator.async_config_entry_first_refresh()

        # Forward setup to platforms (sensors)
        for platform in PLATFORMS:
            hass.async_create_task(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )

        _LOGGER.debug("FWCAM coordinator registered and platforms forwarded.")
        return True
    except Exception as exc:  # pylint: disable=broad-except
        _LOGGER.exception("FWCAM async_setup_entry failed: %s", exc)
        # Return False so HA treats setup as failed without an unhandled 500
        return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading FWCAM integration (entry_id=%s)", entry.entry_id)

    results = []
    for platform in PLATFORMS:
        try:
            res = await hass.config_entries.async_forward_entry_unload(entry, platform)
            results.append(bool(res))
        except Exception:
            _LOGGER.exception("Error unloading platform %s for entry %s", platform, entry.entry_id)
            results.append(False)

    unload_ok = all(results)

    # Cleanup coordinator and stored data
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)

    _LOGGER.debug("FWCAM unloaded (entry_id=%s) unload_ok=%s", entry.entry_id, unload_ok)
    return unload_ok

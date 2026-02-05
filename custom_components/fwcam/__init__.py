# FILE: custom_components/fwcam/__init__.py
#COMMIT TITLE: fix(v0.1.4): validate config entry and fail gracefully
#COMMIT DESCRIPTION:
#- Validate required config entry fields (latitude, longitude, radius) before creating coordinator.
#- Use hass.config defaults when entry data is missing.
#- Log clear errors and return False instead of raising unhandled exceptions.
#- Robust unload handling. 
#FILE DESCRIPTION: Integration bootstrap: validates config entry data, creates and registers the DataUpdateCoordinator, forwards platform setup and handles unload. 
#DEPENDENCIES:
#- imports: homeassistant.const CONF_*, coordinator.FwcamDataUpdateCoordinator, .const DOMAIN

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
    _LOGGER.debug("FWCAM async_setup called (YAML not supported).")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.info("Setting up FWCAM integration (entry_id=%s)", entry.entry_id)
    try:
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN].setdefault(entry.entry_id, {})

        latitude = entry.data.get(CONF_LATITUDE, hass.config.latitude)
        longitude = entry.data.get(CONF_LONGITUDE, hass.config.longitude)
        radius = entry.data.get(CONF_RADIUS, 5)

        if latitude is None or longitude is None:
            _LOGGER.error(
                "FWCAM async_setup_entry: missing coordinates in config entry (entry_id=%s). Reconfigure integration.",
                entry.entry_id,
            )
            return False

        try:
            latitude = float(latitude)
            longitude = float(longitude)
            radius = int(radius)
        except Exception:
            _LOGGER.exception("FWCAM async_setup_entry: invalid types for latitude/longitude/radius")
            return False

        hass.data[DOMAIN][entry.entry_id]["config"] = {
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius,
            **{k: v for k, v in entry.data.items() if k not in (CONF_LATITUDE, CONF_LONGITUDE, CONF_RADIUS)},
        }

        coordinator = FwcamDataUpdateCoordinator(hass, entry)
        hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator

        await coordinator.async_config_entry_first_refresh()

        for platform in PLATFORMS:
            hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, platform))

        _LOGGER.debug("FWCAM coordinator registered and platforms forwarded.")
        return True
    except Exception as exc:
        _LOGGER.exception("FWCAM async_setup_entry failed: %s", exc)
        return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
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
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    _LOGGER.debug("FWCAM unloaded (entry_id=%s) unload_ok=%s", entry.entry_id, unload_ok)
    return unload_ok

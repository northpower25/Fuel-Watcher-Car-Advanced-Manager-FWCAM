# FILE: custom_components/fwcam/__init__.py
# COMMIT TITLE: feat(v0.1.0): register coordinator and forward sensor platforms
# COMMIT DESCRIPTION:
# - Register FwcamDataUpdateCoordinator during async_setup_entry
# - Store coordinator in hass.data[DOMAIN][entry_id]["coordinator"]
# - Forward setup to sensor platform
# - Added graceful unload logic to unload platforms and cleanup
# FILE DESCRIPTION:
#   Integration bootstrap: creates and registers the DataUpdateCoordinator,
#   forwards platform setup (sensors) and handles unload.
# DEPENDENCIES:
#   Imports: coordinator.FwcamDataUpdateCoordinator, const.DOMAIN
#   Used by: sensors, providers, config_flow

from __future__ import annotations

import logging
from typing import Final

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from .const import DOMAIN
from .coordinator import FwcamDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: Final = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration via YAML (not supported)."""
    _LOGGER.debug("FWCAM async_setup called (YAML not supported).")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up FWCAM from a config entry."""
    _LOGGER.info("Setting up FWCAM integration (entry_id=%s)", entry.entry_id)
    try:
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN].setdefault(entry.entry_id, {})

        # Create and store coordinator
        coordinator = FwcamDataUpdateCoordinator(hass, entry)
        hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator

        # Start initial refresh
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
        raise


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


# TODO:
# - Initialize provider registry and caches here
# - Register services (manual refuel, recalc forecast)
# - Create device entries in device registry for each vehicle
# CHANGE HISTORY
# v0.1.0 - Registered coordinator and platform forwarding

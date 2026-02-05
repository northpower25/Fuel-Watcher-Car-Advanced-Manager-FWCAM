# FILE: custom_components/fwcam/__init__.py
# COMMIT TITLE: feat(v0.1.0): add integration bootstrap and setup logic
# COMMIT DESCRIPTION:
# - Added async_setup and async_setup_entry for FWCAM
# - Registered DataUpdateCoordinator placeholder
# - Added logging and domain initialization
# FILE DESCRIPTION:
#   Entry point for the FWCAM Home Assistant integration.
#   Handles setup, teardown, and registration of core services.
# DEPENDENCIES:
#   Uses: const.py
#   Used by: coordinator.py, sensors, config_flow

from __future__ import annotations

import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# SETUP (YAML — not used, but required by HA)
# ─────────────────────────────────────────────
async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration via YAML (not supported)."""
    _LOGGER.debug("FWCAM async_setup called (YAML not supported).")
    return True

# ─────────────────────────────────────────────
# SETUP ENTRY (Config Flow)
# ─────────────────────────────────────────────
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up FWCAM from a config entry."""
    _LOGGER.info("Setting up FWCAM integration (entry_id=%s)", entry.entry_id)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    # Coordinator will be added in next commit
    _LOGGER.debug("FWCAM initialized without coordinator (placeholder).")

    return True

# ─────────────────────────────────────────────
# UNLOAD ENTRY
# ─────────────────────────────────────────────
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading FWCAM integration (entry_id=%s)", entry.entry_id)

    hass.data[DOMAIN].pop(entry.entry_id, None)

    return True

# ─────────────────────────────────────────────
# TODO / FUTURE WORK
# ─────────────────────────────────────────────
# - Register coordinator
# - Register services
# - Register platform forwarders (sensors)
# - Add cleanup logic for providers

# CHANGE HISTORY
# v0.1.0 - Initial creation

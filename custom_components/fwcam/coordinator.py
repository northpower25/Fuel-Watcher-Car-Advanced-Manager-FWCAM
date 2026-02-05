# FILE: custom_components/fwcam/coordinator.py
# File-Version: 0.1.0
# CHANGE HISTORY
# v0.1.0 - Initial creation
# COMMIT TITLE: feat(v0.1.0): add DataUpdateCoordinator for FWCAM
# COMMIT DESCRIPTION:
# - Added FwcamDataUpdateCoordinator implementing periodic updates and fetch placeholder.
# - Provided helper async_get_coordinator and typed return.
# - Added logging, timeout and basic error handling.
# FILE DESCRIPTION:
# Zentrale DataUpdateCoordinator‑Implementierung für die Integration. Verwaltet periodische Datenabrufe (Provider/Forecast) und stellt die Daten für Sensoren/Services bereit. Enthält Platzhalter für async_fetch_data (Provider‑Adapter/Forecast werden dort angebunden).
# DEPENDENCIES:
# Importiert: homeassistant.helpers.update_coordinator, const.py. Wird verwendet von: __init__.py, sensors/*, providers/*.

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict, Optional

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, EVENT_FORECAST_UPDATED

_LOGGER = logging.getLogger(__name__)

DEFAULT_UPDATE_INTERVAL = timedelta(minutes=5)
FETCH_TIMEOUT = 30  # seconds

class FwcamDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """DataUpdateCoordinator for Fuel Watcher Car Advanced Manager.

    Responsibilities:
    - Periodically call async_fetch_data to gather provider, vehicle and forecast data.
    - Expose the latest snapshot via self.data.
    - Emit events on significant updates (e.g., forecast updated).
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, update_interval: Optional[timedelta] = None) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.entry = entry
        self.logger = _LOGGER
        interval = update_interval or DEFAULT_UPDATE_INTERVAL

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}-{entry.entry_id}",
            update_interval=interval,
        )

        # Internal state container
        self._state: Dict[str, Any] = {
            "vehicles": {},
            "forecasts": {},
            "providers": {},
            "last_update": None,
        }

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from providers and compute forecasts.

        This method is called by the DataUpdateCoordinator on its schedule.
        Implementations should raise UpdateFailed on errors.
        """
        try:
            # Use asyncio.wait_for to bound provider calls
            return await asyncio.wait_for(self.async_fetch_data(), timeout=FETCH_TIMEOUT)
        except asyncio.TimeoutError as err:
            raise UpdateFailed("Timeout while fetching FWCAM data") from err
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected error in coordinator fetch: %s", err)
            raise UpdateFailed(err) from err

    async def async_fetch_data(self) -> Dict[str, Any]:
        """Actual data retrieval logic.

        TODO:
        - Call provider adapters to fetch station/prices
        - Read referenced HA entities (odometer, fuel_level, location)
        - Run Forecast Engine and Refuel Detector
        - Return a snapshot dict with keys: vehicles, forecasts, providers, refuel_events

        This placeholder returns the current internal state to keep sensors functional.
        """
        # Placeholder implementation: return current state
        # Replace with real provider/forecast calls in subsequent commits.
        _LOGGER.debug("FWCAM coordinator: async_fetch_data placeholder called.")
        self._state["last_update"] = self.hass.time()
        # Emit event if forecast changed (placeholder logic)
        # self.hass.bus.async_fire(EVENT_FORECAST_UPDATED, {"entry_id": self.entry.entry_id})
        return self._state

    # Convenience accessor
    @property
    def snapshot(self) -> Dict[str, Any]:
        """Return the latest snapshot of coordinator data."""
        return self.data or self._state


# Helper to retrieve coordinator from hass.data
def async_get_coordinator(hass: HomeAssistant, entry_id: str) -> Optional[FwcamDataUpdateCoordinator]:
    """Return the coordinator instance for a given config entry id, if present."""
    domain_store = hass.data.get(DOMAIN, {})
    return domain_store.get(entry_id, {}).get("coordinator")

# FILE: custom_components/fwcam/coordinator.py
# File-Version: 0.1.1
# CHANGE HISTORY
# v0.1.0 - Initial creation
# v0.1.1 - Avoid hass.time() and harden placeholder fetch
# Imports: homeassistant.helpers.update_coordinator.DataUpdateCoordinator, homeassistant.core.HomeAssistant, homeassistant.config_entries.ConfigEntry
# Used by: __init__.py, sensor‑plattformen, provider‑Adapter


from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

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

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        update_interval: Optional[timedelta] = None,
    ) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.entry = entry
        interval = update_interval or DEFAULT_UPDATE_INTERVAL

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}-{entry.entry_id}",
            update_interval=interval,
        )

        # Internal state container (stable default shape)
        self._state: Dict[str, Any] = {
            "vehicles": {},
            "forecasts": {},
            "providers": {},
            "refuel_events": [],
            "last_update": None,
        }

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from providers and compute forecasts.

        This method is called by the DataUpdateCoordinator on its schedule.
        Implementations should raise UpdateFailed on errors.
        """
        try:
            return await asyncio.wait_for(self.async_fetch_data(), timeout=FETCH_TIMEOUT)
        except asyncio.TimeoutError as err:
            _LOGGER.warning("FWCAM coordinator fetch timed out.")
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
        _LOGGER.debug("FWCAM coordinator: async_fetch_data placeholder called.")

        # Defensive: ensure internal state shape exists
        if not isinstance(self._state, dict):
            self._state = {
                "vehicles": {},
                "forecasts": {},
                "providers": {},
                "refuel_events": [],
                "last_update": None,
            }

        # Update last_update with a safe UTC ISO timestamp (avoid hass.time() usage)
        try:
            self._state["last_update"] = datetime.now(timezone.utc).isoformat()
        except Exception:  # fallback to string representation
            self._state["last_update"] = str(datetime.utcnow())

        # Placeholder: no provider calls yet — return snapshot
        snapshot = {
            "vehicles": self._state.get("vehicles", {}),
            "forecasts": self._state.get("forecasts", {}),
            "providers": self._state.get("providers", {}),
            "refuel_events": self._state.get("refuel_events", []),
            "last_update": self._state.get("last_update"),
        }

        # Emit event if forecast changed — placeholder (no-op for now)
        # self.hass.bus.async_fire(EVENT_FORECAST_UPDATED, {"entry_id": self.entry.entry_id})

        return snapshot

    @property
    def snapshot(self) -> Dict[str, Any]:
        """Return the latest snapshot of coordinator data (always a dict)."""
        return self.data or self._state


def async_get_coordinator(hass: HomeAssistant, entry_id: str) -> Optional[FwcamDataUpdateCoordinator]:
    """Return the coordinator instance for a given config entry id, if present."""
    domain_store = hass.data.get(DOMAIN, {})
    return domain_store.get(entry_id, {}).get("coordinator")

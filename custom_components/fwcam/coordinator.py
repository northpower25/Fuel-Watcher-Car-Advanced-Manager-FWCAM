# FILE: custom_components/fwcam/coordinator.py
# COMMIT TITLE: fix(v0.1.2): ensure coordinator is robust to missing config and returns stable snapshot
# COMMIT DESCRIPTION:
# - Coordinator uses hass.data validated config (if present) and avoids assumptions about entry.data.
# - Placeholder async_fetch_data returns a stable snapshot and safe last_update timestamp.
# - Defensive logging for unexpected errors.
# FILE DESCRIPTION:
#   DataUpdateCoordinator for FWCAM. Periodically fetches data (placeholder) and exposes snapshot.
# DEPENDENCIES:
#   - homeassistant.helpers.update_coordinator.DataUpdateCoordinator
#   - homeassistant.core.HomeAssistant
#   - homeassistant.config_entries.ConfigEntry
#   Used by: __init__.py, sensors

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEFAULT_UPDATE_INTERVAL = timedelta(minutes=5)
FETCH_TIMEOUT = 30  # seconds


class FwcamDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """DataUpdateCoordinator for Fuel Watcher Car Advanced Manager."""

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
        """Fetch data from providers and compute forecasts."""
        try:
            return await asyncio.wait_for(self.async_fetch_data(), timeout=FETCH_TIMEOUT)
        except asyncio.TimeoutError as err:
            _LOGGER.warning("FWCAM coordinator fetch timed out.")
            raise UpdateFailed("Timeout while fetching FWCAM data") from err
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected error in coordinator fetch: %s", err)
            raise UpdateFailed(err) from err

    async def async_fetch_data(self) -> Dict[str, Any]:
        """Actual data retrieval logic (placeholder)."""
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

        # Use validated config if present
        config = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {}).get("config", {})
        self._state.setdefault("config", config)

        # Update last_update with a safe UTC ISO timestamp
        try:
            self._state["last_update"] = datetime.now(timezone.utc).isoformat()
        except Exception:
            self._state["last_update"] = str(datetime.utcnow())

        snapshot = {
            "vehicles": self._state.get("vehicles", {}),
            "forecasts": self._state.get("forecasts", {}),
            "providers": self._state.get("providers", {}),
            "refuel_events": self._state.get("refuel_events", []),
            "last_update": self._state.get("last_update"),
            "config": self._state.get("config", {}),
        }

        return snapshot

    @property
    def snapshot(self) -> Dict[str, Any]:
        """Return the latest snapshot of coordinator data (always a dict)."""
        return self.data or self._state

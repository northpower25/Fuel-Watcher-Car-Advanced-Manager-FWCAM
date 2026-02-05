# FILE: custom_components/fwcam/coordinator.py

#COMMIT TITLE: fix(v0.1.3): robust coordinator using validated config
#COMMIT DESCRIPTION:
#• 	Coordinator reads validated config from hass.data and returns a stable placeholder snapshot.
#• 	Avoids assumptions about entry.data and uses safe timestamping. 
# FILE DESCRIPTION: DataUpdateCoordinator for FWCAM. Periodically fetches data (placeholder) and exposes snapshot. 
#DEPENDENCIES:
#• 	homeassistant.helpers.update_coordinator, homeassistant.core, homeassistant.config_entrie
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
FETCH_TIMEOUT = 30


class FwcamDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, update_interval: Optional[timedelta] = None) -> None:
        self.hass = hass
        self.entry = entry
        interval = update_interval or DEFAULT_UPDATE_INTERVAL

        super().__init__(hass, _LOGGER, name=f"{DOMAIN}-{entry.entry_id}", update_interval=interval)

        self._state: Dict[str, Any] = {
            "vehicles": {},
            "forecasts": {},
            "providers": {},
            "refuel_events": [],
            "last_update": None,
            "config": {},
        }

    async def _async_update_data(self) -> Dict[str, Any]:
        try:
            return await asyncio.wait_for(self.async_fetch_data(), timeout=FETCH_TIMEOUT)
        except asyncio.TimeoutError as err:
            _LOGGER.warning("FWCAM coordinator fetch timed out.")
            raise UpdateFailed("Timeout while fetching FWCAM data") from err
        except Exception as err:
            _LOGGER.exception("Unexpected error in coordinator fetch: %s", err)
            raise UpdateFailed(err) from err

    async def async_fetch_data(self) -> Dict[str, Any]:
        _LOGGER.debug("FWCAM coordinator: async_fetch_data placeholder called.")

        if not isinstance(self._state, dict):
            self._state = {
                "vehicles": {},
                "forecasts": {},
                "providers": {},
                "refuel_events": [],
                "last_update": None,
                "config": {},
            }

        config = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {}).get("config", {})
        self._state["config"] = config

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
        return self.data or self._state

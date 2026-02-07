"""Station sensor for displaying recommended fuel stations."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN
from ..coordinator import FwcamDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up station sensor for a config entry."""
    coordinator: FwcamDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    # Create a sensor for the recommended station
    async_add_entities([FwcamStationSensor(coordinator, entry.entry_id)], True)


class FwcamStationSensor(CoordinatorEntity, Entity):
    """Sensor displaying the recommended fuel station with best price."""

    _attr_should_poll = False

    def __init__(
        self, coordinator: FwcamDataUpdateCoordinator, entry_id: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.entry_id = entry_id
        self._attr_name = "FWCAM Recommended Station"
        self._attr_unique_id = f"fwcam_recommended_station_{entry_id}"
        self._state: Any = None
        self._attributes: dict[str, Any] = {}

    @property
    def native_value(self):
        """Return the station name with best price."""
        return self._state

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes about the station and all available stations."""
        return self._attributes

    async def async_added_to_hass(self) -> None:
        """When entity is added, ensure we have initial state and subscribe to updates."""
        await super().async_added_to_hass()
        # Initial update from coordinator snapshot
        self._handle_coordinator_update()

    def _handle_coordinator_update(self) -> None:
        """Read snapshot from coordinator and update internal state."""
        snapshot = self.coordinator.snapshot

        # Get Tankerkönig station data
        providers = snapshot.get("providers", {})
        tankerkoenig_data = providers.get("tankerkoenig", {})
        stations = tankerkoenig_data.get("stations", [])

        if not stations:
            self._state = "No stations available"
            self._attributes = {
                "station_count": 0,
                "error": tankerkoenig_data.get("error", "No data"),
            }
        else:
            # Get configured fuel type
            config = snapshot.get("config", {})
            fuel_type = config.get("fuel_type", "e5")

            # Find the station with the best price for the configured fuel type
            best_station = None
            best_price = float("inf")

            for station in stations:
                price_obj = station.get("price", {})
                if fuel_type == "all":
                    # For "all" type, find the cheapest among all fuel types
                    for ft in ["e5", "e10", "diesel"]:
                        price = price_obj.get(ft)
                        if price and price < best_price:
                            best_price = price
                            best_station = station
                            best_station["selected_fuel_type"] = ft
                            best_station["selected_price"] = price
                else:
                    price = price_obj.get(fuel_type)
                    if price and price < best_price:
                        best_price = price
                        best_station = station
                        best_station["selected_fuel_type"] = fuel_type
                        best_station["selected_price"] = price

            if best_station:
                self._state = best_station.get("name", "Unknown Station")
                self._attributes = {
                    "station_id": best_station.get("id"),
                    "brand": best_station.get("brand"),
                    "street": best_station.get("street"),
                    "house_number": best_station.get("houseNumber"),
                    "post_code": best_station.get("postCode"),
                    "place": best_station.get("place"),
                    "latitude": best_station.get("lat"),
                    "longitude": best_station.get("lng"),
                    "distance": best_station.get("dist"),
                    "is_open": best_station.get("isOpen"),
                    "fuel_type": best_station.get("selected_fuel_type"),
                    "price": best_station.get("selected_price"),
                    "e5_price": best_station.get("price", {}).get("e5"),
                    "e10_price": best_station.get("price", {}).get("e10"),
                    "diesel_price": best_station.get("price", {}).get("diesel"),
                    "station_count": len(stations),
                    "all_stations": [
                        {
                            "name": s.get("name"),
                            "brand": s.get("brand"),
                            "place": s.get("place"),
                            "distance": s.get("dist"),
                            "e5": s.get("price", {}).get("e5"),
                            "e10": s.get("price", {}).get("e10"),
                            "diesel": s.get("price", {}).get("diesel"),
                            "is_open": s.get("isOpen"),
                        }
                        for s in stations
                    ],
                }
                _LOGGER.debug(
                    "Best station: %s at €%.3f for %s (%d stations available)",
                    self._state,
                    best_price,
                    best_station.get("selected_fuel_type"),
                    len(stations),
                )
            else:
                self._state = "No valid prices found"
                self._attributes = {
                    "station_count": len(stations),
                    "error": "No valid prices for selected fuel type",
                }

        # Notify HA of state change
        self.async_write_ha_state()

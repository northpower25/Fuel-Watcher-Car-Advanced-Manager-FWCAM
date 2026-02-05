# FILE: custom_components/fwcam/sensors/consumption_sensor.py
# COMMIT TITLE: feat(v0.1.0): add consumption sensor platform and base sensor entity
# COMMIT DESCRIPTION:
# - Added sensor platform with FwcamConsumptionSensor entity
# - Sensor reads snapshot from coordinator and exposes placeholder attributes
# - Subscribes to coordinator updates to refresh state
# FILE DESCRIPTION:
#   Basic sensor platform for consumption/forecast related sensors.
#   Uses DataUpdateCoordinator snapshot as single source of truth.
# DEPENDENCIES:
#   Imports: homeassistant.helpers.entity, update_coordinator, const, coordinator
#   Used by: Lovelace UI, notifications

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN, ATTR_LITERS, ATTR_ODOMETER
from ..coordinator import FwcamDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORM_NAME = "fwcam_consumption_sensor"


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up sensors for a config entry."""
    coordinator: FwcamDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # For MVP create one generic consumption sensor per configured vehicle mapping.
    # Placeholder: single sensor representing overall fleet or default vehicle.
    async_add_entities([FwcamConsumptionSensor(coordinator, entry.entry_id)], True)


class FwcamConsumptionSensor(CoordinatorEntity, Entity):
    """Sensor exposing consumption and days-to-empty based on coordinator snapshot."""

    _attr_should_poll = False

    def __init__(self, coordinator: FwcamDataUpdateCoordinator, entry_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.entry_id = entry_id
        self._attr_name = "FWCAM Consumption"
        self._attr_unique_id = f"fwcam_consumption_{entry_id}"
        self._state: Any = None
        self._attributes: dict[str, Any] = {}

    @property
    def native_value(self):
        """Return the primary state (e.g., current consumption L/100km)."""
        return self._state

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes like last odometer, last refuel, days to empty."""
        return self._attributes

    async def async_added_to_hass(self) -> None:
        """When entity is added, ensure we have initial state and subscribe to updates."""
        await super().async_added_to_hass()
        # Initial update from coordinator snapshot
        self._handle_coordinator_update()

    def _handle_coordinator_update(self) -> None:
        """Read snapshot from coordinator and update internal state."""
        snapshot = self.coordinator.snapshot

        # Placeholder logic: attempt to read a default vehicle if present
        vehicles = snapshot.get("vehicles", {})
        default_vehicle = None
        if vehicles:
            # pick first vehicle entry
            default_vehicle = next(iter(vehicles.values()))
        # Example placeholders
        if default_vehicle:
            # expected keys: odometer, consumption_l_per_100km, fuel_level, range_km
            self._state = default_vehicle.get("consumption_l_per_100km")
            self._attributes = {
                ATTR_ODOMETER: default_vehicle.get("odometer"),
                "fuel_level": default_vehicle.get("fuel_level"),
                "range_km": default_vehicle.get("range_km"),
            }
        else:
            # No vehicle data yet — keep sensor unavailable
            self._state = None
            self._attributes = {}

        # Notify HA of state change
        self.async_write_ha_state()

    # CoordinatorEntity will call this when coordinator updates
    def _handle_coordinator_update_event(self) -> None:  # kept for clarity; CoordinatorEntity uses _handle_coordinator_update
        self._handle_coordinator_update()

# TODO:
# - Add per-vehicle sensors (consumption, range, days_to_empty)
# - Add sensor attributes for forecast confidence and last_refuel
# - Implement unit conversions and device_class where appropriate
# CHANGE HISTORY
# v0.1.0 - Initial sensor platform

"""Sensor platform for FWCAM integration."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from . import consumption_sensor
from . import station_sensor


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up FWCAM sensors from a config entry."""
    # Setup consumption sensor
    await consumption_sensor.async_setup_entry(hass, entry, async_add_entities)
    
    # Setup station sensor
    await station_sensor.async_setup_entry(hass, entry, async_add_entities)

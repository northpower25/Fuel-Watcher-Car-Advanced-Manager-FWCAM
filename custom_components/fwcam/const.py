# FILE: custom_components/fwcam/const.py
# COMMIT TITLE: feat(v0.1.0): add core constants for FWCAM integration
# COMMIT DESCRIPTION:
# - Added domain constant and default configuration values
# - Added event names and attribute keys for future modules
# - Prepared structure for forecast, refuel detection, and provider adapters
# FILE DESCRIPTION:
#   Centralized constants for the FWCAM integration.
#   All modules import from here to avoid duplication and ensure consistency.
# DEPENDENCIES:
#   Imported by: __init__.py, coordinator.py, config_flow.py, sensors, providers, models.

# ─────────────────────────────────────────────
# DOMAIN
# ─────────────────────────────────────────────
DOMAIN = "fwcam"

# ─────────────────────────────────────────────
# CONFIG KEYS
# ─────────────────────────────────────────────
CONF_VEHICLE_NAME = "vehicle_name"
CONF_FUEL_TYPE = "fuel_type"
CONF_RADIUS = "radius"
CONF_NOTIFY_CHANNELS = "notify_channels"

# ─────────────────────────────────────────────
# DEFAULTS
# ─────────────────────────────────────────────
DEFAULT_RADIUS = 5
DEFAULT_FUEL_TYPE = "e5"
DEFAULT_NOTIFY_CHANNELS = ["telegram", "ha_companion"]

# ─────────────────────────────────────────────
# EVENTS
# ─────────────────────────────────────────────
EVENT_REFUEL_DETECTED = "fwcam_refuel_detected"
EVENT_FORECAST_UPDATED = "fwcam_forecast_updated"

# ─────────────────────────────────────────────
# ATTRIBUTES
# ─────────────────────────────────────────────
ATTR_LITERS = "liters"
ATTR_PRICE = "price"
ATTR_STATION_ID = "station_id"
ATTR_LAT = "lat"
ATTR_LON = "lon"
ATTR_ODOMETER = "odometer"

# ─────────────────────────────────────────────
# TODO / FUTURE WORK
# ─────────────────────────────────────────────
# - Add provider registry constants
# - Add message template keys
# - Add ML model configuration keys

# CHANGE HISTORY
# v0.1.0 - Initial creation

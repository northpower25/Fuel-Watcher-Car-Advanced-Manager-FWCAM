# FILE: custom_components/fwcam/const.py
# COMMIT TITLE: feat(v0.1.0): add constants and defaults
# COMMIT DESCRIPTION:
# - Centralize domain, config keys and defaults used across the integration.
# FILE DESCRIPTION: Constants used by config_flow, init, coordinator and sensors.
# DEPENDENCIES:
# - None (pure constants)

DOMAIN = "fwcam"

CONF_FUEL_TYPE = "fuel_type"
CONF_NOTIFY_CHANNELS = "notify_channels"
CONF_TANKERKOENIG_API_KEY = "tankerkoenig_api_key"

DEFAULT_FUEL_TYPE = "e5"
DEFAULT_RADIUS = 5
DEFAULT_NOTIFY_CHANNELS = []

# Valid fuel types for Tankerkönig API
FUEL_TYPE_OPTIONS = ["e5", "e10", "diesel", "all"]

# Sensor attribute keys
ATTR_LITERS = "liters"
ATTR_ODOMETER = "odometer"

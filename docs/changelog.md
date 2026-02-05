# Changelog

All notable changes to the Fuel Watcher Car Advanced Manager (FWCAM) will be documented in this file.

## [Unreleased]

### Fixed
- **Critical Bug**: Fixed Home Assistant setup failure caused by missing constants in `const.py`
  - Added `ATTR_LITERS` and `ATTR_ODOMETER` constants that were being imported by `consumption_sensor.py` but not defined
  - This was causing a silent ImportError during integration setup, preventing the integration from loading
  - Users were seeing error messages without any system log entries because the error occurred during module import
  - Issue resolved: The integration now loads successfully and sensors can be initialized properly

### Added
- `.gitignore` file to prevent Python cache files and temporary files from being committed to the repository

### Changed
- Removed `__pycache__` directories that were previously committed

## [0.1.4] - Previous Release

Previous version with validated config entry and graceful failure handling.

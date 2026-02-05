# Fuel Watcher Car Advanced Manager (FWCAM)

A Home Assistant custom integration for monitoring fuel consumption, tracking refueling events, and providing intelligent fuel price forecasts.

## Installation

### HACS (Recommended)
1. Add this repository as a custom repository in HACS
2. Search for "Fuel Watcher Car Advanced Manager" in HACS
3. Install the integration
4. Restart Home Assistant

### Manual Installation
1. Copy the `custom_components/fwcam` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Fuel Watcher Car Advanced Manager"
4. Follow the configuration steps:
   - Enter your latitude and longitude (defaults to your Home Assistant location)
   - Set the search radius for fuel stations (default: 5 km)
   - Configure fuel type and notification channels

## Features

- **Consumption Tracking**: Monitor fuel consumption across multiple vehicles
- **Refueling Detection**: Automatic detection and logging of refueling events
- **Price Forecasts**: Intelligent forecasting of fuel price trends
- **Station Recommendations**: Find the best fuel prices near you
- **Notifications**: Get alerts for low fuel, refueling events, and price opportunities

## Support

- **Documentation**: See the [docs](docs/) folder for detailed information
- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/northpower25/Fuel-Watcher-Car-Advanced-Manager-FWCAM/issues)
- **Changelog**: See [CHANGELOG](docs/changelog.md) for version history

## Version

Current version: 0.1.4

## License

See [LICENSE](LICENSE) file for details.
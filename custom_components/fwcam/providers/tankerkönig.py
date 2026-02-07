"""Tankerkönig API provider for fuel station prices."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .base_provider import BaseFuelProvider

_LOGGER = logging.getLogger(__name__)

API_BASE_URL = "https://creativecommons.tankerkoenig.de/api/v4"


class TankerkoenigProvider(BaseFuelProvider):
    """Provider for Tankerkönig fuel station price API."""

    def __init__(self, api_key: str) -> None:
        """Initialize the Tankerkönig provider.
        
        Args:
            api_key: Tankerkönig API key
        """
        super().__init__(api_key)
        self._session: aiohttp.ClientSession | None = None

    async def fetch_stations(
        self,
        latitude: float,
        longitude: float,
        radius: int,
        fuel_type: str,
    ) -> list[dict[str, Any]]:
        """Fetch fuel stations with prices from Tankerkönig API v4.
        
        According to the API specification:
        - Endpoint: /api/v4/stations
        - Parameters: lat, lng, radius (max 25km), type (e5|e10|diesel|all), apikey
        - Response includes stations with price objects containing e5, e10, diesel fields
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius: Search radius in kilometers (max 25)
            fuel_type: Type of fuel (e5, e10, diesel, all)
            
        Returns:
            List of valid stations with price information
        """
        # Ensure radius is within API limits
        radius = min(radius, 25)
        
        url = f"{API_BASE_URL}/stations"
        params = {
            "lat": latitude,
            "lng": longitude,
            "radius": radius,
            "type": fuel_type,
            "apikey": self.api_key,
        }
        
        _LOGGER.debug(
            "Fetching Tankerkönig stations: lat=%s, lng=%s, radius=%s, type=%s",
            latitude,
            longitude,
            radius,
            fuel_type,
        )
        
        try:
            if self._session is None:
                self._session = aiohttp.ClientSession()
            
            async with self._session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    _LOGGER.error(
                        "Tankerkönig API returned status %s: %s",
                        response.status,
                        await response.text(),
                    )
                    return []
                
                data = await response.json()
                
                # Validate response structure according to API spec
                if not data.get("ok"):
                    _LOGGER.error("Tankerkönig API returned ok=false: %s", data.get("msg"))
                    return []
                
                # Extract stations from data.stations (API v4 structure)
                stations = data.get("data", {}).get("stations", [])
                _LOGGER.debug("Received %d stations from Tankerkönig API", len(stations))
                
                # Filter and validate stations to only return those with valid prices
                valid_stations = []
                for station in stations:
                    if self.validate_station(station):
                        valid_stations.append(station)
                    else:
                        _LOGGER.debug(
                            "Station '%s' (id=%s) excluded - no valid price data",
                            station.get("name", "Unknown"),
                            station.get("id", "Unknown"),
                        )
                
                _LOGGER.info(
                    "Tankerkönig: %d valid stations found (out of %d total)",
                    len(valid_stations),
                    len(stations),
                )
                
                return valid_stations
                
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to Tankerkönig API: %s", err)
            return []
        except Exception as err:
            _LOGGER.exception("Unexpected error fetching Tankerkönig data: %s", err)
            return []

    def validate_station(self, station: dict[str, Any]) -> bool:
        """Validate that a station has valid price information.
        
        According to the API specification, each station should have:
        - A 'price' object with e5, e10, diesel fields
        - Valid numeric prices (not null, not 0)
        
        Args:
            station: Station data dictionary from API
            
        Returns:
            True if station has valid prices, False otherwise
        """
        if not isinstance(station, dict):
            return False
        
        # Check if price object exists
        price = station.get("price")
        if not isinstance(price, dict):
            _LOGGER.debug("Station has no price object")
            return False
        
        # Check if at least one valid price exists
        # Valid means: exists, is numeric, and is greater than 0
        has_valid_price = False
        for fuel_type in ["e5", "e10", "diesel"]:
            fuel_price = price.get(fuel_type)
            if fuel_price is not None and isinstance(fuel_price, (int, float)) and fuel_price > 0:
                has_valid_price = True
                break
        
        if not has_valid_price:
            _LOGGER.debug(
                "Station has price object but no valid prices: %s",
                price,
            )
            return False
        
        # Ensure station has required fields
        required_fields = ["id", "name", "brand", "lat", "lng"]
        for field in required_fields:
            if field not in station:
                _LOGGER.debug("Station missing required field: %s", field)
                return False
        
        return True

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None

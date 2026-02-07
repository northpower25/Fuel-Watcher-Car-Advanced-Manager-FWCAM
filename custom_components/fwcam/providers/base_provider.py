"""Base provider class for fuel station price providers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseFuelProvider(ABC):
    """Abstract base class for fuel station price providers."""

    def __init__(self, api_key: str) -> None:
        """Initialize the provider with an API key.
        
        Args:
            api_key: API key for the provider service
        """
        self.api_key = api_key

    @abstractmethod
    async def fetch_stations(
        self,
        latitude: float,
        longitude: float,
        radius: int,
        fuel_type: str,
    ) -> list[dict[str, Any]]:
        """Fetch fuel stations with prices from the provider.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius: Search radius in kilometers
            fuel_type: Type of fuel (e5, e10, diesel, all)
            
        Returns:
            List of station dictionaries with price information
        """
        pass

    @abstractmethod
    def validate_station(self, station: dict[str, Any]) -> bool:
        """Validate that a station has valid price information.
        
        Args:
            station: Station data dictionary
            
        Returns:
            True if station has valid prices, False otherwise
        """
        pass

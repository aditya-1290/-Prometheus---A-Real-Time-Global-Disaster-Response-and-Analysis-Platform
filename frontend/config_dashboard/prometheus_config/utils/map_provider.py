"""
Utility functions for interacting with external map providers and services.
"""

from typing import Dict, Any
import requests
from django.conf import settings

class MapProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.mapbox.com"  # We'll use Mapbox as our provider

    def get_geocoding(self, address: str) -> Dict[str, Any]:
        """Get coordinates for an address."""
        endpoint = f"{self.base_url}/geocoding/v5/mapbox.places/{address}.json"
        params = {
            "access_token": self.api_key,
            "limit": 1
        }
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()

    def get_reverse_geocoding(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get address for coordinates."""
        endpoint = f"{self.base_url}/geocoding/v5/mapbox.places/{lon},{lat}.json"
        params = {
            "access_token": self.api_key,
            "limit": 1
        }
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()

    def get_route(self, start: tuple, end: tuple) -> Dict[str, Any]:
        """Get route between two points."""
        endpoint = f"{self.base_url}/directions/v5/mapbox/driving/{start[1]},{start[0]};{end[1]},{end[0]}"
        params = {
            "access_token": self.api_key,
            "geometries": "geojson"
        }
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()

map_provider = MapProvider(settings.MAPBOX_API_KEY)

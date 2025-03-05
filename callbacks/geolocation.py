import requests
import os
from config import logger, OPENCAGE_API_KEY

def get_city_coordinates(city_name):
    """Fetch city coordinates using OpenCage API."""
    if not OPENCAGE_API_KEY:
        logger.warning("Missing OpenCage API Key!")
        return None, None, "⚠️ Missing API Key."

    base_url = "https://api.opencagedata.com/geocode/v1/json"
    params = {"q": city_name, "key": OPENCAGE_API_KEY, "limit": 1}

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data["results"]:
            return None, None, "⚠️ City not found."

        lat = data["results"][0]["geometry"]["lat"]
        lon = data["results"][0]["geometry"]["lng"]
        return float(lat), float(lon), None

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching city coordinates: {str(e)}")
        return None, None, f"⚠️ Error: {str(e)}"

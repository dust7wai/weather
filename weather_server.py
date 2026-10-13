#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
#   "mcp[cli]",
# ]
# ///
#

import requests
from mcp.server.mcpserver import MCPServer

# Initialize the FastMCP server
mcp = MCPServer("Global Weather & Location Server")


@mcp.tool()
def lookup_location(name: str) -> str:
    """Looks up geographic coordinates (latitude and longitude) for a given city or place name.

    Args:
        name: The name of the city or place to look up (e.g., 'Canberra', 'Paris', 'Tokyo').
    """
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={name}&count=1&language=en"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        results = data.get("results")
        if not results:
            return f"❌ Could not find any location coordinates matching '{name}'."

        location = results[0]
        city = location.get("name")
        country = location.get("country", "Unknown Country")
        admin1 = location.get("admin1", "")  # State/Province
        lat = location.get("latitude")
        lon = location.get("longitude")

        region_info = f"{city}, {admin1}, {country}" if admin1 else f"{city}, {country}"

        return f"📍 Found Location: {region_info}\nLatitude: {lat}\nLongitude: {lon}"

    except requests.exceptions.RequestException as e:
        return f"Error during location lookup for '{name}': {e}"


@mcp.tool()
def get_weather(city: str) -> str:
    """Retrieves the current weather, temperature, and wind speed for any global location using coordinates.

    Args:
        city: The name of the city or place to look up (e.g., 'Canberra', 'Paris', 'Tokyo').
    """

    # First, look up the coordinates for the given city name
    urlCity = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en"
    latitude: float | None = None
    longitude: float | None = None

    try:
        responseCity = requests.get(urlCity)
        responseCity.raise_for_status()
        dataCity = responseCity.json()

        resultsCity = dataCity.get("results")
        if not resultsCity:
            return f"❌ Could not find any location coordinates matching '{city}'."

        location = resultsCity[0]
        latitude = location.get("latitude")
        longitude = location.get("longitude")

        urlForecast = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={latitude}&longitude={longitude}"
            f"&current=temperature_2m,wind_speed_10m"
            f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
            f"&timezone=auto"
        )

        response = requests.get(urlForecast)
        response.raise_for_status()
        data = response.json()

        current = data["current"]
        time = current["time"]
        temp = current["temperature_2m"]
        wind = current["wind_speed_10m"]

        return (
            f"🌍 Weather Report 🌍\n"
            f"Time:    {time}\n"
            f"Temperature: {temp}°C\n"
            f"Wind speed: {wind}km/h"
        )

    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data for coordinates ({latitude}, {longitude}) of city {city}: {e}"


@mcp.tool()
def get_canberra_weather() -> str:
    """Retrieves the current weather, temperature, and wind speed for Canberra, Australia."""
    # Coordinates for Canberra, Australia
    LAT = -35.2835
    LON = 149.1281

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={LAT}&longitude={LON}"
        f"&current=temperature_2m,wind_speed_10m"
        f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
        f"&timezone=Australia%2FSydney"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        current = data["current"]
        time = current["time"]
        temp = current["temperature_2m"]
        wind = current["wind_speed_10m"]

        # Return a clean string for the LLM to process
        return (
            f"☀️ Canberra Current Weather ☀️\n"
            f"Time:    {time}\n"
            f"Temperature: {temp}°C\n"
            f"Wind speed: {wind}km/h"
        )

    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {e}"


if __name__ == "__main__":
    # Run the server using the default Stdio transport
    mcp.run()

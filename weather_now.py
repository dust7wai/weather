#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
# ]
# ///
#


import requests


def get_weather_now() -> None:
    """Retrieves and prints current Canberra weather from the Open-Meteo API."""
    # Coordinates for Canberra, Australia
    LAT: float = -35.2835
    LON: float = 149.1281

    url: str = (
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

        print("☀️ Canberra Current Weather ☀️")
        print(f"Time:    {time}")
        print(f"Temperature: {temp}°C")
        print(f"Wind speed: {wind}km/h")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")


# Backward compatibility alias
get_weather__now = get_weather_now

if __name__ == "__main__":
    get_weather_now()

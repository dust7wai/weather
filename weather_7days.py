#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
#   "datetime",
# ]
# ///
#

from datetime import datetime

import requests


def get_weather_7days() -> None:
    """Retrieves and prints the 7-day weather forecast for Canberra."""
    # Coordinates for Canberra, Australia
    LAT: float = -35.2835
    LON: float = 149.1281

    url: str = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={LAT}&longitude={LON}"
        f"&daily=temperature_2m_max,"
        f"temperature_2m_min,"
        f"precipitation_probability_max"
        f"&timezone=Australia%2FSydney"
        f"&forecast_days=7"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        daily = data["daily"]
        dates = daily["time"]
        max_temps = daily["temperature_2m_max"]
        min_temps = daily["temperature_2m_min"]
        rain_probs = daily["precipitation_probability_max"]

        print("☀️ Canberra 7-day Weather Forecast ☀️")
        print()

        print(f"{'Date':<12}{'Day':<12}{'Min':<8}{'Max':<8}{'Rain':<6}")

        for date, min_temp, max_temp, rain in zip(
            dates, min_temps, max_temps, rain_probs
        ):
            day = datetime.strptime(date, "%Y-%m-%d").strftime("%A")

            print(
                f"{date:<12}{day:<12}{min_temp:>5.1f}°C {max_temp:>5.1f}°C {rain:>4}%"
            )

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")


if __name__ == "__main__":
    get_weather_7days()

"""Live integration tests querying the Open-Meteo public API."""

import pytest
import requests

from weather_7days import get_weather_7days
from weather_now import get_weather_now
from weather_server import get_canberra_weather, get_weather, lookup_location


@pytest.mark.integration
def test_live_lookup_location_canberra() -> None:
    """Tests live location lookup against Open-Meteo geocoding API."""
    try:
        result = lookup_location("Canberra")
    except requests.exceptions.RequestException as exc:
        pytest.skip(f"Live API unreachable: {exc}")

    assert "Canberra" in result
    assert "Australia" in result
    assert "Latitude:" in result
    assert "Longitude:" in result


@pytest.mark.integration
def test_live_lookup_location_not_found() -> None:
    """Tests live location lookup for a non-existent location."""
    try:
        result = lookup_location("XyZqWeRtYuIoP12345NonExistent")
    except requests.exceptions.RequestException as exc:
        pytest.skip(f"Live API unreachable: {exc}")

    assert "Could not find any location coordinates" in result


@pytest.mark.integration
def test_live_get_weather_paris() -> None:
    """Tests live weather retrieval for Paris against Open-Meteo forecast API."""
    try:
        result = get_weather("Paris")
    except requests.exceptions.RequestException as exc:
        pytest.skip(f"Live API unreachable: {exc}")

    assert "🌍 Weather Report 🌍" in result
    assert "Temperature:" in result
    assert "°C" in result
    assert "Wind speed:" in result
    assert "km/h" in result


@pytest.mark.integration
def test_live_get_canberra_weather() -> None:
    """Tests live weather retrieval for Canberra."""
    try:
        result = get_canberra_weather()
    except requests.exceptions.RequestException as exc:
        pytest.skip(f"Live API unreachable: {exc}")

    assert "☀️ Canberra Current Weather ☀️" in result
    assert "Temperature:" in result
    assert "Wind speed:" in result


@pytest.mark.integration
def test_live_weather_now_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    """Tests running live get_weather_now() and checking printed stdout."""
    try:
        get_weather_now()
    except requests.exceptions.RequestException as exc:
        pytest.skip(f"Live API unreachable: {exc}")

    captured = capsys.readouterr()
    assert "☀️ Canberra Current Weather ☀️" in captured.out
    assert "Temperature:" in captured.out
    assert "Wind speed:" in captured.out


@pytest.mark.integration
def test_live_weather_7days_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    """Tests running live get_weather_7days() and checking printed stdout."""
    try:
        get_weather_7days()
    except requests.exceptions.RequestException as exc:
        pytest.skip(f"Live API unreachable: {exc}")

    captured = capsys.readouterr()
    assert "☀️ Canberra 7-day Weather Forecast ☀️" in captured.out
    assert "Date" in captured.out
    assert "Day" in captured.out
    assert "Min" in captured.out
    assert "Max" in captured.out
    assert "Rain" in captured.out

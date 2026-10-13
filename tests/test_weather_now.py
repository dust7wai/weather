"""Unit tests for weather_now.py module."""

import runpy
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests

from weather_now import get_weather__now, get_weather_now


@pytest.fixture
def mock_weather_payload() -> dict[str, Any]:
    """Provides a sample Open-Meteo API response payload."""
    return {
        "latitude": -35.2835,
        "longitude": 149.1281,
        "current": {
            "time": "2026-09-27T17:30",
            "interval": 900,
            "temperature_2m": 22.4,
            "wind_speed_10m": 11.5,
        },
    }


def test_get_weather_now_success(
    mock_weather_payload: dict[str, Any], capsys: pytest.CaptureFixture[str]
) -> None:
    """Tests successful weather retrieval and correct stdout formatting."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = mock_weather_payload
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response) as mock_get:
        get_weather_now()

        # Verify requests.get call and URL arguments
        mock_get.assert_called_once()
        called_url: str = mock_get.call_args[0][0]
        assert "latitude=-35.2835" in called_url
        assert "longitude=149.1281" in called_url
        assert "current=temperature_2m,wind_speed_10m" in called_url
        assert "hourly=temperature_2m,relative_humidity_2m,wind_speed_10m" in called_url
        assert "timezone=Australia%2FSydney" in called_url

        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

    captured = capsys.readouterr()
    expected_lines: list[str] = [
        "☀️ Canberra Current Weather ☀️",
        "Time:    2026-09-27T17:30",
        "Temperature: 22.4°C",
        "Wind speed: 11.5km/h",
    ]
    for line in expected_lines:
        assert line in captured.out


def test_get_weather_now_different_values(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Tests weather formatting with negative temperatures and zero wind."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = {
        "current": {
            "time": "2026-07-15T06:00",
            "temperature_2m": -3.8,
            "wind_speed_10m": 0.0,
        }
    }
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        get_weather_now()

    captured = capsys.readouterr()
    assert "Time:    2026-07-15T06:00" in captured.out
    assert "Temperature: -3.8°C" in captured.out
    assert "Wind speed: 0.0km/h" in captured.out


def test_get_weather_now_extreme_values(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Tests weather formatting with extreme temperature and high wind speed."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = {
        "current": {
            "time": "2026-01-20T14:00",
            "temperature_2m": 42.9,
            "wind_speed_10m": 98.4,
        }
    }
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        get_weather_now()

    captured = capsys.readouterr()
    assert "Time:    2026-01-20T14:00" in captured.out
    assert "Temperature: 42.9°C" in captured.out
    assert "Wind speed: 98.4km/h" in captured.out


def test_get_weather_now_http_error(capsys: pytest.CaptureFixture[str]) -> None:
    """Tests error handling when Open-Meteo returns an HTTP error status."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "500 Server Error"
    )

    with patch("requests.get", return_value=mock_response):
        get_weather_now()

    captured = capsys.readouterr()
    assert "Error fetching weather data: 500 Server Error" in captured.out


def test_get_weather_now_client_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Tests error handling when Open-Meteo returns a 404 client error."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "404 Client Error: Not Found"
    )

    with patch("requests.get", return_value=mock_response):
        get_weather_now()

    captured = capsys.readouterr()
    assert "Error fetching weather data: 404 Client Error: Not Found" in captured.out


def test_get_weather_now_connection_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Tests error handling when network connection fails."""
    with patch(
        "requests.get",
        side_effect=requests.exceptions.ConnectionError("Connection failed"),
    ):
        get_weather_now()

    captured = capsys.readouterr()
    assert "Error fetching weather data: Connection failed" in captured.out


def test_get_weather_now_timeout(capsys: pytest.CaptureFixture[str]) -> None:
    """Tests error handling when the request times out."""
    with patch(
        "requests.get",
        side_effect=requests.exceptions.Timeout("Request timed out"),
    ):
        get_weather_now()

    captured = capsys.readouterr()
    assert "Error fetching weather data: Request timed out" in captured.out


def test_get_weather_now_json_decode_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Tests error handling when response body is not valid JSON."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.raise_for_status.return_value = None
    mock_response.json.side_effect = requests.exceptions.JSONDecodeError(
        "Expecting value", "doc", 0
    )

    with patch("requests.get", return_value=mock_response):
        get_weather_now()

    captured = capsys.readouterr()
    assert (
        "Error fetching weather data: Expecting value: line 1 column 1 (char 0)"
        in captured.out
    )


def test_get_weather_now_request_exception(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Tests handling of general RequestException."""
    with patch(
        "requests.get",
        side_effect=requests.exceptions.RequestException("General error"),
    ):
        get_weather_now()

    captured = capsys.readouterr()
    assert "Error fetching weather data: General error" in captured.out


def test_get_weather_now_missing_current_key() -> None:
    """Tests that KeyError is raised when the payload lacks the 'current' key."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = {"latitude": -35.2835}
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        with pytest.raises(KeyError, match="current"):
            get_weather_now()


def test_get_weather_now_missing_temperature_key() -> None:
    """Tests that KeyError is raised when 'current' lacks 'temperature_2m'."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = {
        "current": {
            "time": "2026-09-27T17:30",
            "wind_speed_10m": 11.5,
        }
    }
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        with pytest.raises(KeyError, match="temperature_2m"):
            get_weather_now()


def test_get_weather_now_missing_wind_speed_key() -> None:
    """Tests that KeyError is raised when 'current' lacks 'wind_speed_10m'."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = {
        "current": {
            "time": "2026-09-27T17:30",
            "temperature_2m": 22.4,
        }
    }
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        with pytest.raises(KeyError, match="wind_speed_10m"):
            get_weather_now()


def test_function_alias_compatibility() -> None:
    """Tests that both get_weather_now and get_weather__now are identical callables."""
    assert callable(get_weather_now)
    assert callable(get_weather__now)
    assert get_weather_now is get_weather__now


def test_main_execution(
    mock_weather_payload: dict[str, Any], capsys: pytest.CaptureFixture[str]
) -> None:
    """Tests that executing the module as __main__ invokes get_weather_now."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = mock_weather_payload
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        runpy.run_module("weather_now", run_name="__main__")

    captured = capsys.readouterr()
    assert "☀️ Canberra Current Weather ☀️" in captured.out
    assert "Temperature: 22.4°C" in captured.out


def test_main_execution_error(capsys: pytest.CaptureFixture[str]) -> None:
    """Tests module execution as __main__ when network error occurs."""
    with patch(
        "requests.get",
        side_effect=requests.exceptions.ConnectionError("Network unavailable"),
    ):
        runpy.run_module("weather_now", run_name="__main__")

    captured = capsys.readouterr()
    assert "Error fetching weather data: Network unavailable" in captured.out

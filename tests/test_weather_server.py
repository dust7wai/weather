"""Unit tests for weather_server.py module."""

import asyncio
import runpy
from typing import Any
from unittest.mock import MagicMock, patch

import requests

from weather_server import get_canberra_weather, get_weather, lookup_location, mcp

# --- Tests for lookup_location ---


def test_lookup_location_success_with_admin1() -> None:
    """Tests location lookup when admin1 (state/province) is present."""
    mock_payload: dict[str, Any] = {
        "results": [
            {
                "name": "Canberra",
                "country": "Australia",
                "admin1": "Australian Capital Territory",
                "latitude": -35.2835,
                "longitude": 149.1281,
            }
        ]
    }
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = mock_payload
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response) as mock_get:
        result = lookup_location("Canberra")

        mock_get.assert_called_once_with(
            "https://geocoding-api.open-meteo.com/v1/search?name=Canberra&count=1&language=en"
        )
        assert (
            "📍 Found Location: Canberra, Australian Capital Territory, Australia"
            in result
        )
        assert "Latitude: -35.2835" in result
        assert "Longitude: 149.1281" in result


def test_lookup_location_success_without_admin1() -> None:
    """Tests location lookup when admin1 is omitted or empty."""
    mock_payload: dict[str, Any] = {
        "results": [
            {
                "name": "Singapore",
                "country": "Singapore",
                "admin1": "",
                "latitude": 1.3521,
                "longitude": 103.8198,
            }
        ]
    }
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = mock_payload
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        result = lookup_location("Singapore")

        assert "📍 Found Location: Singapore, Singapore" in result
        assert "Latitude: 1.3521" in result
        assert "Longitude: 103.8198" in result


def test_lookup_location_unknown_country() -> None:
    """Tests location lookup when country field is missing."""
    mock_payload: dict[str, Any] = {
        "results": [
            {
                "name": "Remote Island",
                "latitude": -10.0,
                "longitude": 100.0,
            }
        ]
    }
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = mock_payload
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        result = lookup_location("Remote Island")

        assert "📍 Found Location: Remote Island, Unknown Country" in result


def test_lookup_location_not_found_empty_results() -> None:
    """Tests location lookup when results list is empty."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = {"results": []}
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        result = lookup_location("Atlantis")
        assert (
            "❌ Could not find any location coordinates matching 'Atlantis'." in result
        )


def test_lookup_location_not_found_missing_results_key() -> None:
    """Tests location lookup when payload lacks the 'results' key completely."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = {}
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        result = lookup_location("Nowhere")
        assert (
            "❌ Could not find any location coordinates matching 'Nowhere'." in result
        )


def test_lookup_location_http_error() -> None:
    """Tests location lookup when geocoding API returns an HTTP error."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "500 Internal Server Error"
    )

    with patch("requests.get", return_value=mock_response):
        result = lookup_location("Berlin")
        assert (
            "Error during location lookup for 'Berlin': 500 Internal Server Error"
            in result
        )


def test_lookup_location_timeout() -> None:
    """Tests location lookup when network request times out."""
    with patch(
        "requests.get",
        side_effect=requests.exceptions.Timeout("Connection timed out"),
    ):
        result = lookup_location("Rome")
        assert "Error during location lookup for 'Rome': Connection timed out" in result


def test_lookup_location_request_exception() -> None:
    """Tests location lookup error handling on network exception."""
    with patch(
        "requests.get",
        side_effect=requests.exceptions.ConnectionError("DNS lookup failed"),
    ):
        result = lookup_location("Paris")
        assert "Error during location lookup for 'Paris': DNS lookup failed" in result


def test_lookup_location_special_characters() -> None:
    """Tests location lookup with spaces and non-ASCII characters."""
    mock_payload: dict[str, Any] = {
        "results": [
            {
                "name": "São Paulo",
                "country": "Brazil",
                "admin1": "São Paulo",
                "latitude": -23.5505,
                "longitude": -46.6333,
            }
        ]
    }
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = mock_payload
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response) as mock_get:
        result = lookup_location("São Paulo")
        mock_get.assert_called_once_with(
            "https://geocoding-api.open-meteo.com/v1/search?name=São Paulo&count=1&language=en"
        )
        assert "Found Location: São Paulo, São Paulo, Brazil" in result
        assert "Latitude: -23.5505" in result


# --- Tests for get_weather ---


def test_get_weather_success() -> None:
    """Tests retrieving weather for a city successfully."""
    mock_geo_resp = MagicMock(spec=requests.Response)
    mock_geo_resp.json.return_value = {
        "results": [{"latitude": 35.6762, "longitude": 139.6503}]
    }
    mock_geo_resp.raise_for_status.return_value = None

    mock_weather_resp = MagicMock(spec=requests.Response)
    mock_weather_resp.json.return_value = {
        "current": {
            "time": "2026-09-27T15:00",
            "temperature_2m": 21.0,
            "wind_speed_10m": 8.0,
        }
    }
    mock_weather_resp.raise_for_status.return_value = None

    with patch(
        "requests.get", side_effect=[mock_geo_resp, mock_weather_resp]
    ) as mock_get:
        result = get_weather("Tokyo")

        assert mock_get.call_count == 2
        assert "name=Tokyo" in mock_get.call_args_list[0][0][0]
        forecast_url: str = mock_get.call_args_list[1][0][0]
        assert "latitude=35.6762&longitude=139.6503" in forecast_url
        assert "timezone=auto" in forecast_url
        assert "current=temperature_2m,wind_speed_10m" in forecast_url
        assert (
            "hourly=temperature_2m,relative_humidity_2m,wind_speed_10m" in forecast_url
        )
        assert "🌍 Weather Report 🌍" in result
        assert "Time:    2026-09-27T15:00" in result
        assert "Temperature: 21.0°C" in result
        assert "Wind speed: 8.0km/h" in result


def test_get_weather_subzero_and_calm() -> None:
    """Tests retrieving weather with negative temperature and zero wind speed."""
    mock_geo_resp = MagicMock(spec=requests.Response)
    mock_geo_resp.json.return_value = {
        "results": [{"latitude": 64.1466, "longitude": -21.9426}]
    }
    mock_geo_resp.raise_for_status.return_value = None

    mock_weather_resp = MagicMock(spec=requests.Response)
    mock_weather_resp.json.return_value = {
        "current": {
            "time": "2026-12-25T12:00",
            "temperature_2m": -15.4,
            "wind_speed_10m": 0.0,
        }
    }
    mock_weather_resp.raise_for_status.return_value = None

    with patch("requests.get", side_effect=[mock_geo_resp, mock_weather_resp]):
        result = get_weather("Reykjavik")
        assert "Temperature: -15.4°C" in result
        assert "Wind speed: 0.0km/h" in result


def test_get_weather_city_not_found_empty_list() -> None:
    """Tests get_weather when city coordinates cannot be found (empty results)."""
    mock_geo_resp = MagicMock(spec=requests.Response)
    mock_geo_resp.json.return_value = {"results": []}
    mock_geo_resp.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_geo_resp) as mock_get:
        result = get_weather("NonExistentPlace")

        assert mock_get.call_count == 1
        assert (
            "❌ Could not find any location coordinates matching 'NonExistentPlace'."
            in result
        )


def test_get_weather_city_not_found_missing_results() -> None:
    """Tests get_weather when geocoding response lacks 'results' key."""
    mock_geo_resp = MagicMock(spec=requests.Response)
    mock_geo_resp.json.return_value = {}
    mock_geo_resp.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_geo_resp):
        result = get_weather("MissingKeyPlace")
        assert (
            "❌ Could not find any location coordinates matching 'MissingKeyPlace'."
            in result
        )


def test_get_weather_geocoding_exception() -> None:
    """Tests get_weather handling network failure during geocoding step."""
    with patch(
        "requests.get",
        side_effect=requests.exceptions.ConnectionError("Geocoding connection timeout"),
    ):
        result = get_weather("Sydney")
        assert (
            "Error fetching weather data for coordinates (None, None) of city Sydney"
            in result
        )
        assert "Geocoding connection timeout" in result


def test_get_weather_geocoding_http_error() -> None:
    """Tests get_weather handling HTTP error during geocoding step."""
    mock_geo_resp = MagicMock(spec=requests.Response)
    mock_geo_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "503 Service Unavailable"
    )

    with patch("requests.get", return_value=mock_geo_resp):
        result = get_weather("Melbourne")
        assert (
            "Error fetching weather data for coordinates (None, None) of city Melbourne"
            in result
        )
        assert "503 Service Unavailable" in result


def test_get_weather_forecast_exception() -> None:
    """Tests get_weather handling HTTP failure during forecast step."""
    mock_geo_resp = MagicMock(spec=requests.Response)
    mock_geo_resp.json.return_value = {
        "results": [{"latitude": 51.5074, "longitude": -0.1278}]
    }
    mock_geo_resp.raise_for_status.return_value = None

    with patch(
        "requests.get",
        side_effect=[
            mock_geo_resp,
            requests.exceptions.HTTPError("500 Internal Server Error"),
        ],
    ):
        result = get_weather("London")
        assert (
            "Error fetching weather data for coordinates (51.5074, -0.1278) of city London"
            in result
        )
        assert "500 Internal Server Error" in result


def test_get_weather_forecast_timeout() -> None:
    """Tests get_weather handling request timeout during forecast step."""
    mock_geo_resp = MagicMock(spec=requests.Response)
    mock_geo_resp.json.return_value = {
        "results": [{"latitude": 40.7128, "longitude": -74.0060}]
    }
    mock_geo_resp.raise_for_status.return_value = None

    with patch(
        "requests.get",
        side_effect=[
            mock_geo_resp,
            requests.exceptions.Timeout("Forecast timed out"),
        ],
    ):
        result = get_weather("New York")
        assert (
            "Error fetching weather data for coordinates (40.7128, -74.006) of city New York"
            in result
        )
        assert "Forecast timed out" in result


# --- Tests for get_canberra_weather ---


def test_get_canberra_weather_success() -> None:
    """Tests retrieving Canberra weather successfully and verifying parameters."""
    mock_resp = MagicMock(spec=requests.Response)
    mock_resp.json.return_value = {
        "current": {
            "time": "2026-09-27T18:00",
            "temperature_2m": 23.1,
            "wind_speed_10m": 12.0,
        }
    }
    mock_resp.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_resp) as mock_get:
        result = get_canberra_weather()

        mock_get.assert_called_once()
        called_url: str = mock_get.call_args[0][0]
        assert "latitude=-35.2835" in called_url
        assert "longitude=149.1281" in called_url
        assert "timezone=Australia%2FSydney" in called_url
        assert "current=temperature_2m,wind_speed_10m" in called_url
        assert "hourly=temperature_2m,relative_humidity_2m,wind_speed_10m" in called_url
        assert "☀️ Canberra Current Weather ☀️" in result
        assert "Time:    2026-09-27T18:00" in result
        assert "Temperature: 23.1°C" in result
        assert "Wind speed: 12.0km/h" in result


def test_get_canberra_weather_subzero() -> None:
    """Tests Canberra weather retrieval with subzero temperature and zero wind."""
    mock_resp = MagicMock(spec=requests.Response)
    mock_resp.json.return_value = {
        "current": {
            "time": "2026-07-01T07:00",
            "temperature_2m": -4.2,
            "wind_speed_10m": 0.0,
        }
    }
    mock_resp.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_resp):
        result = get_canberra_weather()
        assert "Temperature: -4.2°C" in result
        assert "Wind speed: 0.0km/h" in result


def test_get_canberra_weather_http_error() -> None:
    """Tests get_canberra_weather error handling on HTTP 503 error."""
    mock_resp = MagicMock(spec=requests.Response)
    mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "503 Service Unavailable"
    )

    with patch("requests.get", return_value=mock_resp):
        result = get_canberra_weather()
        assert "Error fetching weather data: 503 Service Unavailable" in result


def test_get_canberra_weather_timeout() -> None:
    """Tests get_canberra_weather error handling on timeout."""
    with patch(
        "requests.get",
        side_effect=requests.exceptions.Timeout("Canberra request timed out"),
    ):
        result = get_canberra_weather()
        assert "Error fetching weather data: Canberra request timed out" in result


def test_get_canberra_weather_exception() -> None:
    """Tests get_canberra_weather error handling on general request failure."""
    with patch(
        "requests.get",
        side_effect=requests.exceptions.RequestException("Canberra service offline"),
    ):
        result = get_canberra_weather()
        assert "Error fetching weather data: Canberra service offline" in result


# --- FastMCP Server Tool Registration & Invocation Tests ---


def test_mcp_server_properties() -> None:
    """Tests FastMCP server instance configuration."""
    assert mcp.name == "Global Weather & Location Server"


def test_mcp_registered_tools() -> None:
    """Tests that all 3 weather tools are properly registered with valid schemas on the FastMCP server."""
    tools = asyncio.run(mcp.list_tools())
    tool_names = [tool.name for tool in tools]

    assert "lookup_location" in tool_names
    assert "get_weather" in tool_names
    assert "get_canberra_weather" in tool_names

    tool_dict = {t.name: t for t in tools}

    # Verify lookup_location schema
    loc_tool = tool_dict["lookup_location"]
    assert "name" in loc_tool.input_schema.get("properties", {})
    assert "name" in loc_tool.input_schema.get("required", [])
    assert loc_tool.description is not None
    assert "geographic coordinates" in loc_tool.description

    # Verify get_weather schema
    weather_tool = tool_dict["get_weather"]
    assert "city" in weather_tool.input_schema.get("properties", {})
    assert "city" in weather_tool.input_schema.get("required", [])
    assert weather_tool.description is not None
    assert "current weather" in weather_tool.description

    # Verify get_canberra_weather schema
    canberra_tool = tool_dict["get_canberra_weather"]
    assert canberra_tool.description is not None
    assert "Canberra" in canberra_tool.description


def test_mcp_call_tool_lookup_location_success() -> None:
    """Tests calling the lookup_location tool via the FastMCP server interface."""
    mock_payload: dict[str, Any] = {
        "results": [
            {
                "name": "Canberra",
                "country": "Australia",
                "admin1": "ACT",
                "latitude": -35.2835,
                "longitude": 149.1281,
            }
        ]
    }
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = mock_payload
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        result = asyncio.run(mcp.call_tool("lookup_location", {"name": "Canberra"}))
        assert result.content[0].type == "text"
        assert "📍 Found Location: Canberra, ACT, Australia" in result.content[0].text
        assert "Latitude: -35.2835" in result.content[0].text


def test_mcp_call_tool_lookup_location_not_found() -> None:
    """Tests calling lookup_location tool via FastMCP when location does not exist."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = {"results": []}
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        result = asyncio.run(mcp.call_tool("lookup_location", {"name": "Nonexistent"}))
        assert "❌ Could not find any location coordinates" in result.content[0].text


def test_mcp_call_tool_get_weather_success() -> None:
    """Tests calling the get_weather tool via the FastMCP server interface."""
    mock_geo_resp = MagicMock(spec=requests.Response)
    mock_geo_resp.json.return_value = {
        "results": [{"latitude": 48.8566, "longitude": 2.3522}]
    }
    mock_geo_resp.raise_for_status.return_value = None

    mock_weather_resp = MagicMock(spec=requests.Response)
    mock_weather_resp.json.return_value = {
        "current": {
            "time": "2026-09-27T16:00",
            "temperature_2m": 18.5,
            "wind_speed_10m": 14.2,
        }
    }
    mock_weather_resp.raise_for_status.return_value = None

    with patch("requests.get", side_effect=[mock_geo_resp, mock_weather_resp]):
        result = asyncio.run(mcp.call_tool("get_weather", {"city": "Paris"}))
        assert result.content[0].type == "text"
        assert "🌍 Weather Report 🌍" in result.content[0].text
        assert "Temperature: 18.5°C" in result.content[0].text
        assert "Wind speed: 14.2km/h" in result.content[0].text


def test_mcp_call_tool_get_canberra_weather_success() -> None:
    """Tests calling the get_canberra_weather tool via the FastMCP server interface."""
    mock_resp = MagicMock(spec=requests.Response)
    mock_resp.json.return_value = {
        "current": {
            "time": "2026-09-27T18:00",
            "temperature_2m": 23.1,
            "wind_speed_10m": 12.0,
        }
    }
    mock_resp.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_resp):
        result = asyncio.run(mcp.call_tool("get_canberra_weather", {}))
        assert result.content[0].type == "text"
        assert "☀️ Canberra Current Weather ☀️" in result.content[0].text
        assert "Temperature: 23.1°C" in result.content[0].text


# --- Main execution tests ---


def test_main_execution() -> None:
    """Tests executing weather_server as __main__ invokes mcp.run()."""
    with patch("mcp.server.mcpserver.MCPServer.run") as mock_run:
        runpy.run_module("weather_server", run_name="__main__")
        mock_run.assert_called_once()

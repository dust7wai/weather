# weather

The uv shebang at the top allows
- the scripts to run directly
- without manually creating a virtual environment
- or installing requests and other dependencies

## Canberra Current Weather (weather_now.py)

This script retrieves the current weather for Canberra
using the Open-Meteo API.

Requirements:
- Python
- uv (https://docs.astral.sh/uv/)

### Make the script executable:

```bash
chmod +x ./weather_now.py
```

### Run the script:

```bash
./weather_now.py
```

### Sample output:

```text
 ☀️ Canberra Current Weather ☀️
 Time:    2026-09-26T17:30
 Temperature: 22.4°C
 Wind speed: 11.5km/h #
```

## Canberra 7-day Weather Forecast (weather_7days.py)

This script retrieves the 7-day Weather Forecast for Canberra
using the Open-Meteo API.

Requirements:
- Python
- uv (https://docs.astral.sh/uv/)

### 1. Make the script executable:

```bash
chmod +x ./weather_7days.py
```

### 2. Run the script:

```bash
./weather_7days.py
```

### Sample output:

```text
 ☀️ Canberra 7-day Weather Forecast☀️

 Date          Day         Min     Max     Rain
 2026-09-26    Saturday    8.2°C   22.4°C  10%
 2026-09-27    Sunday      9.1°C   24.1°C  20%
 2026-09-28    Monday      7.5°C   19.8°C  30%
 2026-09-29    Tuesday     6.9°C   18.5°C  40%
 2026-09-30    Wednesday   10.2°C  21.7°C  20%
 2026-10-01    Thursday    11.4°C  25.3°C  10%
 2026-10-02    Friday      12.0°C  27.1°C  10%
```

## Canberra Current Weather MCP Server (weather_server.py)

This script expose a FastMCP instance that retrieves the current weather for Canberra
using the Open-Meteo API.

Requirements:
- Python
- uv (https://docs.astral.sh/uv/)
```bash
uv pip install mcp[cli]
```

### 1. Make the script executable:

```bash
chmod +x ./weather_server.py
```

### 2. Test using the MCP inspector:

```bash
uvx --with "mcp[cli]" --with "requestS" mcp dev ./weather_server.py
```

### 3. Test with Terminal for server output:
```bash: 
(
  echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}, "id": 1}\n'
  echo '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2}\n'
  echo '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "lookup_location", "arguments": {"name": "Canberra"}}, "id": 3}\n'
  echo ' {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "get_weather", "arguments": {"city": "Canberra"}}, "id": 4}'
) | uv run --with mcp==2.3.0 mcp run ./weather_server.py
````

### 4. Test with Terminal interactively:
```bash
cat | uv run --with mcp==2.3.0 mcp run ./weather_server.py
{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}, "id": 1}
{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2}
{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "lookup_location", "arguments": {"name": "Canberra"}}, "id": 3}
{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "get_weather", "arguments": {"city": "Canberra"}}, "id": 4}
```

### 5. Claude Desktop Integration:
``` json
{
    "mcpServers": {
        "weather-mcp-server": {
            "command": "uv",
            "args": [
                "run",
                "--with",
                "mcp==2.3.0",
                "mcp",
                "run",
                "/absolute/path/to/your/weather_server.py"
            ]
        }
    }
}
```

## Running Tests

Run the test suite using `uv`:

```bash
# Run unit tests
uv run pytest -m "not integration"

# Run all tests (including live Open-Meteo integration tests)
uv run pytest
```
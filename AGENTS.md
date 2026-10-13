# Python Development Guidelines
All code contributed to this project must adhere to the following principles.

## 1. Formatting & Linting
All Python code **must** be formatted and linted using `ruff` (or `black` and `isort`) before being submitted. 
- Follow **PEP 8** style guidelines strictly.
- Ensure all imports are sorted.

## 2. Naming Conventions
- **Packages and Modules:** Use short, all-lowercase names. Use underscores if it improves readability (e.g., `weather_server`).
- **Classes:** Use `PascalCase` (e.g., `McpServer`).
- **Functions, Methods, and Variables:** Use `snake_case` (e.g., `lookup_location`).
- **Constants:** Use all-uppercase `SNAKE_CASE` (e.g., `MAX_RETIRES`).

## 3. Error Handling
- Exceptions should be specific. Avoid catching generic `Exception` unless re-raising or logging with full traceback context.
- Always validate inputs and handle potential connection/runtime faults gracefully using `try-except` blocks.
- **Use `sys.stderr` or the standard `logging` library for debug prints.** Do NOT use standard output (`print()`) for logging, as this pollutes the JSON-RPC stream used for `stdio` transport and crashes the connection.

## 4. Simplicity and Clarity
- "Beautiful is better than ugly. Explicit is better than implicit." Write code that is easy to understand.
- Leverage **type hints** for all function signatures and variable declarations to ensure static analysis catches bugs early.
- Avoid over-engineering, deeply nested structures, or unnecessary abstract base classes.

## 5. Documentation
- All public modules, classes, functions, and tools **must** have descriptive docstrings (prefer Google or Sphinx style).
- Tool docstrings are structurally critical, as LLMs use them to understand functionality. Ensure parameter descriptions are explicit.
- Inline comments should explain the *why*, not the *what*.

## 6. Project Structure
- `src/` or root directory containing source code for target entry points (e.g., `server.py`).
- `internal/` or `_internal/` can be used to signify private modules not intended for external API consumption.
- Use `pyproject.toml` at the root for dependency and tool configuration (e.g., managing packages via `uv`, `poetry`, or `pip`).
- At the root, place `README.md`, `AGENTS.md`, and environment lockfiles.

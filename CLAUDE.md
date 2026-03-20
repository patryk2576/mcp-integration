# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP (Model Context Protocol) server implementation using FastMCP with OpenAI Agents SDK integration. The project demonstrates:
- MCP server with custom tools (add, get_secret_word, get_current_weather)
- OpenAI Agents SDK for multi-agent workflows with triage, specialist handoffs, and LLM-as-judge evaluation
- Streamable HTTP transport for MCP communication

## Commands

**Run MCP server:**
```bash
uv run python -m src.main
# or
python src/main.py
```

**Run tests:**
```bash
uv run pytest
uv run pytest -k test_add  # run single test
```

**Run agent workflow:**
```bash
uv run python src/agent.py
```

## Architecture

- **src/main.py**: MCP server using FastMCP with three tools exposed via streamable HTTP
- **src/agent.py**: Multi-agent system using OpenAI Agents SDK with triage routing and evaluator loop
- **tests/test_main.py**: Pytest suite with fixture that spawns server as subprocess for integration testing

## Configuration

- Python 3.12 (uv/uv.lock)
- Environment variables via `.env` file in parent directory: `OPENAI_API_KEY`, `MCP_HOST`, `MCP_PORT`, `MCP_PATH`
- Default MCP endpoint: `http://localhost:8080/mcp`
- VS Code MCP config in `.vscode/mcp.json`

## Testing Notes

- Server fixture in `test_server` spawns `src.main` as subprocess to avoid blocking pytest
- Tests use `stream=True` with SSE parsing for MCP responses
- Log output configured to both console and `pytest.log` file

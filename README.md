# FinAssist — MCP-based Personal Finance Chatbot

Project 1 for CC3067 Networks (Universidad del Valle de Guatemala) —
"Use of an existing protocol" (Model Context Protocol).

## Overview

FinAssist is a web chatbot that acts as an MCP **host**, coordinating
multiple MCP **servers** (the official Filesystem and Git servers, plus
a custom FinAssist server for personal finance management) to answer
general questions and perform actions on behalf of the user, powered by
the Claude API.

The MCP protocol (JSON-RPC 2.0 based) is implemented manually in this
project — no MCP SDK (e.g. FastMCP) is used.

## Features implemented

- [ ] Connection to the Claude API (general Q&A)
- [ ] Session context handling
- [ ] Logging of all MCP server interactions
- [ ] Integration with the official Filesystem MCP server
- [ ] Integration with the official Git MCP server
- [ ] Custom local MCP server: FinAssist (personal finance)
- [ ] Custom remote MCP server: FinAssist deployed to the cloud
- [ ] Wireshark analysis of client-server communication
- [ ] Web UI

*(Checklist to be updated as functionalities are completed)*

## Project structure

```
host/            # MCP host (chatbot) — FastAPI + web UI
mcp_servers/     # MCP servers (official + custom FinAssist)
docs/            # Report, Wireshark captures and analysis
tests/           # Tests
```

## Requirements

- Python 3.11+
- An Anthropic API key (see https://console.anthropic.com)

## Installation

```bash
git clone <repo-url>
cd proyecto1-redes
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Usage

```bash
uvicorn host.main:app --reload --port 8000
```

Then open `http://localhost:8000` in your browser.

*(TODO: add instructions for running the custom FinAssist MCP server
standalone, and for connecting to its remote deployment, once
implemented)*

## Author

Adrián González — Universidad del Valle de Guatemala

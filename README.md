# FinAssist — MCP-based Personal Finance Chatbot

Project 1 for CC3067 Networks (Universidad del Valle de Guatemala) —
"Use of an existing protocol" (Model Context Protocol).

## Overview

FinAssist is a web chatbot that acts as an MCP **host**, coordinating
multiple MCP **servers** (the official Filesystem and Git servers, plus
a custom FinAssist server for personal finance management) to answer
general questions and perform actions on behalf of the user, powered by
the Gemini API.

The MCP protocol (JSON-RPC 2.0 based) is implemented manually in this
project — no MCP SDK (e.g. FastMCP) is used.

## Features implemented

- [x] Connection to the Claude API (general Q&A)
- [x] Session context handling
- [x] Logging of all MCP server interactions
- [x] Integration with the official Filesystem MCP server
- [x] Integration with the official Git MCP server
- [x] Custom local MCP server: FinAssist (personal finance)
- [x] Custom remote MCP server: FinAssist deployed to the cloud
- [ ] Wireshark analysis of client-server communication
- [x] Web UI

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
- A Gemini API key (see https://aistudio.google.com/apikey)
- Node.js (needed for `npx`, used to run the official Filesystem MCP server)
- Git installed and available in your PATH

## Installation

```bash
git clone <repo-url>
cd proyecto1-redes
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

## Usage

```bash
uvicorn host.main:app --port 8000
```

Note: do not use `--reload` — on Windows it forces an event loop that
does not support the subprocesses used to launch the local MCP
servers (see `host/main.py` for details).

Then open `http://localhost:8000` in your browser.

To run the custom FinAssist MCP server on its own (outside the
chatbot), for debugging:

```bash
cd mcp_servers/finassist
python3 test_server_manual.py
```

To use the remote (cloud-deployed) FinAssist server instead of the
local one, set `FINASSIST_REMOTE_URL` in `.env` (see
`mcp_servers/finassist/SPEC.md` for deployment instructions).

## Author

Adrián González — Universidad del Valle de Guatemala

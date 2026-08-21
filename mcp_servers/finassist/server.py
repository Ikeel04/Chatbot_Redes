"""
Servidor MCP de FinAssist - version LOCAL (transporte stdio).

Implementa manualmente el protocolo MCP sobre JSON-RPC 2.0, leyendo
mensajes de stdin y escribiendo respuestas en stdout, SIN usar ningun
SDK de MCP (FastMCP, etc.), tal como exige el enunciado.

La logica de despacho (initialize, tools/list, tools/call) vive en
dispatch.py, compartida con server_remote.py (version HTTP) para que
ambos transportes se comporten identico.
"""

import sys
import json

from db import init_db
from dispatch import handle_message, _error


def main():
    init_db()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            sys.stdout.write(json.dumps(_error(None, -32700, "Parse error")) + "\n")
            sys.stdout.flush()
            continue

        response = handle_message(message)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()

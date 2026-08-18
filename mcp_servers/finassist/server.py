"""
Servidor MCP de FinAssist - version LOCAL (transporte stdio).

Implementa manualmente el protocolo MCP sobre JSON-RPC 2.0, leyendo
mensajes de stdin y escribiendo respuestas en stdout, SIN usar ningun
SDK de MCP (FastMCP, etc.), tal como exige el enunciado.

Metodos que debe soportar como minimo:
    - initialize
    - tools/list
    - tools/call

TODO (siguiente paso):
    1. Loop principal: leer linea de stdin, parsear JSON-RPC
    2. Segun "method", despachar a la logica correspondiente
    3. Escribir la respuesta JSON-RPC en stdout (con el mismo "id")
    4. Manejar errores segun especificacion JSON-RPC (codigo, mensaje)
"""

import sys
import json

from db import init_db
from tools import TOOLS, ejecutar_tool

SERVER_INFO = {
    "name": "finassist-mcp-server",
    "version": "0.1.0",
}


def handle_message(message: dict) -> dict | None:
    method = message.get("method")
    msg_id = message.get("id")

    if method == "initialize":
        # TODO: retornar capabilities y serverInfo segun especificacion MCP
        pass
    elif method == "tools/list":
        # TODO: retornar {"tools": TOOLS}
        pass
    elif method == "tools/call":
        # TODO: extraer params.name y params.arguments, llamar ejecutar_tool()
        pass
    else:
        # TODO: responder con error JSON-RPC "Method not found" (-32601)
        pass

    return None  # TODO: retornar el mensaje de respuesta JSON-RPC


def main():
    init_db()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue  # TODO: responder error de parseo (-32700)

        response = handle_message(message)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()

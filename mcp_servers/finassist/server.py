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

PROTOCOL_VERSION = "2025-06-18"


def _success(msg_id, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def _error(msg_id, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def handle_message(message: dict) -> dict | None:
    method = message.get("method")
    msg_id = message.get("id")
    params = message.get("params", {}) or {}

    # Las notificaciones (sin "id") no requieren respuesta, ej. "notifications/initialized"
    if msg_id is None:
        return None

    if method == "initialize":
        return _success(msg_id, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {
                "tools": {}
            },
            "serverInfo": SERVER_INFO,
        })

    if method == "tools/list":
        return _success(msg_id, {"tools": TOOLS})

    if method == "tools/call":
        nombre_tool = params.get("name")
        argumentos = params.get("arguments", {}) or {}
        try:
            resultado = ejecutar_tool(nombre_tool, argumentos)
            return _success(msg_id, {
                "content": [
                    {"type": "text", "text": json.dumps(resultado, ensure_ascii=False)}
                ],
                "isError": False,
            })
        except Exception as exc:
            return _success(msg_id, {
                "content": [{"type": "text", "text": f"Error al ejecutar la tool: {exc}"}],
                "isError": True,
            })

    return _error(msg_id, -32601, f"Method not found: {method}")


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

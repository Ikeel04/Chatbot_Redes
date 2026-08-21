"""
Logica de despacho JSON-RPC 2.0 / MCP compartida entre el servidor
LOCAL (server.py, transporte stdio) y el servidor REMOTO
(server_remote.py, transporte HTTP). Ambos exponen exactamente las
mismas tools y el mismo comportamiento; solo cambia el transporte por
el que viajan los mensajes.
"""

import json

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
    """
    Procesa un unico mensaje JSON-RPC 2.0 y retorna la respuesta
    correspondiente (o None si es una notificacion, que no requiere
    respuesta segun la especificacion).
    """
    method = message.get("method")
    msg_id = message.get("id")
    params = message.get("params", {}) or {}

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

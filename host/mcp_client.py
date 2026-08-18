"""
Cliente MCP (Model Context Protocol) implementado manualmente sobre JSON-RPC 2.0.

Este cliente NO utiliza SDKs de MCP (como FastMCP). Implementa a mano:
    - El handshake inicial (metodo "initialize")
    - El listado de herramientas ("tools/list")
    - La invocacion de herramientas ("tools/call")
    - El envio/recepcion de mensajes JSON-RPC 2.0

Soporta dos transportes:
    - stdio: para servidores MCP locales (subprocess)
    - http/sse: para servidores MCP remotos

TODO (siguiente paso): implementar la clase MCPClient con:
    - conectar(): inicia el subprocess o la sesion HTTP
    - initialize(): realiza el handshake segun la especificacion MCP
    - list_tools(): pide al servidor su lista de herramientas disponibles
    - call_tool(name, arguments): invoca una herramienta y retorna el resultado
    - cerrar(): cierra la conexion/subprocess
"""

import json
import uuid


class JsonRpcMessage:
    """Utilidades para construir mensajes JSON-RPC 2.0 validos."""

    @staticmethod
    def build_request(method: str, params: dict | None = None, request_id: str | None = None) -> dict:
        return {
            "jsonrpc": "2.0",
            "id": request_id or str(uuid.uuid4()),
            "method": method,
            "params": params or {},
        }

    @staticmethod
    def build_notification(method: str, params: dict | None = None) -> dict:
        # Las notificaciones no llevan "id": no esperan respuesta
        return {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
        }

    @staticmethod
    def serialize(message: dict) -> str:
        return json.dumps(message)

    @staticmethod
    def parse(raw: str) -> dict:
        return json.loads(raw)


class MCPClient:
    """
    Cliente MCP generico. Se instancia una vez por cada servidor MCP
    con el que el anfitrion (host) necesita comunicarse.
    """

    def __init__(self, server_name: str, transport: str = "stdio"):
        self.server_name = server_name
        self.transport = transport  # "stdio" | "http"
        self.tools: list[dict] = []
        # TODO: inicializar el transporte correspondiente

    async def connect(self):
        # TODO: lanzar subprocess (stdio) o abrir sesion http/sse (remoto)
        raise NotImplementedError

    async def initialize(self):
        # TODO: enviar mensaje "initialize" segun especificacion MCP
        # y guardar las capabilities del servidor
        raise NotImplementedError

    async def list_tools(self) -> list[dict]:
        # TODO: enviar "tools/list" y guardar en self.tools
        raise NotImplementedError

    async def call_tool(self, name: str, arguments: dict) -> dict:
        # TODO: enviar "tools/call" con el nombre y argumentos de la tool
        raise NotImplementedError

    async def close(self):
        # TODO: cerrar subprocess o sesion http
        raise NotImplementedError

"""
Cliente MCP (Model Context Protocol) implementado manualmente sobre JSON-RPC 2.0.

Este cliente NO utiliza SDKs de MCP (como FastMCP). Implementa a mano:
    - El handshake inicial (metodo "initialize")
    - El listado de herramientas ("tools/list")
    - La invocacion de herramientas ("tools/call")
    - El envio/recepcion de mensajes JSON-RPC 2.0

Soporta dos transportes:
    - stdio: para servidores MCP locales (subprocess)
    - http: para servidores MCP remotos
"""

import asyncio
import json
import uuid

import httpx

PROTOCOL_VERSION = "2025-06-18"
CLIENT_INFO = {"name": "finassist-mcp-host", "version": "0.1.0"}


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


class MCPClientError(Exception):
    """Error retornado por el servidor MCP (bloque "error" de JSON-RPC)."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class MCPClient:
    """
    Cliente MCP generico. Se instancia una vez por cada servidor MCP
    con el que el anfitrion (host) necesita comunicarse.

    transport="stdio": lanza `command` (lista de argv) como subprocess
                        y habla JSON-RPC por su stdin/stdout.
    transport="http":  hace POST a `url` con cada mensaje JSON-RPC.
    """

    def __init__(self, server_name: str, transport: str = "stdio",
                 command: list[str] | None = None, url: str | None = None):
        self.server_name = server_name
        self.transport = transport  # "stdio" | "http"
        self.command = command
        self.url = url

        self.tools: list[dict] = []
        self.server_info: dict = {}

        self._process: asyncio.subprocess.Process | None = None
        self._http_client: httpx.AsyncClient | None = None
        self._pending: dict[str, asyncio.Future] = {}
        self._reader_task: asyncio.Task | None = None

    # ---------------------------------------------------------------
    # Ciclo de vida de la conexion
    # ---------------------------------------------------------------

    async def connect(self):
        if self.transport == "stdio":
            if not self.command:
                raise ValueError("Se requiere 'command' para transporte stdio")
            self._process = await asyncio.create_subprocess_exec(
                *self.command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            self._reader_task = asyncio.create_task(self._read_stdio_loop())
        elif self.transport == "http":
            if not self.url:
                raise ValueError("Se requiere 'url' para transporte http")
            self._http_client = httpx.AsyncClient(timeout=30.0)
        else:
            raise ValueError(f"Transporte no soportado: {self.transport}")

    async def close(self):
        if self.transport == "stdio" and self._process:
            if self._reader_task:
                self._reader_task.cancel()
            self._process.stdin.close()
            await self._process.wait()
        elif self.transport == "http" and self._http_client:
            await self._http_client.aclose()

    # ---------------------------------------------------------------
    # Transporte: envio/recepcion de mensajes JSON-RPC
    # ---------------------------------------------------------------

    async def _read_stdio_loop(self):
        """Lee lineas de stdout del subprocess y resuelve las futures pendientes."""
        while True:
            line = await self._process.stdout.readline()
            if not line:
                break
            try:
                message = JsonRpcMessage.parse(line.decode().strip())
            except json.JSONDecodeError:
                continue

            msg_id = message.get("id")
            if msg_id is not None and msg_id in self._pending:
                future = self._pending.pop(msg_id)
                if not future.done():
                    future.set_result(message)

    async def _send_request(self, method: str, params: dict | None = None) -> dict:
        request = JsonRpcMessage.build_request(method, params)
        msg_id = request["id"]

        if self.transport == "stdio":
            future = asyncio.get_event_loop().create_future()
            self._pending[msg_id] = future

            self._process.stdin.write((JsonRpcMessage.serialize(request) + "\n").encode())
            await self._process.stdin.drain()

            response = await asyncio.wait_for(future, timeout=30.0)
        else:  # http
            resp = await self._http_client.post(self.url, json=request)
            resp.raise_for_status()
            response = resp.json()

        if "error" in response:
            err = response["error"]
            raise MCPClientError(err.get("code", -1), err.get("message", "Error desconocido"))

        return response.get("result", {})

    # ---------------------------------------------------------------
    # Metodos MCP de alto nivel
    # ---------------------------------------------------------------

    async def initialize(self):
        result = await self._send_request("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": CLIENT_INFO,
        })
        self.server_info = result.get("serverInfo", {})
        return result

    async def list_tools(self) -> list[dict]:
        result = await self._send_request("tools/list")
        self.tools = result.get("tools", [])
        return self.tools

    async def call_tool(self, name: str, arguments: dict) -> dict:
        return await self._send_request("tools/call", {
            "name": name,
            "arguments": arguments,
        })

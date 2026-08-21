"""
MCPManager: el "anfitrion" coordina multiples clientes MCP (filesystem,
git, finassist local, finassist remoto, etc.) y expone una interfaz
unificada de herramientas al LLM.

registrar_servidor() acepta tanto servidores locales (transport="stdio",
con su "command") como remotos (transport="http", con su "url").
"""

from host.mcp_client import MCPClient
from host.logger import mcp_logger


class MCPManager:
    def __init__(self):
        self.clientes: dict[str, MCPClient] = {}
        # Mapea nombre_de_tool -> nombre_del_servidor que la implementa
        self.tool_to_server: dict[str, str] = {}

    def registrar_servidor(self, nombre: str, transport: str = "stdio",
                            command: list[str] | None = None, url: str | None = None):
        self.clientes[nombre] = MCPClient(
            server_name=nombre, transport=transport, command=command, url=url
        )

    async def conectar_todos(self):
        """
        Conecta, inicializa (handshake) y lista las tools de cada
        servidor registrado. Puebla tool_to_server para poder despachar
        las llamadas de tools/call al servidor correcto.
        """
        for nombre, cliente in self.clientes.items():
            await cliente.connect()
            await cliente.initialize()
            tools = await cliente.list_tools()

            for tool in tools:
                tool_name = tool["name"]
                if tool_name in self.tool_to_server:
                    otro_servidor = self.tool_to_server[tool_name]
                    raise ValueError(
                        f"Conflicto de nombres: la tool '{tool_name}' esta "
                        f"definida tanto en '{otro_servidor}' como en '{nombre}'"
                    )
                self.tool_to_server[tool_name] = nombre

    async def cerrar_todos(self):
        for cliente in self.clientes.values():
            await cliente.close()

    def obtener_herramientas_disponibles(self) -> list[dict]:
        """
        Junta las tools de todos los servidores conectados y las
        convierte al formato de "function declarations" que espera la
        API de Gemini:

            {"name": ..., "description": ..., "parameters": <JSON Schema>}

        (MCP ya usa "inputSchema" en formato JSON Schema, asi que solo
        se renombra la llave a "parameters".)
        """
        herramientas = []
        for cliente in self.clientes.values():
            for tool in cliente.tools:
                herramientas.append({
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", {"type": "object", "properties": {}}),
                })
        return herramientas

    async def ejecutar_herramienta(self, nombre_tool: str, argumentos: dict) -> dict:
        servidor = self.tool_to_server.get(nombre_tool)
        if servidor is None:
            raise ValueError(f"Herramienta desconocida: {nombre_tool}")

        mcp_logger.log_request(servidor, nombre_tool, argumentos)
        resultado = await self.clientes[servidor].call_tool(nombre_tool, argumentos)
        mcp_logger.log_response(servidor, nombre_tool, resultado)
        return resultado

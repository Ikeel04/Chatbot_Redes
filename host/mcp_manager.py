"""
MCPManager: el "anfitrion" coordina multiples clientes MCP (filesystem,
git, finassist local, finassist remoto, etc.) y expone una interfaz
unificada de herramientas al LLM.

TODO (siguiente paso):
    - registrar_servidor(nombre, config): agrega un MCPClient a self.clientes
    - conectar_todos(): llama connect() + initialize() + list_tools() en cada cliente
    - obtener_herramientas_disponibles(): junta las tools de todos los servidores
      en el formato que espera la API de Anthropic (tool schema)
    - ejecutar_herramienta(nombre_tool, argumentos): identifica a que servidor
      pertenece la tool y delega la llamada a su MCPClient.call_tool(...)
"""

from host.mcp_client import MCPClient
from host.logger import mcp_logger


class MCPManager:
    def __init__(self):
        self.clientes: dict[str, MCPClient] = {}
        # Mapea nombre_de_tool -> nombre_del_servidor que la implementa
        self.tool_to_server: dict[str, str] = {}

    def registrar_servidor(self, nombre: str, transport: str = "stdio"):
        self.clientes[nombre] = MCPClient(server_name=nombre, transport=transport)

    async def conectar_todos(self):
        # TODO: conectar e inicializar cada cliente, y poblar tool_to_server
        raise NotImplementedError

    def obtener_herramientas_disponibles(self) -> list[dict]:
        # TODO: retornar lista de tools en formato Anthropic tool-use
        raise NotImplementedError

    async def ejecutar_herramienta(self, nombre_tool: str, argumentos: dict) -> dict:
        servidor = self.tool_to_server.get(nombre_tool)
        if servidor is None:
            raise ValueError(f"Herramienta desconocida: {nombre_tool}")

        mcp_logger.log_request(servidor, nombre_tool, argumentos)
        resultado = await self.clientes[servidor].call_tool(nombre_tool, argumentos)
        mcp_logger.log_response(servidor, nombre_tool, resultado)
        return resultado

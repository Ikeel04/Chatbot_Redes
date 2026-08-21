"""
Conexion con el LLM (Google Gemini) a nivel de API. Requisito 1 del
proyecto: el chatbot debe poder responder preguntas generales sobre su
base de entrenamiento, ademas de coordinar el uso de herramientas MCP
via function calling.

Se usa el SDK oficial "google-genai" (no confundir con el paquete viejo
"google-generativeai", que esta deprecado). Esto SI esta permitido: lo
que no se puede usar es un SDK de MCP (FastMCP, etc.), y este cliente
no lo usa - las tools que le pasamos vienen del MCPManager, que las
obtuvo hablando JSON-RPC manualmente con los servidores MCP.
"""

import os

from google import genai
from google.genai import types

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


class LLMClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Falta la variable de entorno GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    def _construir_tools(self, mcp_tools: list[dict]) -> list[types.Tool] | None:
        """
        Convierte las tools que entrega MCPManager.obtener_herramientas_disponibles()
        (formato {"name", "description", "parameters"}) a los FunctionDeclaration
        que espera el SDK de Gemini.
        """
        if not mcp_tools:
            return None

        declaraciones = [
            types.FunctionDeclaration(
                name=tool["name"],
                description=tool.get("description", ""),
                parameters=tool.get("parameters", {"type": "object", "properties": {}}),
            )
            for tool in mcp_tools
        ]
        return [types.Tool(function_declarations=declaraciones)]

    def send_message(self, history: list[types.Content], mcp_tools: list[dict] | None = None):
        """
        Envia el historial de la conversacion al modelo, junto con las
        tools MCP disponibles (si las hay). Retorna la respuesta cruda
        del SDK; quien llame decide si hay function_call(s) pendientes
        o si ya es una respuesta final de texto (ver funciones abajo).
        """
        config = types.GenerateContentConfig(
            tools=self._construir_tools(mcp_tools),
        )
        response = self.client.models.generate_content(
            model=MODEL,
            contents=history,
            config=config,
        )
        return response

    @staticmethod
    def extraer_function_calls(response) -> list[dict]:
        """Retorna [{"name": ..., "arguments": {...}}, ...] si el modelo pidio usar tools."""
        llamadas = []
        candidato = response.candidates[0] if response.candidates else None
        if not candidato or not candidato.content or not candidato.content.parts:
            return llamadas

        for part in candidato.content.parts:
            if part.function_call:
                llamadas.append({
                    "name": part.function_call.name,
                    "arguments": dict(part.function_call.args or {}),
                })
        return llamadas

    @staticmethod
    def extraer_texto(response) -> str:
        """Retorna el texto de la respuesta final del modelo (si no hubo function_call)."""
        candidato = response.candidates[0] if response.candidates else None
        if not candidato or not candidato.content or not candidato.content.parts:
            return ""

        return "".join(
            part.text for part in candidato.content.parts if part.text
        )

    @staticmethod
    def construir_content_usuario(texto: str) -> types.Content:
        return types.Content(role="user", parts=[types.Part(text=texto)])

    @staticmethod
    def construir_content_modelo(response) -> types.Content:
        """Reempaqueta la respuesta del modelo como Content, para agregarla al historial."""
        return response.candidates[0].content

    @staticmethod
    def construir_content_resultado_tool(nombre_tool: str, resultado: dict) -> types.Content:
        """
        Empaqueta el resultado de ejecutar una tool MCP como un
        function_response, en el formato que Gemini espera para
        continuar la conversacion (role="user" con function_response).
        """
        return types.Content(
            role="user",
            parts=[
                types.Part.from_function_response(
                    name=nombre_tool,
                    response={"result": resultado},
                )
            ],
        )

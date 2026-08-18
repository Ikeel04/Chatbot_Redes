"""
Conexion con el LLM (Claude) a nivel de API. Requisito 1 del proyecto:
el chatbot debe poder responder preguntas generales sobre su base de
entrenamiento, ademas de coordinar el uso de herramientas MCP.

Este modulo SI puede usar el SDK oficial de Anthropic (anthropic),
lo que no esta permitido es usar SDKs/librerias de MCP.
"""

import os
from anthropic import Anthropic

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")


class LLMClient:
    def __init__(self):
        self.client = Anthropic()  # toma ANTHROPIC_API_KEY del entorno

    def send_message(self, messages: list[dict], tools: list[dict] | None = None):
        """
        Envia el historial de mensajes (con contexto) al LLM, junto con
        las herramientas MCP disponibles (si las hay), y retorna la
        respuesta cruda de la API.

        TODO (siguiente paso): manejar el ciclo de tool_use / tool_result:
            1. Enviar mensaje al LLM con las tools disponibles
            2. Si la respuesta contiene bloques "tool_use", ejecutar la
               herramienta via MCPManager y devolver el resultado como
               "tool_result" en un nuevo mensaje
            3. Repetir hasta que el LLM devuelva una respuesta final de texto
        """
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=messages,
            tools=tools or [],
        )
        return response

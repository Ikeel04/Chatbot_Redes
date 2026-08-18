"""
Log de todas las interacciones (solicitudes y respuestas) entre el
anfitrion y los servidores MCP. Requisito 3 del proyecto.

Guarda cada entrada en memoria (para mostrarla en la UI Web) y tambien
en un archivo de texto/JSON para revision posterior.
"""

import json
import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent / "mcp_interactions.log"


class MCPLogger:
    def __init__(self):
        self.entries: list[dict] = []

    def _timestamp(self) -> str:
        return datetime.datetime.now().isoformat()

    def log_request(self, servidor: str, tool: str, argumentos: dict):
        entry = {
            "tipo": "request",
            "servidor": servidor,
            "tool": tool,
            "argumentos": argumentos,
            "timestamp": self._timestamp(),
        }
        self._guardar(entry)

    def log_response(self, servidor: str, tool: str, resultado: dict):
        entry = {
            "tipo": "response",
            "servidor": servidor,
            "tool": tool,
            "resultado": resultado,
            "timestamp": self._timestamp(),
        }
        self._guardar(entry)

    def _guardar(self, entry: dict):
        self.entries.append(entry)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def get_entries(self) -> list[dict]:
        return self.entries


# Instancia global compartida por todo el host
mcp_logger = MCPLogger()

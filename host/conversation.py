"""
Manejo del contexto de una sesion de conversacion. Requisito 2 del
proyecto: el chatbot debe mantener el contexto (ej. "Quien fue Alan
Turing?" seguido de "En que fecha nacio?" debe entenderse en contexto).

El historial se guarda como una lista de google.genai.types.Content,
que es el formato que espera directamente la API de Gemini - asi se
evita convertir formatos de ida y vuelta en cada turno.
"""

from google.genai import types


class Conversation:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: list[types.Content] = []

    def add(self, content: types.Content):
        self.history.append(content)

    def get_history(self) -> list[types.Content]:
        return self.history

    def get_texto_plano(self) -> list[dict]:
        """
        Representacion simplificada del historial (solo mensajes de
        usuario/modelo con texto), util para mostrarla en la Web UI o
        en el log, sin exponer los detalles de function_call/response.
        """
        resumen = []
        for content in self.history:
            textos = [p.text for p in (content.parts or []) if p.text]
            if textos:
                resumen.append({"role": content.role, "text": "".join(textos)})
        return resumen


class SessionManager:
    """Guarda una Conversation por sesion (en memoria, simple para el proyecto)."""

    def __init__(self):
        self.sessions: dict[str, Conversation] = {}

    def get_or_create(self, session_id: str) -> Conversation:
        if session_id not in self.sessions:
            self.sessions[session_id] = Conversation(session_id)
        return self.sessions[session_id]


session_manager = SessionManager()

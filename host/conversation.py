"""
Manejo del contexto de una sesion de conversacion. Requisito 2 del
proyecto: el chatbot debe mantener el contexto (ej. "Quien fue Alan
Turing?" seguido de "En que fecha nacio?" debe entenderse en contexto).
"""


class Conversation:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: list[dict] = []

    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content):
        self.messages.append({"role": "assistant", "content": content})

    def get_history(self) -> list[dict]:
        return self.messages


class SessionManager:
    """Guarda una Conversation por sesion (en memoria, simple para el proyecto)."""

    def __init__(self):
        self.sessions: dict[str, Conversation] = {}

    def get_or_create(self, session_id: str) -> Conversation:
        if session_id not in self.sessions:
            self.sessions[session_id] = Conversation(session_id)
        return self.sessions[session_id]


session_manager = SessionManager()

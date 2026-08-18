"""
Punto de entrada del anfitrion (host). Sirve la web UI y expone el
endpoint de chat que conecta al usuario con el LLM + servidores MCP.
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from host.llm_client import LLMClient
from host.conversation import session_manager
from host.mcp_manager import MCPManager
from host.logger import mcp_logger

load_dotenv()

app = FastAPI(title="FinAssist Chatbot - Proyecto 1 Redes")
app.mount("/static", StaticFiles(directory="host/static"), name="static")

llm = LLMClient()
mcp_manager = MCPManager()


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.on_event("startup")
async def startup():
    # TODO: registrar servidores MCP (filesystem, git, finassist local/remoto)
    # y conectar_todos()
    pass


@app.get("/")
async def index():
    return FileResponse("host/static/index.html")


@app.post("/chat")
async def chat(request: ChatRequest):
    conversation = session_manager.get_or_create(request.session_id)
    conversation.add_user_message(request.message)

    # TODO: llamar a llm.send_message() con las tools de mcp_manager,
    # manejar el ciclo tool_use -> mcp_manager.ejecutar_herramienta() -> tool_result
    # hasta obtener una respuesta final de texto.

    return {"response": "TODO: respuesta del LLM"}


@app.get("/logs")
async def logs():
    return mcp_logger.get_entries()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("host.main:app", host="0.0.0.0", port=int(os.getenv("HOST_PORT", 8000)), reload=True)

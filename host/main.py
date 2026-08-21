"""
Punto de entrada del anfitrion (host). Sirve la web UI y expone el
endpoint de chat que conecta al usuario con el LLM (Gemini) y los
servidores MCP.
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

# En Windows, el event loop por defecto (SelectorEventLoop) no soporta
# subprocesos, y mcp_client.py necesita asyncio.create_subprocess_exec
# para lanzar los servidores MCP locales por stdio. Se fuerza el
# ProactorEventLoop, que si los soporta. Debe hacerse antes de que
# uvicorn cree el loop.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

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

# load_dotenv() sin argumentos a veces no encuentra el .env dependiendo
# de como/desde donde se invoque uvicorn (varia entre entornos). Se
# refuerza cargando explicitamente el .env ubicado en la raiz del
# proyecto (un nivel arriba de host/), calculado con una ruta absoluta.
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=True)

if not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError(
        f"No se encontro GEMINI_API_KEY. Se busco el archivo .env en: {_env_path} "
        f"(existe: {_env_path.exists()}). Verifica que el archivo .env este en la "
        f"raiz del proyecto y que contenga la linea GEMINI_API_KEY=..."
    )

app = FastAPI(title="FinAssist Chatbot - Proyecto 1 Redes")
app.mount("/static", StaticFiles(directory="host/static"), name="static")

llm = LLMClient()
mcp_manager = MCPManager()

MAX_ITERACIONES_TOOLS = 15  # limite de vueltas del ciclo tool_call -> resultado -> tool_call

# Carpeta compartida por los servidores oficiales de Filesystem y Git
# (requisito 4). Ambos operan sobre este mismo directorio: el
# Filesystem server puede leer/escribir archivos aqui, y el Git server
# opera sobre el repositorio ubicado aqui.
WORKSPACE_DIR = Path(__file__).resolve().parent.parent / "mcp_workspace"


def _comando_npx(*args: str) -> list[str]:
    """
    En Windows, npx es un script .cmd y asyncio.create_subprocess_exec
    no lo ejecuta directamente (no pasa por una shell). Se envuelve
    con 'cmd /c' en Windows, tal como recomienda la documentacion
    oficial de MCP para servidores basados en npx.
    """
    if sys.platform == "win32":
        return ["cmd", "/c", "npx", *args]
    return ["npx", *args]


def _preparar_workspace_git():
    """
    El servidor Git oficial (mcp-server-git) NO expone una tool
    'git_init': opera sobre un repositorio que ya debe existir,
    recibido via '--repository' al arrancar (limitacion documentada
    del servidor de referencia). Por eso el "crear el repositorio" del
    escenario del enunciado lo hace el host aqui, una sola vez; el
    resto del flujo (crear README, agregarlo, hacer commit) si lo
    hace el chatbot en tiempo real via las tools MCP.
    """
    WORKSPACE_DIR.mkdir(exist_ok=True)
    if not (WORKSPACE_DIR / ".git").exists():
        subprocess.run(
            ["git", "init"], cwd=WORKSPACE_DIR, check=True, capture_output=True
        )


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.on_event("startup")
async def startup():
    finassist_remote_url = os.getenv("FINASSIST_REMOTE_URL")
    if finassist_remote_url:
        # El chatbot usa el servidor remoto exactamente igual que el
        # local (mismo MCPClient generico, solo cambia el transporte):
        # basta con definir FINASSIST_REMOTE_URL en .env para apuntar
        # al servidor desplegado en la nube (requisito 6).
        mcp_manager.registrar_servidor(
            "finassist",
            transport="http",
            url=finassist_remote_url,
        )
    else:
        mcp_manager.registrar_servidor(
            "finassist",
            transport="stdio",
            command=["python3", "mcp_servers/finassist/server.py"],
        )

    _preparar_workspace_git()

    mcp_manager.registrar_servidor(
        "filesystem_official",
        transport="stdio",
        command=_comando_npx(
            "-y", "@modelcontextprotocol/server-filesystem", str(WORKSPACE_DIR)
        ),
    )
    mcp_manager.registrar_servidor(
        "git_official",
        transport="stdio",
        command=[sys.executable, "-m", "mcp_server_git", "--repository", str(WORKSPACE_DIR)],
    )

    await mcp_manager.conectar_todos()


@app.on_event("shutdown")
async def shutdown():
    await mcp_manager.cerrar_todos()


@app.get("/")
async def index():
    return FileResponse("host/static/index.html")


@app.post("/chat")
async def chat(request: ChatRequest):
    conversation = session_manager.get_or_create(request.session_id)
    conversation.add(llm.construir_content_usuario(request.message))

    tools_disponibles = mcp_manager.obtener_herramientas_disponibles()

    for _ in range(MAX_ITERACIONES_TOOLS):
        response = llm.send_message(conversation.get_history(), tools_disponibles)
        conversation.add(llm.construir_content_modelo(response))

        llamadas = llm.extraer_function_calls(response)
        if not llamadas:
            # No pidio usar ninguna tool: ya es la respuesta final
            return {"response": llm.extraer_texto(response)}

        # El modelo pidio una o mas tools: ejecutarlas via MCP y
        # devolver los resultados para que el modelo continue
        for llamada in llamadas:
            try:
                resultado = await mcp_manager.ejecutar_herramienta(
                    llamada["name"], llamada["arguments"]
                )
            except Exception as exc:
                resultado = {"error": str(exc)}

            conversation.add(
                llm.construir_content_resultado_tool(llamada["name"], resultado)
            )

    return {"response": "No se pudo completar la solicitud tras varios intentos con herramientas."}


@app.get("/logs")
async def logs():
    return mcp_logger.get_entries()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("host.main:app", host="0.0.0.0", port=int(os.getenv("HOST_PORT", 8000)), reload=True)

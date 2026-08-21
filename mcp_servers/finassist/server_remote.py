"""
Servidor MCP de FinAssist - version REMOTA (transporte HTTP).

Misma logica que server.py (comparten dispatch.py, tools.py y db.py),
expuesta ahora como servicio HTTP para desplegarse en la nube (Google
Cloud Run) segun la Parte 2 del proyecto. El chatbot le habla igual
que al servidor local, solo cambia el transporte (HTTP en vez de
stdio) en mcp_client.py.

Nota de diseno: se implementa la variante simplificada de "Streamable
HTTP" (JSON-RPC por POST con respuesta JSON directa), sin manejo de
sesion via header Mcp-Session-Id ni streaming SSE, que la spec 2025+
tambien contempla como modo "batch". Se opto por esta variante porque
cubre exactamente lo que pide el enunciado (invocar el servidor
remoto igual que el local) sin la complejidad adicional de manejar
sesiones/streaming, que no aporta valor para el caso de uso de
FinAssist. Implementado manualmente sobre JSON-RPC 2.0, sin usar
ningun SDK de MCP.
"""

import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from db import init_db
from dispatch import handle_message

app = FastAPI(title="FinAssist MCP Server (remoto)")


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/")
async def root():
    return {"status": "ok", "server": "finassist-mcp-server", "transport": "http"}


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    message = await request.json()
    response = handle_message(message)

    if response is None:
        # Era una notificacion (sin "id"): no hay contenido que devolver
        return JSONResponse(content=None, status_code=204)

    return JSONResponse(content=response)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

"""
Servidor MCP de FinAssist - version REMOTA (transporte HTTP/SSE).

Misma logica que server.py (comparte tools.py y db.py), pero expuesto
como servicio HTTP para poder desplegarse en la nube (Google Cloud Run,
Cloudflare Workers, etc.) segun la Parte 2 del proyecto.

TODO (siguiente paso):
    - Definir endpoint POST /mcp que reciba mensajes JSON-RPC en el body
    - Implementar el mismo despacho de metodos que server.py
      (initialize, tools/list, tools/call), reutilizando handle_message
    - (Opcional) endpoint GET /mcp con SSE para notificaciones del servidor
    - Dockerfile para el despliegue en la nube
"""

from fastapi import FastAPI, Request

from db import init_db
from tools import TOOLS, ejecutar_tool

app = FastAPI(title="FinAssist MCP Server (remoto)")


@app.on_event("startup")
async def startup():
    init_db()


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    message = await request.json()
    # TODO: reutilizar la misma logica de despacho que server.py
    # (idealmente factorizada en un modulo comun, ej. dispatch.py)
    return {"jsonrpc": "2.0", "id": message.get("id"), "result": {}}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)

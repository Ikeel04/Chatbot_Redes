# Imagen para desplegar el servidor MCP remoto de FinAssist en
# Google Cloud Run (Parte 2 del proyecto).
FROM python:3.12-slim

WORKDIR /app

# Solo se necesita FastAPI/uvicorn para este servidor especifico
# (no las dependencias del host completo, como google-genai).
COPY mcp_servers/finassist/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp_servers/finassist/ .

# Cloud Run inyecta la variable de entorno PORT; server_remote.py ya
# la respeta (os.getenv("PORT", 8080)).
ENV PORT=8080
EXPOSE 8080

CMD ["python3", "server_remote.py"]

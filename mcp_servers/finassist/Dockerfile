# Imagen para desplegar el servidor MCP remoto de FinAssist en
# Google Cloud Run (Parte 2 del proyecto).
#
# Se construye con --source mcp_servers/finassist (el contexto de build
# es esta misma carpeta), ya que 'gcloud run deploy --source' busca
# automaticamente un archivo llamado 'Dockerfile' en la raiz del
# directorio indicado y no acepta una ruta personalizada.
FROM python:3.12-slim

WORKDIR /app

# Solo se necesita FastAPI/uvicorn para este servidor especifico
# (no las dependencias del host completo, como google-genai).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run inyecta la variable de entorno PORT; server_remote.py ya
# la respeta (os.getenv("PORT", 8080)).
ENV PORT=8080
EXPOSE 8080

CMD ["python3", "server_remote.py"]

# FinAssist MCP Server - Especificación

## Caso de uso de industria

FinAssist simula el servidor MCP de una fintech que permite a un chatbot
ayudar a los usuarios a gestionar sus finanzas personales por lenguaje
natural: registrar gastos, definir presupuestos por categoría, consultar
su estado financiero y recibir alertas de sobregiro.

## Transporte

- **Local**: stdio (subprocess), implementado en `server.py`
- **Remoto**: HTTP, implementado en `server_remote.py`, expuesto en el
  endpoint `POST /mcp`. Se implementó la variante simplificada de
  "Streamable HTTP" (JSON-RPC por POST con respuesta JSON directa),
  sin manejo de sesión (`Mcp-Session-Id`) ni streaming SSE — suficiente
  para el caso de uso del proyecto y evita complejidad innecesaria.
- Ambos transportes comparten la misma lógica de despacho JSON-RPC
  (`dispatch.py`) y la misma lógica de negocio (`tools.py`, `db.py`):
  el comportamiento es idéntico, solo cambia cómo viajan los mensajes.

## Herramientas (tools)

| Tool | Descripción | Parámetros |
|---|---|---|
| `registrar_gasto` | Registra un gasto | `monto`, `categoria`, `fecha`, `descripcion?` |
| `consultar_gastos` | Consulta gastos con filtros | `categoria?`, `fecha_inicio?`, `fecha_fin?` |
| `definir_presupuesto` | Define límite mensual por categoría | `categoria`, `limite_mensual` |
| `consultar_presupuesto` | Compara gasto vs. límite | `categoria` |
| `generar_resumen` | Resumen mensual de gastos | `mes` |
| `alerta_sobregiro` | Lista categorías que excedieron su presupuesto | `mes` |

## Ejemplo de uso

```
Usuario: "Registra un gasto de Q150 en comida hoy"
-> tools/call: registrar_gasto(monto=150, categoria="comida", fecha="2026-08-16")
<- {"id": 1, "monto": 150, "categoria": "comida", "fecha": "2026-08-16", "descripcion": ""}
```

## Despliegue del servidor remoto en Google Cloud Run

Requiere tener el [SDK de Google Cloud](https://cloud.google.com/sdk/docs/install)
instalado y autenticado (`gcloud auth login`).

```bash
# Desde la raiz del proyecto, apuntando --source directamente a la
# carpeta del servidor (gcloud busca automaticamente el Dockerfile
# en la raiz de --source; no existe una bandera para indicar una
# ruta personalizada al Dockerfile).
gcloud run deploy finassist-mcp-server \
  --source mcp_servers/finassist \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

Al terminar, Cloud Run entrega una URL pública (ej.
`https://finassist-mcp-server-xxxxx.us-central1.run.app`). Para que el
chatbot use ese servidor remoto en vez del local, se define en `.env`:

```
FINASSIST_REMOTE_URL=https://finassist-mcp-server-xxxxx.us-central1.run.app/mcp
```

El host (`host/main.py`) detecta automáticamente esta variable al
arrancar: si está definida, registra `finassist` con transporte HTTP
apuntando a esa URL; si no, usa el servidor local por stdio. El
chatbot usa el servidor remoto exactamente igual que el local (mismas
6 tools, mismo `MCPClient` genérico), sin ningún cambio en la lógica
del host más allá del transporte.


# FinAssist MCP Server - Especificación

## Caso de uso de industria

FinAssist simula el servidor MCP de una fintech que permite a un chatbot
ayudar a los usuarios a gestionar sus finanzas personales por lenguaje
natural: registrar gastos, definir presupuestos por categoría, consultar
su estado financiero y recibir alertas de sobregiro.

## Transporte

- **Local**: stdio (subprocess), implementado en `server.py`
- **Remoto**: HTTP, implementado en `server_remote.py`, expuesto en el
  endpoint `POST /mcp`

## Herramientas (tools)

| Tool | Descripción | Parámetros |
|---|---|---|
| `registrar_gasto` | Registra un gasto | `monto`, `categoria`, `fecha`, `descripcion?` |
| `consultar_gastos` | Consulta gastos con filtros | `categoria?`, `fecha_inicio?`, `fecha_fin?` |
| `definir_presupuesto` | Define límite mensual por categoría | `categoria`, `limite_mensual` |
| `consultar_presupuesto` | Compara gasto vs. límite | `categoria` |
| `generar_resumen` | Resumen mensual de gastos | `mes` |
| `alerta_sobregiro` | Lista categorías que excedieron su presupuesto | `mes` |

*(TODO: completar con ejemplos de request/response JSON-RPC reales una
vez implementada la lógica, para el reporte final)*

## Ejemplo de uso (a completar)

```
Usuario: "Registra un gasto de Q150 en comida hoy"
-> tools/call: registrar_gasto(monto=150, categoria="comida", fecha="2026-08-16")
```

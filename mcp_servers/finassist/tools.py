"""
Definicion de las herramientas (tools) que expone el servidor MCP de
FinAssist, en el formato de "tool schema" que espera MCP (y que es
compatible con el formato de tool-use de Anthropic).

Cada tool debe tener: name, description, inputSchema (JSON Schema).
"""

TOOLS = [
    {
        "name": "registrar_gasto",
        "description": "Registra un nuevo gasto del usuario con monto, categoria, fecha y descripcion opcional.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "monto": {"type": "number", "description": "Monto del gasto"},
                "categoria": {"type": "string", "description": "Categoria del gasto, ej. comida, transporte"},
                "fecha": {"type": "string", "description": "Fecha en formato YYYY-MM-DD"},
                "descripcion": {"type": "string", "description": "Descripcion opcional del gasto"},
            },
            "required": ["monto", "categoria", "fecha"],
        },
    },
    {
        "name": "consultar_gastos",
        "description": "Consulta los gastos registrados, opcionalmente filtrados por categoria o rango de fechas.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "categoria": {"type": "string"},
                "fecha_inicio": {"type": "string"},
                "fecha_fin": {"type": "string"},
            },
            "required": [],
        },
    },
    {
        "name": "definir_presupuesto",
        "description": "Define o actualiza el limite de presupuesto mensual para una categoria.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "categoria": {"type": "string"},
                "limite_mensual": {"type": "number"},
            },
            "required": ["categoria", "limite_mensual"],
        },
    },
    {
        "name": "consultar_presupuesto",
        "description": "Consulta cuanto se ha gastado en una categoria frente a su presupuesto definido.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "categoria": {"type": "string"},
            },
            "required": ["categoria"],
        },
    },
    {
        "name": "generar_resumen",
        "description": "Genera un resumen del mes: total gastado, categoria con mas gasto, y comparacion contra presupuesto.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mes": {"type": "string", "description": "Mes en formato YYYY-MM"},
            },
            "required": ["mes"],
        },
    },
    {
        "name": "alerta_sobregiro",
        "description": "Revisa todas las categorias con presupuesto definido e indica cuales fueron excedidas.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mes": {"type": "string", "description": "Mes en formato YYYY-MM"},
            },
            "required": ["mes"],
        },
    },
]


# TODO (siguiente paso): funcion dispatch que reciba (name, arguments)
# y llame a la funcion correspondiente en db.py, retornando el resultado
# en el formato de "tool result" de MCP.
def ejecutar_tool(name: str, arguments: dict) -> dict:
    raise NotImplementedError(f"Tool no implementada aun: {name}")

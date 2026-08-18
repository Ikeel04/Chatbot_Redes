"""
Definicion de las herramientas (tools) que expone el servidor MCP de
FinAssist, en el formato de "tool schema" que espera MCP (y que es
compatible con el formato de tool-use de Anthropic).

Cada tool debe tener: name, description, inputSchema (JSON Schema).
"""

import db

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


def _resumen_texto(mes: str) -> dict:
    gastos = db.gastos_del_mes(mes)
    total = sum(g["monto"] for g in gastos)

    por_categoria: dict[str, float] = {}
    for g in gastos:
        por_categoria[g["categoria"]] = por_categoria.get(g["categoria"], 0) + g["monto"]

    categoria_top = max(por_categoria, key=por_categoria.get) if por_categoria else None

    presupuestos = db.obtener_todos_presupuestos()
    comparacion = []
    for p in presupuestos:
        gastado = por_categoria.get(p["categoria"], 0)
        comparacion.append({
            "categoria": p["categoria"],
            "gastado": gastado,
            "limite_mensual": p["limite_mensual"],
            "excedido": gastado > p["limite_mensual"],
        })

    return {
        "mes": mes,
        "total_gastado": total,
        "categoria_con_mas_gasto": categoria_top,
        "gasto_por_categoria": por_categoria,
        "comparacion_presupuestos": comparacion,
    }


def ejecutar_tool(name: str, arguments: dict) -> dict:
    """
    Despacha la ejecucion de una tool hacia la logica correspondiente
    en db.py. Retorna un dict con el resultado (sera envuelto en el
    formato de "tool result" de MCP por quien llame a esta funcion).
    """

    if name == "registrar_gasto":
        return db.registrar_gasto(
            monto=arguments["monto"],
            categoria=arguments["categoria"],
            fecha=arguments["fecha"],
            descripcion=arguments.get("descripcion", ""),
        )

    if name == "consultar_gastos":
        gastos = db.obtener_gastos(
            categoria=arguments.get("categoria"),
            fecha_inicio=arguments.get("fecha_inicio"),
            fecha_fin=arguments.get("fecha_fin"),
        )
        return {"gastos": gastos, "cantidad": len(gastos)}

    if name == "definir_presupuesto":
        return db.definir_presupuesto(
            categoria=arguments["categoria"],
            limite_mensual=arguments["limite_mensual"],
        )

    if name == "consultar_presupuesto":
        categoria = arguments["categoria"]
        presupuesto = db.obtener_presupuesto(categoria)
        if presupuesto is None:
            return {"categoria": categoria, "error": "No hay presupuesto definido para esta categoria"}

        # Se usa el mes actual del sistema si no se especifica
        from datetime import date
        mes_actual = date.today().strftime("%Y-%m")
        gastado = db.total_gastado_categoria_mes(categoria, mes_actual)

        return {
            "categoria": categoria,
            "limite_mensual": presupuesto["limite_mensual"],
            "gastado": gastado,
            "disponible": presupuesto["limite_mensual"] - gastado,
            "excedido": gastado > presupuesto["limite_mensual"],
        }

    if name == "generar_resumen":
        return _resumen_texto(arguments["mes"])

    if name == "alerta_sobregiro":
        resumen = _resumen_texto(arguments["mes"])
        excedidas = [c for c in resumen["comparacion_presupuestos"] if c["excedido"]]
        return {"mes": arguments["mes"], "categorias_excedidas": excedidas, "hay_alertas": len(excedidas) > 0}

    raise ValueError(f"Tool desconocida: {name}")

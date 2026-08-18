"""
Capa de persistencia de FinAssist usando SQLite.

Tablas:
    gastos(id, monto, categoria, fecha, descripcion)
    presupuestos(categoria, limite_mensual)
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "finassist.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monto REAL NOT NULL,
            categoria TEXT NOT NULL,
            fecha TEXT NOT NULL,
            descripcion TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS presupuestos (
            categoria TEXT PRIMARY KEY,
            limite_mensual REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def registrar_gasto(monto: float, categoria: str, fecha: str, descripcion: str = "") -> dict:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO gastos (monto, categoria, fecha, descripcion) VALUES (?, ?, ?, ?)",
        (monto, categoria, fecha, descripcion),
    )
    conn.commit()
    gasto_id = cursor.lastrowid
    conn.close()
    return {"id": gasto_id, "monto": monto, "categoria": categoria, "fecha": fecha, "descripcion": descripcion}


def obtener_gastos(categoria: str | None = None, fecha_inicio: str | None = None, fecha_fin: str | None = None) -> list[dict]:
    conn = get_connection()
    query = "SELECT * FROM gastos WHERE 1=1"
    params = []

    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if fecha_inicio:
        query += " AND fecha >= ?"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND fecha <= ?"
        params.append(fecha_fin)

    query += " ORDER BY fecha DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def definir_presupuesto(categoria: str, limite_mensual: float) -> dict:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO presupuestos (categoria, limite_mensual) VALUES (?, ?)
        ON CONFLICT(categoria) DO UPDATE SET limite_mensual = excluded.limite_mensual
        """,
        (categoria, limite_mensual),
    )
    conn.commit()
    conn.close()
    return {"categoria": categoria, "limite_mensual": limite_mensual}


def obtener_presupuesto(categoria: str) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM presupuestos WHERE categoria = ?", (categoria,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def obtener_todos_presupuestos() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM presupuestos").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def total_gastado_categoria_mes(categoria: str, mes: str) -> float:
    """mes en formato YYYY-MM"""
    conn = get_connection()
    row = conn.execute(
        "SELECT COALESCE(SUM(monto), 0) as total FROM gastos WHERE categoria = ? AND fecha LIKE ?",
        (categoria, f"{mes}%"),
    ).fetchone()
    conn.close()
    return row["total"]


def gastos_del_mes(mes: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM gastos WHERE fecha LIKE ? ORDER BY fecha DESC", (f"{mes}%",)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

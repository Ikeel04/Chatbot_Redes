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


# TODO (siguiente paso): funciones CRUD que usaran las tools:
#   registrar_gasto(monto, categoria, fecha, descripcion)
#   obtener_gastos(categoria=None, fecha_inicio=None, fecha_fin=None)
#   definir_presupuesto(categoria, limite_mensual)
#   obtener_presupuesto(categoria)
#   obtener_todos_presupuestos()

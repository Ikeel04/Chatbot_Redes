"""
Script de prueba manual para el servidor MCP de FinAssist (server.py).

Lanza el servidor como subprocess y le envia una secuencia de mensajes
JSON-RPC 2.0 por stdin, imprimiendo las respuestas que llegan por stdout.

Uso:
    cd mcp_servers/finassist
    python3 test_server_manual.py
"""

import json
import subprocess


def send(proc, msg):
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()
    if "id" in msg:
        line = proc.stdout.readline()
        print(">>", line.strip())


def main():
    proc = subprocess.Popen(
        ["python3", "server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )

    send(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    send(proc, {
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": "registrar_gasto", "arguments": {
            "monto": 150, "categoria": "comida", "fecha": "2026-08-16", "descripcion": "almuerzo"
        }},
    })
    send(proc, {
        "jsonrpc": "2.0", "id": 4, "method": "tools/call",
        "params": {"name": "definir_presupuesto", "arguments": {
            "categoria": "comida", "limite_mensual": 500
        }},
    })
    send(proc, {
        "jsonrpc": "2.0", "id": 5, "method": "tools/call",
        "params": {"name": "consultar_presupuesto", "arguments": {"categoria": "comida"}},
    })
    send(proc, {
        "jsonrpc": "2.0", "id": 6, "method": "tools/call",
        "params": {"name": "generar_resumen", "arguments": {"mes": "2026-08"}},
    })
    send(proc, {"jsonrpc": "2.0", "id": 7, "method": "metodo_invalido", "params": {}})

    proc.stdin.close()
    proc.terminate()


if __name__ == "__main__":
    main()

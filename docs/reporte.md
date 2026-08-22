# Reporte — Proyecto 1: Uso de un protocolo existente (MCP)

CC3067 Redes — Universidad del Valle de Guatemala
Adrián González

## 1. Especificación de los servidores MCP desarrollados

Ver `mcp_servers/finassist/SPEC.md` para la especificación completa
del servidor propio de FinAssist (tools, parámetros, ejemplos de
request/response, y detalle del despliegue en Google Cloud Run).

Resumen de la arquitectura de transporte: el servidor FinAssist se
implementó una sola vez a nivel de lógica de negocio (`tools.py`,
`db.py`) y protocolo (`dispatch.py`), y se expone por dos transportes
distintos según el entorno:

- **Local** (`server.py`): JSON-RPC 2.0 sobre stdio (subprocess).
- **Remoto** (`server_remote.py`): JSON-RPC 2.0 sobre HTTP (`POST /mcp`),
  desplegado en Google Cloud Run mediante el `Dockerfile` incluido.

El host detecta automáticamente cuál usar según la variable de entorno
`FINASSIST_REMOTE_URL`: si está definida, usa el servidor remoto; si
no, el local — sin ningún otro cambio en la lógica del chatbot, ya que
`mcp_client.py` implementa ambos transportes bajo la misma interfaz.

**Despliegue real:** el servidor remoto quedó desplegado en Google
Cloud Run, proyecto `finassist-mcp-2026`, región `us-central1`, en:

```
https://finassist-mcp-server-8543898875.us-central1.run.app
```

Se verificó funcionando end-to-end desde el chatbot: al registrar un
gasto con el servidor remoto activo, el `id` autoincremental devuelto
correspondió al de la base de datos persistida en Cloud Run (no la
local), confirmando que la interacción viajó realmente por internet
hasta el servicio desplegado.

## 1.1 Integración de servidores MCP oficiales (Filesystem y Git)

Se integraron los servidores oficiales de Anthropic:

- **Filesystem** (`@modelcontextprotocol/server-filesystem`, vía `npx`):
  expone lectura/escritura de archivos sobre un directorio permitido
  (`mcp_workspace/`).
- **Git** (`mcp-server-git`, paquete de Python vía `pip`): expone
  operaciones de Git (`git_status`, `git_add`, `git_commit`, `git_log`,
  etc.) sobre un repositorio fijo, pasado con `--repository` al
  arrancar el servidor.

**Limitación encontrada:** el servidor Git oficial **no expone una
tool `git_init`** — solo opera sobre un repositorio que ya debe
existir. Por eso, el "crear el repositorio" del escenario del
enunciado lo realiza el *host* al arrancar (`git init` una sola vez,
si el directorio `mcp_workspace/` no es ya un repositorio), y el resto
del flujo sí lo ejecuta el chatbot en tiempo real vía MCP: crear el
archivo `README.md` (tool `write_file` del servidor Filesystem),
agregarlo al staging (`git_add`) y hacer commit (`git_commit`), tal
como pide el enunciado.

## 2. Análisis con Wireshark

Se capturó el tráfico real entre el host (ejecutándose en la máquina
local) y el servidor MCP remoto de FinAssist en Cloud Run
(`34.143.77.2`), mientras el chatbot ejecutaba una sesión completa:
`initialize` → `tools/list` → tres `tools/call` (`registrar_gasto`,
`consultar_gastos`, `generar_resumen`). Dado que el tráfico va sobre
HTTPS, se descifró usando la técnica de `SSLKEYLOGFILE`: se definió
esa variable de entorno antes de levantar el host, lo que hace que
Python registre las claves de sesión TLS en un archivo; ese archivo se
configuró en Wireshark (Preferences → Protocols → TLS →
"(Pre)-Master-Secret log filename"), permitiendo ver el contenido
JSON-RPC en texto plano sin comprometer la seguridad del servidor (las
claves son efímeras, válidas solo para esa sesión de captura).

Captura completa: `docs/wireshark/finassist-remoto.pcapng`.

### Mensajes identificados

**Sincronización** — antes de cualquier mensaje JSON-RPC, se observa
el establecimiento de la conexión en tres niveles:
1. Three-way handshake TCP: `SYN` (frame 1368) → `SYN, ACK` (1377) →
   `ACK` (1378).
2. Handshake TLS 1.3: `ClientHello` (1379, `tls.handshake.type == 1`)
   → `ServerHello` + `ChangeCipherSpec` (1446, `type == 2`) →
   intercambio de certificados y `Finished` (1447-1452).
3. Handshake a nivel de aplicación MCP: el primer mensaje JSON-RPC de
   la sesión es siempre `initialize` (frame 1454) — el "saludo" que
   negocia versión de protocolo y capacidades antes de poder listar o
   invocar tools.

**Solicitud / petición** (`POST /mcp`, mensajes con `method`):

| Frame | Método | Contenido |
|---|---|---|
| 1454 | `initialize` | `{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"finassist-mcp-host","version":"0.1.0"}}` |
| 1486 | `tools/list` | `{}` |
| 7316 | `tools/call` | `registrar_gasto(fecha=2026-08-21, categoria=transporte, monto=40)` |
| 11685 | `tools/call` | `consultar_gastos({})` |
| 13330 | `tools/call` | `generar_resumen(mes=2026-08)` |

**Respuesta** (`HTTP/1.1 200 OK`, mensajes con `result`, mismo `id`
que su solicitud correspondiente):

| Frame | Responde a | Contenido (resumen) |
|---|---|---|
| 1480 | 1454 | `serverInfo: finassist-mcp-server v0.1.0` |
| 1526 | 1486 | Lista de las 6 tools con su `inputSchema` completo |
| 7326 | 7316 | `{"id":6,"monto":40,"categoria":"transporte","fecha":"2026-08-21"}` |
| 11688 | 11685 | 6 gastos registrados (incluye los de pruebas anteriores) |
| 13332 | 13330 | Resumen: total `390.0`, categoría con más gasto `comida` |

Cada solicitud y su respuesta comparten el mismo `id` de JSON-RPC
(un UUID), que es como el cliente empareja cada respuesta con su
petición sin depender del orden de llegada — relevante porque HTTP/1.1
con *keep-alive* permite, en principio, varias peticiones en la misma
conexión TCP.

### 2.1 Capa de enlace

Ethernet II: direcciones MAC origen (`CloudNetwork_ac:c5:7b`, la
tarjeta de red local) y destino (`zte_c0:6d:6e`, el router/gateway),
`EtherType 0x0800` (IPv4). A este nivel no hay nada específico de MCP
o HTTP — es simplemente el salto hacia el siguiente nodo de la red
(el router doméstico), ya que el destino real (Cloud Run) está muchos
saltos más adelante en internet.

### 2.2 Capa de red

IPv4, origen `192.168.1.5` (IP privada de la máquina local) → destino
`34.143.77.2` (IP pública del *load balancer* de Google Cloud Run que
enruta hacia el contenedor). `TTL: 128` (valor por defecto de
Windows), `Don't Fragment` activado, protocolo de nivel superior `TCP
(6)`. Esta capa es responsable de rutear el paquete a través de
internet hasta llegar a la infraestructura de Google, sin importarle
el contenido de niveles superiores.

### 2.3 Capa de transporte

TCP sobre el puerto `443` (HTTPS). Se observa el *three-way handshake*
descrito arriba, y luego los datos viajan segmentados: varios mensajes
JSON-RPC (como la respuesta de `tools/list`, de 1924 bytes) exceden el
tamaño máximo de segmento (MSS) y se reensamblan en Wireshark a partir
de varios paquetes TCP (visible en la jerarquía de protocolos como
`tcp.segments`). TCP garantiza aquí la entrega ordenada y confiable de
cada mensaje JSON-RPC, independientemente de que la capa de aplicación
(TLS + HTTP + MCP) no tenga que preocuparse por paquetes perdidos o
fuera de orden.

### 2.4 Capa de aplicación

Esta es la única capa donde vive realmente el protocolo MCP. Dentro de
la sesión TLS ya establecida, se identifican tres protocolos anidados:

1. **HTTP/1.1**: transporta cada mensaje MCP como un `POST /mcp` con
   `Content-Type: application/json`, encabezados como
   `User-Agent: python-httpx/0.28.1` (nuestro `mcp_client.py`) y
   `server: Google Frontend` (confirmando que la respuesta pasa por el
   *edge* de Cloud Run antes de llegar al contenedor).
2. **JSON-RPC 2.0**: el formato del cuerpo de cada mensaje —
   `{"jsonrpc":"2.0","id":...,"method":...,"params":...}` para
   solicitudes, `{"jsonrpc":"2.0","id":...,"result":...}` para
   respuestas — implementado manualmente en `dispatch.py`, sin usar
   ningún SDK de MCP.
3. **MCP**: la semántica específica sobre JSON-RPC (`initialize`,
   `tools/list`, `tools/call`) que define cómo un anfitrión descubre y
   usa las herramientas de un servidor.

## 3. Conclusiones y comentarios sobre el proyecto

*(TODO)*

# Reporte — Proyecto 1: Uso de un protocolo existente (MCP)

CC3067 Redes — Universidad del Valle de Guatemala
Adrián González

## 1. Especificación de los servidores MCP desarrollados

*(TODO: especificación, parámetros y endpoints — puede referenciar
`mcp_servers/finassist/SPEC.md`)*

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

*(TODO: capturas de la comunicación entre el host y el servidor remoto;
identificar mensajes de sincronización, solicitud/petición y respuesta
a nivel JSON-RPC)*

### 2.1 Capa de enlace

### 2.2 Capa de red

### 2.3 Capa de transporte

### 2.4 Capa de aplicación

## 3. Conclusiones y comentarios sobre el proyecto

*(TODO)*

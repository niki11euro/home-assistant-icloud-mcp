# OpenAI Secure MCP Tunnels

## Purpose

Runs one `tunnel-client` process per configured list entry. This lets a single installed Home Assistant App expose multiple private MCP servers while keeping a distinct OpenAI tunnel ID and local bearer token for each target.

Typical configuration:

- `iCloud Core` -> internal Private iCloud MCP `/mcp`
- `iCloud Reminders` -> internal Private iCloud Reminders MCP `/mcp`

## Configuration fields per tunnel

- `name`: local label used in logs
- `control_plane_tunnel_id`: OpenAI Secure MCP Tunnel ID
- `control_plane_api_key`: runtime API key for that tunnel
- `mcp_server_url`: internal Streamable HTTP MCP URL
- `mcp_auth_token`: bearer token configured in the target MCP App

The tunnel does not need, receive, or store the Apple app-specific password.

## Internal URLs

Use the exact Home Assistant internal hostname assigned to the installed MCP App. Do not guess it.

Expected shape:

`http://<repository-id>-icloud-mcp:8080/mcp`

or

`http://<repository-id>-icloud-reminders-mcp:8080/mcp`

## Process behavior

Every configured tunnel runs as a separate child process with a separate loopback health port. If any child exits, the wrapper stops the others and exits so Home Assistant does not leave a partially-working tunnel set running unnoticed.

No Web UI or remote admin/health listener is exposed.

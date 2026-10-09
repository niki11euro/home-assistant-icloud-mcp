# OpenAI Secure MCP Tunnels

## Purpose

One Home Assistant App runs multiple independent OpenAI Secure MCP Tunnel client processes. Each entry has its own Tunnel ID, runtime API key, target URL and MCP bearer token. These must never be exchanged between targets.

Supported examples:

- `iCloud Core` -> Private iCloud MCP (personal calendar and contacts)
- `Lexware Office` -> Lexware Office MCP (business accounting)

These are independent MCP endpoints. Sharing the infrastructure App does not make private iCloud information available to Lexware or vice versa. However, an administrator who can edit this App's settings can access the credentials of all configured tunnels.

## Configuration

Configure an entry per target under `tunnels`:

- `name`: human-readable process label
- `control_plane_tunnel_id`: existing dedicated OpenAI tunnel ID
- `control_plane_api_key`: runtime key belonging to that tunnel
- `mcp_server_url`: exact internal `http://<HA-app-host>:8080/mcp` endpoint
- `mcp_auth_token`: bearer token configured in that MCP target App

Do not put any real secrets into GitHub or into example configuration files.

For Lexware Office MCP, obtain its hostname from Home Assistant App metadata; it may belong to a different Home Assistant App repository. Do not infer an identifier from the source repository name.

## Startup

Installation never starts this App automatically: `boot: manual`. Users can later enable **Start on boot** in Home Assistant. Install and start the target MCP Apps first, then start this tunnel App.

For security, host networking and a remotely accessible management interface are disabled.

## Process supervision

Each entry runs with its own local health port and process. If a tunnel process terminates, the supervisor stops the other tunnel processes and exits, so Home Assistant can surface the failure instead of leaving a partly functional set running.

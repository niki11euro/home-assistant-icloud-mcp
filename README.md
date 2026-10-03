# Home Assistant Private iCloud MCP

Private Home Assistant App repository for exposing selected iCloud services to ChatGPT through OpenAI Secure MCP Tunnel.

This repository intentionally separates private iCloud access from business/WE.R infrastructure.

## Apps

### Private iCloud MCP

Wraps `ThomasCrouzet/icloud-mcp` pinned to the v0.4.1 release commit.

Supported domains:

- Calendar over CalDAV
- Contacts over CardDAV
- Optional iCloud Mail over IMAP/SMTP

The upstream server uses an Apple app-specific password. Never enter the main Apple Account password.

The upstream MCP server is stdio-only. This App places the pinned `supergateway` bridge in front of it and exposes a private Streamable HTTP endpoint at `/mcp`. The endpoint requires a local bearer token and has no host port mapping by default.

### Private iCloud Reminders MCP

Wraps `Lingnik/icloud-reminders-mcp` pinned to a reviewed commit. It accesses legacy/VTODO-capable iCloud Reminders lists over CalDAV and exposes them through an authenticated Streamable HTTP endpoint.

Important: modern Apple Reminders lists may have been migrated to CloudKit and may not be reachable over CalDAV. The App performs a read-only compatibility probe at startup and refuses to run if no VTODO-capable list is available.

### OpenAI Secure MCP Tunnels

Wraps `openai/tunnel-client` v0.0.15. One installed App can run multiple tunnel-client processes. Add one list entry per MCP endpoint/tunnel ID.

This allows, for example:

- tunnel A -> Private iCloud MCP
- tunnel B -> Private iCloud Reminders MCP

Each target keeps its own tunnel ID and local bearer token.

## Installation

Add this repository to the Home Assistant App store:

`https://github.com/niki11euro/home-assistant-icloud-mcp`

Then install the Apps you need.

Recommended order:

1. Install and configure **Private iCloud MCP**.
2. Start it and verify the logs.
3. Optionally install **Private iCloud Reminders MCP** and verify the compatibility probe.
4. Install **OpenAI Secure MCP Tunnels**.
5. Add one tunnel entry for each MCP App you want to expose to ChatGPT.

The internal Home Assistant hostname is assigned by Supervisor from the repository and App slug. Do not guess it. After installation, inspect the installed App metadata/logs and use the exact internal URL in the tunnel configuration, for example:

`http://<repository-id>-icloud-mcp:8080/mcp`

or

`http://<repository-id>-icloud-reminders-mcp:8080/mcp`

## Security defaults

- no host network
- no Home Assistant API access
- no Supervisor API access
- no host port mapping
- MCP endpoints require a separate bearer token
- Apple app-specific passwords stay only inside the corresponding private App
- the tunnel receives only the local MCP token, not the Apple credential
- Mail is disabled by default
- Reminders deletion is disabled by default
- all Apps use `boot: manual_only`

See [SECURITY.md](SECURITY.md), [PREINSTALL_CHECKLIST.md](PREINSTALL_CHECKLIST.md), and [REVERSIBILITY.md](REVERSIBILITY.md).

## Upstream projects

- https://github.com/ThomasCrouzet/icloud-mcp
- https://github.com/Lingnik/icloud-reminders-mcp
- https://github.com/supercorp-ai/supergateway
- https://github.com/openai/tunnel-client

Third-party licenses are preserved in the App directories.

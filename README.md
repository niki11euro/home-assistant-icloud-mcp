# Home Assistant MCP Apps and Shared Secure Tunnels

Home Assistant App repository for a private iCloud MCP server and an OpenAI Secure MCP Tunnels App. The tunnel infrastructure also accepts other independent MCP targets, such as the **Lexware Office MCP** hosted in `niki11euro/home-assistant-lexware-mcp`.

## Apps

### Private iCloud MCP

Wraps `ThomasCrouzet/icloud-mcp`, pinned to the reviewed v0.4.1 release commit.

- Calendar access through CalDAV
- Optional Contacts via CardDAV
- Optional iCloud Mail through IMAP/SMTP
- Authenticated internal Streamable HTTP endpoint at `/mcp`
- Apple app-specific password; do not use the main Apple Account password
- Independent Calendar read/write and Contacts read/write switches, with write disabled by default

### OpenAI Secure MCP Tunnels

Wraps `openai/tunnel-client` v0.0.15. One App manages multiple tunnel entries, each with its own OpenAI tunnel ID, runtime API key and matching target MCP token.

Typical entries:
1. `iCloud Core` -> Private iCloud MCP (personal)
2. `Lexware Office` -> Lexware Office MCP from the separate repository (WE.R)

**Private and business data remain logically separate**: separate endpoints, tunnel identities, tokens and plugins. The shared tunnel App is an infrastructure component, not a shared data store. Its administrator can nevertheless access the credentials for every entry.

## Installation

Register this repository in the Home Assistant App store:

`https://github.com/niki11euro/home-assistant-icloud-mcp`

1. Install and configure Private iCloud MCP.
2. Start the MCP target, verify logs and capabilities.
3. Install the OpenAI Secure MCP Tunnels App and configure an independent entry for every target MCP.
4. Start the shared tunnel App, verify connectivity and test the ChatGPT plugins.

Internal hostnames are assigned by Home Assistant Supervisor. Discover the exact hostname in installed App metadata; never guess it.

## Startup behavior

Both Apps use `boot: manual`: no automatic startup directly after installation. The **Start on boot** switch is available in Home Assistant and is initially off. Turning it on for a working deployment makes the App start after subsequent Home Assistant restarts; it does not automatically change any MCP permissions.

## Security defaults

- no host network, Supervisor API or Home Assistant API access
- no host port published by the iCloud MCP
- private endpoints authenticated with bearer tokens
- service-specific credentials kept only in the corresponding App options
- shared tunnel settings contain per-target runtime secrets; restrict access to administrators
- Mail and write capabilities disabled by default

See [SECURITY.md](SECURITY.md), [PREINSTALL_CHECKLIST.md](PREINSTALL_CHECKLIST.md) and [REVERSIBILITY.md](REVERSIBILITY.md).

## Upstream projects

- https://github.com/ThomasCrouzet/icloud-mcp
- https://github.com/supercorp-ai/supergateway
- https://github.com/openai/tunnel-client

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

# Security

## Credential model

Use an Apple **app-specific** password only, never the main Apple Account password. Store all Apple, OpenAI and target MCP credentials in Home Assistant App settings, not in Git.

Password fields are masked in the UI, but Home Assistant backups may contain their values. Protect backups and restrict Supervisor access.

## Network boundaries

The iCloud MCP exposes an authenticated internal port 8080 without a host port mapping. The shared tunnel establishes outbound HTTPS connections and must be configured with a distinct bearer token, runtime key, and target URL for each MCP endpoint.

The OpenAI tunnel never needs the Apple account password or the Lexware API key; only the target MCP bearer tokens.

## Private versus business

The multi-tunnel App may forward iCloud (personal) and Lexware (business) through **separate tunnels**. Never reuse tunnel identities, bearer tokens or control-plane credentials between these domains. The App shares infrastructure and administratively stores their tunnel credentials, but performs no cross-domain synchronization.

An administrator with access to the multi-tunnel App options can read or replace all tunnel credentials. Keep this permission tightly controlled.

## Least privilege

Begin with `calendar_write: false` and `contacts_write: false`; enable each read/write permission only when needed and tested. Contacts and Mail are optional. The iCloud tool registry enforces the four Calendar/Contacts switches separately. Do not enable mail mutation/send without intentional authorization.

Do not publish MCP host ports or add router forwards. A separately installed target MCP, such as Lexware, must also keep its host-port mapping disabled.

## Reporting

Never place passwords, runtime keys, bearer tokens or personal calendar/contact data in public issues or logs.

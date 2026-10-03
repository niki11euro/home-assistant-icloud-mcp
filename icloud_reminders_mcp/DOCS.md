# Private iCloud Reminders MCP

## Important compatibility limitation

This App uses CalDAV VTODO through `Lingnik/icloud-reminders-mcp`.

Apple moved modern Reminders to a newer CloudKit-backed store. Only VTODO-capable lists that iCloud still exposes over CalDAV are usable here. Some accounts expose none.

At every App start, a read-only compatibility probe lists task-capable CalDAV collections. It does not create or modify any reminder. If zero compatible lists are found, the App exits with a clear log message instead of exposing a non-functional MCP.

## Credentials

Use an Apple app-specific password, preferably a separate one from the Core iCloud App so it can be revoked independently.

Never use the main Apple Account password.

## Delete safety

`allow_delete` defaults to false. Even when enabled, the upstream MCP also requires an explicit confirmation argument for deletion.

## Optional list allowlist

Set `list_allowlist` to comma-separated reminder list display names to restrict which compatible lists are visible to the MCP. Empty means all VTODO-capable lists.

## Internal endpoint

The App listens internally on:

`http://<app-host>:8080/mcp`

The host port is intentionally not published. Requests must include the configured bearer token.

Use that internal URL and the same bearer token in the OpenAI Secure MCP Tunnels App.

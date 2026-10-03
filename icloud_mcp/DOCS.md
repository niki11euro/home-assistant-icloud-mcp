# Private iCloud MCP

## Purpose

Provides iCloud Calendar, Contacts, and optional iCloud Mail as an internal MCP endpoint for use with the OpenAI Secure MCP Tunnel App.

Upstream iCloud MCP is pinned to the commit behind release v0.4.1:

`84cb170b1dd62ee01a5018290b80375ea47c1f19`

The stdio server is bridged to Streamable HTTP with `supergateway` 4.1.0.

## Credentials

Use:

- your Apple Account / iCloud email address
- an Apple app-specific password
- a separate random local MCP bearer token

Never use the main Apple Account password.

## Safe first configuration

Recommended first start:

- `read_only: true`
- `enable_contacts: true` only if contacts are needed
- `enable_mail: false`
- `enable_mail_write: false`
- `enable_mail_send: false`

After read access works, disable `read_only` only if Calendar/Contacts writes are desired.

## Mail

Mail is entirely optional. When enabled and `mail_address` is empty, the App uses `apple_id` as the mailbox address.

Mail mutations require both:

- `enable_mail: true`
- `enable_mail_write: true`
- `read_only: false`

Mail sending additionally requires `enable_mail_send: true` and an exact comma-separated `smtp_allowed_recipients` policy. Avoid `*`.

## Internal endpoint

The App listens internally on:

`http://<app-host>:8080/mcp`

The host port is intentionally not published. Requests must include the configured bearer token.

Use that internal URL and the same bearer token in the OpenAI Secure MCP Tunnels App.

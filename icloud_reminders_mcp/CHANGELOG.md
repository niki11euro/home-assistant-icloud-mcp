# Changelog

## 0.1.1

- Skip the upstream duplicate CalDAV startup discovery after the Home Assistant wrapper compatibility probe.
- This allows the MCP stdio server to answer initialize immediately enough for OpenAI tunnel-client's fixed startup probe deadline.
- Reminder tools and the read-only compatibility probe are unchanged.

## 0.1.0

- Initial Home Assistant App wrapper.
- Pinned Lingnik/icloud-reminders-mcp commit.
- Authenticated Streamable HTTP bridge with supergateway 4.1.0.
- Read-only startup compatibility probe for VTODO-capable reminder lists.
- Reminder deletion disabled by default.

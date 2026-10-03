# Changelog

## 0.1.2

- Replace Supergateway with pinned mcp-proxy 0.12.0 for the Reminders bridge.
- Keep one Python MCP 1.x-compatible stdio session open instead of negotiating the newer server/discover protocol.
- Add a minimal streaming-safe ASGI bearer-token middleware so the internal /mcp endpoint remains authenticated.
- Keep the read-only CalDAV VTODO compatibility probe and all Reminder safety settings unchanged.

## 0.1.1

- Skip the upstream duplicate CalDAV startup discovery after the Home Assistant wrapper compatibility probe.
- This allows the MCP stdio server to start without a second Apple network discovery.
- Reminder tools and the read-only compatibility probe are unchanged.

## 0.1.0

- Initial Home Assistant App wrapper.
- Pinned Lingnik/icloud-reminders-mcp commit.
- Authenticated Streamable HTTP bridge.
- Read-only startup compatibility probe for VTODO-capable reminder lists.
- Reminder deletion disabled by default.

# Pre-install checklist

1. Confirm the personal Home Assistant instance.
2. Create an Apple app-specific password for iCloud Core and a random local bearer token of at least 24 characters.
3. Keep iCloud Mail disabled unless needed, and begin in read-only mode.
4. Obtain separate OpenAI Tunnel IDs and runtime keys for every target MCP.
5. Configure each entry in OpenAI Secure MCP Tunnels with its own URL and corresponding target MCP token.
6. If connecting Lexware Office, install and configure its separate MCP App first. Do not put Lexware API credentials into the shared tunnel.
7. Do not expose any MCP target port to the host or the internet.
8. Confirm Home Assistant Apps are stopped immediately after installation; optional **Start on boot** is off by default.
9. Protect Home Assistant backups because App options contain secrets.

Suggested token generation on a trusted device:

```sh
openssl rand -hex 32
```

Never commit generated secrets into Git.

# Pre-install checklist

Before installation:

1. Confirm this is the private Home Assistant environment.
2. Generate one Apple app-specific password for iCloud Core.
3. If using Reminders, preferably generate a second app-specific password for Reminders.
4. Generate a random local MCP bearer token for each MCP App. Use at least 24 random characters.
5. Create the required OpenAI Secure MCP Tunnel IDs/runtime credentials.
6. Decide which iCloud capabilities are needed. Keep Mail disabled if it is not required.
7. Keep the main Apple Account password out of Home Assistant.
8. Verify that Home Assistant backups are protected because App options can be included in backups.

Suggested local token generation from a trusted shell:

```sh
openssl rand -hex 32
```

Do not commit generated values to Git.

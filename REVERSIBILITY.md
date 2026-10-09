# Reversibility

This repository currently provides two independent Home Assistant Apps:

1. Private iCloud MCP
2. OpenAI Secure MCP Tunnels

Installation does not change Home Assistant Core configuration or router rules.

## Disconnecting an MCP target

1. Remove its entry from the shared tunnel list.
2. Restart the shared tunnel App and verify the remaining tunnels still work.
3. Stop/uninstall the target MCP App only if no longer needed.
4. Disconnect the retired ChatGPT plugin and revoke unused tunnel runtime credentials when possible.

Do not remove the shared tunnel App if another entry (for example Lexware Office) still uses it.

## Removing this entire repository installation

1. Stop the shared tunnel App and the iCloud MCP App.
2. Uninstall both Apps in Home Assistant.
3. Revoke now-unused Apple app-specific password and OpenAI tunnel runtime credentials.
4. Optionally remove the App repository from Home Assistant.

No private calendar or contact data is deleted from Apple's cloud when the App is removed.

# Reversibility

All three Apps are designed to be removable without modifying Home Assistant Core configuration.

## Disconnect ChatGPT first

Stop or remove the relevant tunnel configuration before removing an MCP App.

## Stop Apps

Recommended order:

1. Stop OpenAI Secure MCP Tunnels.
2. Stop Private iCloud Reminders MCP.
3. Stop Private iCloud MCP.

## Revoke credentials

At account.apple.com, revoke any app-specific passwords created for these Apps if you no longer need them.

Revoke/delete OpenAI tunnel runtime credentials according to the tunnel management workflow if the tunnel is being retired.

## Uninstall

Uninstall the Apps from Home Assistant. Then remove this repository from the App store if desired.

No router port forwarding, Home Assistant integration entry, or host-level service is created by this repository.

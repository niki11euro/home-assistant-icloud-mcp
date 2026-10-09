# Private iCloud MCP

## Overview

Apple Calendar (CalDAV), Contacts (CardDAV) and optional iCloud Mail (IMAP/SMTP) are exposed as a private MCP server to the shared OpenAI Secure MCP Tunnels Home Assistant App.

The pinned upstream is `ThomasCrouzet/icloud-mcp` commit `84cb170b1dd62ee01a5018290b80375ea47c1f19`. It is bridged through `supergateway` v4.1.0. The Home Assistant wrapper applies a reviewed patch to the *server-side MCP tool registry*, not just to the HA configuration screen.

## Independent Calendar / Contacts permissions

The Home Assistant **Private iCloud MCP → Configuration** page has four independent switches:

| Option | Initial default | Grants these MCP tools |
|---|---:|---|
| `calendar_read` | true | `list_calendars`, `search_events`, `get_event`, `find_free_slots`, `validate_event` |
| `calendar_write` | false | `create_event`, `update_event`, `delete_event` |
| `contacts_read` | false | `list_address_books`, `search_contacts`, `get_contact` |
| `contacts_write` | false | `create_contact`, `update_contact`, `delete_contact` |

`calendar_capabilities` and `icloud_capabilities` report only local feature metadata and remain available regardless of switches. If both permissions for a domain are off, no domain data tools are registered.

Each switch is independent: write-only configurations are supported when an exact resource identifier is already known. In normal use enable read alongside write to discover calendar and address-book identifiers.

**Mail remains separately configured** using `enable_mail`, `enable_mail_write`, `enable_mail_send` and `smtp_allowed_recipients`. The previous shared `read_only` and `enable_contacts` options are obsolete and no longer displayed. The startup wrapper provides a compatibility fallback for older `options.json` files that lack the new switches.

Save permission changes and **restart this MCP App**. The startup process validates the booleans, exports domain-specific policy flags, and constructs an immutable tool registration plan. Denied tools are absent from MCP `tools/list` and cannot be called directly by name. Refresh the ChatGPT connector if its displayed tool catalog is cached.

## Credentials and networking

Use an Apple app-specific password, never the Apple Account password. The token between the tunnel App and this MCP endpoint must be independent of all business-service tokens.

The App only publishes an authenticated private Streamable HTTP `/mcp` endpoint on the Home Assistant app network. No host or router port forwarding is required.

## Deployment/upgrade note

When updating from 0.1.2, **copy existing settings before deployment**:

- old `read_only: false` implies `calendar_write: true`
- old `enable_contacts: false` implies `contacts_read: false` and `contacts_write: false`
- `calendar_read` was previously always enabled

The new `calendar_write` default is false for clean installations. Existing deployments should have their four explicit switches set from the actual old state and verified after restart. Do not assume a config migration is complete until the MCP `icloud_capabilities` result matches the desired rights.

# Security

## Credential model

Use an Apple app-specific password only. Never enter the main Apple Account password into these Apps.

Home Assistant stores App options in each App's persistent data area. Password fields are masked in the UI, but backups may contain those values. Protect Home Assistant backups accordingly.

## Network boundaries

The iCloud Apps do not publish host ports by default. They expose port 8080 only on the internal App network and require a bearer token before MCP requests are accepted.

The OpenAI tunnel-client establishes outbound HTTPS connectivity. It receives the MCP target URL and local bearer token, but does not need the Apple app-specific password.

## Least privilege

Recommended first deployment:

- iCloud Core: `read_only: true`
- Contacts: enabled only if needed
- Mail: disabled
- Reminders delete: disabled

After testing, enable only the write capabilities you actually need.

## Apple credential scope

Apple app-specific passwords are not fine-grained per iCloud service. Treat each one as a high-value secret even when a given MCP server exposes only a subset of services. Separate app-specific passwords for Core and Reminders are recommended so either integration can be revoked independently.

## Reminders limitation

The Reminders App uses CalDAV VTODO. Accounts whose reminder lists were migrated to Apple's newer CloudKit-based Reminders storage may expose zero compatible lists. The startup compatibility probe is read-only and fails closed if none are available.

## Reporting

Do not include credentials, bearer tokens, tunnel runtime keys, calendar data, contact details, mail content, or reminder content in issues or logs shared publicly.

#!/bin/sh
set -eu

CONFIG_PATH="/data/options.json"

fail() {
  echo "[icloud-reminders] Configuration error: $1" >&2
  exit 1
}

[ -f "$CONFIG_PATH" ] || fail "Missing /data/options.json"

APPLE_ID="$(jq -er '.apple_id' "$CONFIG_PATH")" || fail "apple_id is required"
APP_PASSWORD="$(jq -er '.app_specific_password' "$CONFIG_PATH")" || fail "app_specific_password is required"
MCP_AUTH_TOKEN="$(jq -er '.mcp_auth_token' "$CONFIG_PATH")" || fail "mcp_auth_token is required"
ALLOW_DELETE="$(jq -r '.allow_delete // false' "$CONFIG_PATH")"
LIST_ALLOWLIST="$(jq -r '.list_allowlist // ""' "$CONFIG_PATH")"
REQUEST_TIMEOUT="$(jq -r '.request_timeout // 30' "$CONFIG_PATH")"

[ -n "$APPLE_ID" ] || fail "apple_id is empty"
[ -n "$APP_PASSWORD" ] || fail "app_specific_password is empty"
[ "${#MCP_AUTH_TOKEN}" -ge 24 ] || fail "mcp_auth_token must contain at least 24 characters"
case "$ALLOW_DELETE" in true|false) ;; *) fail "allow_delete must be true or false" ;; esac

export ICLOUD_USERNAME="$APPLE_ID"
export ICLOUD_APP_PASSWORD="$APP_PASSWORD"
export REMINDERS_ALLOW_DELETE="$ALLOW_DELETE"
export ICLOUD_REQUEST_TIMEOUT="$REQUEST_TIMEOUT"
if [ -n "$LIST_ALLOWLIST" ]; then
  export REMINDERS_LIST_ALLOWLIST="$LIST_ALLOWLIST"
fi

# Read-only viability check. No reminder is created, changed, completed or deleted.
python3 - <<'PYPROBE'
import sys
from icloud_reminders_mcp.caldav_client import RemindersClient
from icloud_reminders_mcp.config import Config
from icloud_reminders_mcp.errors import RemindersError

try:
    lists = RemindersClient(Config.from_env()).list_lists()
except RemindersError as exc:
    print(f"[icloud-reminders] Compatibility probe failed: {exc}", file=sys.stderr)
    raise SystemExit(1)

if not lists:
    print(
        "[icloud-reminders] No VTODO-capable reminder lists were found. "
        "This Apple account may use modern CloudKit Reminders, which this CalDAV MCP cannot access.",
        file=sys.stderr,
    )
    raise SystemExit(3)

print(f"[icloud-reminders] Compatibility probe OK: {len(lists)} VTODO-capable list(s) found.")
PYPROBE

export SUPERGATEWAY_API_KEY="$MCP_AUTH_TOKEN"
unset APP_PASSWORD MCP_AUTH_TOKEN

echo "[icloud-reminders] Starting. allow_delete=$ALLOW_DELETE request_timeout=$REQUEST_TIMEOUT"
echo "[icloud-reminders] Internal MCP endpoint: http://<app-host>:8080/mcp (bearer token required)"

exec supergateway \
  --stdio "icloud-reminders-mcp" \
  --outputTransport streamableHttp \
  --stateful \
  --sessionTimeout 300000 \
  --host 0.0.0.0 \
  --port 8080 \
  --streamableHttpPath /mcp \
  --logLevel info

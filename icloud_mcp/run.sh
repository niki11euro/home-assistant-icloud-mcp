#!/bin/sh
set -eu

CONFIG_PATH="/data/options.json"
SECRETS_DIR="/tmp/icloud-mcp-secrets"

fail() {
  echo "[icloud-mcp] Configuration error: $1" >&2
  exit 1
}

[ -f "$CONFIG_PATH" ] || fail "Missing /data/options.json"

APPLE_ID="$(jq -er '.apple_id' "$CONFIG_PATH")" || fail "apple_id is required"
APP_PASSWORD="$(jq -er '.app_specific_password' "$CONFIG_PATH")" || fail "app_specific_password is required"
MCP_AUTH_TOKEN="$(jq -er '.mcp_auth_token' "$CONFIG_PATH")" || fail "mcp_auth_token is required"

[ -n "$APPLE_ID" ] || fail "apple_id is empty"
[ -n "$APP_PASSWORD" ] || fail "app_specific_password is empty"
[ "${#MCP_AUTH_TOKEN}" -ge 24 ] || fail "mcp_auth_token must contain at least 24 characters"

TIMEZONE="$(jq -r '.timezone // "Europe/Berlin"' "$CONFIG_PATH")"
CALENDAR_READ="$(jq -r 'if has("calendar_read") then .calendar_read else true end' "$CONFIG_PATH")"
CALENDAR_WRITE="$(jq -r 'if has("calendar_write") then .calendar_write elif has("read_only") then (.read_only | not) else false end' "$CONFIG_PATH")"
CONTACTS_READ="$(jq -r 'if has("contacts_read") then .contacts_read elif has("enable_contacts") then .enable_contacts else false end' "$CONFIG_PATH")"
CONTACTS_WRITE="$(jq -r 'if has("contacts_write") then .contacts_write elif has("enable_contacts") and has("read_only") then (.enable_contacts and (.read_only | not)) else false end' "$CONFIG_PATH")"
if [ "$CONTACTS_READ" = "true" ] || [ "$CONTACTS_WRITE" = "true" ]; then
  ENABLE_CONTACTS=true
else
  ENABLE_CONTACTS=false
fi
READ_ONLY=false
ENABLE_MAIL="$(jq -r '.enable_mail // false' "$CONFIG_PATH")"
MAIL_ADDRESS="$(jq -r '.mail_address // ""' "$CONFIG_PATH")"
ENABLE_MAIL_WRITE="$(jq -r '.enable_mail_write // false' "$CONFIG_PATH")"
ENABLE_MAIL_SEND="$(jq -r '.enable_mail_send // false' "$CONFIG_PATH")"
SMTP_ALLOWED="$(jq -r '.smtp_allowed_recipients // ""' "$CONFIG_PATH")"

for pair in "calendar_read:$CALENDAR_READ" "calendar_write:$CALENDAR_WRITE" "contacts_read:$CONTACTS_READ" "contacts_write:$CONTACTS_WRITE" "enable_contacts:$ENABLE_CONTACTS" "enable_mail:$ENABLE_MAIL" "enable_mail_write:$ENABLE_MAIL_WRITE" "enable_mail_send:$ENABLE_MAIL_SEND"; do
  key="${pair%%:*}"
  val="${pair#*:}"
  case "$val" in true|false) ;; *) fail "$key must be true or false" ;; esac
done

if [ "$ENABLE_MAIL" != "true" ] && { [ "$ENABLE_MAIL_WRITE" = "true" ] || [ "$ENABLE_MAIL_SEND" = "true" ]; }; then
  fail "mail write/send cannot be enabled while enable_mail is false"
fi

if [ "$ENABLE_MAIL_SEND" = "true" ] && [ -z "$SMTP_ALLOWED" ]; then
  fail "smtp_allowed_recipients is required when enable_mail_send is true"
fi

if [ "$ENABLE_MAIL" = "true" ] && [ -z "$MAIL_ADDRESS" ]; then
  MAIL_ADDRESS="$APPLE_ID"
fi

umask 077
rm -rf "$SECRETS_DIR"
mkdir -p "$SECRETS_DIR"
printf '%s' "$APPLE_ID" > "$SECRETS_DIR/apple-id"
printf '%s' "$APP_PASSWORD" > "$SECRETS_DIR/app-password"
chmod 0600 "$SECRETS_DIR/apple-id" "$SECRETS_DIR/app-password"

export ICLOUD_EMAIL="file://$SECRETS_DIR/apple-id"
export ICLOUD_PASSWORD="file://$SECRETS_DIR/app-password"
export ICLOUD_MCP_DEFAULT_TZ="$TIMEZONE"
export ICLOUD_MCP_READ_ONLY="$READ_ONLY"
export ICLOUD_MCP_ENABLE_CONTACTS="$ENABLE_CONTACTS"
export ICLOUD_MCP_CALENDAR_READ="$CALENDAR_READ"
export ICLOUD_MCP_CALENDAR_WRITE="$CALENDAR_WRITE"
export ICLOUD_MCP_CONTACTS_READ="$CONTACTS_READ"
export ICLOUD_MCP_CONTACTS_WRITE="$CONTACTS_WRITE"
export ICLOUD_MCP_ENABLE_MAIL="$ENABLE_MAIL"
export ICLOUD_MCP_ENABLE_MAIL_WRITE="$ENABLE_MAIL_WRITE"
export ICLOUD_MCP_ENABLE_MAIL_SEND="$ENABLE_MAIL_SEND"
export ICLOUD_MCP_LOG_LEVEL="info"

if [ "$ENABLE_MAIL" = "true" ]; then
  printf '%s' "$MAIL_ADDRESS" > "$SECRETS_DIR/mail-address"
  chmod 0600 "$SECRETS_DIR/mail-address"
  export ICLOUD_MAIL_ADDRESS="file://$SECRETS_DIR/mail-address"
fi

if [ -n "$SMTP_ALLOWED" ]; then
  export ICLOUD_MCP_SMTP_ALLOWED_RECIPIENTS="$SMTP_ALLOWED"
fi

export SUPERGATEWAY_API_KEY="$MCP_AUTH_TOKEN"
unset APP_PASSWORD MCP_AUTH_TOKEN

echo "[icloud-mcp] Starting. calendar_read=$CALENDAR_READ calendar_write=$CALENDAR_WRITE contacts_read=$CONTACTS_READ contacts_write=$CONTACTS_WRITE mail=$ENABLE_MAIL mail_write=$ENABLE_MAIL_WRITE mail_send=$ENABLE_MAIL_SEND timezone=$TIMEZONE"
echo "[icloud-mcp] Internal MCP endpoint: http://<app-host>:8080/mcp (bearer token required)"

exec supergateway \
  --stdio "/usr/local/bin/icloud-mcp" \
  --outputTransport streamableHttp \
  --stateful \
  --sessionTimeout 300000 \
  --host 0.0.0.0 \
  --port 8080 \
  --streamableHttpPath /mcp \
  --logLevel info

#!/bin/sh
set -eu

CONFIG_PATH="/data/options.json"
PIDS=""

fail() {
  echo "[openai-tunnels] Configuration error: $1" >&2
  exit 1
}

cleanup() {
  for pid in $PIDS; do
    kill -TERM "$pid" 2>/dev/null || true
  done
  for pid in $PIDS; do
    wait "$pid" 2>/dev/null || true
  done
}

terminate() {
  cleanup
  exit 0
}

trap terminate INT TERM

[ -f "$CONFIG_PATH" ] || fail "Missing /data/options.json"
COUNT="$(jq -er '.tunnels | length' "$CONFIG_PATH")" || fail "tunnels must be a list"
[ "$COUNT" -gt 0 ] || fail "Configure at least one tunnel entry"

INDEX=0
while [ "$INDEX" -lt "$COUNT" ]; do
  NAME="$(jq -er ".tunnels[$INDEX].name" "$CONFIG_PATH")" || fail "tunnels[$INDEX].name is required"
  TUNNEL_ID="$(jq -er ".tunnels[$INDEX].control_plane_tunnel_id" "$CONFIG_PATH")" || fail "tunnels[$INDEX].control_plane_tunnel_id is required"
  API_KEY="$(jq -er ".tunnels[$INDEX].control_plane_api_key" "$CONFIG_PATH")" || fail "tunnels[$INDEX].control_plane_api_key is required"
  SERVER_URL="$(jq -er ".tunnels[$INDEX].mcp_server_url" "$CONFIG_PATH")" || fail "tunnels[$INDEX].mcp_server_url is required"
  AUTH_TOKEN="$(jq -er ".tunnels[$INDEX].mcp_auth_token" "$CONFIG_PATH")" || fail "tunnels[$INDEX].mcp_auth_token is required"

  [ -n "$NAME" ] || fail "tunnels[$INDEX].name is empty"
  [ -n "$TUNNEL_ID" ] || fail "tunnels[$INDEX].control_plane_tunnel_id is empty"
  [ -n "$API_KEY" ] || fail "tunnels[$INDEX].control_plane_api_key is empty"
  [ "${#AUTH_TOKEN}" -ge 24 ] || fail "tunnels[$INDEX].mcp_auth_token must contain at least 24 characters"
  case "$SERVER_URL" in http://*|https://*) ;; *) fail "tunnels[$INDEX].mcp_server_url must start with http:// or https://" ;; esac

  HEALTH_PORT=$((18080 + INDEX))

  echo "[openai-tunnels] Starting tunnel '$NAME' -> $SERVER_URL"
  (
    export CONTROL_PLANE_TUNNEL_ID="$TUNNEL_ID"
    export CONTROL_PLANE_API_KEY="$API_KEY"
    export MCP_SERVER_URL="$SERVER_URL"
    export MCP_TARGET_AUTH_HEADER="Bearer $AUTH_TOKEN"
    export MCP_EXTRA_HEADERS="Authorization: env:MCP_TARGET_AUTH_HEADER"
    export MCP_DISCOVERY_EXTRA_HEADERS="Authorization: env:MCP_TARGET_AUTH_HEADER"
    export MCP_STARTUP_WAIT_TIMEOUT="60s"
    export HEALTH_LISTEN_ADDR="127.0.0.1:$HEALTH_PORT"
    export OPEN_WEB_UI=false
    export ALLOW_REMOTE_UI=false
    exec /usr/bin/tunnel-client run
  ) &

  PIDS="$PIDS $!"
  INDEX=$((INDEX + 1))
done

# Fail closed: if any configured tunnel process dies, stop the remaining ones and
# let Home Assistant report/restart the App rather than silently losing one tunnel.
while :; do
  for pid in $PIDS; do
    if ! kill -0 "$pid" 2>/dev/null; then
      set +e
      wait "$pid"
      STATUS=$?
      set -e
      echo "[openai-tunnels] A tunnel process exited with status $STATUS; stopping all tunnels." >&2
      cleanup
      exit "$STATUS"
    fi
  done
  sleep 2
done

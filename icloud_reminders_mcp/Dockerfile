FROM python:3.13-alpine

ARG REMINDERS_MCP_COMMIT=bd9b4fac4da99a6bc3bb348a5eeb3eac62489373
ARG SUPERGATEWAY_VERSION=4.1.0
ARG BUILD_VERSION
ARG BUILD_ARCH

LABEL     io.hass.version="$BUILD_VERSION"     io.hass.type="app"     io.hass.arch="$BUILD_ARCH"

RUN apk add --no-cache ca-certificates jq nodejs npm git     && git clone https://github.com/Lingnik/icloud-reminders-mcp.git /tmp/icloud-reminders-mcp     && cd /tmp/icloud-reminders-mcp     && git checkout "$REMINDERS_MCP_COMMIT"     && sed -i 's/    _startup_discovery(client)/    # Home Assistant wrapper already performed the CalDAV compatibility probe./' src/icloud_reminders_mcp/server.py     && pip install --no-cache-dir .     && mkdir -p /licenses/icloud-reminders-mcp     && cp LICENSE /licenses/icloud-reminders-mcp/LICENSE     && cd /     && rm -rf /tmp/icloud-reminders-mcp     && apk del git

RUN npm install -g --omit=dev --ignore-scripts "supergateway@${SUPERGATEWAY_VERSION}"     && npm cache clean --force

RUN mkdir -p /licenses/supergateway \
    && cp /usr/local/lib/node_modules/supergateway/LICENSE /licenses/supergateway/LICENSE
COPY run.sh /run.sh
RUN chmod 0755 /run.sh

EXPOSE 8080
CMD ["/run.sh"]

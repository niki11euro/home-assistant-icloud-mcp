FROM golang:1.26.8-alpine AS icloud-builder

ARG ICLOUD_MCP_COMMIT=84cb170b1dd62ee01a5018290b80375ea47c1f19

RUN apk add --no-cache git ca-certificates python3
WORKDIR /src
COPY patch_contacts.py /tmp/patch_contacts.py
RUN git clone https://github.com/ThomasCrouzet/icloud-mcp.git . \
    && git checkout "$ICLOUD_MCP_COMMIT" \
    && python3 /tmp/patch_contacts.py /src \
    && gofmt -w internal/contacts/operations.go internal/contacts/service.go internal/contacts/contacts_test.go \
    && go test ./internal/contacts \
    && CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/icloud-mcp ./cmd/icloud-mcp

FROM node:24.14.1-alpine

ARG SUPERGATEWAY_VERSION=4.1.0
ARG BUILD_VERSION
ARG BUILD_ARCH

LABEL     io.hass.version="$BUILD_VERSION"     io.hass.type="app"     io.hass.arch="$BUILD_ARCH"

RUN apk add --no-cache ca-certificates jq \
    && npm install -g --omit=dev --ignore-scripts "supergateway@${SUPERGATEWAY_VERSION}" \
    && npm cache clean --force

COPY --from=icloud-builder /out/icloud-mcp /usr/local/bin/icloud-mcp
COPY --from=icloud-builder /src/LICENSE /licenses/icloud-mcp/LICENSE
RUN mkdir -p /licenses/supergateway \
    && cp /usr/local/lib/node_modules/supergateway/LICENSE /licenses/supergateway/LICENSE
COPY run.sh /run.sh
RUN chmod 0755 /run.sh /usr/local/bin/icloud-mcp

EXPOSE 8080
CMD ["/run.sh"]

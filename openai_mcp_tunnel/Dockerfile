FROM ghcr.io/openai/tunnel-client:v0.0.15

ARG BUILD_VERSION
ARG BUILD_ARCH

LABEL     io.hass.version="$BUILD_VERSION"     io.hass.type="app"     io.hass.arch="$BUILD_ARCH"

USER root
RUN apk add --no-cache jq

COPY run.sh /ha-run.sh
RUN chmod 0755 /ha-run.sh

ENTRYPOINT ["/ha-run.sh"]

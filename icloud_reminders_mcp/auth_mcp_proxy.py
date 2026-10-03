#!/usr/bin/env python3
"""Launch mcp-proxy with mandatory bearer authentication on every HTTP request."""

from __future__ import annotations

import hmac
import os
from typing import Any

from starlette.applications import Starlette as OriginalStarlette
from starlette.middleware import Middleware
from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Receive, Scope, Send

import mcp_proxy.mcp_server as mcp_server


class BearerAuthMiddleware:
    """Minimal ASGI bearer-token guard that preserves streaming responses."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") == "http":
            token = os.environ.get("MCP_AUTH_TOKEN", "")
            expected = ("Bearer " + token).encode("utf-8")
            supplied = b""
            for key, value in scope.get("headers", []):
                if key.lower() == b"authorization":
                    supplied = value
                    break

            if not token or not hmac.compare_digest(supplied, expected):
                response = PlainTextResponse(
                    "Unauthorized",
                    status_code=401,
                    headers={"WWW-Authenticate": "Bearer"},
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)


def authenticated_starlette(
    *args: Any,
    middleware: list[Middleware] | None = None,
    **kwargs: Any,
) -> OriginalStarlette:
    chain = list(middleware or [])
    chain.insert(0, Middleware(BearerAuthMiddleware))
    return OriginalStarlette(*args, middleware=chain, **kwargs)


# mcp-proxy constructs its Starlette application inside run_mcp_server().
# Replace only that constructor; all MCP protocol handling stays upstream.
mcp_server.Starlette = authenticated_starlette  # type: ignore[assignment]

from mcp_proxy.__main__ import main  # noqa: E402


if __name__ == "__main__":
    main()

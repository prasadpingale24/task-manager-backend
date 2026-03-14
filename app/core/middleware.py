from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.datastructures import MutableHeaders


class SecurityHeadersMiddleware:
    """
    Pure ASGI middleware to inject security headers into every HTTP response.

    Avoids the known BaseHTTPMiddleware issue with streaming responses that
    causes 'Connection reset by peer' errors in some Starlette/FastAPI versions.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        is_docs = (
            path.startswith("/docs")
            or path.startswith("/redoc")
            or path.startswith("/openapi.json")
        )

        async def send_with_security_headers(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Frame-Options"] = "DENY"
                headers["X-Content-Type-Options"] = "nosniff"
                headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
                headers["X-XSS-Protection"] = "0"
                if is_docs:
                    # Allow Swagger UI assets for docs pages only.
                    headers["Content-Security-Policy"] = (
                        "default-src 'self'; "
                        "style-src 'self' https://cdn.jsdelivr.net; "
                        "script-src 'self' https://cdn.jsdelivr.net; "
                        "img-src 'self' https://fastapi.tiangolo.com data:; "
                        "connect-src 'self'; "
                        "frame-ancestors 'none'; "
                        "base-uri 'none';"
                    )
                else:
                    headers["Content-Security-Policy"] = (
                        "default-src 'none'; frame-ancestors 'none'; base-uri 'none';"
                    )
                # Remove Server header if present
                if "server" in headers:
                    del headers["server"]
            await send(message)

        await self.app(scope, receive, send_with_security_headers)

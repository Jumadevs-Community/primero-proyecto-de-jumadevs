import time
from collections import defaultdict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    LIMIT = 100
    WINDOW = 60

    def __init__(self, app):
        super().__init__(app)
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
        ip = request.client.host
        now = time.time()
        self._hits[ip] = [t for t in self._hits[ip] if t > now - self.WINDOW]
        self._hits[ip].append(now)
        if len(self._hits[ip]) > self.LIMIT:
            return Response(content='{"detail":"Too Many Requests"}', status_code=429, media_type="application/json")
        return await call_next(request)


rate_limit_middleware = RateLimitMiddleware

from collections.abc import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.user import User


class RBACMiddleware(BaseHTTPMiddleware):
    # Route-level role policies. Every non-auth endpoint must be explicitly defined.
    role_policies: dict[tuple[str, str], set[str]] = {
        ("GET", "/inventory"): {"admin", "manager", "operations", "procurement"},
        ("POST", "/holds"): {"admin", "manager", "operations"},
        ("POST", "/quotes/draft"): {"admin", "manager", "procurement"},
        ("POST", "/quotes/approve"): {"admin", "manager"},
    }

    public_paths: set[str] = {"/auth/login", "/health", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next: Callable):
        if request.url.path in self.public_paths:
            return await call_next(request)

        key = (request.method.upper(), request.url.path)
        required_roles = self.role_policies.get(key)
        if required_roles is None:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"error": "RBAC policy not configured for route"},
            )

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Missing bearer token"},
            )

        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_access_token(token)
            username = payload.get("sub")
            if not username:
                raise ValueError("Missing token subject")
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid authentication token"},
            )

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username, User.is_active.is_(True)).first()
            if not user:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"error": "User not found or inactive"},
                )

            user_roles = {role.name for role in user.roles}
            if user_roles.isdisjoint(required_roles):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"error": "Insufficient permissions"},
                )

            request.state.user_id = user.id
            request.state.username = user.username
            request.state.roles = user_roles
        finally:
            db.close()

        return await call_next(request)

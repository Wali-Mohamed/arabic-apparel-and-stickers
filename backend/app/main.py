import os
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine
from app.products import router as products_router
from app.orders import router as orders_router

async def health() -> dict[str, str]:
    return {"status": "ok"}


async def database_health() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

    return {"status": "ok", "database": "connected"}


def create_app() -> FastAPI:
    production = os.getenv("APP_ENV") == "production"
    origin = os.getenv("PUBLIC_ORIGIN", "http://localhost:5173").rstrip("/")
    hosts = [host.strip() for host in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",") if host.strip()]
    if production:
        parsed = urlsplit(origin)
        if not os.getenv("ALLOWED_HOSTS") or any("*" in host for host in hosts):
            raise RuntimeError("Production requires explicit trusted hosts")
        if not os.getenv("PUBLIC_ORIGIN") or not parsed.hostname or parsed.path or parsed.query or parsed.fragment or parsed.username:
            raise RuntimeError("Production requires an exact public origin")
        if parsed.scheme != "https" and not (parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1", "frontend"}):
            raise RuntimeError("Public origin must use HTTPS (HTTP is only for local smoke tests)")
    application = FastAPI(
        title="Arabic Apparel and Stickers API",
        redirect_slashes=not production,
        docs_url=None if production else "/docs",
        redoc_url=None if production else "/redoc",
        openapi_url=None if production else "/openapi.json",
    )
    application.add_middleware(CORSMiddleware, allow_origins=[origin], allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

    @application.middleware("http")
    async def reject_foreign_origin(request: Request, call_next):
        # CORS alone does not stop cross-origin writes. Non-browser API clients
        # without Origin remain allowed; this demo has no authentication.
        if production and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            if request.headers.get("origin") not in {None, origin}:
                return JSONResponse(status_code=403, content={"detail": "Origin is not allowed"})
        return await call_next(request)

    application.add_middleware(TrustedHostMiddleware, allowed_hosts=hosts)
    application.include_router(products_router)
    application.include_router(orders_router)
    application.add_api_route("/health", health, methods=["GET"])
    application.add_api_route("/health/db", database_health, methods=["GET"])
    application.add_api_route("/api/health", health, methods=["GET"])
    application.add_api_route("/api/health/db", database_health, methods=["GET"])
    return application


app = create_app()

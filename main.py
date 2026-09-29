"""
uvicorn main:app --port 8001 --workers 1 --reload
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.settings import settings

from shared.database.migrations import run_startup_migrations
from shared.database.redis_client import get_redis_client, RedisClient
from shared.database.postgres_client import get_postgres_client, PostgresClient
from shared.utils.log_client import log_message
from shared.middleware.docs_protection import DocsProtectionMiddleware
from shared.middleware.rate_limiter.middleware import RateLimitFastAPIMiddleware

# service-level imports
from management.main import management
from storefront.main import storefront


@asynccontextmanager
async def lifespan(app: FastAPI):
    # try:
    #     app.state.redis = await get_redis_client()
    #     app.state.postgres = await get_postgres_client()

    #     await run_startup_migrations()
    #     log_message("Server started successfully", file_name="server", info=True)
    # except Exception:
    #     log_message("Startup failed", file_name="server", error=True)
    #     raise

    yield

    # log_message("Server is shutting down...", file_name="server", info=True)
    # try:
    #     await RedisClient.close_async()
    #     RedisClient.close_sync()
    #     await PostgresClient.close_all()
    #     log_message("Server shut down cleanly", file_name="server", info=True)
    # except Exception:
    #     log_message("Shutdown cleanup failed", file_name="server", error=True)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    root_path="/api",
    lifespan=lifespan,
)

# API doc protection middleware
app.add_middleware(DocsProtectionMiddleware, enabled=True)

# CORS configs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.add_middleware(RateLimitFastAPIMiddleware)

# Register services
app.include_router(management)
app.include_router(storefront)


# Health/Ready check
@app.get("/health")
async def health_check():
    """Liveness check - process is up. No dependency checks here."""
    return JSONResponse(
        content={"status": "ok"}, status_code=200, headers={"Cache-Control": "no-store"}
    )


@app.get("/ready")
async def readiness_check():
    """Readiness check - verifies actual dependencies are reachable."""

    async def check_database():
        try:
            client = PostgresClient()
            result = await client.fetch_value("SELECT 1")
            return "ok" if result == 1 else "unexpected_response"
        except Exception:
            return "error"

    async def check_redis():
        try:
            redis = RedisClient()
            return "ok" if await redis.async_client.ping() else "no_pong"
        except Exception:
            return "error"

    database, redis = await asyncio.gather(check_database(), check_redis())
    checks = {"database": database, "redis": redis}

    is_ready = all(status == "ok" for status in checks.values())

    return JSONResponse(
        content={"status": "ready" if is_ready else "not_ready", "checks": checks},
        status_code=200 if is_ready else 503,
        headers={"Cache-Control": "no-store"},
    )


# Handle 404 Not Found (for non-existent routes)
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404, content={"status": False, "message": "Page not found"}
    )


# Standardized HTTP Exception Handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Log based on status code severity
    log_msg = (
        f"HTTPException ({exc.status_code}) | URL: {request.url} | Error: {exc.detail}"
    )

    if exc.status_code >= 500:
        # Server errors (500+) - Log as ERROR
        log_message(log_msg, file_name="error")
    elif 500 < exc.status_code >= 400:
        # Client errors (400-499) - Log as WARNING
        log_message(log_msg, file_name="warning")
    else:
        # Other status codes - Log as INFO
        log_message(log_msg, file_name="info")

    return JSONResponse(
        status_code=exc.status_code, content={"status": False, "message": exc.detail}
    )


# Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()

    # Get the first error
    if errors:
        first_error = errors[0]

        # Extract field name from location (e.g., ['query', 'status'] -> 'status')
        field_location = first_error.get("loc", [])
        field_name = field_location[-1] if field_location else "field"

        # Get error type and message
        error_type = first_error.get("type", "")
        error_msg = first_error.get("msg", "")

        # Create user-friendly message based on error type
        if "missing" in error_type:
            message = f"Required field '{field_name}' is missing"
        elif "invalid" in error_type or "type_error" in error_type:
            message = f"Invalid value for field '{field_name}': {error_msg}"
        elif "enum" in error_type:
            # For enum validation, show allowed values
            message = f"Invalid value for field '{field_name}'. {error_msg}"
        else:
            message = f"Validation error in field '{field_name}': {error_msg}"
    else:
        message = "Request validation error"

    # Log validation error as WARNING
    log_msg = f"ValidationError (422) | URL: {request.url} | Message: {message} | Total Errors: {len(errors)}"
    log_message(log_msg, file_name="warning")

    return JSONResponse(status_code=422, content={"status": False, "message": message})


# General Exception Handler
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log as CRITICAL since these are unexpected errors
    log_msg = f"UnhandledException (500) | URL: {request.url} | Error: {str(exc)} | Type: {type(exc).__name__}"
    log_message(log_msg, file_name="error")

    # In production, don't expose internal error details
    return JSONResponse(
        status_code=500,
        content={
            "status": False,
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0")

"""
uvicorn main:app --port 8001 --workers 1 --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.settings import settings

# service-level imports
from management.main import management
from shared.utils.log_client import log_message
from storefront.main import storefront


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    root_path="/api",
    lifespan=lifespan,
)

# CORS configs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register services
app.include_router(management)
app.include_router(storefront)


# Health check
@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)


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

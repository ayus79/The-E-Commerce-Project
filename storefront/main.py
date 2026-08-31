from fastapi import APIRouter
from fastapi.responses import JSONResponse


storefront = APIRouter(prefix="/storefront", tags=["Storefront"])


# Health check
@storefront.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)

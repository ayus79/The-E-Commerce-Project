from fastapi import APIRouter
from fastapi.responses import JSONResponse

storefront = APIRouter(prefix="/storefront")


# Health/Ready check
@storefront.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)


@storefront.get("/ready")
async def readiness_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)

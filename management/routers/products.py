from fastapi import APIRouter
from fastapi.responses import JSONResponse


products_v1_route = APIRouter(prefix="/v1", tags=["Management - Products"])


@products_v1_route.get("/products")
async def get_all_products():
    try:
        pass
    except:
        pass

    return JSONResponse()

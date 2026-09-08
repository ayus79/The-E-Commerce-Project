from traceback import format_exc
from fastapi import APIRouter, Depends, Body, Request
from fastapi.responses import JSONResponse
from management.schemas.products import ProductsQuerySchema
from shared.utils.log_client import log_message


products_v1_route = APIRouter(prefix="/v1", tags=["Management - Products"])


@products_v1_route.get("/products")
async def get_all_products_endpoint(
    request: Request, params: ProductsQuerySchema = Depends()
):
    try:
        data = await get_all_products(request, params)
        return JSONResponse(
            content={
                "status": data.get("status"),
                "message": data.get("message"),
                "data": data.get("data"),
            },
            status_code=data.get("status_code", 200),
        )
    except Exception:
        log_message(f"Error: {format_exc()}", error=True)
        return JSONResponse(
            content={"status": False, "message": "Something went wrong.", "data": None},
            status_code=500,
        )

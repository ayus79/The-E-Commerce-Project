from traceback import format_exc

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse

from management.schemas.products import (
    ProductsCreateBodySchema,
    ProductsQuerySchema,
    ProductsUpdateBodySchema,
)
from management.services.products import (
    create_product,
    delete_product,
    get_all_products,
    get_product,
    update_product,
)
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
                "data": data.get("data", None),
            },
            status_code=data.get("status_code", 200),
        )
    except Exception:
        log_message(f"Error: {format_exc()}", error=True)
        return JSONResponse(
            content={"status": False, "message": "Something went wrong.", "data": None},
            status_code=500,
        )


@products_v1_route.get("/products/{product_id}")
async def get_product_endpoint(request: Request, product_id: str):
    try:
        data = await get_product(request, product_id)
        return JSONResponse(
            content={
                "status": data.get("status"),
                "message": data.get("message"),
                "data": data.get("data", None),
            },
            status_code=data.get("status_code", 200),
        )
    except Exception:
        log_message(f"Error: {format_exc()}", error=True)
        return JSONResponse(
            content={"status": False, "message": "Something went wrong.", "data": None},
            status_code=500,
        )


@products_v1_route.post("/products")
async def create_product_endpoint(
    request: Request, params: ProductsCreateBodySchema = Body(...)
):
    try:
        data = await create_product(request, params)
        return JSONResponse(
            content={
                "status": data.get("status"),
                "message": data.get("message"),
                "data": data.get("data", None),
            },
            status_code=data.get("status_code", 200),
        )
    except Exception:
        log_message(f"Error: {format_exc()}", error=True)
        return JSONResponse(
            content={"status": False, "message": "Something went wrong.", "data": None},
            status_code=500,
        )


@products_v1_route.put("/products/{product_id}")
async def update_product_endpoint(
    request: Request, product_id: str, params: ProductsUpdateBodySchema = Body(...)
):
    try:
        data = await update_product(request, product_id, params)
        return JSONResponse(
            content={
                "status": data.get("status"),
                "message": data.get("message"),
                "data": data.get("data", None),
            },
            status_code=data.get("status_code", 200),
        )
    except Exception:
        log_message(f"Error: {format_exc()}", error=True)
        return JSONResponse(
            content={"status": False, "message": "Something went wrong.", "data": None},
            status_code=500,
        )


@products_v1_route.delete("/products/{product_id}")
async def delete_product_endpoint(request: Request, product_id: str):
    try:
        data = await delete_product(request, product_id)
        return JSONResponse(
            content={
                "status": data.get("status"),
                "message": data.get("message"),
                "data": data.get("data", None),
            },
            status_code=data.get("status_code", 200),
        )
    except Exception:
        log_message(f"Error: {format_exc()}", error=True)
        return JSONResponse(
            content={"status": False, "message": "Something went wrong.", "data": None},
            status_code=500,
        )

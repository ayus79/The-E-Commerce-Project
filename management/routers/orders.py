from traceback import format_exc

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse

from management.schemas.orders import (
    OrdersQuerySchema,
    OrdersCreateBodySchema,
    OrdersUpdateBodySchema,
)
from management.services.orders import (
    get_all_orders,
    get_order,
    create_order,
    update_order,
    delete_order,
)
from shared.utils.log_client import log_message

orders_v1_route = APIRouter(prefix="/v1", tags=["Management - Orders"])


@orders_v1_route.get("/orders")
async def get_all_orders_endpoint(
    request: Request, params: OrdersQuerySchema = Depends()
):
    try:
        data = await get_all_orders(request, params)
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


@orders_v1_route.get("/orders/{order_id}")
async def get_order_endpoint(request: Request, order_id: str):
    try:
        data = await get_order(request, order_id)
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


@orders_v1_route.post("/orders")
async def create_order_endpoint(
    request: Request, params: OrdersCreateBodySchema = Body(...)
):
    try:
        data = await create_order(request, params)
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


@orders_v1_route.put("/orders/{order_id}")
async def update_order_endpoint(
    request: Request, order_id: str, params: OrdersUpdateBodySchema = Body(...)
):
    try:
        data = await update_order(request, order_id, params)
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


@orders_v1_route.delete("/orders/{order_id}")
async def delete_order_endpoint(request: Request, order_id: str):
    try:
        data = await delete_order(request, order_id)
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

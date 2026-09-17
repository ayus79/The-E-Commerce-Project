from traceback import format_exc

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse

from management.schemas.customers import (
    CustomersQuerySchema,
    CustomersCreateBodySchema,
    CustomersUpdateBodySchema,
)
from management.services.customers import (
    get_all_customers,
    get_customer,
    create_customer,
    update_customer,
    delete_customer,
)
from shared.utils.log_client import log_message


customers_v1_route = APIRouter(prefix="/v1", tags=["Management - Customers"])


@customers_v1_route.get("/customers")
async def get_all_customers_endpoint(
    request: Request, params: CustomersQuerySchema = Depends()
):
    try:
        data = await get_all_customers(request, params)
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


@customers_v1_route.get("/customers/{customer_id}")
async def get_customer_endpoint(request: Request, customer_id: str):
    try:
        data = await get_customer(request, customer_id)
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


@customers_v1_route.post("/customers")
async def create_customer_endpoint(
    request: Request, params: CustomersCreateBodySchema = Body(...)
):
    try:
        data = await create_customer(request, params)
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


@customers_v1_route.put("/customers/{customer_id}")
async def update_customer_endpoint(
    request: Request, customer_id: str, params: CustomersUpdateBodySchema = Body(...)
):
    try:
        data = await update_customer(request, customer_id, params)
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


@customers_v1_route.delete("/customers/{customer_id}")
async def delete_customer_endpoint(request: Request, customer_id: str):
    try:
        data = await delete_customer(request, customer_id)
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

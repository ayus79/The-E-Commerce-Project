from traceback import format_exc

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse

from management.schemas.payments import (
    PaymentsQuerySchema,
    PaymentsCreateBodySchema,
    PaymentsUpdateBodySchema,
)
from management.services.payments import (
    get_all_payments,
    get_payment,
    create_payment,
    update_payment,
    delete_payment,
)
from shared.utils.log_client import log_message


payments_v1_route = APIRouter(prefix="/v1/payments", tags=["Management - Payments"])


@payments_v1_route.get("")
async def get_all_payments_endpoint(
    request: Request, params: PaymentsQuerySchema = Depends()
):
    try:
        data = await get_all_payments(request, params)
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


@payments_v1_route.get("/{payment_id}")
async def get_payment_endpoint(request: Request, payment_id: str):
    try:
        data = await get_payment(request, payment_id)
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


@payments_v1_route.post("")
async def create_payment_endpoint(
    request: Request, params: PaymentsCreateBodySchema = Body(...)
):
    try:
        data = await create_payment(request, params)
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


@payments_v1_route.put("/{payment_id}")
async def update_payment_endpoint(
    request: Request, payment_id: str, params: PaymentsUpdateBodySchema = Body(...)
):
    try:
        data = await update_payment(request, payment_id, params)
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


@payments_v1_route.delete("/{payment_id}")
async def delete_payment_endpoint(request: Request, payment_id: str):
    try:
        data = await delete_payment(request, payment_id)
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

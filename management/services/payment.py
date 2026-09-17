from fastapi import Request

from management.messages import PAYMENT
from management.schemas.payment import (
    PaymentQuerySchema,
    PaymentCreateBodySchema,
    PaymentUpdateBodySchema,
)


async def get_all_payment(request: Request, params: PaymentQuerySchema) -> list[dict]:

    return {"status": True, "message": PAYMENT["LIST_SUCCESS"], "data": []}


async def get_payment(request: Request, payment_id: str) -> dict:

    return {"status": True, "message": PAYMENT["LIST_SUCCESS"], "data": {}}


async def create_payment(request: Request, params: PaymentCreateBodySchema) -> dict:

    return {"status": True, "message": PAYMENT["LIST_SUCCESS"], "data": []}


async def update_payment(
    request: Request, payment_id: str, params: PaymentUpdateBodySchema
) -> dict:

    return {"status": True, "message": PAYMENT["LIST_SUCCESS"], "data": []}


async def delete_payment(request: Request, payment_id: str) -> dict:

    return {"status": True, "message": PAYMENT["LIST_SUCCESS"], "data": []}

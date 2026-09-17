from fastapi import Request

from management.messages import PAYMENTS
from management.schemas.payments import (
    PaymentsQuerySchema,
    PaymentsCreateBodySchema,
    PaymentsUpdateBodySchema,
)


async def get_all_payments(request: Request, params: PaymentsQuerySchema) -> list[dict]:

    return {"status": True, "message": PAYMENTS["LIST_SUCCESS"], "data": []}


async def get_payment(request: Request, payment_id: str) -> dict:

    return {"status": True, "message": PAYMENTS["LIST_SUCCESS"], "data": {}}


async def create_payment(request: Request, params: PaymentsCreateBodySchema) -> dict:

    return {"status": True, "message": PAYMENTS["LIST_SUCCESS"], "data": []}


async def update_payment(
    request: Request, payment_id: str, params: PaymentsUpdateBodySchema
) -> dict:

    return {"status": True, "message": PAYMENTS["LIST_SUCCESS"], "data": []}


async def delete_payment(request: Request, payment_id: str) -> dict:

    return {"status": True, "message": PAYMENTS["LIST_SUCCESS"], "data": []}

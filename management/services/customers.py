from fastapi import Request

from management.messages import CUSTOMERS
from management.schemas.customers import (
    CustomersQuerySchema,
    CustomersCreateBodySchema,
    CustomersUpdateBodySchema,
)


async def get_all_customers(
    request: Request, params: CustomersQuerySchema
) -> list[dict]:

    return {"status": True, "message": CUSTOMERS["LIST_SUCCESS"], "data": []}


async def get_customer(request: Request, customer_id: str) -> dict:

    return {"status": True, "message": CUSTOMERS["LIST_SUCCESS"], "data": {}}


async def create_customer(request: Request, params: CustomersCreateBodySchema) -> dict:

    return {"status": True, "message": CUSTOMERS["LIST_SUCCESS"], "data": []}


async def update_customer(
    request: Request, customer_id: str, params: CustomersUpdateBodySchema
) -> dict:

    return {"status": True, "message": CUSTOMERS["LIST_SUCCESS"], "data": []}


async def delete_customer(request: Request, customer_id: str) -> dict:

    return {"status": True, "message": CUSTOMERS["LIST_SUCCESS"], "data": []}

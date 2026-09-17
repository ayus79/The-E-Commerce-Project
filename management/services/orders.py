from fastapi import Request

from management.messages import ORDERS
from management.schemas.orders import (
    OrdersQuerySchema,
    OrdersCreateBodySchema,
    OrdersUpdateBodySchema,
)


async def get_all_orders(request: Request, params: OrdersQuerySchema) -> list[dict]:

    return {"status": True, "message": ORDERS["LIST_SUCCESS"], "data": []}


async def get_order(request: Request, order_id: str) -> dict:

    return {"status": True, "message": ORDERS["LIST_SUCCESS"], "data": {}}


async def create_order(request: Request, params: OrdersCreateBodySchema) -> dict:

    return {"status": True, "message": ORDERS["LIST_SUCCESS"], "data": []}


async def update_order(
    request: Request, order_id: str, params: OrdersUpdateBodySchema
) -> dict:

    return {"status": True, "message": ORDERS["LIST_SUCCESS"], "data": []}


async def delete_order(request: Request, order_id: str) -> dict:

    return {"status": True, "message": ORDERS["LIST_SUCCESS"], "data": []}

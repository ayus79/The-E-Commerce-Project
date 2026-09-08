from fastapi import Request
from management.schemas.products import (
    ProductsQuerySchema,
    ProductsUpdateBodySchema,
    ProductsCreateBodySchema,
)
from management.messages import PRODUCTS


async def get_all_products(request: Request, params: ProductsQuerySchema) -> list[dict]:

    return {"status": True, "message": PRODUCTS["LIST_SUCCESS"], "data": []}


async def get_product(request: Request, product_id: str) -> dict:

    return {"status": True, "message": PRODUCTS["LIST_SUCCESS"], "data": {}}


async def create_product(request: Request, params: ProductsUpdateBodySchema) -> dict:

    return {"status": True, "message": PRODUCTS["LIST_SUCCESS"], "data": []}


async def update_product(
    request: Request, product_id: str, params: ProductsCreateBodySchema
) -> dict:

    return {"status": True, "message": PRODUCTS["LIST_SUCCESS"], "data": []}


async def delete_product(request: Request, product_id: str) -> dict:

    return {"status": True, "message": PRODUCTS["LIST_SUCCESS"], "data": []}

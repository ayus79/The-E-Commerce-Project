from fastapi import Request
from management.schemas.products import ProductsQuerySchema
from management.messages import PRODUCTS


async def get_all_products(request: Request, params: ProductsQuerySchema) -> list[dict]:

    return {"status": True, "message": PRODUCTS["LIST_SUCCESS"], "data": []}


async def get_product(request: Request, product_id: str) -> dict:

    return {"status": True, "message": PRODUCTS["LIST_SUCCESS"], "data": {}}

from fastapi import Request
from shared.database.postgres_client import PostgresClient
from management.messages import PRODUCTS
from management.schemas.products import (
    ProductsCreateBodySchema,
    ProductsQuerySchema,
    ProductsUpdateBodySchema,
)


async def get_all_products(request: Request, params: ProductsQuerySchema) -> list[dict]:

    return {"status": True, "message": PRODUCTS["LIST_SUCCESS"], "data": []}


async def get_product(request: Request, product_id: str) -> dict:

    return {"status": True, "message": PRODUCTS["LIST_SUCCESS"], "data": {}}


async def create_product(request: Request, params: ProductsCreateBodySchema) -> dict:
    data = {
        "sku": params.sku,
        "name": params.name,
        "slug": params.slug,
        "description": params.description,
        "price": params.price,
        "currency": params.currency,
        "attributes": params.attributes,
        "is_published": params.is_published,
        "is_active": params.is_active,
    }

    query = """
        INSERT INTO products (
            sku, name, slug, description, price, currency,
            attributes, is_published, is_active
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING id, sku, name, slug, description, price, currency,
                  attributes, is_published, is_active
    """
    inserted_data = await PostgresClient().fetch_one(query, *data.values())

    return {"status": True, "message": PRODUCTS["CREATE"], "data": inserted_data}


async def update_product(
    request: Request, product_id: str, params: ProductsUpdateBodySchema
) -> dict:

    return {"status": True, "message": PRODUCTS["LIST_SUCCESS"], "data": []}


async def delete_product(request: Request, product_id: str) -> dict:

    return {"status": True, "message": PRODUCTS["LIST_SUCCESS"], "data": []}

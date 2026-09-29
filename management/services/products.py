from fastapi import Request
from core.constants import CoreCollections
from shared.database.postgres_client import PostgresClient
from management.messages import PRODUCTS
from management.schemas.products import (
    ProductsCreateBodySchema,
    ProductsQuerySchema,
    ProductsUpdateBodySchema,
)


async def get_all_products(request: Request, params: ProductsQuerySchema) -> list[dict]:
    offset = (params.page - 1) * params.limit
    sort_order = "ASC" if params.sort_order == "asc" else "DESC"

    base_query = f"""
        SELECT id, sku, name, slug, description, price, currency,
               attributes, is_published, is_active, created_at, updated_at
        FROM {CoreCollections.PRODUCTS}
        WHERE ($1::text IS NULL OR name ILIKE '%' || $1 || '%' OR sku ILIKE '%' || $1 || '%')
        ORDER BY {params.sort_by} {sort_order}
        LIMIT $2 OFFSET $3
    """
    count_query = f"""
        SELECT COUNT(*) FROM {CoreCollections.PRODUCTS}
        WHERE ($1::text IS NULL OR name ILIKE '%' || $1 || '%' OR sku ILIKE '%' || $1 || '%')
    """

    client = PostgresClient()
    data = await client.fetch_all(base_query, params.search, params.limit, offset)
    if not data:
        return {"status": False, "message": PRODUCTS["LIST_EMPTY"]}

    total_count = await client.fetch_value(count_query, params.search)

    return {
        "status": True,
        "message": PRODUCTS["LIST_SUCCESS"],
        "data": data,
        "pagination": {
            "page": params.page,
            "limit": params.limit,
            "total": total_count,
            "total_pages": (
                (total_count + params.limit - 1) // params.limit if total_count else 0
            ),
        },
    }


async def get_product(request: Request, product_id: str) -> dict:
    query = f"""
        SELECT id, sku, name, slug, description, price, currency,
               attributes, is_published, is_active
        FROM {CoreCollections.PRODUCTS} WHERE id = $1
    """
    data = await PostgresClient().fetch_one(query, int(product_id))
    if not data:
        return {"status": False, "message": PRODUCTS["NOT_FOUND"], "status_code": 404}

    return {"status": True, "message": PRODUCTS["FETCH_SUCCESS"], "data": data}


async def create_product(request: Request, params: ProductsCreateBodySchema) -> dict:
    data = params.model_dump()

    query = f"""
        INSERT INTO {CoreCollections.PRODUCTS} (
            sku, name, slug, description, price, currency,
            attributes, is_published, is_active
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING id, sku, name, slug, description, price, currency,
                  attributes, is_published, is_active
    """
    inserted_data = await PostgresClient().fetch_one(query, *data.values())

    return {
        "status": True,
        "message": PRODUCTS["CREATE_SUCCESS"],
        "data": inserted_data,
    }


async def update_product(
    request: Request, product_id: str, params: ProductsUpdateBodySchema
) -> dict:

    return {"status": True, "message": PRODUCTS["UPDATE_SUCCESS"], "data": []}


async def delete_product(request: Request, product_id: str) -> dict:

    return {"status": True, "message": PRODUCTS["DELETE_SUCCESS"], "data": []}

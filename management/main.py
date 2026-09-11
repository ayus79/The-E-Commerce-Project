from fastapi import APIRouter
from fastapi.responses import JSONResponse

# module-level imports
from management.routers.checkout import checkout_v1_route
from management.routers.customers import customers_v1_route
from management.routers.orders import orders_v1_route
from management.routers.payment import payment_v1_route
from management.routers.products import products_v1_route

management = APIRouter(prefix="/management")


management.include_router(checkout_v1_route)
management.include_router(orders_v1_route)
management.include_router(customers_v1_route)
management.include_router(products_v1_route)
management.include_router(payment_v1_route)


# Health check
@management.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)

from fastapi import APIRouter
from fastapi.responses import JSONResponse

# module-level imports
from management.routers.customers import customers_v1_route
from management.routers.orders import orders_v1_route
from management.routers.payments import payments_v1_route
from management.routers.products import products_v1_route

management = APIRouter(prefix="/management")


management.include_router(orders_v1_route)
management.include_router(customers_v1_route)
management.include_router(products_v1_route)
management.include_router(payments_v1_route)


# Health/Ready check
@management.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)


@management.get("/ready")
async def readiness_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)

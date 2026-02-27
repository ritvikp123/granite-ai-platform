from fastapi import APIRouter

from app.api.routes_auth import router as auth_router
from app.api.routes_holds import router as holds_router
from app.api.routes_inventory import router as inventory_router
from app.api.routes_quotes import router as quotes_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(inventory_router)
api_router.include_router(holds_router)
api_router.include_router(quotes_router)

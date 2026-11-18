from fastapi import APIRouter

from backend.src.api.v1.endpoints import fiscal

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(fiscal.router)

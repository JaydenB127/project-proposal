from fastapi import APIRouter
from app.api.v1.endpoints import runs, auth

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(runs.router)
api_router.include_router(auth.router)

# routes/__init__.py
from fastapi import APIRouter
from .auth_routes import router as auth_router
from .dataset_routes import router as dataset_router

# Router principal que agrega todos os sub-routers
api_router = APIRouter()

# Incluir todos os routers da aplicação
api_router.include_router(auth_router)
api_router.include_router(dataset_router)

__all__ = ["api_router"]
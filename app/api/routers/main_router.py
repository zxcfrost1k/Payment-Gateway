# РОУТЕРЫ
from fastapi import APIRouter
from app.api.routers.cancel_transaction_router import router as cancel_router

# Основной роутер
main_router = APIRouter()

# Подключение остальных роутеров
main_router.include_router(cancel_router, prefix="/transactions", tags=["transactions"])

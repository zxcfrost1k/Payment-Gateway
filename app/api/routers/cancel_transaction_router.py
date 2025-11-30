# РОУТЕР ОТМЕНЫ ТРАНЗАКЦИИ
from fastapi import APIRouter

# Объект роутера
router = APIRouter()

@router.post("/transactions/{transaction_id}/cancel")
async def cancel_transaction(transaction_id: str):
    return {"message": f"Transaction {transaction_id} cancelled"}

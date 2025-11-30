# ПРЕОБРАЗОВАНИЕ ЗАПРОСА В ФОРМАТ ПРОВАЙДЕРА
from typing import Dict, Any

from app.models.card_models.card_transaction_internal_bank_model import InternalCardTransactionRequest
from app.models.card_models.card_transaction_model import CardTransactionRequest


def transform_to_provider_format_card(request: CardTransactionRequest) -> Dict[str, Any]:
    payload = {
        'amount': request.amount,
        'currency': request.currency,
        'merchant_transaction_id': request.merchant_transaction_id,
        'rate': request.rate,
        'currency_rate': request.currency_rate,
        'client_id': request.client_id
    }

    payload = {k: v for k, v in payload.items() if v is not None}  # Убираем None значения
    return payload

def transform_to_provider_format_card_internal(request: InternalCardTransactionRequest) -> Dict[str, Any]:
    payload = {
        'amount': request.amount,
        'currency': request.currency,
        'merchant_transaction_id': request.merchant_transaction_id,
        'bank_name': request.bank_name,
        'rate': request.rate,
        'currency_rate': request.currency_rate,
        'client_id': request.client_id
    }

    payload = {k: v for k, v in payload.items() if v is not None}  # Убираем None значения
    return payload

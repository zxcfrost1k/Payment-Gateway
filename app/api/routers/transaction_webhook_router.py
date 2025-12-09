# РОУТЕР ВЕБХУКА
from fastapi import APIRouter, Request, HTTPException, Depends, status
import json
import logging
from typing import Dict, Any

from app.api.security.auth import security
from app.core.config import settings
from app.models.other_models import WebhookRequest
from app.api.services.signature_service import verify_signature


logger = logging.getLogger(__name__)
router = APIRouter()


# Проверка подписи вебхука
async def verify_webhook_signature(request: Request):
    if not settings.webhook_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Webhook обработка отключена"
        )

    if not settings.webhook_secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не настроен секретный ключ вебхука"
        )

    # Получение тела запроса
    try:
        body_bytes = await request.body()
        request_body = json.loads(body_bytes.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат JSON"
        )

    # Получение подписи из заголовка
    signature_header = request.headers.get("X-Signature")
    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Отсутствует подпись"
        )

    # Получение полного URL запроса
    full_url = str(request.url)

    # Проверка подписи
    if not verify_signature(full_url, request_body, signature_header, settings.webhook_secret_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверная подпись"
        )

    return request_body


# Обработка входящих вебхуков об изменении статуса платежа
@router.post("/transaction", status_code=status.HTTP_200_OK)
async def handle_transaction_webhook(
        webhook_data: Dict[str, Any] = Depends(verify_webhook_signature),
        token: str = Depends(security)
):
    try:
        # Валидация данных через Pydantic модель
        webhook = WebhookRequest(**webhook_data)

        # Лог полученнего вебхука
        logger.info(f"Получен вебхук для транзакции {webhook.merchant_transaction_id}")
        logger.info(f"Статус: {webhook.status}, Сумма оплаты: {webhook.paid_amount}")

        # Обработка всех статусов
        if webhook.status == "paid":
            logger.info(f"Транзакция {webhook.merchant_transaction_id} оплачена полностью")
            # Здесь можно обновить статус в БД, отправить уведомление и т.д. (при необходимости)

        elif webhook.status == "underpaid":
            logger.warning(f"Транзакция {webhook.merchant_transaction_id} недоплачена")
            logger.warning(f"Ожидалось: {webhook.amount}, получено: {webhook.paid_amount}")

        elif webhook.status == "overpaid":
            logger.warning(f"Транзакция {webhook.merchant_transaction_id} переплачена")
            logger.warning(f"Ожидалось: {webhook.amount}, получено: {webhook.paid_amount}")

        elif webhook.status == "cancel":
            logger.info(f"Транзакция {webhook.merchant_transaction_id} отменена")

        elif webhook.status == "expired":
            logger.info(f"Транзакция {webhook.merchant_transaction_id} просрочена")

        elif webhook.status == "error":
            logger.error(f"Ошибка в транзакции {webhook.merchant_transaction_id}")

        else:
            logger.warning(f"Неизвестный статус {webhook.status} для транзакции {webhook.merchant_transaction_id}")

        # Обновляем информацию о транзакции в вашей системе
        await update_transaction_status(
            merchant_transaction_id=webhook.merchant_transaction_id,
            status=webhook.status,
            paid_amount=webhook.paid_amount,
            currency_rate=webhook.currency_rate,
            amount_in_usd=webhook.amount_in_usd
        )

        return {"status": "ok", "message": "Webhook processed successfully"}

    except Exception as e:
        logger.error(f"Ошибка при обработке вебхука: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке вебхука: {str(e)}"
        )


# Обновление статуса транзакции (???)
async def update_transaction_status(
        merchant_transaction_id: str,
        status: str,
        paid_amount: str,
        currency_rate: str,
        amount_in_usd: str
):
    logger.info(f"Обновление транзакции {merchant_transaction_id}: статус={status}, оплачено={paid_amount}")

    # Временная заглушка
    pass

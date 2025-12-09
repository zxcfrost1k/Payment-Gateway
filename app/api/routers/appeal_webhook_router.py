# РОУТЕР ВЕБХУКА АПЕЛЛЯЦИЙ
from fastapi import APIRouter, Request, HTTPException, Depends, status
import json
import logging
from typing import Dict, Any, Optional

from app.api.security.auth import security
from app.api.services.provider_service import _create_error_response
from app.core.config import settings
from app.models.appeal_model import AppealWebhookRequest
from app.api.services.signature_service import verify_signature


logger = logging.getLogger(__name__)
router = APIRouter()


# Проверка подписи вебхука апелляции
async def verify_appeal_webhook_signature(request: Request):
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


# Обработка входящих вебхуков об изменении статуса апелляции
@router.post("/appeal", status_code=status.HTTP_200_OK)
async def handle_appeal_webhook(
        webhook_data: Dict[str, Any] = Depends(verify_appeal_webhook_signature),
        token: str = Depends(security)  # Проверка токена авторизации
, http_status=None):
    try:
        try:
            # Валидация данных через Pydantic модель
            webhook = AppealWebhookRequest(**webhook_data)
        except Exception as e:
            logger.error(f"Ошибка валидации параметров запроса: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=_create_error_response(
                    code="422",
                    message=str(e)
                )
            )

        # Лог полученного вебхука
        logger.info(f"Получен вебхук апелляции ID: {webhook.id}")
        logger.info(f"Статус: {webhook.status}, Транзакция: {webhook.transaction_id}")

        if webhook.status == "canceled":
            logger.info(f"Апелляция {webhook.id} отклонена")
            logger.info(f"Причина: {webhook.reason}")

            # Обработка отклоненной апелляции
            await handle_canceled_appeal(
                appeal_id=webhook.id,
                transaction_id=webhook.transaction_id,
                merchant_transaction_id=webhook.merchant_transaction_id,
                reason=webhook.reason
            )

        elif webhook.status == "success":
            logger.info(f"Апелляция {webhook.id} успешно одобрена")

            # Обработка успешной апелляции
            await handle_successful_appeal(
                appeal_id=webhook.id,
                transaction_id=webhook.transaction_id,
                merchant_transaction_id=webhook.merchant_transaction_id
            )

        else:
            logger.warning(f"Неизвестный статус {webhook.status} для апелляции {webhook.id}")

        # Обновляем статус апелляции в вашей системе
        await update_appeal_status(
            appeal_id=webhook.id,
            status=webhook.status,
            reason=webhook.reason
        )

        return {"status": "ok", "message": "Appeal webhook processed successfully"}

    except Exception as e:
        logger.error(f"Ошибка при обработке вебхука апелляции: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке вебхука апелляции: {str(e)}"
        )


# Обработка отклоненной апелляции
async def handle_canceled_appeal(
        appeal_id: int,
        transaction_id: int,
        merchant_transaction_id: str,
        reason: Optional[str]
):
    logger.info(f"Обработка отклоненной апелляции {appeal_id}")
    logger.info(f"Транзакция: {transaction_id} ({merchant_transaction_id})")
    logger.info(f"Причина отказа: {reason}")

    # Заглушка
    pass


# Обработка успешной апелляции
async def handle_successful_appeal(
        appeal_id: int,
        transaction_id: int,
        merchant_transaction_id: str
):
    logger.info(f"Обработка успешной апелляции {appeal_id}")
    logger.info(f"Транзакция: {transaction_id} ({merchant_transaction_id})")

    # Заглушка
    pass


# Обновление статуса апелляции
async def update_appeal_status(
        appeal_id: int,
        status: str,
        reason: Optional[str] = None
):
    logger.info(f"Обновление статуса апелляции {appeal_id}: статус={status}, причина={reason}")

    # Заглушка
    pass

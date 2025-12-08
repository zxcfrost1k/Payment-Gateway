# ПОДПИСЬ (вебхук)
import hashlib
import hmac
import json
from urllib.parse import urlparse
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


# Вычисление подписи для вебхука
def calculate_signature(url: str, request_body: Dict[str, Any], secret: str) -> str:
    try:
        # Преобразуем тело запроса в JSON-строку
        request_json_string = json.dumps(request_body)

        # Парсим URL
        parsed_url = urlparse(url)

        # Формируем строку для подписи: тело + путь + параметры запроса
        signature_string = request_json_string + parsed_url.path + parsed_url.query

        # Вычисляем HMAC SHA-256
        signature = hmac.new(
            secret.encode("utf-8"),
            signature_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest().lower()

        return signature

    except Exception as e:
        logger.error(f"Ошибка при вычислении подписи: {str(e)}")
        raise


# Проверка подписи вебхука
def verify_signature(url: str, request_body: Dict[str, Any], signature_header: str, secret: str) -> bool:
    if not signature_header:
        logger.warning("Отсутствует заголовок X-Signature")
        return False

    try:
        expected_signature = calculate_signature(url, request_body, secret)
        # Сравниваем в постоянном времени для защиты от timing attack
        return hmac.compare_digest(expected_signature, signature_header.lower())

    except Exception as e:
        logger.error(f"Ошибка при проверке подписи: {str(e)}")
        return False

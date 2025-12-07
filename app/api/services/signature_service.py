import hashlib
import hmac
import json
from urllib.parse import urlparse
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def calculate_signature(url: str, request_body: Dict[str, Any], secret: str) -> str:
    """
    Вычисление подписи для вебхука

    Args:
        url: Полный URL вебхука
        request_body: Тело запроса в виде словаря
        secret: Секретный ключ для подписи

    Returns:
        HEX-строка подписи в нижнем регистре
    """
    try:
        # Преобразуем тело запроса в JSON-строку
        request_json_string = json.dumps(request_body, separators=(",", ":"))

        # Парсим URL
        parsed_url = urlparse(url)

        # Формируем строку для подписи: тело + путь + параметры запроса
        signature_string = request_json_string + parsed_url.path
        if parsed_url.query:
            signature_string += "?" + parsed_url.query

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


def verify_signature(url: str, request_body: Dict[str, Any], signature_header: str, secret: str) -> bool:
    """
    Проверка подписи вебхука

    Args:
        url: URL запроса
        request_body: Тело запроса
        signature_header: Значение заголовка X-Signature
        secret: Секретный ключ

    Returns:
        True если подпись верна, иначе False
    """
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

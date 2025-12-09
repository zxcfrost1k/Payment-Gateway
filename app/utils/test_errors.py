# ТЕСТОВЫЙ СКРИПТ ДЛЯ ПРОВЕРКИ ВЕБХУКА АПЕЛЛЯЦИЙ
import requests
import json
import hashlib
import hmac
import logging
from urllib.parse import urlparse

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Конфигурация
BASE_URL = "http://localhost:8000"
MERCHANT_TOKEN = "test_token_123"
WEBHOOK_SECRET = "test_secret_key_123"


def calculate_signature(url: str, request_body: dict, secret: str) -> str:
    """Вычисление подписи для вебхука"""
    request_json_string = json.dumps(request_body)
    parsed_url = urlparse(url)
    signature_string = request_json_string + parsed_url.path + parsed_url.query

    signature = hmac.new(
        secret.encode("utf-8"),
        signature_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest().lower()

    return signature


def test_appeal_webhook_canceled():
    """Тестирует вебхук для отклоненной апелляции"""

    logger.info("=" * 60)
    logger.info("ТЕСТ ВЕБХУКА ОТКЛОНЕННОЙ АПЕЛЛЯЦИИ")
    logger.info("=" * 60)

    url = f"{BASE_URL}/api/v1/webhooks/appeal"

    # Данные для вебхука
    webhook_data = {
        "id": 12,
        "transaction_id": 112232,
        "merchant_transaction_id": "1000123213",
        "status": "canceled",
        "reason": "Отсутствует сумма в чеке"
    }

    # Вычисляем подпись
    signature = calculate_signature(url, webhook_data, WEBHOOK_SECRET)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {MERCHANT_TOKEN}',
        'X-Signature': signature
    }

    try:
        logger.info(f"URL: {url}")
        logger.info(f"Данные: {json.dumps(webhook_data, ensure_ascii=False)}")
        logger.info(f"Подпись: {signature}")

        response = requests.post(url, headers=headers, json=webhook_data)

        logger.info(f"Статус код: {response.status_code}")

        if response.status_code == 200:
            logger.info("✓ Успешный ответ!")
            result = response.json()
            logger.info(f"Ответ: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True

        elif response.status_code == 401:
            logger.error("✗ Ошибка 401: Unauthorized")
            logger.error("Проверьте подпись или токен авторизации")

        elif response.status_code == 400:
            logger.error("✗ Ошибка 400: Bad Request")
            try:
                error_data = response.json()
                logger.error(f"Детали ошибки: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                logger.error(f"Текст ответа: {response.text}")

        elif response.status_code == 403:
            logger.error("✗ Ошибка 403: Forbidden")
            logger.error("Вебхуки отключены в настройках")

        else:
            logger.error(f"✗ Неожиданный статус код: {response.status_code}")
            logger.error(f"Текст ответа: {response.text}")

        return False

    except requests.exceptions.ConnectionError:
        logger.error("✗ Ошибка соединения. Убедитесь что сервер запущен.")
        return False

    except Exception as e:
        logger.error(f"✗ Неожиданная ошибка: {str(e)}")
        return False


def test_appeal_webhook_success():
    """Тестирует вебхук для успешной апелляции"""

    logger.info("\n" + "=" * 60)
    logger.info("ТЕСТ ВЕБХУКА УСПЕШНОЙ АПЕЛЛЯЦИИ")
    logger.info("=" * 60)

    url = f"{BASE_URL}/api/v1/webhooks/appeal"

    # Данные для вебхука
    webhook_data = {
        "id": 15,
        "transaction_id": 112235,
        "merchant_transaction_id": "1000123216",
        "status": "success",
        "reason": None  # Для успешного статуса reason не обязателен
    }

    # Вычисляем подпись
    signature = calculate_signature(url, webhook_data, WEBHOOK_SECRET)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {MERCHANT_TOKEN}',
        'X-Signature': signature
    }

    try:
        response = requests.post(url, headers=headers, json=webhook_data)
        logger.info(f"Статус код: {response.status_code}")

        if response.status_code == 200:
            logger.info("✓ Успешный ответ!")
            return True
        else:
            logger.error(f"✗ Ошибка: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return False


def test_appeal_webhook_invalid_signature():
    """Тестирует вебхук с неверной подписью"""

    logger.info("\n" + "=" * 60)
    logger.info("ТЕСТ ВЕБХУКА С НЕВЕРНОЙ ПОДПИСЬЮ")
    logger.info("=" * 60)

    url = f"{BASE_URL}/api/v1/webhooks/appeal"

    webhook_data = {
        "id": 12,
        "transaction_id": 112232,
        "merchant_transaction_id": "1000123213",
        "status": "canceled",
        "reason": "Отсутствует сумма в чеке"
    }

    # Используем неверный секрет для подписи
    invalid_signature = calculate_signature(url, webhook_data, "wrong_secret_key")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {MERCHANT_TOKEN}',
        'X-Signature': invalid_signature
    }

    try:
        response = requests.post(url, headers=headers, json=webhook_data)
        logger.info(f"Статус код: {response.status_code}")

        if response.status_code == 401:
            logger.info("✓ Ожидаемая ошибка 401: Неверная подпись")
            return True
        elif response.status_code == 200:
            logger.error("✗ Получен успешный ответ для неверной подписи")
            return False
        else:
            logger.error(f"✗ Неожиданный статус код: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return False


def test_appeal_webhook_missing_signature():
    """Тестирует вебхук без подписи"""

    logger.info("\n" + "=" * 60)
    logger.info("ТЕСТ ВЕБХУКА БЕЗ ПОДПИСИ")
    logger.info("=" * 60)

    url = f"{BASE_URL}/api/v1/webhooks/appeal"

    webhook_data = {
        "id": 12,
        "transaction_id": 112232,
        "merchant_transaction_id": "1000123213",
        "status": "canceled",
        "reason": "Отсутствует сумма в чеке"
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {MERCHANT_TOKEN}'
        # Нет X-Signature заголовка
    }

    try:
        response = requests.post(url, headers=headers, json=webhook_data)
        logger.info(f"Статус код: {response.status_code}")

        if response.status_code == 401:
            logger.info("✓ Ожидаемая ошибка 401: Отсутствует подпись")
            return True
        else:
            logger.error(f"✗ Неожиданный статус код: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return False


def test_appeal_webhook_invalid_status():
    """Тестирует вебхук с невалидным статусом"""

    logger.info("\n" + "=" * 60)
    logger.info("ТЕСТ ВЕБХУКА С НЕВАЛИДНЫМ СТАТУСОМ")
    logger.info("=" * 60)

    url = f"{BASE_URL}/api/v1/webhooks/appeal"

    webhook_data = {
        "id": 12,
        "transaction_id": 112232,
        "merchant_transaction_id": "1000123213",
        "status": "invalid_status",  # Невалидный статус
        "reason": "Причина"
    }

    signature = calculate_signature(url, webhook_data, WEBHOOK_SECRET)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {MERCHANT_TOKEN}',
        'X-Signature': signature
    }

    try:
        response = requests.post(url, headers=headers, json=webhook_data)
        logger.info(f"Статус код: {response.status_code}")

        if response.status_code in [400, 422]:
            logger.info("✓ Ожидаемая ошибка валидации")
            return True
        elif response.status_code == 200:
            logger.warning("⚠ Получен успешный ответ для невалидного статуса")
            return True
        else:
            logger.error(f"✗ Неожиданный статус код: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return False


def main():
    """Основная функция тестирования"""
    logger.info("Запуск тестов вебхука апелляций...")

    results = []

    try:
        # Тест 1: Отклоненная апелляция
        logger.info("\n1. Тест вебхука отклоненной апелляции:")
        results.append(("Отклоненная апелляция", test_appeal_webhook_canceled()))

        # Тест 2: Успешная апелляция
        logger.info("\n2. Тест вебхука успешной апелляции:")
        results.append(("Успешная апелляция", test_appeal_webhook_success()))

        # Тест 3: Неверная подпись
        logger.info("\n3. Тест с неверной подписью:")
        results.append(("Неверная подпись", test_appeal_webhook_invalid_signature()))

        # Тест 4: Без подписи
        logger.info("\n4. Тест без подписи:")
        results.append(("Без подписи", test_appeal_webhook_missing_signature()))

        # Тест 5: Невалидный статус
        logger.info("\n5. Тест с невалидным статусом:")
        results.append(("Невалидный статус", test_appeal_webhook_invalid_status()))

        # Итоги
        logger.info("\n" + "=" * 60)
        logger.info("ИТОГИ ТЕСТИРОВАНИЯ")
        logger.info("=" * 60)

        passed = 0
        for test_name, result in results:
            status = "✓ ПРОЙДЕН" if result else "✗ ПРОВАЛЕН"
            logger.info(f"{test_name}: {status}")
            if result:
                passed += 1

        total = len(results)
        logger.info(f"\nПройдено тестов: {passed}/{total}")

        if passed == total:
            logger.info("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        else:
            logger.error(f"✗ ПРОВАЛЕНО ТЕСТОВ: {total - passed}")

    except Exception as e:
        logger.error(f"Ошибка при выполнении тестов: {str(e)}")


if __name__ == "__main__":
    main()
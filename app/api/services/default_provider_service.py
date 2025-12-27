# СЕРВИС ДЛЯ РАБОТЫ С ПРОВАЙДЕРОМ
import httpx
import logging
import json
from typing import Dict, Any, Optional, List


from app.models.paygatecore.other_models import BalanceResponse, LimitsResponse, LimitItem
from app.core.config import settings


logger = logging.getLogger(__name__)


# Создание ответа об ошибке
def _create_error_response(code: str,
                           message: str,
                           errors: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
    error_response: Dict[str, Any] = {
        "code": code,
        "message": message
    }

    # Поле errors только при множественных ошибках
    if errors and len(errors) > 1:
        error_response["errors"] = errors

    return error_response


# Обработка HTTP ошибок от провайдера (4xx, 5xx)
def _transform_provider_error_status(error: httpx.HTTPStatusError) -> Exception:
    try:
        error_data = error.response.json()
        status_code = error.response.status_code

        error_message = error_data.get("message", error.response.text)
        error_response = _create_error_response(
            code=str(status_code),
            message=error_message
        )

        error_message = json.dumps(error_response, ensure_ascii=False)
        return Exception(error_message)

    # Невалидный JSON
    except json.JSONDecodeError:
        status_code = error.response.status_code
        error_response = _create_error_response(
            code=str(status_code),
            message=error.response.text
        )
        error_message = json.dumps(error_response, ensure_ascii=False)
        return Exception(error_message)

    # Нет нужных атрибутов или ключей
    except (AttributeError, KeyError):
        status_code = getattr(error.response, "status_code", 500)
        text = getattr(error.response, "text", str(error))

        error_response = _create_error_response(
            code=str(status_code),
            message=text
        )
        error_message = json.dumps(error_response, ensure_ascii=False)
        return Exception(error_message)

    # Непредвиденные ошибки
    except Exception as e:
        # Лог с полным traceback
        logger.exception(f"Непредвиденная ошибка в _transform_provider_error_status")

        error_response = _create_error_response(
            code="500",
            message=f"Ошибка обработки ответа провайдера: {str(e)}"
        )
        error_message = json.dumps(error_response, ensure_ascii=False)
        return Exception(error_message)


# Обработка ошибок запроса к провайдеру (сети, таймауты, соединение)
def _transform_provider_error_request(error: httpx.RequestError) -> Exception:
    # Определение типа ошибки
    if isinstance(error, httpx.ConnectTimeout):
        error_type = "Таймаут подключения"
    elif isinstance(error, httpx.ReadTimeout):
        error_type = "Таймаут чтения ответа"
    elif isinstance(error, httpx.WriteTimeout):
        error_type = "Таймаут отправки запроса"
    elif isinstance(error, httpx.ConnectError):
        error_type = "Ошибка подключения к серверу"
    elif isinstance(error, httpx.PoolTimeout):
        error_type = "Таймаут ожидания свободного соединения"
    elif isinstance(error, httpx.ReadError):
        error_type = "Ошибка чтения данных"
    elif isinstance(error, httpx.WriteError):
        error_type = "Ошибка записи данных"
    else:
        error_type = "Сетевая ошибка"

    # Формирование сообщения об ошибке
    error_response = _create_error_response(
        code="503",
        message=f"{error_type} при обращении к провайдеру"
    )

    error_message = json.dumps(error_response, ensure_ascii=False)
    return Exception(error_message)


# Универсальная функция обработки ошибок провайдера (для любых исключений)
def _transform_provider_error(error: Exception) -> Exception:
    if isinstance(error, httpx.HTTPStatusError):
        return _transform_provider_error_status(error)
    elif isinstance(error, httpx.RequestError):
        return _transform_provider_error_request(error)
    # Для других ошибок
    else:
        error_response = _create_error_response(
            code="500",
            message=str(error) if str(error) else "Неизвестная ошибка провайдера"
        )

        error_message = json.dumps(error_response, ensure_ascii=False)
        return Exception(error_message)


# Преобразование ответа провайдера в нашу модель лимитов
def _transform_limits_response(provider_data: dict) -> LimitsResponse:
    try:
        logger.info(f"Преобразование ответа провайдера: {provider_data}")

        # Создаем словарь для лимитов
        limits_dict = {}

        # 1. Обрабатываем CARD
        if "card" in provider_data and isinstance(provider_data["card"], dict):
            card_data = provider_data["card"]
            if "min_amount" in card_data and "max_amount" in card_data:
                limits_dict["card"] = LimitItem(
                    min_amount=str(card_data["min_amount"]),
                    max_amount=str(card_data["max_amount"])
                )

        # 2. Обрабатываем SBP
        if "sbp" in provider_data and isinstance(provider_data["sbp"], dict):
            sbp_data = provider_data["sbp"]
            if "min_amount" in sbp_data and "max_amount" in sbp_data:
                limits_dict["sbp"] = LimitItem(
                    min_amount=str(sbp_data["min_amount"]),
                    max_amount=str(sbp_data["max_amount"])
                )

        # 3. Обрабатываем QR
        if "qr" in provider_data and isinstance(provider_data["qr"], dict):
            qr_data = provider_data["qr"]
            if "min_amount" in qr_data and "max_amount" in qr_data:
                limits_dict["qr"] = LimitItem(
                    min_amount=str(qr_data["min_amount"]),
                    max_amount=str(qr_data["max_amount"])
                )

        # 4. Обрабатываем SIM
        if "sim" in provider_data and isinstance(provider_data["sim"], dict):
            sim_data = provider_data["sim"]
            if "min_amount" in sim_data and "max_amount" in sim_data:
                limits_dict["sim"] = LimitItem(
                    min_amount=str(sim_data["min_amount"]),
                    max_amount=str(sim_data["max_amount"])
                )

        # Создаем финальный объект
        result = LimitsResponse(**limits_dict)
        logger.info(f"Преобразование завершено успешно")
        return result

    except KeyError as e:
        logger.error(f"Ключевая ошибка при преобразовании лимитов: {str(e)}")
        logger.error(f"Ответ провайдера: {provider_data}")
        raise _transform_provider_error(e)

    except Exception as e:
        logger.error(f"Неожиданная ошибка при преобразовании лимитов: {str(e)}")
        logger.error(f"Тип ошибки: {type(e).__name__}")
        import traceback
        logger.error(f"Трассировка: {traceback.format_exc()}")
        raise _transform_provider_error(e)


# Получаем конфигурацию провайдера
def _get_provider_config(provider_name: str):
    if provider_name not in settings.providers:
        raise KeyError(f"Provider {provider_name} not found")
    return settings.providers[provider_name]


class ProviderService:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=5.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )

    # Получение баланса
    async def get_balance(self) -> BalanceResponse:
        try:
            headers = {
                "Authorization": f"Bearer {settings.provider_api_key}",
                "Content-Type": "application/json"
            }

            logger.info("Отправка запроса провайдеру на баланс")

            # В режиме отладки - заглушка
            if settings.debug:
                return BalanceResponse(
                    balance="100.00",
                    currency_rate="90.32"
                )

            # Реальный запрос к провайдеру
            response = await self.client.get(
                f"{settings.provider_base_url}/api/v1/balance",
                headers=headers
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f"Получен ответ от провайдера на баланс: {provider_data}")

            return BalanceResponse(
                balance=provider_data["balance"],
                currency_rate=provider_data["currency_rate"]
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка при запросе баланса: {e.response.status_code}")
            raise _transform_provider_error(e)
        except Exception as e:
            logger.error(f"Ошибка при получении баланса: {str(e)}")
            raise _transform_provider_error(e)

    # Получение лимитов
    async def get_limits(self,
                         currency_code: str
                         ) -> LimitsResponse:
        try:
            headers = {
                "Authorization": f"Bearer {settings.provider_api_key}",
                "Content-Type": "application/json"
            }

            logger.info(f"Запрос лимитов для валюты: {currency_code}")

            # В режиме отладки возвращаем заглушку
            if settings.debug:
                logger.info("Режим DEBUG - возвращаем тестовые данные лимитов")
                return _transform_limits_response({
                    "card": {
                        "min_amount": "100",
                        "max_amount": "200000"
                    },
                    "sbp": {
                        "min_amount": "100",
                        "max_amount": "200000"
                    }
                })

            # Реальный запрос к провайдеру
            response = await self.client.get(
                f"{settings.provider_base_url}/api/v1/limits/{currency_code}",
                headers=headers
            )

            response.raise_for_status()
            provider_data = response.json()
            logger.info(f"Получен ответ лимитов от провайдера: {provider_data}")

            return _transform_limits_response(provider_data)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка при запросе лимитов: {e.response.status_code}")
            raise _transform_provider_error(e)
        except Exception as e:
            logger.error(f"Ошибка при получении лимитов: {str(e)}")
            raise _transform_provider_error(e)


    # Выход из приложения
    async def close(self):
        await self.client.aclose()


# Создание объекта класса ProviderService
provider_service = ProviderService()

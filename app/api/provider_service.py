# СЕРВИС ДЛЯ РАБОТЫ С ПРОВАЙДЕРОМ
import httpx
import logging

from app.api.tool_for_provider_service.transform_from_provider_format import transform_from_provider_format_card, \
    transform_from_provider_format_card_internal, transform_from_provider_format_sbp, \
    transform_from_provider_format_sbp_internal, transform_from_provider_format_qr, transform_from_provider_format_sim
from app.api.tool_for_provider_service.transform_to_provider_format import transform_to_provider_format_card, \
    transform_to_provider_format_card_internal
from app.core.config import settings
from app.models.card_models.card_transaction_internal_bank_model import InternalCardTransactionRequest, \
    InternalCardTransactionResponse
from app.models.card_models.card_transaction_model import CardTransactionRequest, CardTransactionResponse
from app.models.qr_and_sim_models.qr_transaction_model import QrTransactionResponse
from app.models.qr_and_sim_models.sim_transaction_model import SimTransactionResponse
from app.models.sbp_models.sbp_transaction_model import SbpTransactionResponse
from app.models.sbp_models.sbp_transaction_model_iternal import InternalSbpTransactionResponse

logger = logging.getLogger(__name__)

# Перехват ошибок провайдера
def _transform_provider_error(error: httpx.HTTPStatusError) -> Exception:
    # noinspection PyBroadException
    try:
        error_data = error.response.json()
        error_message = error_data.get('message', error.response.text)
        return Exception(f'Ошибка провайдера: {error_message}')
    except:
        return Exception(f'Ошибка провайдера: {error.response.text}')

# Обращение к серверу провайдера
class ProviderService:
    def __init__(self):
        self.client = httpx.AsyncClient(
            # Настройка таумаутов: общий - 30, на установку соединений - 5
            timeout=httpx.Timeout(30.0, connect=5.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20) # Ограничение пула соединений
        )

    async def create_card_transaction(self, request: CardTransactionRequest) -> CardTransactionResponse:
        try:
            # Преобразование запроса (нашего) в формат провайдера
            provider_payload = transform_to_provider_format_card(request)
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f'Отправка запроса провайдеру: {provider_payload}')
            response = await self.client.post(
                f'{settings.provider_base_url}/transactions/card',
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()  # Проверка HTTP статуса
            provider_data = response.json()  # Парс JSON ответа
            logger.info(f'Получен ответ от провайдера: {provider_data}')

            return transform_from_provider_format_card(provider_data)

        except httpx.HTTPStatusError as e:
            # Лог HTTP ошибок (4xx, 5xx)
            logger.error(f'Ошибка HTTP API провайдера {e.response.status_code}: {e.response.text}')
            raise _transform_provider_error(e)

        except httpx.RequestError as e:
            # Лог ошибок сети (таймауты, соединения и тп)
            logger.error(f'Сетевая ошибка API провайдера {str(e)}')
            raise Exception(f'Сетевая ошибка при обращении к провайдеру: {str(e)}')

        except Exception as e:
            # Лог всех остальных ошибок
            logger.error(f'Непредвиденная ошибка в службе провайдера: {str(e)}')
            raise

    async def create_card_transaction_internal(self,
                                               request: InternalCardTransactionRequest) -> InternalCardTransactionResponse:
        try:
            # Преобразование запроса (нашего) в формат провайдера
            provider_payload = transform_to_provider_format_card_internal(request)
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f'Отправка запроса провайдеру: {provider_payload}')
            response = await self.client.post(
                f'{settings.provider_base_url}/transactions/card',
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()  # Проверка HTTP статуса
            provider_data = response.json()  # Парс JSON ответа
            logger.info(f'Получен ответ от провайдера: {provider_data}')

            return transform_from_provider_format_card_internal(provider_data)

        except httpx.HTTPStatusError as e:
            # Лог HTTP ошибок (4xx, 5xx)
            logger.error(f'Ошибка HTTP API провайдера {e.response.status_code}: {e.response.text}')
            raise _transform_provider_error(e)

        except httpx.RequestError as e:
            # Лог ошибок сети (таймауты, соединения и тп)
            logger.error(f'Сетевая ошибка API провайдера {str(e)}')
            raise Exception(f'Сетевая ошибка при обращении к провайдеру: {str(e)}')

        except Exception as e:
            # Лог всех остальных ошибок
            logger.error(f'Непредвиденная ошибка в службе провайдера: {str(e)}')
            raise

    async def create_card_transaction_transgran(self,
                                               request: CardTransactionRequest) -> InternalCardTransactionResponse:
        try:
            # Преобразование запроса (нашего) в формат провайдера
            provider_payload = transform_to_provider_format_card(request)
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f'Отправка запроса провайдеру: {provider_payload}')
            response = await self.client.post(
                f'{settings.provider_base_url}/transactions/card',
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()  # Проверка HTTP статуса
            provider_data = response.json()  # Парс JSON ответа
            logger.info(f'Получен ответ от провайдера: {provider_data}')

            return transform_from_provider_format_card_internal(provider_data)

        except httpx.HTTPStatusError as e:
            # Лог HTTP ошибок (4xx, 5xx)
            logger.error(f'Ошибка HTTP API провайдера {e.response.status_code}: {e.response.text}')
            raise _transform_provider_error(e)

        except httpx.RequestError as e:
            # Лог ошибок сети (таймауты, соединения и тп)
            logger.error(f'Сетевая ошибка API провайдера {str(e)}')
            raise Exception(f'Сетевая ошибка при обращении к провайдеру: {str(e)}')

        except Exception as e:
            # Лог всех остальных ошибок
            logger.error(f'Непредвиденная ошибка в службе провайдера: {str(e)}')
            raise

    async def create_spb_transaction(self,
                                     request: CardTransactionRequest) -> SbpTransactionResponse:
        try:
            # Преобразование запроса (нашего) в формат провайдера
            provider_payload = transform_to_provider_format_card(request)
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f'Отправка запроса провайдеру: {provider_payload}')
            response = await self.client.post(
                f'{settings.provider_base_url}/transactions/card',
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()  # Проверка HTTP статуса
            provider_data = response.json()  # Парс JSON ответа
            logger.info(f'Получен ответ от провайдера: {provider_data}')

            return transform_from_provider_format_sbp(provider_data)

        except httpx.HTTPStatusError as e:
            # Лог HTTP ошибок (4xx, 5xx)
            logger.error(f'Ошибка HTTP API провайдера {e.response.status_code}: {e.response.text}')
            raise _transform_provider_error(e)

        except httpx.RequestError as e:
            # Лог ошибок сети (таймауты, соединения и тп)
            logger.error(f'Сетевая ошибка API провайдера {str(e)}')
            raise Exception(f'Сетевая ошибка при обращении к провайдеру: {str(e)}')

        except Exception as e:
            # Лог всех остальных ошибок
            logger.error(f'Непредвиденная ошибка в службе провайдера: {str(e)}')
            raise


    async def create_spb_transaction_internal(self,
                                     request: InternalCardTransactionRequest) -> InternalSbpTransactionResponse:
        try:
            # Преобразование запроса (нашего) в формат провайдера
            provider_payload = transform_to_provider_format_card_internal(request)
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f'Отправка запроса провайдеру: {provider_payload}')
            response = await self.client.post(
                f'{settings.provider_base_url}/transactions/card',
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()  # Проверка HTTP статуса
            provider_data = response.json()  # Парс JSON ответа
            logger.info(f'Получен ответ от провайдера: {provider_data}')

            return transform_from_provider_format_sbp_internal(provider_data)

        except httpx.HTTPStatusError as e:
            # Лог HTTP ошибок (4xx, 5xx)
            logger.error(f'Ошибка HTTP API провайдера {e.response.status_code}: {e.response.text}')
            raise _transform_provider_error(e)

        except httpx.RequestError as e:
            # Лог ошибок сети (таймауты, соединения и тп)
            logger.error(f'Сетевая ошибка API провайдера {str(e)}')
            raise Exception(f'Сетевая ошибка при обращении к провайдеру: {str(e)}')

        except Exception as e:
            # Лог всех остальных ошибок
            logger.error(f'Непредвиденная ошибка в службе провайдера: {str(e)}')
            raise

    async def create_spb_transaction_transgran(self,
                                     request: CardTransactionRequest) -> InternalSbpTransactionResponse:
        try:
            # Преобразование запроса (нашего) в формат провайдера
            provider_payload = transform_to_provider_format_card(request)
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f'Отправка запроса провайдеру: {provider_payload}')
            response = await self.client.post(
                f'{settings.provider_base_url}/transactions/card',
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()  # Проверка HTTP статуса
            provider_data = response.json()  # Парс JSON ответа
            logger.info(f'Получен ответ от провайдера: {provider_data}')

            return transform_from_provider_format_sbp_internal(provider_data)

        except httpx.HTTPStatusError as e:
            # Лог HTTP ошибок (4xx, 5xx)
            logger.error(f'Ошибка HTTP API провайдера {e.response.status_code}: {e.response.text}')
            raise _transform_provider_error(e)

        except httpx.RequestError as e:
            # Лог ошибок сети (таймауты, соединения и тп)
            logger.error(f'Сетевая ошибка API провайдера {str(e)}')
            raise Exception(f'Сетевая ошибка при обращении к провайдеру: {str(e)}')

        except Exception as e:
            # Лог всех остальных ошибок
            logger.error(f'Непредвиденная ошибка в службе провайдера: {str(e)}')
            raise


    async def create_qr_transaction(self,
                                     request: CardTransactionRequest) -> QrTransactionResponse:
        try:
            # Преобразование запроса (нашего) в формат провайдера
            provider_payload = transform_to_provider_format_card(request)
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f'Отправка запроса провайдеру: {provider_payload}')
            response = await self.client.post(
                f'{settings.provider_base_url}/transactions/card',
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()  # Проверка HTTP статуса
            provider_data = response.json()  # Парс JSON ответа
            logger.info(f'Получен ответ от провайдера: {provider_data}')

            return transform_from_provider_format_qr(provider_data)

        except httpx.HTTPStatusError as e:
            # Лог HTTP ошибок (4xx, 5xx)
            logger.error(f'Ошибка HTTP API провайдера {e.response.status_code}: {e.response.text}')
            raise _transform_provider_error(e)

        except httpx.RequestError as e:
            # Лог ошибок сети (таймауты, соединения и тп)
            logger.error(f'Сетевая ошибка API провайдера {str(e)}')
            raise Exception(f'Сетевая ошибка при обращении к провайдеру: {str(e)}')

        except Exception as e:
            # Лог всех остальных ошибок
            logger.error(f'Непредвиденная ошибка в службе провайдера: {str(e)}')
            raise

    async def create_sim_transaction(self,
                                     request: CardTransactionRequest) -> SimTransactionResponse:
        try:
            # Преобразование запроса (нашего) в формат провайдера
            provider_payload = transform_to_provider_format_card(request)
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f'Отправка запроса провайдеру: {provider_payload}')
            response = await self.client.post(
                f'{settings.provider_base_url}/transactions/card',
                headers=headers,
                json=provider_payload
            )

            response.raise_for_status()  # Проверка HTTP статуса
            provider_data = response.json()  # Парс JSON ответа
            logger.info(f'Получен ответ от провайдера: {provider_data}')

            return transform_from_provider_format_sim(provider_data)

        except httpx.HTTPStatusError as e:
            # Лог HTTP ошибок (4xx, 5xx)
            logger.error(f'Ошибка HTTP API провайдера {e.response.status_code}: {e.response.text}')
            raise _transform_provider_error(e)

        except httpx.RequestError as e:
            # Лог ошибок сети (таймауты, соединения и тп)
            logger.error(f'Сетевая ошибка API провайдера {str(e)}')
            raise Exception(f'Сетевая ошибка при обращении к провайдеру: {str(e)}')

        except Exception as e:
            # Лог всех остальных ошибок
            logger.error(f'Непредвиденная ошибка в службе провайдера: {str(e)}')
            raise

    async def cancel_transaction(self,transaction_id: str) -> bool | None:
        try:
            headers = {
                'Authorization': f'Bearer {settings.provider_api_key}',
                'Content-Type': 'application/json'
            }
            logger.info(f'Отправка запроса на отмену транзакции {transaction_id}')
            response = await self.client.post(
                f'{settings.provider_base_url}/transactions/{transaction_id}/cancel',
                headers=headers
            )

            if response.status_code == 204:
                logger.info(f'Транзакция {transaction_id} успешно отменена')
                return True
            elif response.status_code == 400:
                # Пытаемся распарсить ошибку от провайдера
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', 'Transaction should be in progress.')
                    logger.warning(f'Не удалось отменить транзакцию {transaction_id}: {error_message}')
                    raise Exception(f'Ошибка отмены транзакции: {error_message}')
                except:
                    logger.warning(f'Не удалось отменить транзакцию {transaction_id}:'
                                   f' Transaction should be in progress.')
                    raise Exception('Ошибка отмены транзакции: Transaction should be in progress.')
            else:
                response.raise_for_status()

        except httpx.HTTPStatusError as e:
            logger.error(f'Ошибка HTTP API провайдера при отмене транзакции'
                         f' {e.response.status_code}: {e.response.text}')
            raise _transform_provider_error(e)

        except httpx.RequestError as e:
            logger.error(f'Сетевая ошибка API провайдера при отмене транзакции: {str(e)}')
            raise Exception(f'Сетевая ошибка при обращении к провайдеру: {str(e)}')

        except Exception as e:
            logger.error(f'Непредвиденная ошибка при отмене транзакции: {str(e)}')
            raise


    async def close(self):
        await self.client.aclose()


provider_service = ProviderService()

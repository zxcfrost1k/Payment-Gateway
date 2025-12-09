# МОДЕЛИ ДАННЫХ (Апелляции)
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator
import re
from decimal import Decimal, InvalidOperation

from app.api.resources.valid_res import valid_res
from app.core.config import settings


# Модель для создания апелляций
class AppealCreateRequest(BaseModel):
    transaction_id: str = Field(..., min_length=1, description="Идентификатор транзакции")
    amount: str = Field(..., min_length=1, description="Сумма апелляции")

    @field_validator("amount")  # Валидация поля amount
    @classmethod
    def validate_amount(csl, value: str) -> str:
        try:
            amount = Decimal(value)
            if not re.match(r"^\d+$", value.strip()):
                raise ValueError("Поле amount должно быть целым числом")
            if amount <= 0:
                raise ValueError("Поле amount должно быть положительным числом")
            if value.startswith("0"):
                raise ValueError("Неправильный формат поля amount")
        except (ValueError, InvalidOperation):
            raise ValueError("Неправильный формат поля amount")
        return value


class AppealCreateResponse(BaseModel):
    id: int  # Идентификатор апелляции в системе провайдера


# Модель для реквизитов транзакции
class TransactionRequisite(BaseModel):
    bank: Optional[str] = Field(None, description="Банк")
    card: Optional[str] = Field(None, description="Номер карты")
    owner: Optional[str] = Field(None, description="Владелец счета")
    country_name: Optional[str] = Field(None, description="Название страны")


# Модель для просмотра апелляции
class AppealDetailResponse(BaseModel):
    id: int = Field(..., description="Идентификатор апелляции")
    created_at: datetime = Field(..., description="Дата создания апелляции")
    status: str = Field(..., description="Статус апелляции")
    amount: str = Field(..., description="Сумма апелляции")
    appeal_cancel_reason_name: Optional[str] = Field(None, description="Причина отмены апелляции")
    transaction_id: int = Field(..., description="Идентификатор транзакции")
    merchant_transaction_id: str = Field(..., description="Идентификатор транзакции в системе мерчанта")
    transaction_created_at: datetime = Field(..., description="Дата создания транзакции")
    transaction_amount: Optional[str] = Field(None, description="Сумма транзакции")
    transaction_paid_amount: str = Field(..., description="Фактическая оплаченная сумма")
    transaction_requisite: TransactionRequisite = Field(..., description="Реквизиты транзакции")
    transaction_currency_code: str = Field(..., description="Код валюты транзакции")


# Модель для элемента списка апелляций
class AppealListItem(BaseModel):
    id: int = Field(..., description="Идентификатор апелляции")
    created_at: datetime = Field(..., description="Дата создания апелляции")
    status: str = Field(..., description="Статус апелляции")
    amount: str = Field(..., description="Сумма апелляции")
    transaction_id: int = Field(..., description="Идентификатор транзакции")
    merchant_transaction_id: str = Field(..., description="Идентификатор транзакции в системе мерчанта")


# Модель для списка апелляций с пагинацией
class AppealListResponse(BaseModel):
    items: List[AppealListItem] = Field(..., description="Список апелляций")
    page_number: int = Field(..., description="Номер текущей страницы")
    page_size: int = Field(..., description="Количество элементов на странице")


# Модель для списка апелляций с фильтрами
class AppealListRequest(BaseModel):
    status: Optional[str] = Field(None, description="Статус апелляции")
    transaction_id: Optional[int] = Field(None, description="Идентификатор транзакции")
    merchant_transaction_id: Optional[str] = Field(None, description="Идентификатор транзакции в системе мерчанта")
    page_size: int = Field(default=10, ge=1, le=100, description="Количество элементов на странице")
    page_number: int = Field(default=1, ge=1, description="Номер страницы")

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            if value not in valid_res.valid_appeal_statuses:
                raise ValueError(f"Статус должен быть одним из: {', '.join(settings.valid_appeal_statuses)}")
        return value

# Модель для вебхука апелляции
class AppealWebhookRequest(BaseModel):
    id: int = Field(..., description="Идентификатор апелляции в системе провайдера")
    transaction_id: int = Field(..., description="Идентификатор заявки в системе провайдера")
    merchant_transaction_id: str = Field(..., description="Идентификатор заявки в системе мерчанта")
    status: str = Field(..., description="Статус апелляции")
    reason: Optional[str] = Field(None, description="Причина отмены апелляции")

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            if value not in valid_res.valid_appeal_statuses:
                raise ValueError(f"Неизвестный статус: {value}")
        return value

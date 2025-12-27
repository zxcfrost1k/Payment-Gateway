# ИНСТРУМЕНТЫ
from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import Dict, Any

from app.api.resources.garex_resources.bank_resources import bank_res
from app.core.config import settings
from app.models.paygatecore.card_models.pay_in_card_bank_model import (
    PayInCardBankRequest,
    PayInCardBankResponse,
    PayInCardBankResponse2
)
from app.models.paygatecore.card_models.pay_in_card_model import (
    PayInCardRequest,
    PayInCardResponse,
    PayInCardResponse2
)
from app.models.paygatecore.qr_and_sim_models.pay_in_sim_model import PayInSimResponse


def _get_country(bank_code: str) -> str:
    if bank_code in bank_res.BANKS_RUS:
        return "РФ"
    elif bank_code in bank_res.BANKS_AZ:
        return "Азербайджан"
    elif bank_code in bank_res.BANKS_ABH:
        return "Абхазия"
    else:
        return "Таджикистан"


def transform_to_provider_format(request: PayInCardRequest, method: str) -> Dict[str, Any]:
    payload = {
        "orderId": request.merchant_transaction_id,
        "merchantId": settings.merchant_token,
        "method": method,
        "amount": int(request.amount),
        "currency": request.currency,
        "user_id": "??",
        "callbackUri": settings.webhook_base_url
    }
    return payload


def transform_to_provider_format_with_bank(request: PayInCardBankRequest, method: str, bank_code: str) -> Dict[str, Any]:
    payload = {
        "orderId": request.merchant_transaction_id,
        "merchantId": settings.merchant_token,
        "method": method,
        "assetOrBank": bank_code,
        "amount": int(request.amount),
        "currency": request.currency,
        "user_id": "??",
        "callbackUri": settings.webhook_base_url
    }
    return payload


def transform_from_provider_format(provider_response: Dict[str, Any]) -> PayInCardResponse:
    try:
        return PayInCardResponse(
            id=provider_response["result"]["id"],
            merchant_transaction_id=provider_response["result"]["orderId"],
            expires_at=datetime.now() + timedelta(minutes = 10),
            amount=str(provider_response["result"]["amount"]),
            currency="RUB",
            currency_rate=str(provider_response["result"]["rate"]),
            amount_in_usd=str(provider_response["result"]["amount"] / provider_response["result"]["rate"]),
            rate="",
            commission=str(provider_response["result"]["fee"] * provider_response["result"]["amount"]),
            card_number=provider_response["result"]["address"],
            owner_name=provider_response["result"]["recipient"],
            bank_name=provider_response["result"]["bankName"],
            country_name=_get_country(provider_response["result"]["bank"]),
            payment_currency="RUB",
            payment_link=provider_response["url"]
        )
    except KeyError:
        raise HTTPException(
            status_code=520,
            detail="Неизвестная ошибка при получении ответа"
        )


def transform_from_provider_format_2(provider_response: Dict[str, Any]) -> PayInCardResponse2:
    try:
        return PayInCardResponse2(
            id=provider_response["result"]["id"],
            merchant_transaction_id=provider_response["result"]["orderId"],
            expires_at=datetime.now() + timedelta(minutes=10),
            amount=str(provider_response["result"]["amount"]),
            currency="RUB",
            currency_rate=str(provider_response["result"]["rate"]),
            amount_in_usd=str(provider_response["result"]["amount"] / provider_response["result"]["rate"]),
            rate="",
            commission=str(provider_response["result"]["fee"] * provider_response["result"]["amount"]),
            card_number=provider_response["result"]["address"],
            owner_name=provider_response["result"]["recipient"],
            bank_name=provider_response["result"]["bankName"],
            country_name=_get_country(provider_response["result"]["bank"]),
            payment_currency="RUB"
        )
    except KeyError:
        raise HTTPException(
            status_code=520,
            detail="Неизвестная ошибка при получении ответа"
        )


def transform_from_provider_format_3(provider_response: Dict[str, Any]) -> PayInSimResponse:
    try:
        return PayInSimResponse(
            id=provider_response["result"]["id"],
            merchant_transaction_id=provider_response["result"]["orderId"],
            expires_at=datetime.now() + timedelta(minutes = 10),
            amount=str(provider_response["result"]["amount"]),
            currency="RUB",
            currency_rate=str(provider_response["result"]["rate"]),
            amount_in_usd=str(provider_response["result"]["amount"] / provider_response["result"]["rate"]),
            rate="",
            commission=str(provider_response["result"]["fee"] * provider_response["result"]["amount"]),
            phone_number=provider_response["result"]["address"],
            owner_name=provider_response["result"]["recipient"],
            operator=provider_response["result"]["bankName"]
        )
    except KeyError:
        raise HTTPException(
            status_code=520,
            detail="Неизвестная ошибка при получении ответа"
        )


def transform_from_provider_format_with_bank(provider_response: Dict[str, Any]) -> PayInCardBankResponse:
    try:
        return PayInCardBankResponse(
            id=provider_response["result"]["id"],
            merchant_transaction_id=provider_response["result"]["orderId"],
            expires_at=datetime.now() + timedelta(minutes = 10),
            amount=str(provider_response["result"]["amount"]),
            currency="RUB",
            currency_rate=str(provider_response["result"]["rate"]),
            amount_in_usd=str(provider_response["result"]["amount"] / provider_response["result"]["rate"]),
            rate="",
            commission=str(provider_response["result"]["fee"] * provider_response["result"]["amount"]),
            phone_number=provider_response["result"]["address"],
            owner_name=provider_response["result"]["recipient"],
            bank_name=provider_response["result"]["bankName"],
            country_name=_get_country(provider_response["result"]["bank"]),
            payment_currency="RUB",
            payment_link=provider_response["url"]
        )
    except KeyError:
        raise HTTPException(
            status_code=520,
            detail="Неизвестная ошибка при получении ответа"
        )


def transform_from_provider_format_with_bank_2(provider_response: Dict[str, Any]) -> PayInCardBankResponse2:
    try:
        return PayInCardBankResponse2(
            id=provider_response["result"]["id"],
            merchant_transaction_id=provider_response["result"]["orderId"],
            expires_at=datetime.now() + timedelta(minutes = 10),
            amount=str(provider_response["result"]["amount"]),
            currency="RUB",
            currency_rate=str(provider_response["result"]["rate"]),
            amount_in_usd=str(provider_response["result"]["amount"] / provider_response["result"]["rate"]),
            rate="",
            commission=str(provider_response["result"]["fee"] * provider_response["result"]["amount"]),
            phone_number=provider_response["result"]["address"],
            owner_name=provider_response["result"]["recipient"],
            bank_name=provider_response["result"]["bankName"],
            country_name=_get_country(provider_response["result"]["bank"]),
            payment_currency="RUB"
        )
    except KeyError:
        raise HTTPException(
            status_code=520,
            detail="Неизвестная ошибка при получении ответа"
        )

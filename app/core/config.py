# КОНФИГУРАЦИЯ
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Настройки API
    api_base_url: str = 'http://localhost:8000'

    # Токен мерчанта для аутентификации в нашем API
    merchant_token: str = 'test_token_123'

    # Настройки провайдера
    provider_base_url: str = 'https://api.provider.com'
    provider_api_key: str = 'provider_test_key'

    debug: bool = True

    class Config:
        env_file = '../set.env'
        case_sensitive = False


settings = Settings()

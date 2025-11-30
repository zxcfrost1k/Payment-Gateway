# MIDDLEWARE ДЛЯ АУТЕНТИФИКАЦИИ
from typing import Dict, Any
import logging

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

logger = logging.getLogger(__name__)

def verify_token(token: str) -> bool: # Проверка токена
    logger.info(f'Verifying token. Expected: {settings.merchant_token}, Received: {token}')
    return token == settings.merchant_token


def _create_error_response(code: str, message: str, errors: Dict[str, Any] = None) -> Dict[str, Any]:
    '''Создание ответа об ошибке согласно ТЗ - code на первом месте, потом message'''
    error_response = {
        'code': code,
        'message': message
    }

    if errors:
        error_response['errors'] = errors

    return error_response


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        try:
            credentials: HTTPAuthorizationCredentials = await super().__call__(request)
            logger.info(f'Received credentials: {credentials}')

            if not credentials: # Проверка на отсутствие учетных данных
                logger.warning('No credentials provided')
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=_create_error_response(
                        code='AUTH_ERROR',
                        message='Unauthorised'
                    )
                )

            if not credentials.scheme == 'Bearer': # Проверка схемы аутентификации
                logger.warning(f'Invalid scheme: {credentials.scheme}')
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=_create_error_response(
                        code='AUTH_SCHEME_ERROR',
                        message='Неверная схема аутентификации'
                    )
                )

            if not verify_token(credentials.credentials): # Проверка валидности токена
                logger.warning('Token verification failed')
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=_create_error_response(
                        code='INVALID_TOKEN',
                        message='Недействительный токен'
                    )
                )

            logger.info('Token verification successful')
            return credentials.credentials
        except HTTPException as e:
            # Пробрасываем уже созданные HTTPException
            logger.error(f'HTTPException in auth: {e.detail}')
            raise e
        except Exception as e:
            logger.error(f'Unexpected error in auth: {str(e)}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=_create_error_response(
                    code='AUTH_SERVICE_ERROR',
                    message='Ошибка службы аутентификации'
                )
            )


security = JWTBearer()

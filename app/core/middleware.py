"""
Middleware для логирования и других функций
"""
import logging
import time
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict
import json
from collections import defaultdict
import asyncio

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP запросов"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Логируем входящий запрос
        start_time = time.time()

        # Получаем тело запроса (если есть)
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body = body_bytes.decode('utf-8')
                    # Не логируем чувствительные данные
                    if 'password' in body.lower():
                        body = "[REDACTED - contains password]"
                    elif len(body) > 1000:
                        body = body[:1000] + "... [TRUNCATED]"
            except Exception:
                body = "[UNABLE TO READ BODY]"

        logger.info(f"REQUEST: {request.method} {request.url} - Body: {body}")

        # Выполняем запрос
        try:
            response = await call_next(request)
        except Exception as e:
            # Логируем ошибки
            logger.error(f"ERROR: {request.method} {request.url} - {str(e)}")
            raise

        # Логируем ответ
        process_time = time.time() - start_time
        logger.info(
            f"RESPONSE: {request.method} {request.url} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware для ограничения количества запросов"""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Получаем IP адрес клиента
        client_ip = self._get_client_ip(request)

        # Очищаем старые запросы
        current_time = time.time()
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < 60  # 60 секунд = 1 минута
        ]

        # Проверяем лимит
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )

        # Добавляем текущий запрос
        self.requests[client_ip].append(current_time)

        # Выполняем запрос
        response = await call_next(request)
        return response

    def _get_client_ip(self, request: Request) -> str:
        """Получить IP адрес клиента"""
        # Проверяем заголовки прокси
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Проверяем другие заголовки
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Используем client.host
        return request.client.host if request.client else "unknown"


class CORSMiddleware(BaseHTTPMiddleware):
    """Middleware для обработки CORS (расширенная версия)"""

    def __init__(self, app, allow_origins=None, allow_credentials=True,
                 allow_methods=None, allow_headers=None):
        super().__init__(app)
        self.allow_origins = allow_origins or ["*"]
        self.allow_credentials = allow_credentials
        self.allow_methods = allow_methods or ["*"]
        self.allow_headers = allow_headers or ["*"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Добавляем CORS заголовки
        if self.allow_origins != ["*"]:
            origin = request.headers.get("origin")
            if origin in self.allow_origins:
                response.headers["Access-Control-Allow-Origin"] = origin
        else:
            response.headers["Access-Control-Allow-Origin"] = "*"

        response.headers["Access-Control-Allow-Credentials"] = str(self.allow_credentials).lower()
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)

        return response
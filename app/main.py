from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.exceptions import ValidationException, BusinessLogicException
from app.core.middleware import LoggingMiddleware, RateLimitMiddleware

# Импорт роутеров (раскомментируй когда создашь)
from app.modules.auth.router import router as auth_router
from app.modules.patients.router import router as patients_router
from app.modules.appointments.router import router as appointments_router
from app.modules.visits.router import router as visits_router
from app.modules.prescriptions.router import router as prescriptions_router
from app.modules.operations.router import router as operations_router
from app.modules.stats.router import router as stats_router
from app.modules.billing.router import router as billing_router

app = FastAPI(
    title=settings.app_name,
    description="API для медицинской информационной системы",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# Middleware для логирования
app.add_middleware(LoggingMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Глобальная обработка ошибок валидации
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации Pydantic с улучшенной детализацией"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_type = error.get("type", "unknown")

        # Улучшаем сообщения об ошибках
        if error_type == "missing":
            message = f"Обязательное поле '{field}' отсутствует"
        elif error_type == "extra_forbidden":
            message = f"Неожиданное поле '{field}'"
        elif error_type == "string_too_short":
            min_length = error.get("ctx", {}).get("min_length", "неизвестно")
            message = f"Поле '{field}' слишком короткое (минимум {min_length} символов)"
        elif error_type == "string_too_long":
            max_length = error.get("ctx", {}).get("max_length", "неизвестно")
            message = f"Поле '{field}' слишком длинное (максимум {max_length} символов)"
        elif error_type == "value_error.const":
            message = f"Поле '{field}' должно иметь значение {error.get('ctx', {}).get('given', 'неизвестно')}"
        elif "datetime" in error_type:
            message = f"Поле '{field}' должно быть корректной датой/временем"
        elif "int" in error_type:
            message = f"Поле '{field}' должно быть целым числом"
        elif "float" in error_type:
            message = f"Поле '{field}' должно быть числом"
        elif "bool" in error_type:
            message = f"Поле '{field}' должно быть true или false"
        else:
            message = f"{field}: {message}"

        errors.append({
            "field": field,
            "message": message,
            "error_type": error_type
        })

    return JSONResponse(
        status_code=422,
        content={
            "error": "Ошибка валидации данных",
            "detail": errors,
            "type": "validation_error",
            "path": str(request.url),
            "method": request.method
        }
    )


# Глобальная обработка бизнес-ошибок
@app.exception_handler(BusinessLogicException)
async def business_logic_exception_handler(request: Request, exc: BusinessLogicException):
    """Обработчик бизнес-ошибок с дополнительной информацией"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Ошибка бизнес-логики",
            "detail": exc.detail,
            "type": "business_logic_error",
            "path": str(request.url),
            "method": request.method
        }
    )


# Глобальная обработка всех HTTP исключений
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Обработчик всех HTTP исключений с улучшенной детализацией"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP ошибка",
            "detail": exc.detail,
            "type": "http_error",
            "status_code": exc.status_code,
            "path": str(request.url),
            "method": request.method
        }
    )


# Глобальная обработка непредвиденных ошибок
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Обработчик непредвиденных ошибок"""
    # Логируем ошибку для отладки
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Внутренняя ошибка сервера",
            "detail": "Произошла непредвиденная ошибка. Попробуйте позже.",
            "type": "internal_server_error",
            "path": str(request.url),
            "method": request.method
        }
    )


# Подключение роутеров (раскомментируй когда создашь)
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(patients_router, prefix="/patients", tags=["Patients"])
app.include_router(appointments_router, prefix="/appointments", tags=["Appointments"])
app.include_router(visits_router, prefix="/visits", tags=["Visits"])
app.include_router(prescriptions_router, prefix="/prescriptions", tags=["Prescriptions"])
app.include_router(operations_router, prefix="/operations", tags=["Operations"])
app.include_router(stats_router, prefix="/stats", tags=["Statistics"])
app.include_router(billing_router, prefix="/billing", tags=["Billing"])

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

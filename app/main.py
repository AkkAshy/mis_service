from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.exceptions import ValidationException, BusinessLogicException

# Импорт роутеров (раскомментируй когда создашь)
from app.modules.auth.router import router as auth_router
from app.modules.patients.router import router as patients_router
from app.modules.appointments.router import router as appointments_router
# from app.modules.visits.router import router as visits_router
# from app.modules.prescriptions.router import router as prescriptions_router

app = FastAPI(
    title=settings.app_name,
    description="API для медицинской информационной системы",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

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
    """Обработчик ошибок валидации Pydantic"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": errors,
            "type": "validation_error"
        }
    )


# Глобальная обработка бизнес-ошибок
@app.exception_handler(BusinessLogicException)
async def business_logic_exception_handler(request: Request, exc: BusinessLogicException):
    """Обработчик бизнес-ошибок"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Business Logic Error",
            "detail": exc.detail,
            "type": "business_logic_error"
        }
    )


# Подключение роутеров (раскомментируй когда создашь)
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(patients_router, prefix="/patients", tags=["Patients"])
app.include_router(appointments_router, prefix="/appointments", tags=["Appointments"])
# app.include_router(visits_router, prefix="/visits", tags=["Visits"])
# app.include_router(prescriptions_router, prefix="/prescriptions", tags=["Prescriptions"])

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

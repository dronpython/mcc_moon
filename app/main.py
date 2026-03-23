from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.routers import organizations
from app.dependencies import verify_api_key

app = FastAPI(
    title="Organization Directory API",
    description="""
    ## API для управления справочником организаций

    ### Возможности:
    * Поиск организаций по различным критериям
    * Геопоиск организаций в заданном радиусе

    ### Особенности:
    * Древовидная структура видов деятельности
    * Поддержка множественных телефонных номеров
    * Геопространственный поиск
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(organizations.router, dependencies=[Depends(verify_api_key)])


@app.get("/")
def root():
    return {
        "message": "Organization Directory API",
        "documentation": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json"
    }


@app.get("/health")
def health_check():
    """Проверка работоспособности API"""
    return {"status": "healthy"}


# Кастомная OpenAPI конфигурация (опционально)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Добавляем теги для группировки эндпоинтов
    openapi_schema["tags"] = [
        {"name": "organizations", "description": "Операции с организациями"},
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
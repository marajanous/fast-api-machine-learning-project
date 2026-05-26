import logging
import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from app.infrastructure.clients.mongodb import _client
from app.infrastructure.clients.minio import minio_manager
from app.api.routers import auth, datasets
from app.infrastructure.services.domain_exception import DomainException
from app.api.routers import auth, datasets, models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting infrastructure initialization in clean architecture...")
        _client.connect()  
        minio_manager.connect()  
    except Exception as e:
        logger.error(f"Critical error during application startup: {e}")
    
    yield  
    
    logger.info("Shutting down application and cleaning up resources...")
    _client.close()  

app = FastAPI(
    title="MLOps Project API",
    description="Robust layered architecture compliant with SOLID principles and FastAPI standards.",
    version="2.0.0",
    lifespan=lifespan
)

@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    logger.warning(f"Domain error caught: {exc.message}")
    
    status_code = status.HTTP_400_BAD_REQUEST
    if exc.__class__.__name__ == "DatasetNotFoundException":
        status_code = status.HTTP_404_NOT_FOUND
        
    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "detail": exc.message}
    )

@app.get("/")
async def root():
    return {"status": "FastAPI in Docker is running in clean architecture!"}

app.include_router(auth.router)
app.include_router(datasets.router)
app.include_router(models.router)

def save_automatic_documentation():
    os.makedirs("docs", exist_ok=True)
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    with open("docs/openapi.json", "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

save_automatic_documentation()
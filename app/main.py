import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.infrastructure.clients.mongodb import mongo_manager
from app.infrastructure.clients.minio import minio_manager
from app.routers import auth, datasets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    try:
        logger.info("Spouštím inicializaci infrastruktury v čisté architektuře...")
        mongo_manager.connect()  
        minio_manager.connect()  
    except Exception as e:
        logger.error(f"Kritická chyba při startu aplikace: {e}")
    
    yield  
    
    logger.info("Ukončuji aplikaci a čistím prostředky...")
    mongo_manager.close()  

app = FastAPI(
    title="MLOps Project API",
    description="Robustní vrstvená architektura splňující SOLID principy a FastAPI standardy.",
    version="2.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"status": "FastAPI v Dockeru běží v čisté architektuře!"}

app.include_router(auth.router)
app.include_router(datasets.router)

import os
import json
from fastapi.openapi.utils import get_openapi

def ulozi_automatickou_dokumentaci():
    os.makedirs("docs", exist_ok=True)
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    with open("docs/openapi.json", "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

ulozi_automatickou_dokumentaci()
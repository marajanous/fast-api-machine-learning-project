import logging
from fastapi import FastAPI
from app.routers import auth, datasets 

# Nastavení logování
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MLOps Project API")

# úvodní endpoint
@app.get("/")
async def root():
    return {"status": "FastAPI v Dockeru běží!"}

# Registrace endpointů do aplikace
app.include_router(auth.router)
app.include_router(datasets.router)
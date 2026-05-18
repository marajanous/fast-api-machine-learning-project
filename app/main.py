import logging
from fastapi import FastAPI
from pydantic import BaseModel

# 1. Nastavení logování (bod 4 od Michala)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 2. Inicializace FastAPI aplikace
app = FastAPI(title="MLOps Project API")

# 3. Schéma pro validaci dat (Pydantic - bod 4)
class User(BaseModel):
    username: str
    email: str

# 4. API Endpointy (bod 6)

@app.get("/")
async def root():
    return {"status": "FastAPI v Dockeru běží!"}

@app.post("/login", tags=["Auth"])
async def login():
    """Endpoint pro přihlášení."""
    logger.info("Pokus o přihlášení uživatele")
    return {"message": "Login successful (mock)"}

@app.post("/logout", tags=["Auth"])
async def logout():
    """Endpoint pro odhlášení."""
    logger.info("Uživatel se odhlásil")
    return {"message": "Logout successful"}

@app.get("/me", response_model=User, tags=["Auth"])
async def get_me():
    """Vrátí informace o aktuálním uživateli."""
    # Zatím vracíme testovací data, později napojíme na MongoDB
    return {
        "username": "pilot_student", 
        "email": "student@seznam.cz"
    }
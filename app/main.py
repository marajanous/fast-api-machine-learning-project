import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

# 1. Logování
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 2. Inicializace aplikace 
app = FastAPI(title="MLOps Project API")

# 3. Modely
class User(BaseModel):
    username: str
    email: str

# 4. Auth Endpointy 
@app.get("/")
async def root():
    return {"status": "FastAPI v Dockeru běží!"}

@app.post("/login", tags=["Auth"])
async def login():
    logger.info("Pokus o přihlášení")
    return {"message": "Login successful (mock)"}

@app.get("/me", response_model=User, tags=["Auth"])
async def get_me():
    return {"username": "pilot_student", "email": "student@seznam.cz"}

# 5. Dataset Management Endpointy 
@app.post("/datasets/upload", tags=["Datasets"])
async def upload_dataset(file: UploadFile = File(...)):
    """Nahraje .csv soubor do systému."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Povoleny jsou pouze .csv soubory")
    
    logger.info(f"Nahrávám soubor {file.filename} do MinIO")
    logger.info(f"Ukládám metadata souboru {file.filename} do MongoDB")
    
    return {
        "message": "Dataset úspěšně nahrán",
        "filename": file.filename
    }

@app.delete("/datasets/{filename}", tags=["Datasets"])
async def remove_dataset(filename: str):
    """Smaže dataset."""
    logger.info(f"Odstraňuji dataset: {filename}")
    return {"message": f"Dataset {filename} byl úspěšně odstraněn"}
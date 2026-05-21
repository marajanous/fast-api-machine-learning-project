import hashlib
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.infrastructure.clients.mongodb import mongo_manager

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

def hash_password(password: str) -> str:
    """Bezpečné zahashování hesla pomocí SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    logger.info(f"Pokus o registraci uživatele: {user.email}")
    
    existing_user = await mongo_manager.db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Uživatel s tímto e-mailem již existuje."
        )
    
    hashed = hash_password(user.password)
    await mongo_manager.db["users"].insert_one({
        "email": user.email,
        "password": hashed
    })
    
    return {"status": "success", "message": "Uživatel byl úspěšně registrován!"}

@router.post("/login")
async def login(user: UserLogin):
    logger.info(f"Pokus o přihlášení uživatele: {user.email}")
    
    db_user = await mongo_manager.db["users"].find_one({"email": user.email})
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Nesprávný e-mail nebo heslo."
        )
    
    if db_user["password"] != hash_password(user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Nesprávný e-mail nebo heslo."
        )
    
    return {"status": "success", "message": "Přihlášení bylo úspěšné!"}
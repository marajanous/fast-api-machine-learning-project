import logging
import hashlib
import os
from fastapi import APIRouter, HTTPException, status
from app.models.user import User
from app.config.database import db

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Zahešuje heslo pomocí PBKDF2 s náhodnou solí."""
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}:{pwd_hash.hex()}"

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Ověří zadané heslo proti uloženému zahešovanému heslu."""
    try:
        salt_hex, hash_hex = stored_password.split(":")
        salt = bytes.fromhex(salt_hex)
        stored_hash = bytes.fromhex(hash_hex)
        
        new_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        return new_hash == stored_hash
    except Exception:
        return False

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: User):
    logger.info(f"Registrace nového uživatele: {user_data.email}")
    
    # Kontrola, zda uživatel s tímto e-mailem v DB neexistuje
    existing_user = await db["users"].find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uživatel s tímto e-mailem již existuje"
        )
    
    secure_password = hash_password(user_data.password)
    
    new_user = {
        "username": user_data.username,
        "email": user_data.email,
        "password": secure_password
    }
    await db["users"].insert_one(new_user)
    
    return {"status": "success", "message": "Uživatel byl úspěšně zaregistrován"}

@router.post("/login")
async def login(user_data: User):
    logger.info(f"Pokus o přihlášení uživatele: {user_data.email}")
    
    # Vyhledání uživatele v MongoDB podle e-mailu
    user = await db["users"].find_one({"email": user_data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nesprávný e-mail nebo heslo"
        )
    
    # Ověření hesla
    if not verify_password(user["password"], user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nesprávný e-mail nebo heslo"
        )
    
    return {
        "status": "success", 
        "message": f"Uživatel {user['username']} byl úspěšně přihlášen!"
    }

@router.post("/logout")
async def logout():
    logger.info("Uživatel se odhlásil")
    return {"message": "Odhlášení úspěšné"}
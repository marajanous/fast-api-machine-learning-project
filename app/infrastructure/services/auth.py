import hashlib
import logging
from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import jwt 

from app.config.settings import settings
from app.infrastructure.services.exceptions import UserAlreadyExistsException

logger = logging.getLogger(__name__)

class AuthenticationService:
    def __init__(self, db_client):
        self.db = db_client
        self.logged_out_emails = set()

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15) 
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    async def register_user(self, email: str, password: str) -> Optional[str]:
        logger.info(f"Service: Registering user {email}")
        
        existing_user = await self.db["users"].find_one({"email": email})
        if existing_user:
            raise UserAlreadyExistsException(email)
            
        hashed = self.hash_password(password)
        await self.db["users"].insert_one({
            "email": email,
            "password": hashed
        })
        return email

    async def login_user(self, email: str, password: str) -> Optional[str]:
        logger.info(f"Service: Logging in user {email}")
        
        db_user = await self.db["users"].find_one({"email": email})
        if not db_user:
            return None
            
        if db_user["password"] != self.hash_password(password):
            return None
            
        if email in self.logged_out_emails:
            self.logged_out_emails.remove(email)
            
        access_token = self.create_access_token(data={"sub": email})
        return access_token

    async def logout_user(self, email: str) -> bool:
        logger.info(f"Service: Logging out user {email}")
        self.logged_out_emails.add(email)
        return True
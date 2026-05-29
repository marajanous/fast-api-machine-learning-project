import logging
from jose import jwt, JWTError
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.infrastructure.clients.mongodb import _client
from app.infrastructure.services.auth import AuthenticationService
from app.config.settings import settings
from app.api.models.auth import UserRegister, UserLogout
from app.infrastructure.services.domain_exception import UserAlreadyExistsException

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_auth_service() -> AuthenticationService:
    return AuthenticationService(db_client=_client.db)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"email": email}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister, auth_service: AuthenticationService = Depends(get_auth_service)):
    logger.info(f"Router: Registration request: {user.email}")
    result = await auth_service.register_user(user.email, user.password)
    if not result:
        raise UserAlreadyExistsException(f"User with email '{user.email}' already exists.")
    return {"status": "success", "message": "User registered successfully."}

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    logger.info(f"Router: Login request via OAuth2: {form_data.username}")
    token = await auth_service.login_user(form_data.username, form_data.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password."
        )
    return {"access_token": token, "token_type": "bearer"}

@router.post("/logout")
async def logout(user: UserLogout, auth_service: AuthenticationService = Depends(get_auth_service)):
    logger.info(f"Router: Logout request: {user.email}")
    await auth_service.logout_user(user.email)
    return {"status": "success", "message": "User logged out successfully."}

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    logger.info(f"Router: Fetching profile for user: {current_user['email']}")
    return {
        "status": "success",
        "user": {
            "email": current_user["email"]
        }
    }
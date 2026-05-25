from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    mongo_uri: str = Field(
        default="mongodb://root:password@mongodb:27017/?authSource=admin", 
        alias="MONGO_URL"
    )
    
    minio_endpoint: str = Field(
        default="minio:9000", 
        alias="MINIO_ENDPOINT_URL"
    )
    
    minio_access_key: str = Field(
        default="minioadmin", 
        alias="MINIO_ROOT_USER"
    )
    
    minio_secret_key: str = Field(
        default="SuperSecretMinioPassword123", 
        alias="MINIO_ROOT_PASSWORD"
    )

    secret_key: str = Field(
        default="SUPER_SECRET_KEY_123_ABC", 
        alias="JWT_SECRET_KEY"
    )
    algorithm: str = Field(
        default="HS256", 
        alias="JWT_ALGORITHM"
    )

    @field_validator("minio_endpoint")
    @classmethod
    def validate_endpoint_format(cls, v: str) -> str:
        if ":" not in v:
            raise ValueError("Endpoint configuration must contain a valid port separator (':').")
        return v

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
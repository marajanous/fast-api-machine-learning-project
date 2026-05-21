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

    @field_validator("minio_endpoint")
    @classmethod
    def validate_endpoint_format(cls, v: str) -> str:
    
        if ":" not in v:
            raise ValueError("Konfigurace koncového bodu musí obsahovat platný oddělovač portů (':').")
        return v

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
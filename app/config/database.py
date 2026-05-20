import os
from motor.motor_asyncio import AsyncIOMotorClient
import boto3

# Načtení URL z ENV 
MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:password@mongodb:27017/")
client = AsyncIOMotorClient(MONGO_URI)
db = client["mlops_database"]  # Název naší databáze

# Inicializace MinIO klienta
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD", "minioadminpassword")

minio_client = boto3.client(
    "s3",
    endpoint_url=f"http://{MINIO_ENDPOINT}",
    aws_access_key_id=MINIO_ROOT_USER,
    aws_secret_access_key=MINIO_ROOT_PASSWORD,
)
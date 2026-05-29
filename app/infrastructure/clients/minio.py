import logging
import boto3
from botocore.client import Config
from app.config.settings import settings

logger = logging.getLogger(__name__)

class MinioClientManager:
    def __init__(self):
        self.client = None

    def connect(self):
        try:
            logger.info("Connecting to MinIO...")
            self.client = boto3.client(
                's3',
                endpoint_url=f"http://{settings.minio_endpoint}",
                aws_access_key_id=settings.minio_access_key,
                aws_secret_access_key=settings.minio_secret_key,
                config=Config(signature_version='s3v4'),
                region_name='us-east-1'
            )
            logger.info("MinIO client successfully initialized.")
        except Exception as e:
            logger.error(f"Critical error connecting to MinIO: {e}")
            raise e

minio_manager = MinioClientManager()
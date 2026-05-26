import logging
from app.infrastructure.clients.minio import MinioClientManager
from app.infrastructure.services.domain_exception import DatasetNotFoundException

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, mongo, minio: MinioClientManager):
        self.mongo = mongo
        self.minio = minio

    async def save_dataset(self, filename: str, content_type: str, file_obj) -> None:
        logger.info(f"StorageService: Uploading file {filename} to MinIO...")
        self.minio.client.upload_fileobj(file_obj, "datasets", filename)

        logger.info(f"StorageService: Saving metadata for file {filename} to MongoDB...")
        metadata = {
            "filename": filename,
            "content_type": content_type,
            "status": "uploaded"
        }
        await self.mongo.db["datasets"].insert_one(metadata)

    async def delete_dataset(self, filename: str) -> None:
        record = await self.mongo.db["datasets"].find_one({"filename": filename})
        if not record:
            raise DatasetNotFoundException(filename)

        logger.info(f"StorageService: Deleting file {filename} from MinIO...")
        self.minio.client.remove_object("datasets", filename)

        logger.info(f"StorageService: Deleting metadata for file {filename} from MongoDB...")
        await self.mongo.db["datasets"].delete_one({"filename": filename})
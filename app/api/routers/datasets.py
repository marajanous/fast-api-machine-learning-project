import logging
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from pydantic import BaseModel, Field

from app.infrastructure.clients.mongodb import _client
from app.infrastructure.clients.minio import minio_manager, MinioClientManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/datasets", tags=["Datasets"])


class DatasetColumnInfo(BaseModel):
    column_name: str = Field(..., description="Name of the column in the CSV file")
    data_type: str = Field(..., description="Expected data type (e.g., int, float, string)")
    required: bool = Field(..., description="Indicates if the column is required")
    description: str = Field(..., description="Detailed description of what the variable means")

class UploadResponse(BaseModel):
    status: str = Field(..., description="Operation status (success/error)")
    message: str = Field(..., description="Detailed message for the user")


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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset with name '{filename}' was not found in the database."
            )

        logger.info(f"StorageService: Deleting file {filename} from MinIO...")
        self.minio.client.remove_object("datasets", filename)

        logger.info(f"StorageService: Deleting metadata for file {filename} from MongoDB...")
        await self.mongo.db["datasets"].delete_one({"filename": filename})


def get_mongo_client():
    return _client

def get_minio_manager() -> MinioClientManager:
    return minio_manager

def get_storage_service(
    mongo = Depends(get_mongo_client),
    minio: MinioClientManager = Depends(get_minio_manager)
) -> StorageService:
    return StorageService(mongo=mongo, minio=minio)


@router.get(
    "/info", 
    response_model=list[DatasetColumnInfo], 
    summary="Get required CSV dataset structure"
)
async def get_dataset_structure_info():
    required_structure = [
        {
            "column_name": "age",
            "data_type": "int",
            "required": True,
            "description": "Age of the patient or client in years (e.g., 35)."
        },
        {
            "column_name": "income",
            "data_type": "float",
            "required": True,
            "description": "Total annual net income in CZK."
        },
        {
            "column_name": "target",
            "data_type": "int",
            "required": False,
            "description": "Target variable for ML training (0 = failed, 1 = succeeded)."
        }
    ]
    return required_structure


@router.post(
    "/upload", 
    response_model=UploadResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new CSV dataset"
)
async def upload_dataset(
    file: UploadFile = File(...),
    storage: StorageService = Depends(get_storage_service)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only files with the .csv extension are allowed."
        )

    try:
        await storage.save_dataset(
            filename=file.filename,
            content_type=file.content_type,
            file_obj=file.file
        )
        return UploadResponse(
            status="success",
            message=f"Dataset {file.filename} was successfully uploaded and registered."
        )
    except Exception as e:
        logger.error(f"Error during dataset upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while saving the dataset."
        )


@router.delete(
    "/{filename}", 
    response_model=UploadResponse, 
    summary="Delete a dataset from the system"
)
async def delete_dataset(
    filename: str,
    storage: StorageService = Depends(get_storage_service)
):
    try:
        await storage.delete_dataset(filename=filename)
        return UploadResponse(
            status="success",
            message=f"Dataset {filename} was completely deleted from MinIO and MongoDB."
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error during dataset deletion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while deleting the dataset."
        )
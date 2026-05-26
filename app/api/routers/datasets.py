import logging
from fastapi import APIRouter, Depends, File, UploadFile, status
from app.infrastructure.clients.mongodb import _client
from app.infrastructure.clients.minio import minio_manager, MinioClientManager
from app.infrastructure.services.storage import StorageService
from app.api.models.datasets import DatasetColumnInfo, UploadResponse
from app.infrastructure.services.domain_exception import InvalidDatasetFormatException

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/datasets", tags=["Datasets"])

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
        raise InvalidDatasetFormatException("Only files with the .csv extension are allowed.")

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
        raise e

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
    except Exception as e:
        logger.error(f"Error during dataset deletion: {str(e)}")
        raise e
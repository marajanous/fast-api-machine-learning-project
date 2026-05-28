import asyncio
import logging
from uuid import uuid4
from app.config.settings import settings

logger = logging.getLogger(__name__)

tasks_db = {}

class ModelTrainingService:
    def __init__(self, storage_service):
        self.storage_service = storage_service

    async def create_training_task(self, model_name: str, dataset_id: str) -> str:
        task_id = str(uuid4())
        tasks_db[task_id] = {
            "task_id": task_id,
            "model_name": model_name,
            "dataset_id": dataset_id,
            "status": "pending",
            "result": None
        }
        return task_id

    async def run_training_background(self, task_id: str) -> None:
        if task_id not in tasks_db:
            return

        task = tasks_db[task_id]
        dataset_filename = task["dataset_id"]

        if not dataset_filename.lower().endswith(".csv"):
            dataset_filename = f"{dataset_filename}.csv"

        logger.info(f"Background training started for ID: {task_id}. Fetching dataset: {dataset_filename}")
        tasks_db[task_id]["status"] = "running"

        try:
            actual_client = self.storage_service.minio.client
            bucket_name = getattr(settings, "MINIO_BUCKET", "datasets")
            
            response = actual_client.get_object(Bucket=bucket_name, Key=dataset_filename)
            
            if isinstance(response, dict) and 'Body' in response:
                dataset_content = response['Body'].read()
            else:
                dataset_content = response.read()
                
            if hasattr(response, 'close'):
                response.close()

            logger.info(f"Successfully fetched {len(dataset_content)} bytes from MinIO for task {task_id}")

            await asyncio.sleep(5)

            tasks_db[task_id]["status"] = "completed"
            tasks_db[task_id]["result"] = f"SUCCESSFULLY_TRAINED_MODEL_USING_{len(dataset_content)}_BYTES"
            logger.info(f"Training finished successfully for ID: {task_id}")

        except Exception as e:
            logger.error(f"Training failed for task {task_id}: {str(e)}")
            tasks_db[task_id]["status"] = "failed"
            tasks_db[task_id]["result"] = f"Error: {str(e)}"

    async def get_task_status(self, task_id: str) -> dict:
        if task_id not in tasks_db:
            from app.infrastructure.services.domain_exception import DomainException
            raise DomainException(f"Training task '{task_id}' was not found.")
        return tasks_db[task_id]
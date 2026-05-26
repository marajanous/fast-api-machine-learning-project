import asyncio
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)

tasks_db = {}

class ModelTrainingService:
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

        logger.info(f"Background placeholder task started for ID: {task_id}")
        tasks_db[task_id]["status"] = "running"

        await asyncio.sleep(20)

        tasks_db[task_id]["status"] = "completed"
        tasks_db[task_id]["result"] = f"DUMMY_MODEL_BYTES_FOR_{tasks_db[task_id]['model_name'].upper()}"
        logger.info(f"Background placeholder task finished for ID: {task_id}")

    async def get_task_status(self, task_id: str) -> dict:
        if task_id not in tasks_db:
            from app.infrastructure.services.domain_exception import DomainException
            raise DomainException(f"Training task '{task_id}' was not found.")
        return tasks_db[task_id]
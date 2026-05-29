import logging
from fastapi import APIRouter, Depends, BackgroundTasks, status, HTTPException, Request
from fastapi.responses import PlainTextResponse
from app.infrastructure.services.model_training import ModelTrainingService
from app.api.models.models import ModelInfo, TrainResponse, TaskStatusResponse
from app.infrastructure.services.storage import StorageService
from app.api.routers.datasets import get_storage_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/model", tags=["Models"])

def get_model_training_service(storage_service: StorageService = Depends(get_storage_service)) -> ModelTrainingService:
    return ModelTrainingService(storage_service=storage_service)

@router.get("/info", response_model=list[ModelInfo])
async def get_models_info():
    return [
        {"model_name": "linear_regression", "description": "Placeholder for simple linear model."},
        {"model_name": "random_forest", "description": "Placeholder for ensemble tree model."}
    ]

@router.post("/{model_name}/train/{dataset_id}", response_model=TrainResponse, status_code=status.HTTP_202_ACCEPTED)
async def train_model(
    model_name: str,
    dataset_id: str,
    background_tasks: BackgroundTasks,
    service: ModelTrainingService = Depends(get_model_training_service)
):
    task_id = await service.create_training_task(model_name=model_name, dataset_id=dataset_id)
    background_tasks.add_task(service.run_training_background, task_id)
    return {"task_id": task_id}

@router.get("/task/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(task_id: str, service: ModelTrainingService = Depends(get_model_training_service)):
    task = await service.get_task_status(task_id)
    return {
        "task_id": task["task_id"],
        "status": task["status"],
        "model_name": task["model_name"],
        "dataset_id": task["dataset_id"]
    }

@router.get("/{task_id}/result", response_class=PlainTextResponse)
async def get_training_result(task_id: str, service: ModelTrainingService = Depends(get_model_training_service)):
    task = await service.get_task_status(task_id)
    
    if task["status"] == "failed":
        raise HTTPException(
            status_code=400,
            detail=f"Training failed. Reason: {task['result']}"
        )
        
    if task["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Training is still in progress. Current status: {task['status']}"
        )
        
    return task["result"]
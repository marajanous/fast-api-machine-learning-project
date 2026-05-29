from pydantic import BaseModel, Field

class ModelInfo(BaseModel):
    model_name: str = Field(..., description="Unique name of the machine learning model")
    description: str = Field(..., description="Short overview of what the model does")

class TrainResponse(BaseModel):
    task_id: str = Field(..., description="Identifier of the asynchronous background training task")

class TaskStatusResponse(BaseModel):
    task_id: str = Field(..., description="Identifier of the task")
    status: str = Field(..., description="Current state of the task (pending, running, completed)")
    model_name: str = Field(..., description="Name of the trained model")
    dataset_id: str = Field(..., description="ID of the dataset used for training")
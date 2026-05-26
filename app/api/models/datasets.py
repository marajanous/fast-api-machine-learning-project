from pydantic import BaseModel, Field

class DatasetColumnInfo(BaseModel):
    column_name: str = Field(..., description="Name of the column in the CSV file")
    data_type: str = Field(..., description="Expected data type (e.g., int, float, string)")
    required: bool = Field(..., description="Indicates if the column is required")
    description: str = Field(..., description="Detailed description of what the variable means")

class UploadResponse(BaseModel):
    status: str = Field(..., description="Operation status (success/error)")
    message: str = Field(..., description="Detailed message for the user")
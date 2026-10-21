from typing import Any, Optional, Dict
from pydantic import BaseModel

class APIResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: str
    walmart_m5_available: bool
    available_models: list[str]
    system_info: Dict[str, Any]


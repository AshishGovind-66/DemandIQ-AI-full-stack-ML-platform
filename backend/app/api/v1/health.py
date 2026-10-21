import platform
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.core.config import settings
from backend.app.database.session import get_db
from backend.app.preprocessing.m5_loader import M5DataLoader
from backend.app.forecasting.registry import ModelRegistry
from backend.app.schemas.common import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)):
    """Health check endpoint confirming database, filesystem, and model status."""
    # Check database
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Check M5 files presence
    m5_status = M5DataLoader.get_status()

    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database=db_status,
        walmart_m5_available=m5_status["all_core_present"],
        available_models=ModelRegistry.list_models(),
        system_info={
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "m5_files": m5_status["files"]
        }
    )


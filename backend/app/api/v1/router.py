from fastapi import APIRouter

from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.datasets import router as datasets_router
from backend.app.api.v1.models import router as models_router
from backend.app.api.v1.forecasts import router as forecasts_router
from backend.app.api.v1.inventory import router as inventory_router
from backend.app.api.v1.explainability import router as explainability_router
from backend.app.api.v1.reports import router as reports_router
from backend.app.api.v1.dashboard import router as dashboard_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router, tags=["Health"])
api_v1_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_v1_router.include_router(datasets_router, prefix="/datasets", tags=["Datasets"])
api_v1_router.include_router(models_router, tags=["Models & Training"])
api_v1_router.include_router(forecasts_router, prefix="/forecasts", tags=["Forecasting"])
api_v1_router.include_router(inventory_router, prefix="/inventory", tags=["Inventory Optimization"])
api_v1_router.include_router(explainability_router, prefix="/explainability", tags=["Explainability"])
api_v1_router.include_router(reports_router, prefix="/reports", tags=["Reports & Exports"])


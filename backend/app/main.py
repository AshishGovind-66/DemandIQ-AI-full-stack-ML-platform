from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.database.session import init_db
from backend.app.api.v1.router import api_v1_router
from backend.app.api.v1.health import router as root_health_router
from backend.app.utils.exceptions import DemandIQException

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events."""
    logger.info("Starting up DemandIQ AI Backend Service...")
    settings.ensure_directories()
    init_db()
    logger.info("DemandIQ AI Backend ready to receive requests.")
    yield
    logger.info("Shutting down DemandIQ AI Backend Service.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Demand Forecasting and Inventory Optimization System for Retail Businesses",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include top-level /health endpoint
app.include_router(root_health_router)

# Include API v1 router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.exception_handler(DemandIQException)
async def demandiq_exception_handler(request: Request, exc: DemandIQException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.message}
    )

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "tagline": settings.PROJECT_TAGLINE,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)


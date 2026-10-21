import os
from pathlib import Path
from typing import List

# Base directory for the backend app
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

class Settings:
    PROJECT_NAME: str = "DemandIQ AI"
    PROJECT_TAGLINE: str = "Forecast Smarter. Stock Smarter. Grow Better."
    VERSION: str = "1.0.0"
    PROJECT_ROOT: Path = PROJECT_ROOT
    API_V1_STR: str = os.getenv("API_V1_PREFIX", "/api/v1")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    
    # Server
    HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("BACKEND_PORT", 8000))
    
    # CORS
    _cors_str: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    CORS_ORIGINS: List[str] = [origin.strip() for origin in _cors_str.split(",") if origin.strip()]
    
    # Database: Default fallback is SQLite for instant zero-dependency local dev
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{PROJECT_ROOT / 'demandiq.db'}")
    
    # File storage paths
    DATA_RAW_DIR: Path = Path(os.getenv("DATA_RAW_DIR", str(PROJECT_ROOT / "data" / "raw")))
    DATA_PROCESSED_DIR: Path = Path(os.getenv("DATA_PROCESSED_DIR", str(PROJECT_ROOT / "data" / "processed")))
    DATA_SAMPLE_DIR: Path = PROJECT_ROOT / "data" / "sample"
    M5_DIR: Path = PROJECT_ROOT / "m5-forecasting-accuracy"
    MODELS_DIR: Path = Path(os.getenv("MODELS_DIR", str(PROJECT_ROOT / "models")))
    REPORTS_DIR: Path = Path(os.getenv("REPORTS_DIR", str(PROJECT_ROOT / "reports")))
    
    # Max file upload size (default: 100MB)
    MAX_UPLOAD_SIZE_BYTES: int = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", 100 * 1024 * 1024))
    
    # Supported ML models
    SUPPORTED_MODELS: List[str] = [
        "naive",
        "seasonal_naive",
        "linear_regression",
        "random_forest",
        "xgboost",
        "lightgbm"
    ]

    def ensure_directories(self) -> None:
        """Create storage directories if they do not exist."""
        for d in [self.DATA_RAW_DIR, self.DATA_PROCESSED_DIR, self.DATA_SAMPLE_DIR, self.MODELS_DIR, self.REPORTS_DIR]:
            d.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()

import os
import uuid
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd

from backend.app.core.config import settings
from backend.app.core.logging import logger

class ExportService:
    """Handles generating and exporting CSV and JSON reports."""

    @classmethod
    def export_dataframe_to_csv(cls, df: pd.DataFrame, prefix: str = "export") -> Path:
        """Saves a dataframe to a timestamped CSV in reports directory."""
        filename = f"{prefix}_{uuid.uuid4().hex[:8]}.csv"
        out_path = settings.REPORTS_DIR / filename
        df.to_csv(out_path, index=False)
        logger.info(f"Exported CSV to {out_path}")
        return out_path

    @classmethod
    def export_dict_to_json(cls, data: Dict[str, Any], prefix: str = "report") -> Path:
        """Saves a dictionary to JSON in reports directory."""
        filename = f"{prefix}_{uuid.uuid4().hex[:8]}.json"
        out_path = settings.REPORTS_DIR / filename
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Exported JSON to {out_path}")
        return out_path

    @classmethod
    def generate_inventory_csv(cls, recommendations: List[Dict[str, Any]]) -> Path:
        """Exports inventory recommendations list to CSV."""
        df = pd.DataFrame(recommendations)
        return cls.export_dataframe_to_csv(df, prefix="inventory_recommendations")

    @classmethod
    def generate_forecast_csv(cls, forecast_points: List[Dict[str, Any]]) -> Path:
        """Exports forecast points list to CSV."""
        df = pd.DataFrame(forecast_points)
        return cls.export_dataframe_to_csv(df, prefix="demand_forecast")


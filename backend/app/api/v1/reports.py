import os
import re
from pathlib import Path
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.app.core.config import settings
from backend.app.core.logging import logger

router = APIRouter()

def is_safe_filename(filename: str) -> bool:
    """Ensures filename has no directory traversal."""
    if ".." in filename or "/" in filename or "\\" in filename:
        return False
    return bool(re.match(r"^[a-zA-Z0-9_\-\.]+\.(csv|json|pdf)$", filename))

@router.get("/download/{filename}")
def download_report(filename: str):
    """Safely downloads a generated report CSV or JSON file."""
    if not is_safe_filename(filename):
        raise HTTPException(status_code=400, detail="Invalid filename format.")

    file_path = settings.REPORTS_DIR / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Requested report file was not found.")

    media_type = "text/csv" if filename.endswith(".csv") else "application/json"
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type=media_type
    )

@router.get("")
def list_reports():
    """Lists all generated report files available for download."""
    reports = []
    if settings.REPORTS_DIR.exists():
        for p in sorted(settings.REPORTS_DIR.glob("*.*"), key=lambda f: f.stat().st_mtime, reverse=True):
            if p.name == ".gitkeep":
                continue
            reports.append({
                "filename": p.name,
                "size_bytes": p.stat().st_size,
                "modified_time": p.stat().st_mtime,
                "type": p.suffix.replace(".", "").upper(),
                "download_url": f"/api/v1/reports/download/{p.name}"
            })
    return {"reports": reports}


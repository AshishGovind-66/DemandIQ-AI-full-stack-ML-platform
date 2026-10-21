import os
import re
import uuid
from pathlib import Path
from typing import List, Optional
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.database.session import get_db
from backend.app.models.db_models import DatasetModel
from backend.app.schemas.dataset import (
    DatasetResponse,
    ValidationResult,
    ColumnMappingConfig,
    DataProfilingReport,
    M5SubsetRequest
)
from backend.app.preprocessing.validator import DatasetValidator
from backend.app.preprocessing.column_mapper import ColumnMapper
from backend.app.preprocessing.m5_loader import M5DataLoader
from backend.app.services.eda_service import EDAService

router = APIRouter()

def sanitize_filename(filename: str) -> str:
    """Sanitizes filename and prevents directory traversal attacks."""
    basename = os.path.basename(filename)
    safe = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", basename)
    return safe or "uploaded_data.csv"

def seed_sample_dataset_if_empty(db: Session):
    """Proactively ensures the synthetic retail sample is available on first run."""
    count = db.query(DatasetModel).count()
    sample_file = settings.DATA_SAMPLE_DIR / "retail_sales_sample.csv"
    if count == 0 and sample_file.exists():
        try:
            df = pd.read_csv(sample_file)
            dataset = DatasetModel(
                id="sample-retail-dataset",
                name="Retail Sales Demo (Beverages & Grocery)",
                filename="retail_sales_sample.csv",
                file_path=str(sample_file),
                file_type="sample_csv",
                file_size_bytes=sample_file.stat().st_size,
                row_count=len(df),
                column_count=len(df.columns),
                columns_json=df.columns.tolist(),
                column_mapping={
                    "date_col": "date",
                    "target_col": "sales",
                    "product_id_col": "product_id",
                    "store_id_col": "store_id",
                    "category_col": "category",
                    "price_col": "sell_price",
                    "promo_col": "on_promotion"
                },
                summary_metrics={
                    "total_sales": float(df["sales"].sum()),
                    "products": int(df["product_id"].nunique())
                }
            )
            db.add(dataset)
            db.commit()
            logger.info("Auto-registered sample retail dataset.")
        except Exception as e:
            logger.error(f"Failed to auto-seed sample dataset: {e}")

@router.get("", response_model=List[DatasetResponse])
def list_datasets(db: Session = Depends(get_db)):
    """Lists all available datasets."""
    seed_sample_dataset_if_empty(db)
    datasets = db.query(DatasetModel).filter(DatasetModel.is_active == True).order_by(DatasetModel.created_at.desc()).all()
    return [
        DatasetResponse(
            id=d.id,
            name=d.name,
            filename=d.filename,
            file_type=d.file_type or "csv",
            file_size_bytes=d.file_size_bytes or 0,
            row_count=d.row_count or 0,
            column_count=d.column_count or 0,
            columns=d.columns_json or [],
            column_mapping=d.column_mapping or {},
            created_at=d.created_at.isoformat() if d.created_at else ""
        )
        for d in datasets
    ]

@router.post("/upload", response_model=DatasetResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    dataset_name: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Uploads and profiles an arbitrary retail sales CSV file."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files (.csv) are currently supported.")

    safe_name = sanitize_filename(file.filename)
    unique_id = str(uuid.uuid4())
    stored_filename = f"{unique_id}_{safe_name}"
    save_path = settings.DATA_RAW_DIR / stored_filename

    # Read contents with size check
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File exceeds maximum upload limit of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB.")

    with open(save_path, "wb") as f:
        f.write(contents)

    try:
        df = pd.read_csv(save_path)
    except Exception as e:
        if save_path.exists():
            save_path.unlink()
        raise HTTPException(status_code=400, detail=f"Could not parse uploaded CSV: {str(e)}")

    # Auto detect column mapping
    columns = df.columns.tolist()
    auto_mapping = ColumnMapper.auto_detect_mapping(columns)

    display_name = dataset_name or safe_name.replace(".csv", "").replace("_", " ").title()
    dataset = DatasetModel(
        id=unique_id,
        name=display_name,
        filename=safe_name,
        file_path=str(save_path),
        file_type="user_csv",
        file_size_bytes=len(contents),
        row_count=len(df),
        column_count=len(columns),
        columns_json=columns,
        column_mapping=auto_mapping.dict(),
        summary_metrics={"total_rows": len(df)}
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return DatasetResponse(
        id=dataset.id,
        name=dataset.name,
        filename=dataset.filename,
        file_type=dataset.file_type,
        file_size_bytes=dataset.file_size_bytes,
        row_count=dataset.row_count,
        column_count=dataset.column_count,
        columns=dataset.columns_json,
        column_mapping=dataset.column_mapping,
        created_at=dataset.created_at.isoformat()
    )

@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Retrieves dataset metadata."""
    dataset = db.query(DatasetModel).filter(DatasetModel.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return DatasetResponse(
        id=dataset.id,
        name=dataset.name,
        filename=dataset.filename,
        file_type=dataset.file_type,
        file_size_bytes=dataset.file_size_bytes,
        row_count=dataset.row_count,
        column_count=dataset.column_count,
        columns=dataset.columns_json or [],
        column_mapping=dataset.column_mapping or {},
        created_at=dataset.created_at.isoformat() if dataset.created_at else ""
    )

@router.get("/{dataset_id}/preview")
def preview_dataset(dataset_id: str, limit: int = 50, db: Session = Depends(get_db)):
    """Returns top rows of dataset for UI preview."""
    dataset = db.query(DatasetModel).filter(DatasetModel.id == dataset_id).first()
    if not dataset or not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="Dataset file not found")
    try:
        df = pd.read_csv(dataset.file_path, nrows=limit)
        return {
            "dataset_id": dataset.id,
            "columns": df.columns.tolist(),
            "rows": df.fillna("").to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read dataset preview: {str(e)}")

@router.post("/{dataset_id}/validate", response_model=ValidationResult)
def validate_dataset(
    dataset_id: str,
    mapping: Optional[ColumnMappingConfig] = None,
    db: Session = Depends(get_db)
):
    """Runs data quality validation and compatibility checks."""
    dataset = db.query(DatasetModel).filter(DatasetModel.id == dataset_id).first()
    if not dataset or not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="Dataset file not found")

    df = pd.read_csv(dataset.file_path, nrows=5000)
    cfg = mapping or ColumnMappingConfig(**(dataset.column_mapping or {}))
    return DatasetValidator.validate_dataframe(df, mapping=cfg)

@router.post("/{dataset_id}/map-columns", response_model=DatasetResponse)
def update_column_mapping(
    dataset_id: str,
    mapping: ColumnMappingConfig,
    db: Session = Depends(get_db)
):
    """Updates column mapping and creates standardized canonical copy."""
    dataset = db.query(DatasetModel).filter(DatasetModel.id == dataset_id).first()
    if not dataset or not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="Dataset file not found")

    df = pd.read_csv(dataset.file_path)
    clean_df = ColumnMapper.apply_mapping(df, mapping)
    
    # Save canonical processed dataset
    processed_path = settings.DATA_PROCESSED_DIR / f"canonical_{dataset.id}.csv"
    clean_df.to_csv(processed_path, index=False)

    dataset.column_mapping = mapping.dict()
    dataset.file_path = str(processed_path)  # Point to canonical file
    dataset.row_count = len(clean_df)
    dataset.columns_json = clean_df.columns.tolist()
    db.commit()

    return DatasetResponse(
        id=dataset.id,
        name=dataset.name,
        filename=dataset.filename,
        file_type=dataset.file_type,
        file_size_bytes=dataset.file_size_bytes,
        row_count=dataset.row_count,
        column_count=dataset.column_count,
        columns=dataset.columns_json,
        column_mapping=dataset.column_mapping,
        created_at=dataset.created_at.isoformat() if dataset.created_at else ""
    )

@router.get("/{dataset_id}/profile", response_model=DataProfilingReport)
def profile_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Performs full exploratory data analysis (EDA) profiling report."""
    dataset = db.query(DatasetModel).filter(DatasetModel.id == dataset_id).first()
    if not dataset or not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="Dataset file not found")

    raw_df = pd.read_csv(dataset.file_path)
    # Check if raw_df is already in canonical format
    if "date" in raw_df.columns and "sales" in raw_df.columns:
        canonical_df = raw_df
    else:
        mapping = ColumnMappingConfig(**(dataset.column_mapping or {}))
        canonical_df = ColumnMapper.apply_mapping(raw_df, mapping)

    return EDAService.profile_dataset(canonical_df, dataset_id=dataset.id, dataset_name=dataset.name)

@router.post("/m5/extract", response_model=DatasetResponse)
def extract_m5_subset(
    request: M5SubsetRequest,
    db: Session = Depends(get_db)
):
    """Extracts a manageable subset from Walmart M5 dataset and registers it."""
    m5_status = M5DataLoader.get_status()
    if not m5_status["all_core_present"]:
        raise HTTPException(status_code=400, detail="Walmart M5 raw files not found on disk.")

    subset_id = str(uuid.uuid4())
    filename = f"m5_subset_{subset_id[:8]}.csv"
    
    try:
        clean_df = M5DataLoader.extract_subset(
            store_ids=request.store_ids,
            item_limit=min(request.item_limit or 20, 50),
            days_limit=min(request.days_limit or 365, 730),
            output_filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract M5 subset: {str(e)}")

    save_path = settings.DATA_PROCESSED_DIR / filename
    stores_str = ", ".join(request.store_ids or ["CA_1"])
    dataset = DatasetModel(
        id=subset_id,
        name=f"Walmart M5 Subset ({stores_str} - {request.item_limit} items)",
        filename=filename,
        file_path=str(save_path),
        file_type="m5_walmart",
        file_size_bytes=save_path.stat().st_size,
        row_count=len(clean_df),
        column_count=len(clean_df.columns),
        columns_json=clean_df.columns.tolist(),
        column_mapping={
            "date_col": "date",
            "target_col": "sales",
            "product_id_col": "product_id",
            "store_id_col": "store_id",
            "category_col": "category",
            "price_col": "sell_price",
            "promo_col": "on_promotion"
        },
        summary_metrics={
            "total_sales": float(clean_df["sales"].sum()),
            "items_count": int(clean_df["product_id"].nunique())
        }
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return DatasetResponse(
        id=dataset.id,
        name=dataset.name,
        filename=dataset.filename,
        file_type=dataset.file_type,
        file_size_bytes=dataset.file_size_bytes,
        row_count=dataset.row_count,
        column_count=dataset.column_count,
        columns=dataset.columns_json,
        column_mapping=dataset.column_mapping,
        created_at=dataset.created_at.isoformat()
    )


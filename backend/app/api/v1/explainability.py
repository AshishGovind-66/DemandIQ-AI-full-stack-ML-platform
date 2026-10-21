import os
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.db_models import TrainedModelRecord, DatasetModel
from backend.app.schemas.explainability import ShapExplanationRequest, ShapExplanationResponse
from backend.app.schemas.dataset import ColumnMappingConfig
from backend.app.preprocessing.column_mapper import ColumnMapper
from backend.app.explainability.shap_explainer import ShapExplainerService

router = APIRouter()

@router.post("/shap", response_model=ShapExplanationResponse)
def compute_shap_explanations(
    request: ShapExplanationRequest,
    db: Session = Depends(get_db)
):
    """Calculates SHAP feature attributions and driver importance for a trained model."""
    model_rec = db.query(TrainedModelRecord).filter(TrainedModelRecord.id == request.model_id).first()
    if not model_rec or not os.path.exists(model_rec.artifact_path):
        raise HTTPException(status_code=404, detail="Model artifact not found.")

    dataset = db.query(DatasetModel).filter(DatasetModel.id == model_rec.dataset_id).first()
    if not dataset or not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="Dataset file not found.")

    raw_df = pd.read_csv(dataset.file_path)
    if "date" in raw_df.columns and "sales" in raw_df.columns:
        canonical_df = raw_df
    else:
        mapping = ColumnMappingConfig(**(dataset.column_mapping or {}))
        canonical_df = ColumnMapper.apply_mapping(raw_df, mapping)

    response = ShapExplainerService.explain(
        artifact_path=model_rec.artifact_path,
        sample_df=canonical_df,
        sample_size=request.sample_size,
        product_id=request.product_id
    )

    return response


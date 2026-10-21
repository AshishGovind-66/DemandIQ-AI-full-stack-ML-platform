import os
import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

# Ensure backend root is on sys.path
TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.config import settings
from backend.app.database.session import SessionLocal, init_db, Base, engine
from backend.app.main import app
from fastapi.testclient import TestClient

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Initializes tables for test session."""
    init_db()
    yield

@pytest.fixture
def db_session():
    """Provides an isolated database session per test."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def sample_sales_df():
    """Small synthetic retail sales DataFrame for unit testing."""
    dates = pd.date_range("2023-01-01", periods=60, freq="D")
    records = []
    for d in dates:
        for p in ["SKU_1", "SKU_2"]:
            records.append({
                "date": d.strftime("%Y-%m-%d"),
                "product_id": p,
                "store_id": "STORE_1",
                "category": "Food",
                "sales": 10 + (2 if p == "SKU_2" else 0) + (d.dayofweek % 3),
                "sell_price": 4.99,
                "on_promotion": 1 if d.dayofweek == 5 else 0
            })
    return pd.DataFrame(records)


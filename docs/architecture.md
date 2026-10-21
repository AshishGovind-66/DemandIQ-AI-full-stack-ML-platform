# DemandIQ AI — System Architecture & Component Interaction

## 1. System Overview

DemandIQ AI is a modular, production-ready machine learning platform designed for retail demand forecasting and inventory replenishment optimization.

```
+------------------------------------------------------------------------+
|                      Next.js 16 (App Router + Tailwind)                 |
|  - Dashboard Overview         - Dataset Hub & Schema Mapper            |
|  - Exploratory Data Analysis  - Model Training & Leaderboard           |
|  - Multi-Step Forecasts       - Inventory Policy Optimization Engine    |
|  - Explainable AI (SHAP)      - Export Center & System Diagnostics      |
+-----------------------------------+------------------------------------+
                                    | REST API Calls (Fetch / CORS)
                                    v
+------------------------------------------------------------------------+
|                      FastAPI Backend Service (Python 3)                |
|  - /health                   - /api/v1/datasets                        |
|  - /api/v1/models            - /api/v1/forecasts                       |
|  - /api/v1/inventory         - /api/v1/explainability                  |
|  - /api/v1/reports           - /api/v1/dashboard                       |
+--------+--------------------------+---------------------+--------------+
         |                          |                     |
         v                          v                     v
+------------------+     +-------------------+   +-----------------------+
|  Database Layer  |     |  ML Pipeline Core |   | Storage Subsystem     |
| - SQLite (Local) |     | - FeatureEngine   |   | - data/raw (CSVs)     |
| - Supabase /     |     | - ModelRegistry   |   | - data/processed      |
|   PostgreSQL     |     | - Backtester      |   | - models/*.joblib     |
|   (Production)   |     | - SHAP Explainer  |   | - reports/*.csv       |
+------------------+     +-------------------+   +-----------------------+
```

## 2. Component Breakdown

### Frontend (Next.js 16 + React 19 + TypeScript + Tailwind CSS)
- **App Router Architecture:** Modular routes under `frontend/src/app/` (`/dashboard`, `/datasets`, `/eda`, `/training`, `/models`, `/forecasts`, `/inventory`, `/explainability`, `/reports`, `/settings`).
- **Interactive Visualizations:** Powered by `recharts` for time-series composed actual vs predicted intervals, bar charts for weekly seasonality and feature importances.
- **Centralized API Client (`frontend/src/lib/api.ts`):** Strictly typed fetch wrapper with `NEXT_PUBLIC_API_URL` configuration.

### Backend (FastAPI + Pydantic v2 + SQLAlchemy 2.0)
- **Modular Routers (`backend/app/api/v1/`):** Clean separation of concerns across health, dataset management, background training jobs, forecasts, and inventory policies.
- **Background Job Manager (`backend/app/services/job_manager.py`):** Enables non-blocking asynchronous model training with live percentage progress tracking.
- **Database Abstraction (`backend/app/database/`):** Connects to PostgreSQL (e.g. Supabase) or falls back dynamically to SQLite (`demandiq.db`) with zero external infrastructure required.

### Machine Learning & Preprocessing Core (`backend/app/preprocessing/` & `backend/app/forecasting/`)
- **Leakage-Free Feature Engineering:** Strictly chronological shifts and expanding windows. Rolling features at time $t$ use observations strictly $\le t-1$.
- **Model Registry:** Pluggable forecasters implementing `BaseForecaster`:
  - `NaiveForecaster` (lag 1 baseline)
  - `SeasonalNaiveForecaster` (lag 7 weekly baseline)
  - `LinearRegressionForecaster` (L2 Ridge)
  - `RandomForestForecaster` (Bagging ensemble)
  - `XGBoostForecaster` (Histogram gradient boosting)
  - `LightGBMForecaster` (Fast histogram boosting)
- **Artifact Serialization:** Joblib bundles model weights, fitted encoders, and validation metadata into versioned `.joblib` files in `models/`.

### Inventory Optimization Engine (`backend/app/inventory/optimization_engine.py`)
- Calculates Lead-Time Demand (LTD), Safety Stock (SS) with Normal/empirical quantile z-factors, dynamic Reorder Points (ROP), and suggests optimal procurement batches under Minimum Order Quantity (MOQ) and Pack-Size constraints.


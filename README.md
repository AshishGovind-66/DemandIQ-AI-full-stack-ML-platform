# DemandIQ AI

> **Forecast Smarter. Stock Smarter. Grow Better.**
> 
> *An AI-Powered Demand Forecasting and Inventory Optimization System for Retail Businesses.*

---

## 🌟 Executive Overview

**DemandIQ AI** is a reusable, enterprise-grade machine learning platform engineered to help retailers predict future product demand, quantify forecast uncertainty, prevent costly stockouts, and optimize inventory replenishment decisions.

The platform natively supports the **Walmart M5 forecasting competition dataset** while offering configurable preprocessing and schema mapping for any arbitrary retail sales CSV upload.

### Key Capabilities

- **Leakage-Free ML Forecasting:** Strict chronological time-series splitting (train, validation, out-of-sample test) with rolling multi-step recursive forecasting.
- **Model Benchmark Leaderboard:** Automated side-by-side comparison of **Naive**, **Seasonal Naive**, **Ridge Regression**, **Random Forest**, **XGBoost**, and **LightGBM** evaluated on Weighted Absolute Percentage Error (WAPE), MAE, RMSE, and Forecast Bias.
- **Inventory Optimization Engine:** Mathematical calculation of **Safety Stock (SS)**, **Reorder Points (ROP)**, **Target Stock Levels**, and **Suggested Replenishment Orders** under configurable lead times, cycle service levels (90%–99%), Minimum Order Quantities (MOQ), and pack-size constraints.
- **Explainable AI (SHAP):** Transparent attribution of demand drivers (promotions, price elasticity, day-of-week seasonality, lag effects) using Tree and Linear SHAP explainers.
- **Zero-Friction Local Development:** Runs out-of-the-box using the existing Python installation and an automatic SQLite fallback, with production readiness for PostgreSQL and Supabase.

---

## 🏗️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Next.js 16 (App Router), TypeScript, Tailwind CSS, Recharts, Lucide Icons |
| **Backend** | Python 3, FastAPI, Pydantic v2, SQLAlchemy 2.0, Uvicorn |
| **Machine Learning** | Scikit-learn, XGBoost, LightGBM, Statsmodels, SHAP, Joblib, SciPy |
| **Database** | SQLite (zero-config local fallback) / PostgreSQL (Supabase compatible) |
| **Deployment Targets** | Frontend: Vercel \| Backend: Railway \| Database: Supabase PostgreSQL |

---

## 📁 Monorepo Project Structure

```
DemandIQ-AI/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint & lifecycle
│   │   ├── core/                    # Config, paths, structured logging
│   │   ├── api/v1/                  # Endpoints (health, datasets, models, forecasts, inventory, SHAP)
│   │   ├── schemas/                 # Pydantic request & response models
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   ├── services/                # Background job manager, EDA service
│   │   ├── preprocessing/           # Column mapper, M5 loader, validator, feature engineer
│   │   ├── forecasting/             # Model registry, baselines, ML models, trainer, predictor
│   │   ├── inventory/               # Safety stock, ROP, order-up-to optimization engine
│   │   ├── explainability/          # SHAP explainer & driver narratives
│   │   ├── reporting/               # CSV & JSON report export services
│   │   └── database/                # Database engine & session management
│   ├── tests/                       # 27 automated unit and integration tests
│   ├── requirements.txt             # Backend dependencies
│   ├── Dockerfile                   # Production Docker image
│   └── pytest.ini                   # Test configuration
│
├── frontend/
│   ├── src/
│   │   ├── app/                     # Next.js App Router pages (/dashboard, /datasets, /eda, etc.)
│   │   ├── components/              # Layout, Sidebar, Header, MetricCard, StatusBadge
│   │   ├── lib/                     # Centralized API client (api.ts)
│   │   └── types/                   # TypeScript interfaces
│   ├── package.json                 # Frontend dependencies
│   └── tsconfig.json                # TypeScript compiler config
│
├── data/
│   ├── raw/                         # Raw CSV datasets
│   ├── processed/                   # Standardized canonical datasets
│   └── sample/                      # Bundled retail sample dataset
│
├── notebooks/                       # 7 End-to-end Jupyter analysis notebooks
│   ├── 01_data_inspection.ipynb
│   ├── 02_exploratory_data_analysis.ipynb
│   ├── 03_preprocessing_and_features.ipynb
│   ├── 04_baseline_forecasting.ipynb
│   ├── 05_model_training.ipynb
│   ├── 06_model_evaluation.ipynb
│   └── 07_inventory_optimization.ipynb
│
├── models/                          # Serialized .joblib model artifacts
├── reports/                         # Generated CSV and JSON report exports
├── scripts/                         # Utility scripts
├── docs/                            # architecture.md, methodology.md, dataset_setup.md
├── docker-compose.yml               # Container orchestration
└── requirements.txt                 # Root Python dependencies
```

---

## 🚀 Quickstart Guide (Windows PowerShell)

> **Important Note:** DemandIQ AI uses your existing Python installation directly. **No virtual environment (`venv`, `.venv`, Conda) is required or created.**

### 1. Prerequisites
- **Python 3.10+** (verified on Python 3.14.0)
- **Node.js 18+** & **npm** (verified on Node v24.19.0)

### 2. Verify / Install Python Dependencies
```powershell
python -m pip install -r requirements.txt
```

### 3. Run Automated Test Suite
Verify that all 27 unit and integration tests pass:
```powershell
python -m pytest backend/tests -v
```

### 4. Start the FastAPI Backend Server
From the root workspace directory:
```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Backend API URL:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive OpenAPI Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Endpoint:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 5. Start the Next.js Frontend
Open a separate PowerShell terminal window:
```powershell
cd frontend
npm run dev
```
- **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000)

---

## 📊 End-to-End Application Workflow

```
1. Upload / Select Dataset  ──>  2. Schema Mapping & Validation  ──>  3. Exploratory Data Analysis
                                                                               │
7. Export CSV Reports       <──  6. Inventory Optimization Engine <──  5. Multi-Step Forecasting <──  4. Model Training & Comparison
                                 (Safety Stock, ROP, Order Qty)        (7, 14, 30-day horizons)      (Naive, Ridge, XGBoost, LGBM)
```

1. **Dataset Hub (`/datasets`):** Upload any retail CSV or click **"Extract M5 Subset"** to extract a memory-conscious slice of the Walmart M5 dataset. Validate schema integrity with automatic column mapping.
2. **Exploratory Analysis (`/eda`):** Inspect empirical daily trends, day-of-week seasonality, top-selling SKUs, and distribution metrics.
3. **Model Training (`/training`):** Configure candidate models and forecast horizons. An asynchronous background worker executes chronological train/val splits and feature engineering without blocking the UI.
4. **Model Leaderboard (`/models`):** Compare models on test-set **WAPE**, **MAE**, **RMSE**, and **Forecast Bias**.
5. **Demand Forecasts (`/forecasts`):** Generate multi-step forward trajectories with empirical prediction intervals (90%, 95%, 99%).
6. **Inventory Optimization (`/inventory`):** Calculate safety stock, reorder points, and suggested order quantities accounting for MOQ and pack sizes. Identify items at stockout risk or excess inventory.
7. **Explainable AI (`/explainability`):** Understand statistical drivers of demand with SHAP feature attributions.
8. **Reports & Exports (`/reports`):** Download generated CSV files of forecasts and inventory replenishment recommendations.

---

## 📐 Inventory Optimization Formulas

DemandIQ AI calculates replenishment decisions using classical supply chain inventory theory:

| Metric | Formula | Description |
|---|---|---|
| **Expected Lead-Time Demand (LTD)** | $\text{LTD} = \mu_D \cdot L$ | Forecasted daily demand $\mu_D$ multiplied by lead time $L$. |
| **Safety Stock (SS)** | $\text{SS} = z \cdot \sigma_D \cdot \sqrt{L}$ | Buffer stock covering demand volatility $\sigma_D$ for target service level $z$. |
| **Reorder Point (ROP)** | $\text{ROP} = \text{LTD} + \text{SS}$ | Inventory threshold triggering a new procurement order. |
| **Order-Up-To Target ($S$)** | $S = \mu_D \cdot (L + R) + z \cdot \sigma_D \cdot \sqrt{L + R}$ | Protection period covering Lead Time $L$ plus Review Period $R$. |
| **Suggested Order Qty** | $\text{Order} = \max(0, S - \text{Inventory Position})$ | Replenishment quantity constrained by Minimum Order Qty (MOQ) and pack size multiples. |

---

## 🚢 Deployment Preparation

### Frontend Deployment (Vercel)
1. Push repository to GitHub.
2. Import project into Vercel and set the **Root Directory** to `frontend`.
3. Configure environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-railway-url.railway.app
   ```
4. Deploy!

### Backend Deployment (Railway)
1. Connect repository to Railway.
2. Set the Dockerfile path to `backend/Dockerfile` or configure the start command:
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
   ```
3. Set environment variables:
   ```
   ENVIRONMENT=production
   DEBUG=False
   DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/[DB]
   CORS_ORIGINS=https://your-frontend-vercel-domain.vercel.app
   ```

### Database (Supabase PostgreSQL)
1. Create a free Supabase project.
2. Copy the Connection Pooling URI (`postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`).
3. Set `DATABASE_URL` in Railway or `.env`. The backend automatically initializes all tables on startup.

---

## 💼 Resume & Interview Project Description

> **DemandIQ AI — Full-Stack AI Demand Forecasting & Inventory Optimization Platform**
> - Architected a production-ready machine learning platform with **FastAPI**, **Next.js 16**, and **SQLAlchemy**, supporting both Walmart M5 benchmarks and custom retail CSV uploads.
> - Implemented leakage-free chronological feature engineering (cyclical calendar features, multi-step lags, rolling window statistics) and evaluated **LightGBM**, **XGBoost**, and **Ridge** models against naive seasonal baselines.
> - Engineered an inventory replenishment optimization engine calculating **Safety Stock**, **Reorder Points (ROP)**, and **Order-Up-To quantities** under stochastic lead-time demand, MOQ, and pack-size constraints.
> - Integrated **SHAP (Shapley Additive exPlanations)** to provide transparent global and local demand driver attributions.
> - Authored 27 automated unit and integration tests covering zero-denominator WAPE, temporal splits, and inventory policies with 100% pass rate.

---

## 📄 License
This project is open-source under the MIT License.


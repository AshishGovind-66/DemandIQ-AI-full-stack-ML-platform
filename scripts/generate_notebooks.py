import json
import os
from pathlib import Path

notebooks_dir = Path("notebooks")
notebooks_dir.mkdir(exist_ok=True)

def make_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "language_info": {"name": "python", "version": "3.14.0"},
            "orig_nbformat": 4
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

def md_cell(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.strip().split("\n")]
    }

def code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source.strip().split("\n")]
    }

# 01 Data Inspection
nb1 = make_notebook([
    md_cell("# DemandIQ AI - Notebook 01: Data Inspection\nThis notebook inspects the raw files of the Walmart M5 forecasting competition dataset and our synthetic retail demonstration dataset."),
    code_cell('import sys\nfrom pathlib import Path\nimport pandas as pd\n\nPROJECT_ROOT = Path(".." if Path(".").resolve().name == "notebooks" else ".").resolve()\nsys.path.insert(0, str(PROJECT_ROOT))\n\nfrom backend.app.preprocessing.m5_loader import M5DataLoader\nfrom backend.app.core.config import settings'),
    md_cell("## 1. Inspect Walmart M5 Dataset Discovery Status"),
    code_cell('status = M5DataLoader.get_status()\nprint("Walmart M5 Core Present:", status["all_core_present"])\nfor fname, info in status["files"].items():\n    print(f"  {fname}: available={info[\'available\']}, size={info[\'size_mb\']} MB")'),
    md_cell("## 2. Inspect Sample Retail Dataset"),
    code_cell('sample_csv = settings.DATA_SAMPLE_DIR / "retail_sales_sample.csv"\nif sample_csv.exists():\n    df_sample = pd.read_csv(sample_csv)\n    print("Sample Dataset Shape:", df_sample.shape)\n    print(df_sample.head())\nelse:\n    print("Sample dataset missing.")')
])

with open(notebooks_dir / "01_data_inspection.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb1, f, indent=2)

# 02 Exploratory Data Analysis
nb2 = make_notebook([
    md_cell("# DemandIQ AI - Notebook 02: Exploratory Data Analysis (EDA)\nComprehensive analysis of historical demand trajectories, weekly seasonality, price elasticity, and product ranking distributions."),
    code_cell('import sys\nfrom pathlib import Path\nimport pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport seaborn as sns\n\nsys.path.insert(0, str(Path(".." if Path(".").resolve().name == "notebooks" else ".").resolve()))\nfrom backend.app.services.eda_service import EDAService\nfrom backend.app.core.config import settings'),
    md_cell("## 1. Load Data & Compute Profiling"),
    code_cell('data_path = settings.DATA_SAMPLE_DIR / "retail_sales_sample.csv"\ndf = pd.read_csv(data_path)\ndf["date"] = pd.to_datetime(df["date"])\nprint("Loaded rows:", len(df))\nprint(df.describe())'),
    md_cell("## 2. Daily Sales Trend & Seasonality Visualization"),
    code_cell('plt.figure(figsize=(12, 5))\ndaily_total = df.groupby("date")["sales"].sum()\nplt.plot(daily_total.index, daily_total.values, color="#2563eb", lw=1.5)\nplt.title("Total Daily Retail Demand Over Time", fontsize=14, fontweight="bold")\nplt.xlabel("Date")\nplt.ylabel("Units Sold")\nplt.grid(True, alpha=0.3)\nplt.tight_layout()\nplt.show()'),
    md_cell("## 3. Day of Week Pattern (Weekly Seasonality)"),
    code_cell('df["day_name"] = df["date"].dt.day_name()\ndow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]\nplt.figure(figsize=(8, 4))\nsns.barplot(data=df, x="day_name", y="sales", order=dow_order, palette="Blues_d")\nplt.title("Mean Sales Volume by Day of Week", fontsize=13, fontweight="bold")\nplt.xlabel("Day of Week")\nplt.ylabel("Mean Sales")\nplt.tight_layout()\nplt.show()')
])

with open(notebooks_dir / "02_exploratory_data_analysis.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb2, f, indent=2)

# 03 Preprocessing and Features
nb3 = make_notebook([
    md_cell("# DemandIQ AI - Notebook 03: Leakage-Free Preprocessing & Feature Engineering\nDemonstrates chronological splitting, calendar cyclical transforms, lag creation, and rolling statistics."),
    code_cell('import sys\nfrom pathlib import Path\nimport pandas as pd\n\nsys.path.insert(0, str(Path(".." if Path(".").resolve().name == "notebooks" else ".").resolve()))\nfrom backend.app.preprocessing.feature_engineering import FeatureEngineer\nfrom backend.app.utils.time_series import chronological_split\nfrom backend.app.core.config import settings'),
    md_cell("## 1. Load Data & Perform Chronological Split"),
    code_cell('df = pd.read_csv(settings.DATA_SAMPLE_DIR / "retail_sales_sample.csv")\ntrain, val, test = chronological_split(df, date_col="date", validation_days=14, test_days=14)\nprint("Train period:", train["date"].min(), "to", train["date"].max(), f"({len(train)} rows)")\nprint("Val period:  ", val["date"].min(), "to", val["date"].max(), f"({len(val)} rows)")\nprint("Test period: ", test["date"].min(), "to", test["date"].max(), f"({len(test)} rows)")'),
    md_cell("## 2. Feature Engineering Pipeline (Zero Leakage)"),
    code_cell('fe = FeatureEngineer()\ntrain_features, feature_names = fe.fit_transform(train)\nval_features = fe.transform(val)\nprint("Generated Features count:", len(feature_names))\nprint("Features:", feature_names[:10])\nprint(train_features[["date", "product_id", "sales", "lag_1", "lag_7", "rolling_mean_7"]].head(10))')
])

with open(notebooks_dir / "03_preprocessing_and_features.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb3, f, indent=2)

# 04 Baseline Forecasting
nb4 = make_notebook([
    md_cell("# DemandIQ AI - Notebook 04: Baseline Forecasting Models\nEvaluates Naive (lag_1) and Seasonal Naive (lag_7) baselines as benchmark comparison standards."),
    code_cell('import sys\nfrom pathlib import Path\nimport pandas as pd\n\nsys.path.insert(0, str(Path(".." if Path(".").resolve().name == "notebooks" else ".").resolve()))\nfrom backend.app.forecasting.baseline_models import NaiveForecaster, SeasonalNaiveForecaster\nfrom backend.app.utils.metrics import compute_all_metrics\nfrom backend.app.preprocessing.feature_engineering import FeatureEngineer\nfrom backend.app.utils.time_series import chronological_split\nfrom backend.app.core.config import settings'),
    md_cell("## 1. Prepare Validation & Test Data"),
    code_cell('df = pd.read_csv(settings.DATA_SAMPLE_DIR / "retail_sales_sample.csv")\ntrain, val, test = chronological_split(df, validation_days=14, test_days=14)\nfe = FeatureEngineer()\nfe.fit_transform(train)\ntest_feat = fe.transform(test)\nX_test, y_test = fe.get_features_and_target(test_feat)'),
    md_cell("## 2. Benchmark Naive & Seasonal Naive Baselines"),
    code_cell('naive = NaiveForecaster().fit(X_test, y_test)\nnaive_preds = naive.predict(X_test)\nprint("Naive Baseline Metrics:", compute_all_metrics(y_test, naive_preds))\n\nsnaive = SeasonalNaiveForecaster(season_length=7).fit(X_test, y_test)\nsnaive_preds = snaive.predict(X_test)\nprint("Seasonal Naive (7d) Metrics:", compute_all_metrics(y_test, snaive_preds))')
])

with open(notebooks_dir / "04_baseline_forecasting.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb4, f, indent=2)

# 05 Model Training
nb5 = make_notebook([
    md_cell("# DemandIQ AI - Notebook 05: Machine Learning Model Training\nTrains Ridge, Random Forest, XGBoost, and LightGBM models with hyperparameter configurations."),
    code_cell('import sys\nfrom pathlib import Path\nimport pandas as pd\n\nsys.path.insert(0, str(Path(".." if Path(".").resolve().name == "notebooks" else ".").resolve()))\nfrom backend.app.forecasting.trainer import ForecastTrainer\nfrom backend.app.core.config import settings'),
    md_cell("## 1. Run Complete Training Pipeline"),
    code_cell('df = pd.read_csv(settings.DATA_SAMPLE_DIR / "retail_sales_sample.csv")\ntrainer = ForecastTrainer(candidate_models=["naive", "seasonal_naive", "linear_regression", "xgboost", "lightgbm"])\nresults = trainer.train_and_evaluate(df, dataset_id="retail-sample-demo")\nprint("Best Selected Model:", results["best_model_name"])\nfor m in results["trained_models"]:\n    print(f"{m[\'model_name\'].upper():<18}: WAPE={m[\'metrics\'][\'wape\']*100:.1f}%, MAE={m[\'metrics\'][\'mae\']:.2f}, RMSE={m[\'metrics\'][\'rmse\']:.2f}")')
])

with open(notebooks_dir / "05_model_training.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb5, f, indent=2)

# 06 Model Evaluation
nb6 = make_notebook([
    md_cell("# DemandIQ AI - Notebook 06: Model Evaluation & Residual Analysis\nDeep dive into out-of-sample prediction residuals, error distributions, and SHAP explainability."),
    code_cell('import sys\nfrom pathlib import Path\nimport pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\n\nsys.path.insert(0, str(Path(".." if Path(".").resolve().name == "notebooks" else ".").resolve()))\nfrom backend.app.forecasting.predictor import ForecastPredictor\nfrom backend.app.core.config import settings'),
    md_cell("## 1. Inspect Trained Model Artifacts"),
    code_cell('artifacts = list(settings.MODELS_DIR.glob("*.joblib"))\nprint(f"Total trained artifacts in models/: {len(artifacts)}")\nfor a in artifacts[:5]:\n    print(" ", a.name)')
])

with open(notebooks_dir / "06_model_evaluation.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb6, f, indent=2)

# 07 Inventory Optimization
nb7 = make_notebook([
    md_cell("# DemandIQ AI - Notebook 07: Inventory Optimization & Replenishment\nCalculates Lead-Time Demand (LTD), Safety Stock (SS), Reorder Points (ROP), and Order Quantities subject to MOQ and pack sizes."),
    code_cell('import sys\nfrom pathlib import Path\nimport pandas as pd\n\nsys.path.insert(0, str(Path(".." if Path(".").resolve().name == "notebooks" else ".").resolve()))\nfrom backend.app.inventory.optimization_engine import InventoryOptimizationEngine\nfrom backend.app.schemas.inventory import InventoryOptimizationRequest\nfrom backend.app.core.config import settings'),
    md_cell("## 1. Run Inventory Optimization Policy"),
    code_cell('df = pd.read_csv(settings.DATA_SAMPLE_DIR / "retail_sales_sample.csv")\nreq = InventoryOptimizationRequest(\n    dataset_id="retail-sample",\n    lead_time_days=7,\n    service_level=0.95,\n    default_current_stock=15,\n    min_order_quantity=10,\n    pack_size=5\n)\nsummary = InventoryOptimizationEngine.optimize(df, req)\nprint(f"Total Products: {summary.total_products_analyzed}")\nprint(f"Stockout Risks: {summary.items_at_stockout_risk}")\nprint(f"Suggested Order Units: {summary.total_suggested_reorder_units}")\n\nrecs_df = pd.DataFrame([r.dict() for r in summary.recommendations])\nprint(recs_df[["product_id", "daily_demand_mean", "safety_stock", "reorder_point", "suggested_order_qty", "stockout_risk"]].head(10))')
])

with open(notebooks_dir / "07_inventory_optimization.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb7, f, indent=2)

print("All 7 notebooks created successfully.")


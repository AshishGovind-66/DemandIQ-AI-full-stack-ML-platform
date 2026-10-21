# DemandIQ AI — Dataset Setup & Configuration Guide

DemandIQ AI supports both the Walmart M5 forecasting competition dataset and custom user-uploaded CSV retail datasets.

---

## 1. Walmart M5 Dataset Structure

The Walmart M5 dataset consists of hierarchical daily unit sales across Walmart stores in California (CA), Texas (TX), and Wisconsin (WI).

### Raw Files
- `calendar.csv`: Contains calendar dates, weekly identifiers (`wm_yr_wk`), event names, and SNAP eligibility flags (`snap_CA`, `snap_TX`, `snap_WI`).
- `sales_train_validation.csv`: Wide-format table containing 30,490 series and historical unit sales from day `d_1` to `d_1913`.
- `sell_prices.csv`: Contains historical weekly selling prices per store and product.
- `sales_train_evaluation.csv`: Full evaluation split extending through day `d_1941`.

### Discovery Order
The system automatically searches for M5 files across:
1. `data/raw/`
2. `m5-forecasting-accuracy/`
3. Root workspace directory

### Memory-Conscious Subsetting
To prevent high memory usage, DemandIQ AI implements `M5DataLoader.extract_subset()`:
- Filters specific store IDs (e.g. `CA_1`).
- Selects top $N$ products by sales volume (e.g. 15 to 50 items).
- Melts only recent historical windows (e.g. last 180 to 365 days).
- Automatically merges prices, events, and SNAP flags.
- Produces a canonical long-format CSV in `data/processed/`.

---

## 2. Custom User-Uploaded Datasets

DemandIQ AI accepts any standard retail sales CSV file.

### Required Core Columns
1. **Date Column:** Any standard date format (`YYYY-MM-DD`, `DD/MM/YYYY`, ISO 8601).
2. **Sales / Target Column:** Numeric quantity sold or demand volume. Negative demand (returns) will be clipped to 0.

### Optional Enrichment Columns
- **Product ID:** SKU or item identifier.
- **Store ID:** Store or warehouse identifier.
- **Category:** Merchandise department or product category.
- **Sell Price:** Selling unit price.
- **Promotion Flag:** Binary indicator (1 if on discount/promotion, 0 otherwise).

### Auto-Detection & Mapping
When a file is uploaded, the built-in `ColumnMapper` heuristically scans column headers to automatically detect column purposes. Users can verify or adjust the mappings in the **Datasets Hub** UI before training.


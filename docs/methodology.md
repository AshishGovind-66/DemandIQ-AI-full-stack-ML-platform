# DemandIQ AI — Forecasting & Inventory Optimization Methodology

This document details the mathematical, statistical, and engineering formulations utilized throughout DemandIQ AI.

---

## 1. Time-Series Splitting & Data Leakage Prevention

Standard random $k$-fold cross-validation is mathematically invalid for time-series forecasting because it permits future data points to predict past observations (temporal leakage).

DemandIQ AI enforces strict chronological partitioning:
1. **Training Set:** Chronological window from start date $T_0$ to $T_{\text{val\_start}} - 1$.
2. **Validation Set:** Chronological window of $V$ days from $T_{\text{val\_start}}$ to $T_{\text{test\_start}} - 1$. Used exclusively for hyperparameter tuning and model selection.
3. **Out-of-Sample Test Set:** The most recent $H$ days from $T_{\text{test\_start}}$ to $T_{\text{end}}$. Evaluated strictly once to estimate unbiased generalization error.

---

## 2. Feature Engineering

Features generated at timestamp $t$ strictly rely on data available at or before $t-1$:
- **Lags:** $y_{t-1}, y_{t-7}, y_{t-14}, y_{t-28}$.
- **Rolling Statistics:** Computed over shifted sales:
  $$\text{rolling\_mean}_w(t) = \frac{1}{w}\sum_{i=1}^w y_{t-i}$$
  $$\text{rolling\_std}_w(t) = \sqrt{\frac{1}{w-1}\sum_{i=1}^w (y_{t-i} - \text{rolling\_mean}_w(t))^2}$$
- **Cyclical Calendar Encodings:**
  $$\text{dow\_sin} = \sin\left(\frac{2\pi \cdot \text{day\_of\_week}}{7}\right), \quad \text{dow\_cos} = \cos\left(\frac{2\pi \cdot \text{day\_of\_week}}{7}\right)$$
  $$\text{month\_sin} = \sin\left(\frac{2\pi \cdot \text{month}}{12}\right), \quad \text{month\_cos} = \cos\left(\frac{2\pi \cdot \text{month}}{12}\right)$$

---

## 3. Forecast Evaluation Metrics

### Mean Absolute Error (MAE)
$$\text{MAE} = \frac{1}{N} \sum_{i=1}^N |y_i - \hat{y}_i|$$

### Root Mean Squared Error (RMSE)
$$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (y_i - \hat{y}_i)^2}$$

### Weighted Absolute Percentage Error (WAPE)
$$\text{WAPE} = \frac{\sum_{i=1}^N |y_i - \hat{y}_i|}{\sum_{i=1}^N y_i}$$
*Zero-Denominator Handling:* If $\sum y_i = 0$, WAPE returns $0.0$ if $\sum |y_i - \hat{y}_i| = 0$, and $1.0$ otherwise.

### Forecast Bias
$$\text{Bias} = \frac{\sum_{i=1}^N (\hat{y}_i - y_i)}{\sum_{i=1}^N y_i}$$
Positive bias denotes over-forecasting (excess inventory risk); negative bias denotes under-forecasting (stockout risk).

---

## 4. Inventory Optimization Engine

### Expected Lead-Time Demand (LTD)
$$\text{LTD} = \mu_D \cdot L$$
Where $\mu_D$ is the mean daily forecasted demand and $L$ is supplier lead time in days.

### Safety Stock (SS)
Under fixed lead time with independent daily demand variations:
$$\text{SS} = z \cdot \sigma_D \cdot \sqrt{L}$$
Where:
- $z$ is the standard normal quantile for the target Cycle Service Level (e.g., $z=1.6449$ for 95% CSL).
- $\sigma_D$ is the empirical standard deviation of daily demand.

### Reorder Point (ROP)
$$\text{ROP} = \text{LTD} + \text{SS} = (\mu_D \cdot L) + (z \cdot \sigma_D \cdot \sqrt{L})$$

### Order-Up-To Target Stock ($S$)
For periodic review systems with review period $R$:
$$\text{Protection Period} = L + R$$
$$S = \mu_D \cdot (L + R) + z \cdot \sigma_D \cdot \sqrt{L + R}$$

### Replenishment Quantity & Constraints
$$\text{Inventory Position} = \text{Stock On Hand} + \text{Stock On Order} - \text{Backorders}$$
$$\text{Raw Order} = \begin{cases} \max(0, S - \text{Inventory Position}) & \text{if Inventory Position} \le \text{ROP} \\ 0 & \text{otherwise} \end{cases}$$

Subject to Minimum Order Quantity ($\text{MOQ}$) and Pack-Size ($P$):
$$\text{Order Qty} = \left\lceil \frac{\max(\text{Raw Order}, \text{MOQ})}{P} \right\rceil \cdot P$$


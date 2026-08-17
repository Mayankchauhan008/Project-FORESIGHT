# 📦 FORESIGHT — Demand & Inventory Intelligence

> A retail intelligence and decision-support dashboard built with Python, Streamlit, Pandas and Plotly.

## 🎯 Project Overview

FORESIGHT transforms retail sales and inventory data into actionable business decisions.

```text
Sales Data
    ↓
Data Cleaning & Standardization
    ↓
Demand Analysis
    ↓
Inventory Analysis
    ↓
Risk Scoring
    ↓
Decision Engine
    ↓
Interactive Dashboard
    ↓
Business Action
```

The system helps answer:

- Which SKUs need replenishment?
- Which products have inventory risk?
- Which products have excess stock?
- Which products should be monitored?
- How much inventory value is exposed?
- Which products require immediate action?

---

## 🚀 Main Features

### 📊 Sales Analytics
- Revenue analysis
- Sales quantity analysis
- SKU performance
- Sales trends
- Category/store/channel analysis when available

### 📈 Demand Forecast
- Historical demand analysis
- Demand trends
- Forecasting support
- Inventory planning

### 📦 Inventory Dashboard
- Current stock
- Reorder point
- Safety stock
- Inventory coverage
- SKU-level inventory position

### ⚠️ Risk Dashboard
Inventory is classified into:

| Risk | Meaning |
|---|---|
| 🔴 Critical | Severe shortage |
| 🟠 High | Below required inventory level |
| 🟡 Medium | Approaching reorder level |
| 🟢 Low | Healthy inventory |

### 🔎 Product Details
Provides individual SKU-level information including:
- Stock
- Demand
- Days of cover
- Reorder point
- Safety stock
- Risk score
- Inventory status

### 🎯 Decision Cockpit
The main operational decision-support page.

Decision categories:

```text
🔴 Reorder Now
🟡 Watch / Volatile
🟠 Markdown / Clear
🟢 Healthy
```

The cockpit includes:
- Category filter
- SKU filter
- Decision filter
- KPI cards
- Reorder priorities
- Demand coverage
- Inventory decision matrix
- Recommended actions
- CSV decision-queue export

---

# 🧠 Decision Logic

## 🔴 Reorder Now

A SKU becomes a reorder candidate when:

- Stock is zero, OR
- Stock is at/below reorder point, OR
- Inventory coverage is 7 days or less.

## 🟡 Watch / Volatile

A SKU is monitored when:

- Risk score is elevated,
- Coverage is relatively low, or
- Stock is approaching the reorder threshold.

## 🟠 Markdown / Clear

Markdown is deliberately conservative.

A SKU must have strong evidence of excess inventory:

```text
Stock > 3 × Reorder Point
AND
Days of Cover >= 120
```

This prevents high stock alone from classifying every SKU as excess inventory.

## 🟢 Healthy

SKUs that do not require immediate intervention are classified as healthy.

---

# 🏗️ Project Structure

```text
PROJECT-FORESIGHT/
│
├── dashboard/
│   ├── app.py
│   ├── dashboard_utils.py
│   │
│   └── pages/
│       ├── Executive_Summary.py
│       ├── Sales_Analytics.py
│       ├── Demand_Forecast.py
│       ├── Inventory_Dashboard.py
│       ├── Risk_Dashboard.py
│       ├── Product_Details.py
│       └── Decision_Cockpit.py
│
├── src/
│   ├── risk_scoring.py
│   ├── forecasting.py
│   └── ...
│
├── Data/
│   ├── raw/
│   ├── processed/
│   └── cleaned/
│
├── notebooks/
│   ├── 01_Data_Loading.ipynb
│   ├── 02_Data_Cleaning.ipynb
│   ├── 03_EDA.ipynb
│   ├── 04_Feature_Engineering.ipynb
│   └── ...
│
├── requirements.txt
├── README.md
└── .gitignore
```

> Adjust filenames/folders if your final repository uses different names.

---

# 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming |
| Streamlit | Interactive web dashboard |
| Pandas | Data processing |
| NumPy | Numerical calculations |
| Plotly | Interactive visualizations |
| Scikit-learn | ML/preprocessing where required |
| Forecasting models | Demand prediction |
| Git/GitHub | Version control |

---

# 📁 Data

Typical sales fields:

```text
sku_id
date
quantity
revenue
unit_price
category
brand
store
customer
channel
```

Typical inventory fields:

```text
sku_id
stock_on_hand
reorder_point
safety_stock
store_id
inventory_date
```

The dashboard utilities support multiple possible column names and standardize them into common fields.

Supported data directories include:

```text
Data/processed/
Data/cleaned/
data/processed/
data/cleaned/
```

---

# 🔄 Processing Pipeline

1. Load sales and inventory data.
2. Clean and normalize columns.
3. Convert numeric fields safely.
4. Standardize SKU, revenue, quantity and inventory fields.
5. Calculate inventory risk.
6. Calculate SKU-level product risk.
7. Calculate demand/coverage metrics.
8. Apply the Decision Cockpit rules.
9. Display interactive dashboards.
10. Export operational decision queues.

---

# 🖥️ Installation

## 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd PROJECT-FORESIGHT
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available:

```bash
pip install streamlit pandas numpy plotly scikit-learn
```

## 4. Run the dashboard

```bash
streamlit run dashboard/app.py
```

Or:

```bash
python -m streamlit run dashboard/app.py
```

Open:

```text
http://localhost:8501
```

---

# 🧭 Dashboard Modules

```text
🏠 Home / Executive Summary
📊 Sales Analytics
📈 Demand Forecast
📦 Inventory Dashboard
⚠️ Risk Dashboard
🔎 Product Details
🎯 Decision Cockpit
```

---

# 🎯 Decision Cockpit Workflow

1. Open **Decision Cockpit**.
2. Select a **Category**.
3. Select a **SKU** or **All SKUs**.
4. Select one or more decision categories.
5. Review KPI cards:
   - SKUs in View
   - Revenue at Risk
   - Inventory Value
   - Average Risk Score
6. Review the operational decision queue.
7. Open **Demand Coverage**.
8. Open **Decisioning Grid**.
9. Download the decision queue as CSV.

---

# 📤 Decision Queue

The cockpit can export a CSV containing fields such as:

```text
sku_id
category
decision
stock_on_hand
reorder_point
recent_demand
days_of_cover
risk_score
revenue_at_risk
capital_locked
```

This makes the dashboard useful for operational follow-up, not only visualization.

---

# 📈 Business Value

FORESIGHT moves retail analysis from:

```text
Raw Data → Reports → Charts
```

to:

```text
Raw Data
   ↓
Analytics
   ↓
Risk Detection
   ↓
Decision
   ↓
Action
```

Potential business benefits:

- Reduce stockout risk
- Improve inventory visibility
- Identify excess inventory
- Prioritize replenishment
- Support markdown decisions
- Improve demand planning
- Reduce manual analysis
- Provide actionable management KPIs

---

# 🧪 Data Validation

Before running the dashboard, verify:

- Sales CSV exists
- Inventory CSV exists
- SKU IDs are populated
- Stock values are numeric
- Reorder points are numeric
- Dates are correctly parsed
- Sales quantities are valid
- Revenue values are valid

The dashboard includes validation checks for unavailable or empty data.

---

# ⚠️ Troubleshooting

### Streamlit not recognized

```bash
python -m streamlit run dashboard/app.py
```

### Missing module

Example:

```text
ModuleNotFoundError: No module named 'streamlit'
```

Install dependencies:

```bash
pip install -r requirements.txt
```

or:

```bash
pip install streamlit pandas numpy plotly scikit-learn
```

### CSV not found

Check:

```text
Data/processed/
Data/cleaned/
data/processed/
data/cleaned/
```

### Category shows `Unknown`

Check that the SKU/sales data contains a field such as:

```text
category
product_category
category_name
item_category
```

### All SKUs appear as Markdown

Check inventory coverage and decision thresholds.

The current cockpit intentionally uses the stronger rule:

```text
Stock > 3 × Reorder Point
AND
Days of Cover >= 120
```

---

# 🔐 GitHub Hygiene

Do not commit:

```text
venv/
__pycache__/
*.pyc
.env
API keys
credentials
large raw datasets
temporary files
```

Use `.gitignore`.

---

# 👨‍💻 Author

**Mayank & Riya ** 


---

# 📜 Project

**FORESIGHT — Demand & Inventory Intelligence**

A retail analytics and decision-support platform combining:

```text
Demand
+
Inventory
+
Risk
+
Decision Intelligence
```

---

# 🔮 Future Enhancements

- Advanced demand forecasting
- Automated purchase-order recommendations
- Supplier lead-time integration
- Store-level optimization
- Promotion-aware forecasting
- Anomaly detection
- ML-based inventory optimization
- Real-time database integration
- Automated email alerts
- Cloud deployment
- Role-based access
- Power BI integration

---

## ⭐ Support

If you find this project useful, consider giving the GitHub repository a ⭐.

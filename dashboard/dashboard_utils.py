# ============================================================
# PROJECT FORESIGHT - DASHBOARD UTILITIES
# ============================================================

from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIRS = [
    PROJECT_ROOT / "data" / "raw",
    PROJECT_ROOT / "data" / "processed",
    PROJECT_ROOT / "data" / "cleaned",
    PROJECT_ROOT / "Data" / "raw",
    PROJECT_ROOT / "Data" / "processed",
    PROJECT_ROOT / "Data" / "cleaned",
]


# ============================================================
# GENERAL HELPERS
# ============================================================

def to_numeric(series, default=0.0):
    """Safely convert values to numeric."""

    if isinstance(series, pd.Series):
        return (
            pd.to_numeric(series, errors="coerce")
            .replace([np.inf, -np.inf], np.nan)
            .fillna(default)
        )

    if series is None:
        return default

    try:
        value = pd.to_numeric(series, errors="coerce")
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def numeric_series(df, column, default=0.0):
    """Return one dataframe column as a clean numeric Series."""

    if df is None or column not in df.columns:
        return pd.Series(dtype="float64")

    return to_numeric(df[column], default=default)


def clean_columns(df):
    """Normalize column names and keep original meanings."""

    if df is None:
        return pd.DataFrame()

    result = df.copy()
    result.columns = (
        result.columns.astype(str)
        .str.strip()
        .str.replace("\ufeff", "", regex=False)
    )
    return result


def find_column(df, candidates):
    """Find a column by exact, case-insensitive or normalized name."""

    if df is None or df.empty:
        return None

    columns = list(df.columns)

    for candidate in candidates:
        if candidate in columns:
            return candidate

    lower_map = {
        str(col).strip().lower(): col
        for col in columns
    }

    for candidate in candidates:
        key = str(candidate).strip().lower()
        if key in lower_map:
            return lower_map[key]

    def normalize(value):
        return (
            str(value)
            .strip()
            .lower()
            .replace("_", "")
            .replace("-", "")
            .replace(" ", "")
            .replace("/", "")
        )

    normalized_map = {
        normalize(col): col
        for col in columns
    }

    for candidate in candidates:
        key = normalize(candidate)
        if key in normalized_map:
            return normalized_map[key]

    return None


# ============================================================
# COLUMN FINDERS
# ============================================================

def find_sales_column(df, column_type=None):
    """Find a sales column. No type defaults to revenue."""

    mapping = {
        "revenue": [
            "dashboard_revenue",
            "total_value",
            "revenue",
            "sales_amount",
            "sales_value",
            "total_sales",
            "sales",
            "amount",
            "net_sales",
            "gross_sales",
            "total_revenue",
        ],
        "quantity": [
            "quantity",
            "qty",
            "units_sold",
            "units",
            "sales_quantity",
            "order_quantity",
        ],
        "unit_price": [
            "dashboard_unit_price",
            "unit_price",
            "unit_price_x",
            "unit_price_y",
            "selling_price",
            "sale_price",
            "price",
        ],
        "date": [
            "date",
            "sales_date",
            "transaction_date",
            "order_date",
            "invoice_date",
            "datetime",
        ],
        "sku": [
            "sku_id",
            "sku",
            "product_id",
            "product_code",
            "item_id",
            "product",
        ],
        "store": [
            "store_id",
            "store",
            "store_code",
        ],
        "customer": [
            "customer_id",
            "customer",
            "customer_code",
        ],
        "category": [
            "category",
            "product_category",
            "item_category",
            "category_name",
        ],
        "brand": [
            "brand",
            "brand_name",
        ],
        "channel": [
            "channel",
            "sales_channel",
            "preferred_channel",
        ],
    }

    if column_type is None:
        column_type = "revenue"

    candidates = mapping.get(
        str(column_type).lower(),
        []
    )

    return find_column(df, candidates)


def find_inventory_column(df, column_type=None):
    """Find an inventory column. No type defaults to stock."""

    mapping = {
        "stock": [
            "stock_on_hand",
            "stock",
            "inventory",
            "inventory_quantity",
            "current_stock",
            "available_stock",
            "quantity",
        ],
        "reorder": [
            "reorder_point",
            "reorder_level",
            "reorder",
            "reorder_quantity",
            "reorder_threshold",
        ],
        "safety": [
            "safety_stock",
            "safety",
            "minimum_stock",
        ],
        "sku": [
            "sku_id",
            "sku",
            "product_id",
            "product_code",
            "item_id",
        ],
        "store": [
            "store_id",
            "store",
            "store_code",
        ],
        "date": [
            "snapshot_date",
            "date",
            "inventory_date",
        ],
    }

    if column_type is None:
        column_type = "stock"

    candidates = mapping.get(
        str(column_type).lower(),
        []
    )

    return find_column(df, candidates)


def find_product_column(df):
    """Find the product/SKU identifier."""

    return find_column(
        df,
        [
            "sku_id",
            "sku",
            "product_id",
            "product_code",
            "item_id",
            "product",
            "product_name",
        ],
    )


# ============================================================
# FILE DISCOVERY
# ============================================================

def find_existing_file(candidates):
    for directory in DATA_DIRS:
        for filename in candidates:
            path = directory / filename
            if path.exists() and path.is_file():
                return path
    return None


def get_sales_file():
    return find_existing_file(
        [
            "bm_sales.csv",
            "cleaned_sales.csv",
            "final_dataset.csv",
            "feature_engineered.csv",
            "sales_transactions.csv",
            "sales.csv",
            "sales_data.csv",
        ]
    )


def get_inventory_file():
    return find_existing_file(
        [
            "bm_inventory.csv",
            "cleaned_inventory.csv",
            "inventory_snapshot.csv",
            "inventory.csv",
            "inventory_data.csv",
        ]
    )


# ============================================================
# SALES LOADER
# ============================================================

@st.cache_data(show_spinner=False)
def load_sales_data():
    path = get_sales_file()

    if path is None:
        return pd.DataFrame()

    try:
        df = pd.read_csv(path, low_memory=False)
    except Exception as exc:
        st.error(f"Sales data loading error: {exc}")
        return pd.DataFrame()

    if df.empty:
        return df

    df = clean_columns(df)

    date_col = find_sales_column(df, "date")
    qty_col = find_sales_column(df, "quantity")
    price_col = find_sales_column(df, "unit_price")
    revenue_col = find_sales_column(df, "revenue")
    sku_col = find_sales_column(df, "sku")
    store_col = find_sales_column(df, "store")
    customer_col = find_sales_column(df, "customer")
    category_col = find_sales_column(df, "category")
    brand_col = find_sales_column(df, "brand")
    channel_col = find_sales_column(df, "channel")

    # Date
    if date_col:
        df["date"] = pd.to_datetime(
            df[date_col],
            errors="coerce",
        )
    else:
        df["date"] = pd.NaT

    # Quantity
    if qty_col:
        df["quantity"] = to_numeric(df[qty_col])
    else:
        df["quantity"] = 0.0

    # Unit price
    if price_col:
        df["dashboard_unit_price"] = to_numeric(
            df[price_col]
        )
    else:
        df["dashboard_unit_price"] = 0.0

    # Revenue
    if revenue_col:
        revenue = to_numeric(df[revenue_col])
        if revenue.abs().sum() > 0:
            df["dashboard_revenue"] = revenue
        else:
            df["dashboard_revenue"] = (
                df["quantity"]
                * df["dashboard_unit_price"]
            )
    else:
        df["dashboard_revenue"] = (
            df["quantity"]
            * df["dashboard_unit_price"]
        )

    # SKU
    if sku_col:
        df["sku_id"] = (
            df[sku_col]
            .astype(str)
            .replace(
                {
                    "nan": "",
                    "None": "",
                }
            )
        )
    else:
        df["sku_id"] = ""

    # Store
    if store_col and "store_id" not in df.columns:
        df["store_id"] = df[store_col]

    # Customer
    if customer_col and "customer_id" not in df.columns:
        df["customer_id"] = df[customer_col]

    # Category
    if category_col:
        df["category"] = (
            df[category_col]
            .astype(str)
            .replace(
                {
                    "nan": "Unknown",
                    "None": "Unknown",
                }
            )
        )
    else:
        df["category"] = "Unknown"

    # Brand
    if brand_col:
        df["brand"] = (
            df[brand_col]
            .astype(str)
            .replace(
                {
                    "nan": "Unknown",
                    "None": "Unknown",
                }
            )
        )
    else:
        df["brand"] = "Unknown"

    # Channel
    if channel_col and "channel" not in df.columns:
        df["channel"] = df[channel_col]

    return df


# ============================================================
# INVENTORY LOADER
# ============================================================

@st.cache_data(show_spinner=False)
def load_inventory_data():
    path = get_inventory_file()

    if path is None:
        return pd.DataFrame()

    try:
        df = pd.read_csv(path, low_memory=False)
    except Exception as exc:
        st.error(f"Inventory data loading error: {exc}")
        return pd.DataFrame()

    if df.empty:
        return df

    df = clean_columns(df)

    stock_col = find_inventory_column(df, "stock")
    reorder_col = find_inventory_column(df, "reorder")
    safety_col = find_inventory_column(df, "safety")
    sku_col = find_inventory_column(df, "sku")
    store_col = find_inventory_column(df, "store")
    date_col = find_inventory_column(df, "date")

    # Stock
    df["stock_on_hand"] = (
        to_numeric(df[stock_col])
        if stock_col
        else 0.0
    )

    # Reorder point
    df["reorder_point"] = (
        to_numeric(df[reorder_col])
        if reorder_col
        else 0.0
    )

    # Safety stock
    df["safety_stock"] = (
        to_numeric(df[safety_col])
        if safety_col
        else 0.0
    )

    # SKU
    if sku_col:
        df["sku_id"] = (
            df[sku_col]
            .astype(str)
            .replace(
                {
                    "nan": "",
                    "None": "",
                }
            )
        )
    else:
        df["sku_id"] = ""

    # Store
    if store_col and "store_id" not in df.columns:
        df["store_id"] = df[store_col]

    # Inventory date
    if date_col:
        df["inventory_date"] = pd.to_datetime(
            df[date_col],
            errors="coerce",
        )
    else:
        df["inventory_date"] = pd.NaT

    return df


# ============================================================
# SKU-LEVEL RISK ENGINE
# ============================================================

def calculate_product_risk(
    inventory,
    sales=None,
    demand_days=90,
):
    """
    Aggregate store-level inventory into SKU-level records
    and calculate shortage, demand coverage and risk.
    """

    if inventory is None or inventory.empty:
        return pd.DataFrame()

    inv = inventory.copy()

    # Remove invalid SKUs
    inv["sku_id"] = (
        inv["sku_id"]
        .astype(str)
        .str.strip()
    )

    inv = inv[
        ~inv["sku_id"].isin(
            [
                "",
                "nan",
                "None",
            ]
        )
    ].copy()

    if inv.empty:
        return pd.DataFrame()

    # Aggregate store-level inventory into SKU level.
    grouped = (
        inv.groupby(
            "sku_id",
            as_index=False,
        )
        .agg(
            stock_on_hand=(
                "stock_on_hand",
                "sum",
            ),
            reorder_point=(
                "reorder_point",
                "sum",
            ),
            safety_stock=(
                "safety_stock",
                "sum",
            ),
            store_count=(
                "store_id",
                "nunique",
            )
            if "store_id" in inv.columns
            else ("sku_id", "count"),
        )
    )

    # --------------------------------------------------------
    # Recent demand
    # --------------------------------------------------------

    grouped["recent_demand"] = 0.0

    if (
        sales is not None
        and not sales.empty
        and "sku_id" in sales.columns
        and "quantity" in sales.columns
    ):
        s = sales.copy()

        s["sku_id"] = (
            s["sku_id"]
            .astype(str)
            .str.strip()
        )

        s["quantity"] = to_numeric(
            s["quantity"]
        )

        if "date" in s.columns:
            s["date"] = pd.to_datetime(
                s["date"],
                errors="coerce",
            )

            max_date = s["date"].max()

            if pd.notna(max_date):
                cutoff = (
                    max_date
                    - pd.Timedelta(
                        days=int(demand_days)
                    )
                )

                s = s[
                    s["date"] >= cutoff
                ]

        demand = (
            s.groupby(
                "sku_id",
                as_index=False,
            )["quantity"]
            .sum()
            .rename(
                columns={
                    "quantity": "recent_demand",
                }
            )
        )

        grouped = grouped.merge(
            demand,
            on="sku_id",
            how="left",
            suffixes=("", "_sales"),
        )

        if "recent_demand_sales" in grouped.columns:
            grouped["recent_demand"] = (
                grouped["recent_demand_sales"]
            )
            grouped = grouped.drop(
                columns=["recent_demand_sales"]
            )

    grouped["recent_demand"] = to_numeric(
        grouped["recent_demand"]
    )

    demand_days = max(
        int(demand_days),
        1,
    )

    grouped["daily_demand"] = (
        grouped["recent_demand"]
        / demand_days
    )

    # --------------------------------------------------------
    # Days of cover
    # --------------------------------------------------------

    grouped["days_of_cover"] = np.where(
        grouped["daily_demand"] > 0,
        grouped["stock_on_hand"]
        / grouped["daily_demand"],
        np.inf,
    )

    # --------------------------------------------------------
    # Stock ratio
    # --------------------------------------------------------

    grouped["stock_reorder_ratio"] = np.where(
        grouped["reorder_point"] > 0,
        grouped["stock_on_hand"]
        / grouped["reorder_point"],
        np.nan,
    )

    # --------------------------------------------------------
    # Shortage risk
    # --------------------------------------------------------

    stock = grouped["stock_on_hand"]
    reorder = grouped["reorder_point"]
    safety = grouped["safety_stock"]

    shortage_risk = np.where(
        stock <= 0,
        100.0,
        np.where(
            (safety > 0) & (stock <= safety),
            100.0,
            np.where(
                (reorder > 0) & (stock < reorder),
                50.0
                + 50.0
                * (
                    (reorder - stock)
                    / np.maximum(
                        reorder - safety,
                        1,
                    )
                ),
                0.0,
            ),
        ),
    )

    shortage_risk = np.clip(
        shortage_risk,
        0,
        100,
    )

    grouped["shortage_risk_score"] = shortage_risk

    # --------------------------------------------------------
    # Overstock risk
    # --------------------------------------------------------

    overstock_risk = np.where(
        reorder > 0,
        np.clip(
            (
                grouped["stock_reorder_ratio"] - 2.0
            )
            / 1.5
            * 100,
            0,
            100,
        ),
        0,
    )

    grouped["overstock_risk_score"] = (
        pd.Series(
            overstock_risk,
            index=grouped.index,
        )
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .fillna(0)
    )

    # --------------------------------------------------------
    # Stock risk
    # --------------------------------------------------------

    grouped["stock_risk_score"] = np.maximum(
        grouped["shortage_risk_score"],
        grouped["overstock_risk_score"],
    )

    # --------------------------------------------------------
    # Demand / coverage risk
    # --------------------------------------------------------

    cover = grouped["days_of_cover"]

    demand_risk = np.select(
        [
            cover <= 7,
            cover <= 14,
            cover <= 30,
            cover <= 60,
            cover <= 90,
            cover <= 180,
        ],
        [
            100.0,
            75.0,
            50.0,
            30.0,
            15.0,
            10.0,
        ],
        default=0.0,
    )

    # No recent demand means demand risk = 0,
    # not automatically HIGH risk.
    demand_risk = np.where(
        grouped["recent_demand"] <= 0,
        0.0,
        demand_risk,
    )

    grouped["demand_risk_score"] = demand_risk

    # --------------------------------------------------------
    # Final risk score
    # --------------------------------------------------------

    grouped["risk_score"] = (
        grouped["stock_risk_score"] * 0.60
        + grouped["demand_risk_score"] * 0.40
    ).clip(
        0,
        100,
    )

    # --------------------------------------------------------
    # Risk level
    # --------------------------------------------------------

    grouped["risk_level"] = np.select(
        [
            grouped["risk_score"] >= 75,
            grouped["risk_score"] >= 50,
            grouped["risk_score"] >= 25,
        ],
        [
            "Critical",
            "High",
            "Medium",
        ],
        default="Low",
    )

    # --------------------------------------------------------
    # Inventory status
    # --------------------------------------------------------

    grouped["inventory_status"] = np.select(
        [
            stock <= 0,
            (safety > 0) & (stock <= safety),
            (reorder > 0) & (stock <= reorder),
            (reorder > 0)
            & (stock > reorder * 2),
        ],
        [
            "OUT OF STOCK",
            "CRITICAL",
            "REORDER",
            "OVERSTOCK",
        ],
        default="HEALTHY",
    )

    # --------------------------------------------------------
    # Business action
    # --------------------------------------------------------

    grouped["recommended_action"] = np.select(
        [
            grouped["inventory_status"] == "OUT OF STOCK",
            grouped["inventory_status"] == "CRITICAL",
            grouped["inventory_status"] == "REORDER",
            grouped["inventory_status"] == "OVERSTOCK",
            grouped["risk_level"] == "Critical",
            grouped["risk_level"] == "High",
        ],
        [
            "Immediate replenishment",
            "Urgent replenishment",
            "Plan replenishment",
            "Reduce / slow replenishment",
            "Immediate risk review",
            "Prioritize monitoring",
        ],
        default="Monitor",
    )

    return grouped


# ============================================================
# COMPATIBILITY: CALCULATE_RISK
# ============================================================

def calculate_risk(
    inventory,
    sales=None,
    demand_days=90,
):
    """
    Public compatibility function used by Inventory/Risk/
    Executive pages.
    """

    if sales is None:
        sales = pd.DataFrame()

    return calculate_product_risk(
        inventory,
        sales,
        demand_days=demand_days,
    )


# ============================================================
# EXECUTIVE METRICS
# ============================================================

def get_executive_metrics():

    sales = load_sales_data()
    inventory = load_inventory_data()

    revenue = 0.0
    transactions = 0
    unique_skus = 0

    if not sales.empty:

        revenue = float(
            numeric_series(
                sales,
                "dashboard_revenue",
            ).sum()
        )

        transactions = len(sales)

        valid_skus = (
            sales["sku_id"]
            .astype(str)
            .str.strip()
        )

        valid_skus = valid_skus[
            ~valid_skus.isin(
                [
                    "",
                    "nan",
                    "None",
                ]
            )
        ]

        unique_skus = int(
            valid_skus.nunique()
        )

    risk = calculate_product_risk(
        inventory,
        sales,
        demand_days=90,
    )

    if risk.empty:
        critical = high = medium = low = 0
        average_risk = 0.0
    else:
        levels = (
            risk["risk_level"]
            .astype(str)
            .str.strip()
        )

        critical = int(
            (levels == "Critical").sum()
        )

        high = int(
            (levels == "High").sum()
        )

        medium = int(
            (levels == "Medium").sum()
        )

        low = int(
            (levels == "Low").sum()
        )

        average_risk = float(
            pd.to_numeric(
                risk["risk_score"],
                errors="coerce",
            )
            .fillna(0)
            .mean()
        )

    return {
        "revenue": revenue,
        "transactions": transactions,
        "unique_skus": unique_skus,
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "average_risk": average_risk,
    }


# ============================================================
# REVENUE HELPERS
# ============================================================

def get_daily_revenue():

    sales = load_sales_data()

    if sales.empty or "date" not in sales.columns:
        return pd.DataFrame()

    return (
        sales.dropna(
            subset=["date"]
        )
        .groupby(
            "date",
            as_index=False,
        )["dashboard_revenue"]
        .sum()
        .sort_values("date")
    )


def get_category_revenue():

    sales = load_sales_data()

    if sales.empty or "category" not in sales.columns:
        return pd.DataFrame()

    valid = sales[
        sales["category"]
        .astype(str)
        .str.strip()
        .str.lower()
        .ne("unknown")
    ].copy()

    if valid.empty:
        return pd.DataFrame()

    return (
        valid.groupby(
            "category",
            as_index=False,
        )["dashboard_revenue"]
        .sum()
        .sort_values(
            "dashboard_revenue",
            ascending=False,
        )
    )


def get_channel_revenue():

    sales = load_sales_data()

    if sales.empty or "channel" not in sales.columns:
        return pd.DataFrame()

    valid = sales[
        sales["channel"]
        .astype(str)
        .str.strip()
        .str.lower()
        .ne("nan")
    ].copy()

    if valid.empty:
        return pd.DataFrame()

    return (
        valid.groupby(
            "channel",
            as_index=False,
        )["dashboard_revenue"]
        .sum()
        .sort_values(
            "dashboard_revenue",
            ascending=False,
        )
    )


def get_top_products(limit=10):

    sales = load_sales_data()

    if sales.empty or "sku_id" not in sales.columns:
        return pd.DataFrame()

    valid = sales[
        ~sales["sku_id"]
        .astype(str)
        .str.strip()
        .isin(
            [
                "",
                "nan",
                "None",
            ]
        )
    ].copy()

    if valid.empty:
        return pd.DataFrame()

    result = (
        valid.groupby(
            "sku_id",
            as_index=False,
        )
        .agg(
            Revenue=(
                "dashboard_revenue",
                "sum",
            ),
            Quantity=(
                "quantity",
                "sum",
            ),
            Transactions=(
                "sku_id",
                "count",
            ),
        )
        .sort_values(
            "Revenue",
            ascending=False,
        )
        .head(limit)
    )

    return result


def get_risk_summary():

    levels = [
        "Critical",
        "High",
        "Medium",
        "Low",
    ]

    inventory = load_inventory_data()
    sales = load_sales_data()

    risk = calculate_product_risk(
        inventory,
        sales,
        demand_days=90,
    )

    if risk.empty:
        counts = [0, 0, 0, 0]
    else:
        value_counts = (
            risk["risk_level"]
            .value_counts()
        )

        counts = [
            int(value_counts.get(level, 0))
            for level in levels
        ]

    return pd.DataFrame(
        {
            "Risk Level": levels,
            "SKU Count": counts,
        }
    )


def get_data_summary():

    sales_file = get_sales_file()
    inventory_file = get_inventory_file()

    sales = load_sales_data()
    inventory = load_inventory_data()

    return {
        "sales_loaded": not sales.empty,
        "inventory_loaded": not inventory.empty,
        "sales_rows": len(sales),
        "inventory_rows": len(inventory),
        "sales_file": (
            str(sales_file)
            if sales_file
            else "Not found"
        ),
        "inventory_file": (
            str(inventory_file)
            if inventory_file
            else "Not found"
        ),
    }


# ============================================================
# CHART STYLE
# ============================================================

def get_plotly_template():

    try:
        theme = st.get_option(
            "theme.base"
        )
    except Exception:
        theme = "light"

    return (
        "plotly_dark"
        if str(theme).lower() == "dark"
        else "plotly_white"
    )


def chart_layout(fig, height=400):

    fig.update_layout(
        template=get_plotly_template(),
        height=height,
        margin=dict(
            l=30,
            r=30,
            t=65,
            b=30,
        ),
        font=dict(
            size=13,
        ),
    )

    return fig


# ============================================================
# FOOTER
# ============================================================

def footer():

    st.divider()

    st.caption(
        "FORESIGHT • Retail Intelligence Dashboard"
    )


# ============================================================
# THEME / STYLE
# ============================================================

def apply_dashboard_style():

    st.markdown(
        """
        <style>

        .block-container {
            padding-top: 1.7rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }

        [data-testid="stAppViewContainer"] {
            background: var(--background-color);
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stSidebar"] {
            background: var(--secondary-background-color);
            border-right: 1px solid rgba(128,128,128,0.18);
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--text-color) !important;
        }

        p, label, .stMarkdown {
            color: var(--text-color) !important;
        }

        [data-testid="stMetric"] {
            background: var(--secondary-background-color);
            border: 1px solid rgba(128,128,128,0.22);
            border-radius: 14px;
            padding: 16px;
        }

        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"],
        [data-testid="stMetricDelta"] {
            color: var(--text-color) !important;
        }

        [data-baseweb="select"] > div {
            background: var(--secondary-background-color);
            color: var(--text-color);
            border-color: rgba(128,128,128,0.3);
        }

        [data-baseweb="select"] span {
            color: var(--text-color);
        }

        .module-card {
            background: var(--secondary-background-color);
            border: 1px solid rgba(128,128,128,0.22);
            border-radius: 16px;
            padding: 24px;
            min-height: 160px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        }

        .module-title {
            color: var(--text-color) !important;
            font-size: 22px;
            font-weight: 750;
        }

        .module-text {
            color: var(--text-color) !important;
            opacity: 0.78;
            line-height: 1.55;
        }

        .hero-section {
            background:
                linear-gradient(
                    135deg,
                    #172554 0%,
                    #1e3a8a 55%,
                    #2563eb 100%
                );
            border-radius: 20px;
            padding: 38px;
            color: white;
            margin-bottom: 25px;
            box-shadow: 0 12px 30px rgba(0,0,0,0.18);
        }

        .hero-title {
            color: white !important;
            font-size: 42px;
            font-weight: 800;
        }

        .hero-subtitle {
            color: #bfdbfe !important;
            font-size: 21px;
            font-weight: 600;
        }

        .hero-text {
            color: #dbeafe !important;
            font-size: 16px;
            line-height: 1.6;
            max-width: 850px;
        }

        .dashboard-footer {
            margin-top: 35px;
            padding-top: 18px;
            color: var(--text-color);
            opacity: 0.65;
            font-size: 13px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
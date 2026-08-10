from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

RAW_DIR = DATA_DIR / "raw"

PROCESSED_DIR = DATA_DIR / "processed"


# ============================================================
# COMMON STYLE
# ============================================================
def apply_dashboard_style():

    st.markdown(
        """
        <style>

        /* =====================================================
           PROJECT FORESIGHT - THEME SAFE BACKGROUND
           ===================================================== */

        /*
           IMPORTANT:
           Do NOT force white/black text here.

           Streamlit automatically provides:
           
           --background-color
           --secondary-background-color
           --text-color

           according to:
           
           Light
           Dark
           System
        */


        /* =====================================================
           MAIN APPLICATION BACKGROUND
           ===================================================== */

        [data-testid="stAppViewContainer"] {

            background-color: var(--background-color) !important;

        }


        /* =====================================================
           MAIN CONTENT
           ===================================================== */

        [data-testid="stMain"] {

            background-color: var(--background-color) !important;

        }


        /* =====================================================
           MAIN BLOCK
           ===================================================== */

        .main {

            background-color: var(--background-color) !important;

        }


        /* =====================================================
           CONTENT CONTAINER
           ===================================================== */

        .block-container {

            background-color: transparent !important;

        }


        /* =====================================================
           TOP HEADER
           ===================================================== */

        [data-testid="stHeader"] {

            background-color: var(--background-color) !important;

        }


        /* =====================================================
           SIDEBAR
           
           IMPORTANT:
           We use Streamlit's secondary background variable
           instead of forcing a fixed dark color.
           
           This allows Light/Dark/System to work correctly.
           ===================================================== */

        section[data-testid="stSidebar"] {

            background-color: var(--secondary-background-color) !important;

        }


        section[data-testid="stSidebar"] > div {

            background-color: var(--secondary-background-color) !important;

        }


        /* =====================================================
           DO NOT OVERRIDE TEXT COLORS
           
           Streamlit controls:
           
           Light mode → dark text
           Dark mode → light text
           System → system theme text
           ===================================================== */


        </style>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# CSV LOADER
# ============================================================

def load_csv(path):

    path = Path(path)

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)

    except Exception:

        try:
            return pd.read_csv(
                path,
                encoding="latin1"
            )

        except Exception:
            return pd.DataFrame()


# ============================================================
# RAW DATA LOADERS
# ============================================================

@st.cache_data
def load_sales_data():

    return load_csv(
        RAW_DIR / "bm_sales.csv"
    )


@st.cache_data
def load_inventory_data():

    return load_csv(
        RAW_DIR / "bm_inventory.csv"
    )


@st.cache_data
def load_customer_data():

    return load_csv(
        RAW_DIR / "bm_customers.csv"
    )


@st.cache_data
def load_store_data():

    return load_csv(
        RAW_DIR / "bm_stores.csv"
    )


@st.cache_data
def load_sku_data():

    return load_csv(
        RAW_DIR / "bm_skus.csv"
    )


@st.cache_data
def load_promotion_data():

    return load_csv(
        RAW_DIR / "bm_promotions.csv"
    )


# ============================================================
# PROCESSED DATA LOADERS
# ============================================================

@st.cache_data
def load_prediction_data():

    return load_csv(
        PROCESSED_DIR / "prediction_report.csv"
    )


@st.cache_data
def load_model_summary():

    return load_csv(
        PROCESSED_DIR / "model_summary_final.csv"
    )


@st.cache_data
def load_recommendation_data():

    return load_csv(
        PROCESSED_DIR / "inventory_recommendation.csv"
    )


# ============================================================
# COLUMN FINDER
# ============================================================

def find_column(df, possible_names):

    if df.empty:
        return None

    columns = {
        str(c).lower().strip(): c
        for c in df.columns
    }

    # Exact match
    for name in possible_names:

        key = name.lower().strip()

        if key in columns:
            return columns[key]

    # Partial match
    for col in df.columns:

        col_lower = str(col).lower()

        for name in possible_names:

            if name.lower() in col_lower:
                return col

    return None


# ============================================================
# PRODUCT COLUMN
# ============================================================

def find_product_column(df):

    return find_column(
        df,
        [
            "sku_id",
            "sku",
            "product_id",
            "product",
            "product_code",
            "item_id"
        ]
    )


# ============================================================
# STORE COLUMN
# ============================================================

def find_store_column(df):

    return find_column(
        df,
        [
            "store_id",
            "store",
            "store_code"
        ]
    )


# ============================================================
# DATE COLUMN
# ============================================================

def find_date_column(df):

    return find_column(
        df,
        [
            "date",
            "sales_date",
            "transaction_date",
            "order_date",
            "timestamp"
        ]
    )


# ============================================================
# SALES COLUMN
# ============================================================

def find_sales_column(df):

    return find_column(
        df,
        [
            "sales",
            "sales_amount",
            "revenue",
            "amount",
            "total_sales",
            "total_amount",
            "net_sales",
            "selling_price"
        ]
    )


# ============================================================
# QUANTITY COLUMN
# ============================================================

def find_quantity_column(df):

    return find_column(
        df,
        [
            "quantity",
            "qty",
            "units",
            "units_sold",
            "sales_quantity"
        ]
    )


# ============================================================
# INVENTORY COLUMN
# ============================================================

def find_inventory_column(df):

    return find_column(
        df,
        [
            "inventory_quantity",
            "inventory",
            "stock",
            "stock_quantity",
            "quantity_on_hand",
            "on_hand"
        ]
    )


# ============================================================
# NUMERIC CONVERSION
# ============================================================

def numeric_series(df, column):

    if column is None:

        return pd.Series(
            0,
            index=df.index,
            dtype="float64"
        )

    return pd.to_numeric(
        df[column],
        errors="coerce"
    ).fillna(0)


# ============================================================
# PLOTLY LAYOUT
# ============================================================

def chart_layout(fig, height=420):

    fig.update_layout(

        template="plotly_white",

        height=height,

        paper_bgcolor="#ffffff",

        plot_bgcolor="#ffffff",

        font=dict(
            color="#374151"
        ),

        title_font=dict(
            color="#111827",
            size=20
        ),

        margin=dict(
            l=30,
            r=30,
            t=65,
            b=30
        )
    )

    return fig


# ============================================================
# PAGE FOOTER
# ============================================================

def footer():

    st.divider()

    st.caption(
        "Project Foresight • Retail AI Intelligence Platform"
    )
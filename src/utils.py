from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = Path(r"C:\Users\mayank\OneDrive\Desktop\Project-FORESIGHT\data")
RAW_DIR = Path(r"C:\Users\mayank\OneDrive\Desktop\Project-FORESIGHT\data\raw")
PROCESSED_DIR = Path(r"C:\Users\mayank\OneDrive\Desktop\Project-FORESIGHT\data\processed")

MODEL_DIR = Path(r"C:\Users\mayank\OneDrive\Desktop\Project-FORESIGHT\models")
IMAGE_DIR = Path(r"C:\Users\mayank\OneDrive\Desktop\Project-FORESIGHT\images")

# ============================================================
# GENERIC CSV LOADER
# ============================================================

def load_csv(path):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return pd.read_csv(path)


# ============================================================
# DATASET LOADERS
# ============================================================

def load_sales():
    return load_csv(RAW_DIR / "bm_sales.csv")


def load_inventory():
    return load_csv(RAW_DIR / "bm_inventory.csv")


def load_skus():
    return load_csv(RAW_DIR / "bm_skus.csv")


def load_stores():
    return load_csv(RAW_DIR / "bm_stores.csv")


def load_customers():
    return load_csv(RAW_DIR / "bm_customers.csv")


def load_promotions():
    return load_csv(RAW_DIR / "bm_promotions.csv")


def load_prediction_report():

    path = PROCESSED_DIR / "prediction_report.csv"

    if not path.exists():
        return pd.DataFrame()

    return pd.read_csv(path)


def load_inventory_recommendation():

    path = PROCESSED_DIR / "inventory_recommendation.csv"

    if not path.exists():
        return pd.DataFrame()

    return pd.read_csv(path)


def load_model_summary():

    possible_files = [
        PROCESSED_DIR / "model_summary_final.csv",
        PROCESSED_DIR / "model_summary.csv"
    ]

    for path in possible_files:

        if path.exists():
            return pd.read_csv(path)

    return pd.DataFrame()


# ============================================================
# COLUMN DETECTION
# ============================================================

def find_column(df, candidates):

    columns = {
        str(col).lower().strip(): col
        for col in df.columns
    }

    for candidate in candidates:

        candidate = candidate.lower().strip()

        if candidate in columns:
            return columns[candidate]

    return None


def find_date_column(df):

    candidates = [
        "date",
        "transaction_date",
        "sales_date",
        "order_date",
        "invoice_date",
        "timestamp",
        "datetime"
    ]

    return find_column(df, candidates)


def find_sales_column(df):

    candidates = [
        "sales",
        "sale",
        "sales_amount",
        "revenue",
        "revenue_amount",
        "amount",
        "total_amount",
        "total_sales",
        "price"
    ]

    return find_column(df, candidates)


def find_quantity_column(df):

    candidates = [
        "quantity",
        "qty",
        "units",
        "units_sold",
        "sales_quantity",
        "stock",
        "inventory",
        "stock_quantity",
        "available_quantity",
        "current_stock"
    ]

    return find_column(df, candidates)


def find_product_column(df):

    candidates = [
        "sku_id",
        "product_id",
        "product",
        "product_name",
        "sku"
    ]

    return find_column(df, candidates)


def find_store_column(df):

    candidates = [
        "store_id",
        "store",
        "store_name",
        "branch_id"
    ]

    return find_column(df, candidates)


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

def clean_column_names(df):

    df = df.copy()

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )

    return df


# ============================================================
# FORMATTING
# ============================================================

def format_currency(value):

    if pd.isna(value):
        return "₹0"

    return f"₹{value:,.0f}"


def format_number(value):

    if pd.isna(value):
        return "0"

    return f"{value:,.0f}"


def format_percentage(value):

    if pd.isna(value):
        return "0%"

    return f"{value:.2f}%"
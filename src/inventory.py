import pandas as pd
import numpy as np


def calculate_inventory_metrics(
    inventory_df
):

    df = inventory_df.copy()

    quantity_candidates = [
        "quantity",
        "qty",
        "stock",
        "stock_quantity",
        "inventory",
        "inventory_quantity",
        "available_quantity",
        "current_stock"
    ]

    quantity_column = None

    for col in quantity_candidates:

        if col in df.columns:

            quantity_column = col
            break

    if quantity_column is None:

        numeric_columns = (
            df.select_dtypes(
                include=np.number
            ).columns
        )

        if len(numeric_columns) == 0:

            df["inventory_quantity"] = 0

        else:

            quantity_column = (
                numeric_columns[0]
            )

    if quantity_column:

        df["inventory_quantity"] = pd.to_numeric(
            df[quantity_column],
            errors="coerce"
        ).fillna(0)

    df["inventory_status"] = np.select(

        [
            df["inventory_quantity"] <= 0,

            df["inventory_quantity"] <= 10,

            df["inventory_quantity"] <= 50
        ],

        [
            "Out of Stock",
            "Critical",
            "Low"
        ],

        default="Healthy"
    )

    return df


def calculate_stockout_risk(
    inventory_df
):

    df = inventory_df.copy()

    if "inventory_quantity" not in df.columns:

        df = calculate_inventory_metrics(
            df
        )

    df["stockout_risk"] = np.select(

        [
            df["inventory_quantity"] <= 0,

            df["inventory_quantity"] <= 10,

            df["inventory_quantity"] <= 25
        ],

        [
            "Very High",
            "High",
            "Medium"
        ],

        default="Low"
    )

    return df


def calculate_reorder_quantity(
    current_stock,
    average_daily_demand,
    lead_time_days=7,
    safety_days=3
):

    reorder_point = (
        average_daily_demand
        *
        (lead_time_days + safety_days)
    )

    return max(
        0,
        reorder_point - current_stock
    )
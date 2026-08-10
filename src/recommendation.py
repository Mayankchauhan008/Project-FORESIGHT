import pandas as pd


def generate_inventory_recommendations(
    inventory_df
):

    df = inventory_df.copy()

    if "inventory_quantity" not in df.columns:

        return df

    df["recommendation"] = (
        "No Action Required"
    )

    df.loc[
        df["inventory_quantity"] <= 0,
        "recommendation"
    ] = "URGENT: Replenish Stock"

    df.loc[
        (
            df["inventory_quantity"] > 0
        )
        &
        (
            df["inventory_quantity"] <= 10
        ),
        "recommendation"
    ] = "Reorder Soon"

    df.loc[
        (
            df["inventory_quantity"] > 10
        )
        &
        (
            df["inventory_quantity"] <= 25
        ),
        "recommendation"
    ] = "Monitor Inventory"

    return df


def get_priority_recommendations(
    inventory_df,
    limit=20
):

    df = generate_inventory_recommendations(
        inventory_df
    )

    priority = {

        "URGENT: Replenish Stock": 1,

        "Reorder Soon": 2,

        "Monitor Inventory": 3,

        "No Action Required": 4

    }

    df["priority"] = (
        df["recommendation"]
        .map(priority)
        .fillna(5)
    )

    return (
        df
        .sort_values("priority")
        .head(limit)
    )
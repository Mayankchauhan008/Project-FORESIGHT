# ============================================================
# PROJECT FORESIGHT
# RISK SCORING ENGINE
# ============================================================

import numpy as np
import pandas as pd


# ============================================================
# FIND SKU COLUMN
# ============================================================

def _find_sku_column(df):

    candidates = [
        "sku_id",
        "product_id",
        "product",
        "sku",
        "product_sku"
    ]

    for column in candidates:

        if column in df.columns:
            return column

    return None


# ============================================================
# NUMERIC CONVERSION
# ============================================================

def _numeric(df, column, default=0):

    if column not in df.columns:

        return pd.Series(
            default,
            index=df.index,
            dtype="float64"
        )

    return pd.to_numeric(
        df[column],
        errors="coerce"
    ).fillna(default)


# ============================================================
# DEMAND CALCULATION
# ============================================================

def _calculate_recent_demand(
    sales,
    sku_column,
    demand_days=90
):

    result = pd.DataFrame(
        columns=[
            sku_column,
            "recent_demand",
            "daily_demand",
            "days_of_cover"
        ]
    )

    if sales is None or sales.empty:

        return result

    sales = sales.copy()

    sales_sku_column = _find_sku_column(
        sales
    )

    if sales_sku_column is None:

        return result

    if "quantity" not in sales.columns:

        return result

    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    if "date" in sales.columns:

        sales["date"] = pd.to_datetime(
            sales["date"],
            errors="coerce"
        )

        sales = sales.dropna(
            subset=["date"]
        )

        if sales.empty:

            return result

        last_date = sales["date"].max()

        start_date = (
            last_date
            - pd.Timedelta(
                days=demand_days - 1
            )
        )

        sales = sales[
            sales["date"] >= start_date
        ]

    # --------------------------------------------------------
    # Quantity
    # --------------------------------------------------------

    sales["quantity"] = pd.to_numeric(
        sales["quantity"],
        errors="coerce"
    ).fillna(0)

    # --------------------------------------------------------
    # Aggregate demand by SKU
    # --------------------------------------------------------

    demand = (

        sales

        .groupby(
            sales_sku_column,
            as_index=False
        )["quantity"]

        .sum()

        .rename(
            columns={
                sales_sku_column: sku_column,
                "quantity": "recent_demand"
            }
        )

    )

    demand["daily_demand"] = (

        demand["recent_demand"]
        / demand_days

    )

    return demand


# ============================================================
# MAIN RISK FUNCTION
# ============================================================

def calculate_risk_score(
    inventory,
    sales=None,
    demand_days=90
):

    if inventory is None:

        return pd.DataFrame()

    if inventory.empty:

        return inventory.copy()

    df = inventory.copy()

    # ========================================================
    # FIND SKU
    # ========================================================

    sku_column = _find_sku_column(
        df
    )

    if sku_column is None:

        raise ValueError(
            "No SKU/product column found in inventory data."
        )

    # ========================================================
    # REQUIRED INVENTORY COLUMNS
    # ========================================================

    if "stock_on_hand" not in df.columns:

        raise ValueError(
            "Inventory data must contain "
            "'stock_on_hand'."
        )

    if "reorder_point" not in df.columns:

        raise ValueError(
            "Inventory data must contain "
            "'reorder_point'."
        )

    # ========================================================
    # NUMERIC VALUES
    # ========================================================

    df["stock_on_hand"] = _numeric(
        df,
        "stock_on_hand"
    )

    df["reorder_point"] = _numeric(
        df,
        "reorder_point"
    )

    if "safety_stock" in df.columns:

        df["safety_stock"] = _numeric(
            df,
            "safety_stock"
        )

    else:

        df["safety_stock"] = (
            df["reorder_point"] * 0.5
        )

    # ========================================================
    # AGGREGATE STORE INVENTORY → SKU
    # ========================================================

    aggregation = {

        "stock_on_hand": "sum",

        "reorder_point": "sum",

        "safety_stock": "sum"

    }

    if "store_id" in df.columns:

        aggregation["store_id"] = "nunique"

    if "last_restock_date" in df.columns:

        aggregation["last_restock_date"] = "max"

    if "snapshot_date" in df.columns:

        aggregation["snapshot_date"] = "max"

    risk_df = (

        df

        .groupby(
            sku_column,
            as_index=False
        )

        .agg(
            aggregation
        )

    )

    # ========================================================
    # RENAME STORE COUNT
    # ========================================================

    if "store_id" in risk_df.columns:

        risk_df = risk_df.rename(
            columns={
                "store_id": "store_count"
            }
        )

    else:

        risk_df["store_count"] = 1

    # ========================================================
    # STOCK / REORDER RATIO
    # ========================================================

    risk_df["stock_to_reorder_ratio"] = np.where(

        risk_df["reorder_point"] > 0,

        risk_df["stock_on_hand"]
        /
        risk_df["reorder_point"],

        np.inf

    )

    # ========================================================
    # SHORTAGE RISK
    #
    # 0   = safely above reorder point
    # 100 = at/below safety stock
    # ========================================================

    shortage_risk = np.zeros(
        len(risk_df),
        dtype=float
    )

    safety = risk_df["safety_stock"].values

    reorder = risk_df["reorder_point"].values

    stock = risk_df["stock_on_hand"].values

    # At/below safety stock
    mask_critical = stock <= safety

    shortage_risk[mask_critical] = 100

    # Between safety and reorder point
    mask_between = (

        (stock > safety)
        &
        (stock < reorder)

    )

    denominator = (
        reorder[mask_between]
        -
        safety[mask_between]
    )

    shortage_risk[mask_between] = (

        50

        +

        50
        *
        (
            reorder[mask_between]
            -
            stock[mask_between]
        )
        /
        np.where(
            denominator == 0,
            1,
            denominator
        )

    )

    shortage_risk = np.clip(
        shortage_risk,
        0,
        100
    )

    risk_df[
        "shortage_risk_score"
    ] = shortage_risk

    # ========================================================
    # OVERSTOCK RISK
    #
    # Ratio <= 2.0  -> no overstock risk
    # Ratio >= 3.5  -> maximum overstock risk
    # ========================================================

    overstock_risk = np.clip(

        (
            risk_df[
                "stock_to_reorder_ratio"
            ]
            - 2.0
        )

        /

        1.5

        * 100,

        0,

        100

    )

    risk_df[
        "overstock_risk_score"
    ] = overstock_risk

    # ========================================================
    # RECENT DEMAND
    # ========================================================

    demand = _calculate_recent_demand(

        sales,

        sku_column,

        demand_days

    )

    if not demand.empty:

        risk_df = risk_df.merge(

            demand,

            on=sku_column,

            how="left"

        )

    else:

        risk_df[
            "recent_demand"
        ] = 0

        risk_df[
            "daily_demand"
        ] = 0

    # ========================================================
    # MISSING DEMAND
    # ========================================================

    risk_df[
        "recent_demand"
    ] = pd.to_numeric(

        risk_df[
            "recent_demand"
        ],

        errors="coerce"

    ).fillna(0)

    risk_df[
        "daily_demand"
    ] = pd.to_numeric(

        risk_df[
            "daily_demand"
        ],

        errors="coerce"

    ).fillna(0)

    # ========================================================
    # DAYS OF INVENTORY COVER
    # ========================================================

    risk_df[
        "days_of_cover"
    ] = np.where(

        risk_df[
            "daily_demand"
        ] > 0,

        risk_df[
            "stock_on_hand"
        ]
        /
        risk_df[
            "daily_demand"
        ],

        np.inf

    )

    # ========================================================
    # DEMAND / COVER RISK
    #
    # Very low coverage = shortage risk
    # Very high coverage = overstock risk
    # ========================================================

    days_cover = risk_df[
        "days_of_cover"
    ].values

    demand_risk = np.zeros(
        len(risk_df),
        dtype=float
    )

    # No demand
    no_demand = (
        risk_df[
            "daily_demand"
        ].values <= 0
    )

    demand_risk[no_demand] = 40

    # Low coverage
    demand_risk[
        (~no_demand) & (days_cover <= 7)
    ] = 100

    demand_risk[
        (~no_demand)
        &
        (days_cover > 7)
        &
        (days_cover <= 14)
    ] = 80

    demand_risk[
        (~no_demand)
        &
        (days_cover > 14)
        &
        (days_cover <= 30)
    ] = 60

    demand_risk[
        (~no_demand)
        &
        (days_cover > 30)
        &
        (days_cover <= 60)
    ] = 40

    demand_risk[
        (~no_demand)
        &
        (days_cover > 60)
        &
        (days_cover <= 90)
    ] = 25

    demand_risk[
        (~no_demand)
        &
        (days_cover > 90)
        &
        (days_cover <= 180)
    ] = 15

    demand_risk[
        (~no_demand)
        &
        (days_cover > 180)
    ] = 40

    risk_df[
        "demand_risk_score"
    ] = demand_risk

    # ========================================================
    # FINAL RISK SCORE
    #
    # Stock risk = shortage + overstock
    # Demand risk = inventory coverage
    # ========================================================

    risk_df[
        "stock_risk_score"
    ] = np.maximum(

        risk_df[
            "shortage_risk_score"
        ],

        risk_df[
            "overstock_risk_score"
        ]

    )

    risk_df[
        "risk_score"
    ] = (

        0.60
        *
        risk_df[
            "stock_risk_score"
        ]

        +

        0.40
        *
        risk_df[
            "demand_risk_score"
        ]

    )

    risk_df[
        "risk_score"
    ] = np.clip(

        risk_df[
            "risk_score"
        ],

        0,

        100

    )

    # ========================================================
    # RISK LEVEL
    # ========================================================

    risk_df[
        "risk_level"
    ] = pd.cut(

        risk_df[
            "risk_score"
        ],

        bins=[

            -np.inf,

            25,

            50,

            75,

            np.inf

        ],

        labels=[

            "LOW",

            "MEDIUM",

            "HIGH",

            "CRITICAL"

        ],

        right=False

    )

    # ========================================================
    # INVENTORY HEALTH
    # ========================================================

    risk_df[
        "inventory_status"
    ] = np.select(

        [

            risk_df[
                "stock_on_hand"
            ] <= 0,

            risk_df[
                "stock_on_hand"
            ]
            <=
            risk_df[
                "safety_stock"
            ],

            risk_df[
                "stock_on_hand"
            ]
            <=
            risk_df[
                "reorder_point"
            ],

            risk_df[
                "stock_on_hand"
            ]
            >
            (
                risk_df[
                    "reorder_point"
                ]
                * 2
            )

        ],

        [

            "OUT OF STOCK",

            "CRITICAL",

            "LOW STOCK",

            "OVERSTOCK"

        ],

        default="HEALTHY"

    )

    # ========================================================
    # ACTION
    # ========================================================

    risk_df[
        "recommended_action"
    ] = np.select(

        [

            risk_df[
                "inventory_status"
            ]
            ==
            "OUT OF STOCK",

            risk_df[
                "inventory_status"
            ]
            ==
            "CRITICAL",

            risk_df[
                "inventory_status"
            ]
            ==
            "LOW STOCK",

            risk_df[
                "inventory_status"
            ]
            ==
            "OVERSTOCK"

        ],

        [

            "Immediate replenishment",

            "Urgent replenishment",

            "Plan replenishment",

            "Reduce / slow replenishment"

        ],

        default="Monitor"

    )

    # ========================================================
    # CLEAN NUMERIC VALUES
    # ========================================================

    numeric_columns = [

        "stock_on_hand",

        "reorder_point",

        "safety_stock",

        "stock_to_reorder_ratio",

        "shortage_risk_score",

        "overstock_risk_score",

        "stock_risk_score",

        "recent_demand",

        "daily_demand",

        "demand_risk_score",

        "days_of_cover",

        "risk_score"

    ]

    for column in numeric_columns:

        if column in risk_df.columns:

            risk_df[column] = pd.to_numeric(

                risk_df[column],

                errors="coerce"

            )

    return risk_df
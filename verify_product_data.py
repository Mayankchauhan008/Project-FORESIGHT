import sys
from pathlib import Path

import pandas as pd
import numpy as np


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORT YOUR ACTUAL RISK ENGINE
# ============================================================

from src.risk_scoring import calculate_risk_score


# ============================================================
# FIND INVENTORY FILE
# ============================================================

possible_files = [

    PROJECT_ROOT / "data" / "raw" / "bm_inventory.csv",

    PROJECT_ROOT / "data" / "raw" / "inventory_snapshot.csv",

    PROJECT_ROOT / "data" / "processed" / "cleaned_inventory.csv",

    PROJECT_ROOT / "Data" / "raw" / "bm_inventory.csv",

    PROJECT_ROOT / "Data" / "cleaned" / "inventory_recommendation.csv",

]


inventory_file = None


for file in possible_files:

    if file.exists():

        inventory_file = file

        break


if inventory_file is None:

    print()
    print("=" * 70)
    print("ERROR: Inventory CSV was not found.")
    print("=" * 70)

    print()
    print("Checked:")

    for file in possible_files:

        print(
            f"  {file}"
        )

    sys.exit(1)


print()
print("=" * 70)
print("PROJECT FORESIGHT - PRODUCT VERIFICATION")
print("=" * 70)

print()
print(
    f"Inventory file: {inventory_file}"
)


# ============================================================
# LOAD DATA
# ============================================================

inventory = pd.read_csv(
    inventory_file
)


print()
print(
    f"Rows loaded: {len(inventory):,}"
)

print(
    f"Columns: {len(inventory.columns)}"
)

print()
print("Columns:")

for column in inventory.columns:

    print(
        f"  - {column}"
    )


# ============================================================
# FIND PRODUCT COLUMN
# ============================================================

product_candidates = [

    "sku_id",
    "sku",
    "product_id",
    "product",
    "product_id",
    "item_id"

]


product_col = None


for column in product_candidates:

    if column in inventory.columns:

        product_col = column

        break


if product_col is None:

    # Fallback: search by name

    for column in inventory.columns:

        name = column.lower()

        if (
            "sku" in name
            or "product" in name
        ):

            product_col = column

            break


if product_col is None:

    print()
    print(
        "ERROR: Product/SKU column could not be detected."
    )

    sys.exit(1)


print()
print(
    f"Product column: {product_col}"
)


# ============================================================
# FIND INVENTORY COLUMN
# ============================================================

inventory_candidates = [

    "inventory_quantity",
    "inventory_qty",
    "stock_quantity",
    "stock_qty",
    "current_stock",
    "stock",
    "quantity",
    "inventory"

]


inventory_col = None


for column in inventory_candidates:

    if column in inventory.columns:

        inventory_col = column

        break


if inventory_col is None:

    for column in inventory.columns:

        name = column.lower()

        if (
            "inventory" in name
            or "stock" in name
        ):

            inventory_col = column

            break


if inventory_col is None:

    print()
    print(
        "ERROR: Inventory/stock column could not be detected."
    )

    sys.exit(1)


print(
    f"Inventory column: {inventory_col}"
)


# ============================================================
# CALCULATE RISK
# ============================================================

print()
print(
    "Calculating risk scores..."
)


risk_df = calculate_risk_score(
    inventory.copy()
)


# ============================================================
# VERIFY REQUIRED COLUMNS
# ============================================================

required_columns = [

    "risk_score",
    "risk_level"

]


missing = [

    column

    for column in required_columns

    if column not in risk_df.columns

]


if missing:

    print()
    print(
        "ERROR: Risk engine did not create:"
    )

    for column in missing:

        print(
            f"  - {column}"
        )

    sys.exit(1)


# ============================================================
# CREATE VERIFICATION TABLE
# ============================================================

verification = pd.DataFrame()


verification["SKU"] = (

    risk_df[
        product_col
    ]

    .astype(str)

)


verification["Current Stock"] = pd.to_numeric(

    risk_df[
        inventory_col
    ],

    errors="coerce"

).fillna(0)


verification["Risk Score"] = pd.to_numeric(

    risk_df[
        "risk_score"
    ],

    errors="coerce"

).fillna(0)


verification["Risk Level"] = (

    risk_df[
        "risk_level"
    ]

    .astype(str)

)


# ============================================================
# INVENTORY STATUS
# ============================================================

def get_inventory_status(stock):

    if stock <= 0:

        return "Out of Stock"

    elif stock <= 10:

        return "Critical"

    elif stock <= 50:

        return "Low"

    else:

        return "Healthy"


verification[
    "Inventory Status"
] = verification[
    "Current Stock"
].apply(
    get_inventory_status
)


# ============================================================
# CHECK RISK LEVEL AGAINST SCORE
# ============================================================

def expected_risk_level(score):

    if score >= 75:

        return "CRITICAL"

    elif score >= 50:

        return "HIGH"

    elif score >= 25:

        return "MEDIUM"

    else:

        return "LOW"


verification[
    "Expected Risk Level"
] = verification[
    "Risk Score"
].apply(
    expected_risk_level
)


verification[
    "Risk Level Correct"
] = (

    verification[
        "Risk Level"
    ]

    .str.upper()

    ==

    verification[
        "Expected Risk Level"
    ]

)


# ============================================================
# CHECK INVENTORY STATUS
# ============================================================

verification[
    "Expected Inventory Status"
] = verification[
    "Current Stock"
].apply(
    get_inventory_status
)


verification[
    "Inventory Status Correct"
] = (

    verification[
        "Inventory Status"
    ]

    ==

    verification[
        "Expected Inventory Status"
    ]

)


# ============================================================
# OVERALL VERIFICATION
# ============================================================

verification[
    "Overall Correct"
] = (

    verification[
        "Risk Level Correct"
    ]

    &

    verification[
        "Inventory Status Correct"
    ]

)


# ============================================================
# SUMMARY
# ============================================================

total_products = len(
    verification
)


correct_products = int(

    verification[
        "Overall Correct"
    ].sum()

)


incorrect_products = (

    total_products
    -
    correct_products

)


print()
print("=" * 70)
print("VERIFICATION SUMMARY")
print("=" * 70)

print()
print(
    f"Total Products : {total_products:,}"
)

print(
    f"Correct        : {correct_products:,}"
)

print(
    f"Incorrect      : {incorrect_products:,}"
)


if total_products > 0:

    accuracy = (
        correct_products
        /
        total_products
        *
        100
    )

else:

    accuracy = 0


print(
    f"Verification   : {accuracy:.2f}%"
)


# ============================================================
# SHOW INCORRECT PRODUCTS
# ============================================================

incorrect = verification[
    ~verification[
        "Overall Correct"
    ]
].copy()


if not incorrect.empty:

    print()
    print("=" * 70)
    print("PRODUCTS REQUIRING ATTENTION")
    print("=" * 70)

    print()

    print(

        incorrect[
            [
                "SKU",
                "Current Stock",
                "Risk Score",
                "Risk Level",
                "Expected Risk Level",
                "Inventory Status",
                "Expected Inventory Status"
            ]
        ]

        .to_string(
            index=False
        )

    )

else:

    print()
    print("=" * 70)
    print("ALL PRODUCTS VERIFIED SUCCESSFULLY")
    print("=" * 70)


# ============================================================
# SPECIFIC SKU 1002
# ============================================================

sku_1002 = verification[
    verification[
        "SKU"
    ] == "1002"
]


if not sku_1002.empty:

    print()
    print("=" * 70)
    print("SKU 1002 VERIFICATION")
    print("=" * 70)

    print()

    print(
        sku_1002.to_string(
            index=False
        )
    )


# ============================================================
# SAVE REPORT
# ============================================================

output_file = (

    PROJECT_ROOT
    /
    "data"
    /
    "processed"
    /
    "product_verification.csv"

)


output_file.parent.mkdir(
    parents=True,
    exist_ok=True
)


verification.to_csv(
    output_file,
    index=False
)


print()
print(
    f"Verification report saved to:"
)

print(
    output_file
)


print()
print("=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
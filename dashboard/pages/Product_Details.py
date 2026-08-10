# ============================================================
# PROJECT FORESIGHT
# PRODUCT DETAILS DASHBOARD
# ============================================================

import sys
from pathlib import Path

# ============================================================
# PROJECT ROOT FIX
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# COMMON UTILITIES
# ============================================================

from dashboard_utils import (
    apply_dashboard_style,
    load_sales_data,
    load_inventory_data,
    find_product_column,
    find_inventory_column,
    chart_layout,
    footer
)


from src.risk_scoring import (
    calculate_risk_score
)


# ============================================================
# COMMON STYLE
# ============================================================

apply_dashboard_style()


# ============================================================
# PAGE HEADER
# ============================================================

st.title(
    "🔎 Product Details"
)

st.write(
    "Explore individual SKU performance, inventory health, "
    "demand and risk."
)

st.divider()


# ============================================================
# LOAD DATA
# ============================================================

inventory = load_inventory_data()

sales = load_sales_data()


# ============================================================
# VALIDATE INVENTORY
# ============================================================

if inventory.empty:

    st.error(
        "Inventory data could not be loaded."
    )

    st.stop()


# ============================================================
# CALCULATE RISK
# ============================================================

try:

    risk_df = calculate_risk_score(
        inventory,
        sales,
        demand_days=90
    )

except Exception as e:

    st.error(
        "Risk calculation failed."
    )

    st.exception(e)

    st.stop()


# ============================================================
# VALIDATE RISK DATA
# ============================================================

if risk_df.empty:

    st.error(
        "No product risk information was generated."
    )

    st.stop()


# ============================================================
# FIND PRODUCT COLUMN
# ============================================================

product_col = find_product_column(
    risk_df
)


# ============================================================
# FIND INVENTORY COLUMN
# ============================================================

inventory_col = find_inventory_column(
    risk_df
)


# ============================================================
# PRODUCT COLUMN VALIDATION
# ============================================================

if product_col is None:

    st.error(
        "No product / SKU column was detected."
    )

    st.write(
        "Available columns:"
    )

    st.write(
        list(risk_df.columns)
    )

    st.stop()


# ============================================================
# PRODUCT LIST
# ============================================================

products = sorted(

    risk_df[
        product_col
    ]
    .dropna()
    .astype(str)
    .unique()
    .tolist()

)


if not products:

    st.warning(
        "No products were found."
    )

    st.stop()


# ============================================================
# PRODUCT SELECTOR
# ============================================================

selected_product = st.selectbox(

    "🔍 Select Product / SKU",

    products

)


# ============================================================
# SELECT PRODUCT
# ============================================================

product_data = risk_df[

    risk_df[
        product_col
    ]
    .astype(str)
    ==
    selected_product

].copy()


if product_data.empty:

    st.warning(
        "No data found for the selected product."
    )

    st.stop()


# ============================================================
# SELECT FIRST RECORD
# ============================================================

row = product_data.iloc[0]


# ============================================================
# SAFE NUMERIC FUNCTION
# ============================================================

def safe_float(
    value,
    default=0.0
):

    try:

        value = float(value)

        if np.isfinite(value):

            return value

        return default

    except Exception:

        return default


# ============================================================
# CURRENT STOCK
# ============================================================

if inventory_col is not None:

    current_stock = safe_float(
        row[inventory_col]
    )

else:

    # Try common inventory column names
    possible_stock_columns = [

        "stock_on_hand",

        "inventory_quantity",

        "current_stock",

        "quantity",

        "stock"

    ]

    current_stock = 0.0

    for column in possible_stock_columns:

        if column in row.index:

            current_stock = safe_float(
                row[column]
            )

            break


# ============================================================
# RISK SCORE
# ============================================================

risk_score = safe_float(

    row.get(
        "risk_score",
        0
    )

)


risk_score = max(
    0,
    min(
        100,
        risk_score
    )
)


# ============================================================
# RISK LEVEL
# ============================================================

risk_level = str(

    row.get(
        "risk_level",
        "UNKNOWN"
    )

)


risk_level = risk_level.upper()


# ============================================================
# INVENTORY STATUS
# ============================================================

inventory_status = str(

    row.get(
        "inventory_status",
        ""
    )

)


# If risk engine did not provide inventory status,
# calculate a basic status.

if not inventory_status:

    if current_stock <= 0:

        inventory_status = "OUT OF STOCK"

    elif current_stock <= 10:

        inventory_status = "CRITICAL"

    elif current_stock <= 50:

        inventory_status = "LOW STOCK"

    else:

        inventory_status = "HEALTHY"


# ============================================================
# PRODUCT HEADER
# ============================================================

st.header(

    f"🛍️ Product / SKU: {selected_product}"

)


# ============================================================
# PRODUCT KPI SECTION
# ============================================================

c1, c2, c3, c4 = st.columns(4)


# ------------------------------------------------------------
# CURRENT STOCK
# ------------------------------------------------------------

with c1:

    st.metric(

        "📦 Current Stock",

        f"{current_stock:,.0f}"

    )


# ------------------------------------------------------------
# RISK SCORE
# ------------------------------------------------------------

with c2:

    st.metric(

        "⚠️ Risk Score",

        f"{risk_score:.1f}/100"

    )


# ------------------------------------------------------------
# RISK LEVEL
# ------------------------------------------------------------

with c3:

    st.metric(

        "🎯 Risk Level",

        risk_level

    )


# ------------------------------------------------------------
# INVENTORY STATUS
# ------------------------------------------------------------

with c4:

    st.metric(

        "📊 Inventory Status",

        inventory_status

    )


st.divider()


# ============================================================
# ADDITIONAL PRODUCT METRICS
# ============================================================

st.subheader(
    "📈 Product Intelligence"
)


m1, m2, m3, m4 = st.columns(4)


# ============================================================
# RECENT DEMAND
# ============================================================

recent_demand = safe_float(

    row.get(
        "recent_demand",
        0
    )

)


with m1:

    st.metric(

        "📊 Recent Demand",

        f"{recent_demand:,.0f}"

    )


# ============================================================
# DAYS OF COVER
# ============================================================

days_of_cover = safe_float(

    row.get(
        "days_of_cover",
        0
    )

)


with m2:

    if days_of_cover > 1000:

        cover_text = "1000+ days"

    else:

        cover_text = (
            f"{days_of_cover:.1f} days"
        )

    st.metric(

        "📅 Days of Cover",

        cover_text

    )


# ============================================================
# REORDER POINT
# ============================================================

reorder_point = safe_float(

    row.get(
        "reorder_point",
        0
    )

)


with m3:

    st.metric(

        "🔄 Reorder Point",

        f"{reorder_point:,.0f}"

    )


# ============================================================
# SAFETY STOCK
# ============================================================

safety_stock = safe_float(

    row.get(
        "safety_stock",
        0
    )

)


with m4:

    st.metric(

        "🛡️ Safety Stock",

        f"{safety_stock:,.0f}"

    )


st.divider()


# ============================================================
# RISK ANALYSIS
# ============================================================

st.header(
    "🎯 Risk Analysis"
)


c1, c2 = st.columns(2)


# ============================================================
# RISK GAUGE
# ============================================================

with c1:

    theme_base = st.get_option(
        "theme.base"
    )

    if theme_base == "dark":

        plotly_template = "plotly_dark"

    else:

        plotly_template = "plotly_white"


    # Determine gauge color
    if risk_score >= 75:

        gauge_color = "#DC2626"

    elif risk_score >= 50:

        gauge_color = "#F97316"

    elif risk_score >= 25:

        gauge_color = "#EAB308"

    else:

        gauge_color = "#22C55E"


    fig = go.Figure(

        go.Indicator(

            mode="gauge+number",

            value=risk_score,

            title={
                "text": "Product Risk Score"
            },

            number={
                "suffix": "/100"
            },

            gauge={

                "axis": {

                    "range": [
                        0,
                        100
                    ]

                },

                "bar": {

                    "color": gauge_color,

                    "thickness": 0.7

                },

                "steps": [

                    {

                        "range": [
                            0,
                            25
                        ],

                        "color": "#DCFCE7"

                    },

                    {

                        "range": [
                            25,
                            50
                        ],

                        "color": "#FEF3C7"

                    },

                    {

                        "range": [
                            50,
                            75
                        ],

                        "color": "#FFEDD5"

                    },

                    {

                        "range": [
                            75,
                            100
                        ],

                        "color": "#FEE2E2"

                    }

                ]

            }

        )

    )


    fig.update_layout(

        template=plotly_template,

        height=400,

        margin=dict(

            l=20,

            r=20,

            t=60,

            b=20

        )

    )


    st.plotly_chart(

        fig,

        width="stretch"

    )


# ============================================================
# RISK COMPONENTS
# ============================================================

with c2:

    stock_risk = safe_float(

        row.get(
            "stock_risk_score",
            0
        )

    )


    demand_risk = safe_float(

        row.get(
            "demand_risk_score",
            0
        )

    )


    risk_components = pd.DataFrame(

        {

            "Metric": [

                "Stock Risk",

                "Demand Risk",

                "Overall Risk"

            ],

            "Score": [

                stock_risk,

                demand_risk,

                risk_score

            ]

        }

    )


    fig = px.bar(

        risk_components,

        x="Metric",

        y="Score",

        range_y=[
            0,
            100
        ],

        title="Risk Components",

        text="Score"

    )


    fig.update_traces(

        texttemplate="%{text:.1f}",

        textposition="outside"

    )


    chart_layout(

        fig,

        400

    )


    st.plotly_chart(

        fig,

        width="stretch"

    )


st.divider()


# ============================================================
# INVENTORY COVERAGE
# ============================================================

st.header(
    "📦 Inventory Coverage"
)


coverage_data = pd.DataFrame(

    {

        "Metric": [

            "Current Stock",

            "Reorder Point",

            "Safety Stock"

        ],

        "Quantity": [

            current_stock,

            reorder_point,

            safety_stock

        ]

    }

)


fig = px.bar(

    coverage_data,

    x="Metric",

    y="Quantity",

    title="Stock vs Replenishment Levels",

    text="Quantity"

)


fig.update_traces(

    texttemplate="%{text:,.0f}",

    textposition="outside"

)


chart_layout(

    fig,

    380

)


st.plotly_chart(

    fig,

    width="stretch"

)


st.divider()


# ============================================================
# BUSINESS RECOMMENDATION
# ============================================================

st.header(
    "💡 Business Recommendation"
)


if risk_score >= 75:

    st.error(

        "🔴 URGENT: This SKU has critical risk. "
        "Immediate inventory intervention is recommended."

    )


elif risk_score >= 50:

    st.warning(

        "🟠 HIGH PRIORITY: This SKU requires close monitoring. "
        "Review demand, stock coverage and replenishment needs."

    )


elif risk_score >= 25:

    st.warning(

        "🟡 MONITOR: This SKU has moderate risk. "
        "Continue monitoring demand and inventory."

    )


else:

    st.success(

        "🟢 HEALTHY: This SKU currently has low risk. "
        "Continue normal inventory monitoring."

    )


# ============================================================
# STOCK-SPECIFIC RECOMMENDATION
# ============================================================

if current_stock <= 0:

    st.error(

        "🚨 Stock is currently zero. "
        "Immediate replenishment should be considered."

    )


elif current_stock <= reorder_point:

    st.warning(

        "🔄 Current stock is at or below the reorder point. "
        "Consider replenishment."

    )


elif current_stock <= safety_stock:

    st.warning(

        "🛡️ Current stock is close to safety-stock levels. "
        "Monitor demand carefully."

    )


else:

    st.success(

        "✅ Current stock is above the immediate "
        "replenishment threshold."

    )


st.divider()


# ============================================================
# PRODUCT DATA
# ============================================================

st.header(
    "📋 Product Data"
)


# Display selected product information vertically.

display_data = product_data.T.copy()


display_data.columns = [
    "Value"
]


st.dataframe(

    display_data,

    width="stretch",

    height=450

)


st.divider()


# ============================================================
# DOWNLOAD PRODUCT DATA
# ============================================================

csv_data = product_data.to_csv(
    index=False
)


st.download_button(

    label="⬇️ Download Product Data",

    data=csv_data,

    file_name=(
        f"{selected_product}_details.csv"
    ),

    mime="text/csv"

)


# ============================================================
# FOOTER
# ============================================================

footer()
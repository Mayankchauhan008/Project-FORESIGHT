# ============================================================
# PROJECT FORESIGHT
# EXECUTIVE SUMMARY
# ============================================================

import sys
from pathlib import Path


# ============================================================
# PROJECT ROOT FIX
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


# ============================================================
# IMPORTS
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px


from dashboard_utils import (
    apply_dashboard_style,
    load_sales_data,
    load_inventory_data,
    find_sales_column,
    numeric_series,
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
# HEADER
# ============================================================

st.title(
    "📋 Executive Summary"
)

st.write(
    "High-level business intelligence for strategic retail decision-making."
)

st.divider()


# ============================================================
# LOAD DATA
# ============================================================

sales = load_sales_data()

inventory = load_inventory_data()


if inventory.empty:

    st.error(
        "Inventory data could not be loaded."
    )

    st.stop()


if sales.empty:

    st.warning(
        "Sales data could not be loaded. "
        "Risk calculations will use inventory information only."
    )


# ============================================================
# RISK ENGINE
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


if risk_df.empty:

    st.error(
        "No risk records were generated."
    )

    st.stop()


# ============================================================
# SALES METRICS
# ============================================================

sales_col = find_sales_column(
    sales
)


if sales_col:

    total_revenue = numeric_series(
        sales,
        sales_col
    ).sum()

else:

    total_revenue = 0


transactions = len(
    sales
)


# IMPORTANT:
# Inventory has store-level records.
# risk_df is already aggregated at SKU level.
#
# Therefore:
# DO NOT use len(inventory)
# Use len(risk_df)
#
products = len(
    risk_df
)


# ============================================================
# RISK COUNTS
# ============================================================

critical = int(

    (
        risk_df[
            "risk_level"
        ]
        ==
        "CRITICAL"
    ).sum()

)


high = int(

    (
        risk_df[
            "risk_level"
        ]
        ==
        "HIGH"
    ).sum()

)


medium = int(

    (
        risk_df[
            "risk_level"
        ]
        ==
        "MEDIUM"
    ).sum()

)


low = int(

    (
        risk_df[
            "risk_level"
        ]
        ==
        "LOW"
    ).sum()

)


# ============================================================
# PORTFOLIO RISK
# ============================================================

average_risk = float(

    risk_df[
        "risk_score"
    ].mean()

)


# ============================================================
# INVENTORY HEALTH
# ============================================================

out_of_stock = int(

    (
        risk_df[
            "inventory_status"
        ]
        ==
        "OUT OF STOCK"
    ).sum()

)


critical_stock = int(

    (
        risk_df[
            "inventory_status"
        ]
        ==
        "CRITICAL"
    ).sum()

)


low_stock = int(

    (
        risk_df[
            "inventory_status"
        ]
        ==
        "LOW STOCK"
    ).sum()

)


overstock = int(

    (
        risk_df[
            "inventory_status"
        ]
        ==
        "OVERSTOCK"
    ).sum()

)


healthy_stock = int(

    (
        risk_df[
            "inventory_status"
        ]
        ==
        "HEALTHY"
    ).sum()

)


# ============================================================
# KPI SECTION
# ============================================================

c1, c2, c3, c4, c5 = st.columns(5)


# ------------------------------------------------------------
# REVENUE
# ------------------------------------------------------------

with c1:

    st.metric(

        "💰 Revenue",

        f"₹{total_revenue:,.0f}"

    )


# ------------------------------------------------------------
# TRANSACTIONS
# ------------------------------------------------------------

with c2:

    st.metric(

        "🧾 Transactions",

        f"{transactions:,}"

    )


# ------------------------------------------------------------
# UNIQUE PRODUCTS
# ------------------------------------------------------------

with c3:

    st.metric(

        "🛍️ Unique SKUs",

        f"{products:,}"

    )


# ------------------------------------------------------------
# CRITICAL
# ------------------------------------------------------------

with c4:

    st.metric(

        "🔴 Critical",

        critical

    )


# ------------------------------------------------------------
# HIGH
# ------------------------------------------------------------

with c5:

    st.metric(

        "🟠 High Risk",

        high

    )


st.divider()


# ============================================================
# BUSINESS HEALTH
# ============================================================

st.header(
    "📊 Business Health"
)


c1, c2 = st.columns(2)


# ============================================================
# REVENUE CHART
# ============================================================

with c1:

    if sales_col and not sales.empty:

        try:

            sales_chart = sales.copy()


            # ------------------------------------------------
            # Prefer actual SKU for revenue analysis
            # ------------------------------------------------

            if "sku_id" in sales_chart.columns:

                group_column = "sku_id"

                title = (
                    "Top 10 Revenue-Contributing SKUs"
                )

            elif "store_id" in sales_chart.columns:

                group_column = "store_id"

                title = (
                    "Top 10 Revenue-Contributing Stores"
                )

            else:

                group_column = None


            if group_column:

                sales_chart[sales_col] = pd.to_numeric(

                    sales_chart[
                        sales_col
                    ],

                    errors="coerce"

                ).fillna(0)


                sales_summary = (

                    sales_chart

                    .groupby(
                        group_column,
                        as_index=False
                    )[sales_col]

                    .sum()

                    .sort_values(

                        sales_col,

                        ascending=False

                    )

                    .head(10)

                )


                fig = px.bar(

                    sales_summary,

                    x=sales_col,

                    y=group_column,

                    orientation="h",

                    title=title,

                    text=sales_col

                )


                fig.update_traces(

                    texttemplate="₹%{text:,.0f}",

                    textposition="outside"

                )


                chart_layout(

                    fig,

                    450

                )


                st.plotly_chart(

                    fig,

                    width="stretch"

                )

            else:

                st.info(
                    "No suitable revenue grouping column found."
                )


        except Exception as e:

            st.info(
                "Revenue chart could not be generated."
            )


    else:

        st.info(
            "Sales data is not available."
        )


# ============================================================
# RISK PIE CHART
# ============================================================

with c2:

    risk_data = pd.DataFrame(

        {

            "Risk Level": [

                "Critical",

                "High",

                "Medium",

                "Low"

            ],

            "Count": [

                critical,

                high,

                medium,

                low

            ]

        }

    )


    # --------------------------------------------------------
    # Remove zero-count categories
    # --------------------------------------------------------

    risk_data = risk_data[
        risk_data["Count"] > 0
    ]


    if not risk_data.empty:

        fig = px.pie(

            risk_data,

            names="Risk Level",

            values="Count",

            hole=0.5,

            title="SKU Risk Health",

            color="Risk Level",

            color_discrete_map={

                "Critical": "#DC2626",

                "High": "#F97316",

                "Medium": "#EAB308",

                "Low": "#22C55E"

            }

        )


        fig.update_traces(

            textinfo="percent+label",

            hovertemplate=(

                "<b>%{label}</b><br>"
                "SKUs: %{value}<br>"
                "Share: %{percent}"

                "<extra></extra>"

            )

        )


        chart_layout(

            fig,

            450

        )


        st.plotly_chart(

            fig,

            width="stretch"

        )

    else:

        st.info(
            "No risk classification data available."
        )


st.divider()


# ============================================================
# INVENTORY HEALTH SUMMARY
# ============================================================

st.header(
    "📦 Inventory Health"
)


health_data = pd.DataFrame(

    {

        "Inventory Status": [

            "Out of Stock",

            "Critical",

            "Low Stock",

            "Overstock",

            "Healthy"

        ],

        "SKUs": [

            out_of_stock,

            critical_stock,

            low_stock,

            overstock,

            healthy_stock

        ]

    }

)


health_data = health_data[
    health_data["SKUs"] > 0
]


if not health_data.empty:

    fig = px.bar(

        health_data,

        x="Inventory Status",

        y="SKUs",

        title="Inventory Health by SKU",

        text="SKUs"

    )


    fig.update_traces(

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

else:

    st.info(
        "No inventory health data available."
    )


st.divider()


# ============================================================
# RISK OVERVIEW
# ============================================================

st.header(
    "⚠️ Risk Overview"
)


risk_distribution = pd.DataFrame(

    {

        "Risk Level": [

            "Critical",

            "High",

            "Medium",

            "Low"

        ],

        "SKUs": [

            critical,

            high,

            medium,

            low

        ]

    }

)


risk_distribution = risk_distribution[
    risk_distribution["SKUs"] > 0
]


if not risk_distribution.empty:

    fig = px.bar(

        risk_distribution,

        x="Risk Level",

        y="SKUs",

        title="SKU Risk Distribution",

        text="SKUs",

        color="Risk Level",

        color_discrete_map={

            "Critical": "#DC2626",

            "High": "#F97316",

            "Medium": "#EAB308",

            "Low": "#22C55E"

        }

    )


    fig.update_traces(

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


else:

    st.info(
        "No risk distribution data available."
    )


# ============================================================
# PORTFOLIO RISK SCORE
# ============================================================

st.metric(

    "🎯 Average Portfolio Risk",

    f"{average_risk:.1f}/100"

)


# ============================================================
# DYNAMIC PORTFOLIO MESSAGE
# ============================================================

if average_risk >= 75:

    st.error(

        "🔴 Portfolio risk is critical. "
        "Immediate inventory intervention is recommended."

    )

elif average_risk >= 50:

    st.warning(

        "🟠 Portfolio risk is high. "
        "Prioritize the highest-risk SKUs."

    )

elif average_risk >= 25:

    st.warning(

        "🟡 Portfolio risk is moderate. "
        "Review inventory coverage and replenishment plans."

    )

else:

    st.success(

        "🟢 Overall portfolio risk is low. "
        "Continue monitoring demand and inventory levels."

    )


# ============================================================
# RISK STATUS MESSAGES
# ============================================================

if out_of_stock > 0:

    st.error(

        f"🔴 {out_of_stock:,} SKU(s) are currently "
        f"out of stock and require immediate replenishment."

    )


if critical_stock > 0:

    st.error(

        f"🚨 {critical_stock:,} SKU(s) are at or below "
        f"safety stock."

    )


if low_stock > 0:

    st.warning(

        f"🟠 {low_stock:,} SKU(s) are below the "
        f"reorder point."

    )


if overstock > 0:

    st.info(

        f"📦 {overstock:,} SKU(s) show potential "
        f"overstock conditions."

    )


st.divider()


# ============================================================
# TOP RISK PRODUCTS
# ============================================================

st.header(
    "🚨 Highest Risk SKUs"
)


top_risk = (

    risk_df

    .sort_values(

        "risk_score",

        ascending=False

    )

    .head(10)

)


top_columns = [

    column

    for column in [

        "sku_id",

        "stock_on_hand",

        "reorder_point",

        "recent_demand",

        "days_of_cover",

        "risk_score",

        "risk_level",

        "inventory_status",

        "recommended_action"

    ]

    if column in top_risk.columns

]


if not top_risk.empty:

    st.dataframe(

        top_risk[
            top_columns
        ],

        width="stretch",

        height=350

    )

else:

    st.info(
        "No high-risk SKUs found."
    )


st.divider()


# ============================================================
# BUSINESS RECOMMENDATIONS
# ============================================================

st.header(
    "💡 Business Recommendations"
)


# ============================================================
# RECOMMENDATION 1
# ============================================================

if critical > 0 or out_of_stock > 0:

    st.error(

        "1️⃣ Prioritize immediate replenishment for "
        f"{max(critical, out_of_stock):,} critical SKU(s)."

    )

else:

    st.success(

        "1️⃣ No immediate critical replenishment "
        "pressure detected."

    )


# ============================================================
# RECOMMENDATION 2
# ============================================================

if high > 0:

    st.warning(

        f"2️⃣ Closely monitor {high:,} high-risk SKU(s) "
        "and review their demand coverage."

    )

else:

    st.success(

        "2️⃣ No SKU is currently classified as high risk."

    )


# ============================================================
# RECOMMENDATION 3
# ============================================================

if overstock > 0:

    st.info(

        f"3️⃣ Review {overstock:,} potential overstock SKU(s) "
        "to reduce excess inventory and working capital."

    )

else:

    st.success(

        "3️⃣ No significant overstock group detected."

    )


# ============================================================
# RECOMMENDATION 4
# ============================================================

st.success(

    "4️⃣ Use recent demand and inventory coverage "
    "together when planning replenishment."

)


# ============================================================
# RECOMMENDATION 5
# ============================================================

st.info(

    "5️⃣ Review SKU-level risk before making store-level "
    "inventory allocation decisions."

)


st.divider()


# ============================================================
# EXECUTIVE STATUS
# ============================================================

st.header(
    "🚀 Executive Status"
)


c1, c2, c3, c4 = st.columns(4)


with c1:

    if not sales.empty:

        st.success(
            "✅ Data Pipeline"
        )

    else:

        st.warning(
            "⚠️ Sales Data"
        )


with c2:

    st.success(
        "✅ Forecasting"
    )


with c3:

    if not risk_df.empty:

        st.success(
            "✅ Risk Engine"
        )

    else:

        st.error(
            "❌ Risk Engine"
        )


with c4:

    st.success(
        "✅ Dashboard"
    )


# ============================================================
# DATA QUALITY NOTE
# ============================================================

st.divider()


st.caption(

    f"Risk analysis is performed at SKU level using "
    f"{len(inventory):,} inventory records aggregated "
    f"into {len(risk_df):,} unique SKUs. "
    f"Recent demand is calculated from the latest 90 days "
    f"of available sales data."

)


# ============================================================
# FOOTER
# ============================================================

footer()
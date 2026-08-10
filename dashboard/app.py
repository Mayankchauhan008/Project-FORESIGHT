import sys
from pathlib import Path

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


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
    find_inventory_column,
    find_product_column,
    numeric_series,
    chart_layout,
    footer
)


# ============================================================
# PAGE STYLE
# ============================================================

apply_dashboard_style()


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Foresight | Retail AI",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "🛒 Project Foresight"
)

st.subheader(
    "Retail AI Intelligence Platform"
)

st.write(
    """
    Transform retail data into actionable business decisions using
    sales analytics, demand forecasting, inventory intelligence and
    risk scoring.
    """
)


# ============================================================
# LOAD DATA
# ============================================================

sales = load_sales_data()

inventory = load_inventory_data()


# ============================================================
# DATA STATUS
# ============================================================

sales_available = not sales.empty

inventory_available = not inventory.empty


# ============================================================
# BUSINESS KPIs
# ============================================================

sales_col = find_sales_column(
    sales
) if sales_available else None


inventory_col = find_inventory_column(
    inventory
) if inventory_available else None


product_col = find_product_column(
    inventory
) if inventory_available else None


# Revenue

if sales_available and sales_col:

    total_revenue = numeric_series(
        sales,
        sales_col
    ).sum()

else:

    total_revenue = 0


# Transactions

transactions = len(
    sales
) if sales_available else 0


# Products

products = len(
    inventory
) if inventory_available else 0


# Inventory

if inventory_available and inventory_col:

    inventory_units = numeric_series(
        inventory,
        inventory_col
    ).sum()

else:

    inventory_units = 0


# ============================================================
# COMMAND CENTER
# ============================================================

st.divider()

st.header(
    "📊 Business Command Center"
)


c1, c2, c3, c4 = st.columns(4)


with c1:

    st.metric(
        "💰 Total Revenue",
        f"₹{total_revenue:,.0f}"
    )


with c2:

    st.metric(
        "🧾 Transactions",
        f"{transactions:,}"
    )


with c3:

    st.metric(
        "🛍️ Products / SKUs",
        f"{products:,}"
    )


with c4:

    st.metric(
        "📦 Inventory Units",
        f"{inventory_units:,.0f}"
    )


# ============================================================
# PLATFORM HEALTH
# ============================================================

st.divider()

st.header(
    "🧠 Intelligence Platform Health"
)


h1, h2, h3, h4 = st.columns(4)


with h1:

    if sales_available:

        st.success(
            "✅ Sales Data\n\nLoaded"
        )

    else:

        st.error(
            "❌ Sales Data\n\nUnavailable"
        )


with h2:

    if inventory_available:

        st.success(
            "✅ Inventory Data\n\nLoaded"
        )

    else:

        st.error(
            "❌ Inventory Data\n\nUnavailable"
        )


with h3:

    if products > 0:

        st.success(
            "✅ Product Intelligence\n\nActive"
        )

    else:

        st.warning(
            "⚠️ Product Intelligence\n\nUnavailable"
        )


with h4:

    st.success(
        "✅ AI Pipeline\n\nReady"
    )


# ============================================================
# BUSINESS OVERVIEW
# ============================================================

st.divider()

st.header(
    "📈 Business Overview"
)


left, right = st.columns(2)


# ============================================================
# REVENUE CONTRIBUTORS
# ============================================================

with left:

    if sales_available and sales_col:

        try:

            category_col = sales.columns[0]

            revenue_summary = (

                sales

                .groupby(
                    category_col
                )[sales_col]

                .sum()

                .reset_index()

                .sort_values(
                    sales_col,
                    ascending=False
                )

                .head(10)

            )

            fig = px.bar(

                revenue_summary,

                x=sales_col,

                y=category_col,

                orientation="h",

                title="Top Revenue Contributors"

            )

            chart_layout(
                fig,
                420
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        except Exception:

            st.info(
                "Revenue visualization is unavailable."
            )

    else:

        st.info(
            "Sales data is unavailable."
        )


# ============================================================
# INVENTORY DISTRIBUTION
# ============================================================

with right:

    if inventory_available and inventory_col:

        try:

            inventory_values = numeric_series(
                inventory,
                inventory_col
            )

            fig = px.histogram(

                inventory_values,

                nbins=25,

                title="Inventory Quantity Distribution"

            )

            chart_layout(
                fig,
                420
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        except Exception:

            st.info(
                "Inventory visualization is unavailable."
            )

    else:

        st.info(
            "Inventory data is unavailable."
        )


# ============================================================
# RETAIL AI PIPELINE
# ============================================================

st.divider()

st.header(
    "🔄 Retail AI Pipeline"
)


p1, p2, p3, p4, p5, p6 = st.columns(6)


with p1:

    st.info(
        "📁\n\nRaw Data"
    )


with p2:

    st.info(
        "🧹\n\nCleaning"
    )


with p3:

    st.info(
        "🔍\n\nEDA"
    )


with p4:

    st.info(
        "⚙️\n\nFeatures"
    )


with p5:

    st.info(
        "📈\n\nForecast"
    )


with p6:

    st.info(
        "📦\n\nInventory"
    )


# ============================================================
# BUSINESS CAPABILITIES
# ============================================================

st.divider()

st.header(
    "🚀 Business Capabilities"
)


b1, b2, b3 = st.columns(3)


with b1:

    st.subheader(
        "📊 Sales Intelligence"
    )

    st.write(
        """
        Understand revenue, transactions,
        product performance and sales trends.
        """
    )


with b2:

    st.subheader(
        "📈 Demand Forecasting"
    )

    st.write(
        """
        Estimate future demand and support
        smarter purchasing decisions.
        """
    )


with b3:

    st.subheader(
        "⚠️ Risk Intelligence"
    )

    st.write(
        """
        Identify inventory risk and prioritize
        products requiring business attention.
        """
    )


# ============================================================
# QUICK NAVIGATION
# ============================================================

st.divider()

st.header(
    "🧭 Explore the Platform"
)


q1, q2, q3, q4 = st.columns(4)


with q1:

    st.info(
        "📊 Sales Analytics\n\nRevenue & sales performance"
    )


with q2:

    st.info(
        "📈 Demand Forecast\n\nFuture demand prediction"
    )


with q3:

    st.info(
        "📦 Inventory Dashboard\n\nStock health & replenishment"
    )


with q4:

    st.info(
        "⚠️ Risk Dashboard\n\nRisk monitoring & actions"
    )


# ============================================================
# FOOTER
# ============================================================

footer()
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import plotly.express as px

from dashboard_utils import (
    apply_dashboard_style,
    load_sales_data,
    load_inventory_data,
    calculate_product_risk,
    get_channel_revenue,
    get_top_products,
    chart_layout,
    footer,
)

st.set_page_config(
    page_title="FORESIGHT | Retail AI Intelligence",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_dashboard_style()

sales = load_sales_data()
inventory = load_inventory_data()

if inventory.empty:
    risk = pd.DataFrame()
else:
    risk = calculate_product_risk(
        inventory,
        sales,
        demand_days=90
    )

sales_available = not sales.empty
inventory_available = not inventory.empty

total_revenue = (
    float(
        pd.to_numeric(
            sales["dashboard_revenue"],
            errors="coerce"
        )
        .fillna(0)
        .sum()
    )
    if sales_available and "dashboard_revenue" in sales.columns
    else 0.0
)

transactions = len(sales)

unique_sales_skus = (
    int(
        sales["sku_id"]
        .astype(str)
        .replace("nan", "")
        .nunique()
    )
    if sales_available and "sku_id" in sales.columns
    else 0
)

inventory_units = (
    float(
        pd.to_numeric(
            inventory["stock_on_hand"],
            errors="coerce"
        )
        .fillna(0)
        .sum()
    )
    if inventory_available and "stock_on_hand" in inventory.columns
    else 0.0
)

critical = (
    int((risk["risk_level"] == "Critical").sum())
    if not risk.empty else 0
)

high = (
    int((risk["risk_level"] == "High").sum())
    if not risk.empty else 0
)

medium = (
    int((risk["risk_level"] == "Medium").sum())
    if not risk.empty else 0
)

low = (
    int((risk["risk_level"] == "Low").sum())
    if not risk.empty else 0
)

st.markdown(
    """
    <div class="hero-section">
        <div style="font-size:48px;">🛒</div>
        <div class="hero-title">FORESIGHT</div>
        <div class="hero-subtitle">
            Retail AI Intelligence Platform
        </div>
        <div class="hero-text">
            A decision-support dashboard for sales analytics,
            demand forecasting, inventory intelligence and
            product-level risk assessment.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.header("📊 Business Overview")

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
        "🛍️ Unique Sales SKUs",
        f"{unique_sales_skus:,}"
    )

with c4:
    st.metric(
        "📦 Inventory Units",
        f"{inventory_units:,.0f}"
    )

st.divider()

st.header("🔄 Retail Intelligence Pipeline")

p1, p2, p3, p4 = st.columns(4)

with p1:
    st.markdown(
        """
        <div class="module-card">
            <div style="font-size:34px;">📁</div>
            <div class="module-title">Data Loading</div>
            <div class="module-text">
                Sales and inventory sources are loaded
                and normalized.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with p2:
    st.markdown(
        """
        <div class="module-card">
            <div style="font-size:34px;">🧹</div>
            <div class="module-title">Data Processing</div>
            <div class="module-text">
                Dates, quantities, revenue and inventory
                fields are standardized.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with p3:
    st.markdown(
        """
        <div class="module-card">
            <div style="font-size:34px;">🔍</div>
            <div class="module-title">Analytics</div>
            <div class="module-text">
                Sales trends, product performance and
                inventory health are analyzed.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with p4:
    st.markdown(
        """
        <div class="module-card">
            <div style="font-size:34px;">🤖</div>
            <div class="module-title">AI Intelligence</div>
            <div class="module-text">
                Demand coverage and product risk are
                converted into actions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

st.header("⚠️ Inventory Risk Snapshot")

r1, r2, r3, r4 = st.columns(4)

with r1:
    st.metric("🔴 Critical", critical)

with r2:
    st.metric("🟠 High", high)

with r3:
    st.metric("🟡 Medium", medium)

with r4:
    st.metric("🟢 Low", low)

if critical:
    st.error(
        f"{critical:,} SKU(s) require immediate attention."
    )
elif high:
    st.warning(
        f"{high:,} SKU(s) should be prioritized for review."
    )
else:
    st.success(
        "No critical or high-risk SKUs are currently detected."
    )

if not risk.empty:

    risk_chart = (
        risk["risk_level"]
        .value_counts()
        .reindex(
            ["Critical", "High", "Medium", "Low"],
            fill_value=0
        )
        .rename_axis("Risk Level")
        .reset_index(name="SKU Count")
    )

    fig = px.bar(
        risk_chart,
        x="Risk Level",
        y="SKU Count",
        color="Risk Level",
        color_discrete_map={
            "Critical": "#dc2626",
            "High": "#f97316",
            "Medium": "#eab308",
            "Low": "#22c55e",
        },
        text="SKU Count",
        title="SKU Risk Distribution",
    )

    fig.update_traces(
        textposition="outside"
    )

    chart_layout(
        fig,
        360
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

st.divider()

st.header("📈 Business Snapshot")

left, right = st.columns(2)

with left:

    channel = get_channel_revenue()

    if channel.empty:

        st.info(
            "Channel revenue data is unavailable."
        )

    else:

        fig = px.bar(
            channel,
            x="dashboard_revenue",
            y="channel",
            orientation="h",
            title="Revenue by Sales Channel",
            text="dashboard_revenue",
        )

        fig.update_traces(
            texttemplate="₹%{text:,.0f}",
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

with right:

    top = get_top_products(10)

    if top.empty:

        st.info(
            "Top-product sales data is unavailable."
        )

    else:

        fig = px.bar(
            top,
            x="Revenue",
            y="sku_id",
            orientation="h",
            title="Top Revenue SKUs",
            text="Revenue",
        )

        fig.update_traces(
            texttemplate="₹%{text:,.0f}",
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

st.header("🧭 Platform Modules")

m1, m2, m3 = st.columns(3)

with m1:
    st.info(
        "📊 Sales Analytics\n\n"
        "Revenue, units, categories and top SKUs."
    )

with m2:
    st.info(
        "🔮 Demand Forecast\n\n"
        "Historical demand, trend and transparent baseline forecast."
    )

with m3:
    st.info(
        "📦 Inventory Dashboard\n\n"
        "Stock, reorder status and inventory health."
    )

m4, m5, m6 = st.columns(3)

with m4:
    st.warning(
        "⚠️ Risk Dashboard\n\n"
        "Product-level shortage and coverage risk."
    )

with m5:
    st.info(
        "🔎 Product Details\n\n"
        "Investigate any individual SKU."
    )

with m6:
    st.info(
        "📋 Executive Summary\n\n"
        "Strategic business view for decision makers."
    )

st.divider()

st.header("✅ Data Health")

h1, h2, h3 = st.columns(3)

with h1:
    st.success(
        f"Sales loaded: {len(sales):,} records"
        if sales_available
        else "Sales data unavailable"
    )

with h2:
    st.success(
        f"Inventory loaded: {len(inventory):,} records"
        if inventory_available
        else "Inventory data unavailable"
    )

with h3:
    st.success(
        f"Risk engine: {len(risk):,} SKU-level records"
        if not risk.empty
        else "Risk engine unavailable"
    )

footer()
import streamlit as st
import pandas as pd
import plotly.express as px

import streamlit as st

from auth import (
    require_login,
    render_user_sidebar,
)

from dashboard_utils import (
    apply_dashboard_style,
    load_sales_data,
    load_inventory_data,
    calculate_product_risk,
    get_category_revenue,
    get_channel_revenue,
    get_top_products,
    get_executive_metrics,
    chart_layout,
    footer,
)

require_login()
render_user_sidebar()

st.set_page_config(
    page_title="Executive Summary",
    page_icon="📋",
    layout="wide",
)

apply_dashboard_style()

sales = load_sales_data()
inventory = load_inventory_data()
risk = calculate_product_risk(inventory, sales, demand_days=90)
metrics = get_executive_metrics()

st.title("📋 Executive Summary")
st.caption(
    "High-level business intelligence for strategic retail decision-making."
)
st.divider()

# ------------------------------------------------------------
# KPIs
# ------------------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric("💰 Revenue", f"₹{metrics['revenue']:,.0f}")
with c2:
    st.metric("🧾 Transactions", f"{metrics['transactions']:,}")
with c3:
    st.metric("📦 Unique SKUs", f"{metrics['unique_skus']:,}")
with c4:
    st.metric("🔴 Critical", f"{metrics['critical']:,}")
with c5:
    st.metric("🟠 High Risk", f"{metrics['high']:,}")

st.divider()

# ------------------------------------------------------------
# Business health
# ------------------------------------------------------------
st.header("📊 Business Health")
left, right = st.columns(2)

with left:
    channel = get_channel_revenue()
    st.subheader("💰 Revenue by Sales Channel")
    if channel.empty:
        st.info("Sales-channel revenue data unavailable.")
    else:
        fig = px.bar(
            channel,
            x="channel",
            y="dashboard_revenue",
            title="Revenue by Sales Channel",
            text="dashboard_revenue",
        )
        fig.update_traces(
            texttemplate="₹%{text:,.0f}",
            textposition="outside",
        )
        chart_layout(fig, 420)
        st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("🚨 SKU Risk Health")
    if risk.empty:
        st.info("Risk data unavailable.")
    else:
        risk_counts = (
            risk["risk_level"]
            .value_counts()
            .reindex(
                ["Critical", "High", "Medium", "Low"],
                fill_value=0,
            )
            .rename_axis("Risk Level")
            .reset_index(name="SKU Count")
        )
        fig = px.pie(
            risk_counts,
            names="Risk Level",
            values="SKU Count",
            hole=0.45,
            title="SKU Risk Distribution",
            color="Risk Level",
            color_discrete_map={
                "Critical": "#dc2626",
                "High": "#f97316",
                "Medium": "#eab308",
                "Low": "#22c55e",
            },
        )
        chart_layout(fig, 420)
        st.plotly_chart(fig, width="stretch")

st.divider()

# ------------------------------------------------------------
# Inventory health
# ------------------------------------------------------------
st.header("📦 Inventory Health")

if risk.empty:
    st.info("Inventory risk data unavailable.")
else:
    health = (
        risk["inventory_status"]
        .value_counts()
        .reindex(
            [
                "OUT OF STOCK",
                "CRITICAL",
                "REORDER",
                "OVERSTOCK",
                "HEALTHY",
            ],
            fill_value=0,
        )
        .rename_axis("Inventory Status")
        .reset_index(name="SKU Count")
    )

    fig = px.bar(
        health,
        x="Inventory Status",
        y="SKU Count",
        title="Inventory Status by SKU",
        text="SKU Count",
    )
    fig.update_traces(textposition="outside")
    chart_layout(fig, 380)
    st.plotly_chart(fig, width="stretch")

st.divider()

# ------------------------------------------------------------
# Top products
# ------------------------------------------------------------
st.header("🏆 Top Products")

top = get_top_products(10)

if top.empty:
    st.info("Product sales data unavailable.")
else:
    st.dataframe(
        top,
        width="stretch",
        hide_index=True,
    )

st.divider()

# ------------------------------------------------------------
# Risk overview and recommendations
# ------------------------------------------------------------
st.header("🎯 Executive Risk Position")

average_risk = metrics.get("average_risk", 0.0)
st.metric("Average Portfolio Risk", f"{average_risk:.1f}/100")

if average_risk >= 75:
    st.error(
        "Critical portfolio position. Immediate management attention is recommended."
    )
elif average_risk >= 50:
    st.warning(
        "High portfolio risk. Prioritize the highest-risk SKUs."
    )
elif average_risk >= 25:
    st.info(
        "Moderate portfolio risk. Continue close monitoring."
    )
else:
    st.success(
        "Overall portfolio risk is currently low."
    )

critical = metrics["critical"]
high = metrics["high"]

if critical:
    st.error(
        f"🔴 {critical:,} SKU(s) require immediate attention."
    )
elif high:
    st.warning(
        f"🟠 {high:,} SKU(s) should be prioritized."
    )
else:
    st.success(
        "🟢 No critical/high SKU group is currently detected."
    )

st.subheader("💡 Business Recommendations")
st.write("1. Use demand trends to improve purchasing decisions.")
st.write("2. Prioritize SKUs below safety/reorder thresholds.")
st.write("3. Review overstock products to reduce working capital.")
st.write("4. Combine sales, demand and inventory views before major replenishment decisions.")

footer()
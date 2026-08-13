import streamlit as st
import pandas as pd
import plotly.express as px

from dashboard_utils import (
    apply_dashboard_style,
    load_inventory_data,
    load_sales_data,
    calculate_product_risk,
    chart_layout,
    footer,
)

st.set_page_config(
    page_title="Risk Dashboard",
    page_icon="🚨",
    layout="wide",
)

apply_dashboard_style()

st.title(
    "🚨 Risk Dashboard"
)

st.caption(
    "Identify product-level shortage, demand-coverage and overstock risk."
)

st.divider()

inventory = load_inventory_data()
sales = load_sales_data()

if inventory.empty:

    st.error(
        "Inventory data is unavailable."
    )

    st.stop()

risk = calculate_product_risk(
    inventory,
    sales,
    demand_days=90
)

if risk.empty:

    st.error(
        "No SKU-level risk records were generated."
    )

    st.stop()

levels = [
    "Critical",
    "High",
    "Medium",
    "Low"
]

counts = (
    risk["risk_level"]
    .value_counts()
    .reindex(
        levels,
        fill_value=0
    )
)

critical = int(
    counts["Critical"]
)

high = int(
    counts["High"]
)

medium = int(
    counts["Medium"]
)

low = int(
    counts["Low"]
)

average_risk = float(
    risk["risk_score"].mean()
)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(
        "🔴 Critical",
        f"{critical:,}"
    )

with c2:
    st.metric(
        "🟠 High",
        f"{high:,}"
    )

with c3:
    st.metric(
        "🟡 Medium",
        f"{medium:,}"
    )

with c4:
    st.metric(
        "🟢 Low",
        f"{low:,}"
    )

with c5:
    st.metric(
        "🎯 Avg Risk",
        f"{average_risk:.1f}/100"
    )

st.divider()

left, right = st.columns(2)

with left:

    risk_chart = (
        counts
        .rename_axis("Risk Level")
        .reset_index(name="SKU Count")
    )

    fig = px.bar(
        risk_chart,
        x="Risk Level",
        y="SKU Count",
        text="SKU Count",
        title="Risk Level Distribution"
    )

    fig.update_traces(
        textposition="outside"
    )

    chart_layout(
        fig,
        420
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

with right:

    fig = px.pie(
        risk_chart,
        names="Risk Level",
        values="SKU Count",
        hole=0.50,
        title="Risk Share"
    )

    chart_layout(
        fig,
        420
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

st.divider()

st.subheader(
    "📈 Risk Score Distribution"
)

fig = px.histogram(
    risk,
    x="risk_score",
    nbins=20,
    title="Portfolio Risk Score Distribution"
)

fig.update_xaxes(
    range=[0, 100]
)

chart_layout(
    fig,
    380
)

st.plotly_chart(
    fig,
    width="stretch"
)

if critical:

    st.error(
        f"{critical:,} SKU(s) have critical risk."
    )

elif high:

    st.warning(
        f"{high:,} SKU(s) have high risk."
    )

else:

    st.success(
        "No critical or high-risk SKU group is currently detected."
    )

st.divider()

st.header(
    "🚨 Highest Risk Products"
)

highest = (
    risk
    .sort_values(
        "risk_score",
        ascending=False
    )
    .head(25)
)

columns = [
    "sku_id",
    "stock_on_hand",
    "reorder_point",
    "safety_stock",
    "recent_demand",
    "days_of_cover",
    "stock_risk_score",
    "demand_risk_score",
    "risk_score",
    "risk_level",
    "inventory_status",
    "recommended_action",
]

columns = [
    c for c in columns
    if c in highest.columns
]

st.dataframe(
    highest[columns],
    width="stretch",
    height=500,
    hide_index=True
)

st.divider()

st.header(
    "📦 Potential Overstock"
)

overstock = (
    risk[
        risk["inventory_status"]
        ==
        "OVERSTOCK"
    ]
    .sort_values(
        "stock_reorder_ratio",
        ascending=False
    )
    .head(20)
)

if overstock.empty:

    st.success(
        "No significant overstock group is currently detected."
    )

else:

    st.dataframe(
        overstock[columns],
        width="stretch",
        height=400,
        hide_index=True
    )

st.download_button(
    "⬇️ Download Risk Report",
    risk.to_csv(index=False),
    "risk_report.csv",
    "text/csv"
)

footer()
import streamlit as st
import pandas as pd
import plotly.express as px

from auth import (
    require_login,
    render_user_sidebar,
)

from dashboard_utils import (
    apply_dashboard_style,
    load_inventory_data,
    calculate_product_risk,
    chart_layout,
    footer,
)

require_login()
render_user_sidebar()

st.set_page_config(
    page_title="Inventory Dashboard",
    page_icon="📦",
    layout="wide",
)

apply_dashboard_style()

st.title(
    "📦 Inventory Dashboard"
)

st.caption(
    "Inventory availability, stock levels and replenishment intelligence."
)

st.divider()

inventory = load_inventory_data()

if inventory.empty:

    st.error(
        "Inventory data is unavailable."
    )

    st.stop()

risk = calculate_product_risk(
    inventory,
    pd.DataFrame(),
    demand_days=90
)

total_skus = (
    inventory["sku_id"].nunique()
    if "sku_id" in inventory.columns
    else len(inventory)
)

total_stock = float(
    pd.to_numeric(
        inventory["stock_on_hand"],
        errors="coerce"
    )
    .fillna(0)
    .sum()
)

if "sku_id" in risk.columns:
    stock_by_sku = (
        risk.groupby(
            "sku_id",
            as_index=False
        )["stock_on_hand"]
        .sum()
    )
else:
    stock_by_sku = pd.DataFrame()

risk_counts = (
    risk["risk_level"]
    .value_counts()
    .reindex(
        [
            "Critical",
            "High",
            "Medium",
            "Low"
        ],
        fill_value=0
    )
)

critical = int(
    risk_counts["Critical"]
)

high = int(
    risk_counts["High"]
)

medium = int(
    risk_counts["Medium"]
)

low = int(
    risk_counts["Low"]
)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(
        "📦 Total SKUs",
        f"{total_skus:,}"
    )

with c2:
    st.metric(
        "📊 Total Stock",
        f"{total_stock:,.0f}"
    )

with c3:
    st.metric(
        "🔴 Critical",
        f"{critical:,}"
    )

with c4:
    st.metric(
        "🟠 High",
        f"{high:,}"
    )

with c5:
    st.metric(
        "🟢 Low Risk",
        f"{low:,}"
    )

st.divider()

left, right = st.columns(2)

with left:

    st.subheader(
        "📊 Stock Distribution"
    )

    fig = px.histogram(
        inventory,
        x="stock_on_hand",
        nbins=30,
        title="Stock on Hand"
    )

    fig.update_xaxes(
        title="Stock Units"
    )

    fig.update_yaxes(
        title="Inventory Records"
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

    st.subheader(
        "🚨 Risk Distribution"
    )

    risk_chart = (
        risk_counts
        .rename_axis("Risk Level")
        .reset_index(name="SKU Count")
    )

    fig = px.pie(
        risk_chart,
        names="Risk Level",
        values="SKU Count",
        hole=0.45,
        title="Inventory Risk"
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

st.header(
    "🔄 Reorder Analysis"
)

if "reorder_point" in inventory.columns:

    inv_view = inventory.copy()

    inv_view["reorder_status"] = (
        inv_view["stock_on_hand"]
        <=
        inv_view["reorder_point"]
    ).map(
        {
            True: "REORDER",
            False: "HEALTHY"
        }
    )

    reorder = inv_view[
        inv_view["reorder_status"] == "REORDER"
    ]

    st.metric(
        "🔄 Store-SKU Records Requiring Reorder",
        f"{len(reorder):,}"
    )

    if reorder.empty:

        st.success(
            "No store-SKU inventory records currently require reorder."
        )

    else:

        show_cols = [
            "store_id",
            "sku_id",
            "stock_on_hand",
            "reorder_point",
            "safety_stock",
            "reorder_status"
        ]

        show_cols = [
            c for c in show_cols
            if c in reorder.columns
        ]

        st.dataframe(
            reorder[show_cols],
            width="stretch",
            height=400,
            hide_index=True
        )

else:

    st.info(
        "Reorder-point information is unavailable."
    )

st.divider()

st.header(
    "📈 Inventory Risk Scores"
)

if not risk.empty:

    fig = px.histogram(
        risk,
        x="risk_score",
        nbins=20,
        title="SKU Risk Score Distribution"
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

st.download_button(
    "⬇️ Download Inventory Intelligence",
    risk.to_csv(index=False),
    "inventory_intelligence.csv",
    "text/csv"
)

footer()
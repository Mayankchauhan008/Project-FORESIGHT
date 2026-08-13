import streamlit as st
import pandas as pd
import plotly.express as px

from dashboard_utils import (
    apply_dashboard_style,
    load_sales_data,
    get_channel_revenue,
    get_top_products,
    chart_layout,
    footer,
)

st.set_page_config(
    page_title="Sales Analytics",
    page_icon="📊",
    layout="wide",
)

apply_dashboard_style()

st.title(
    "📊 Sales Analytics"
)

st.caption(
    "Detailed analysis of retail sales performance."
)

st.divider()

sales = load_sales_data()

if sales.empty:
    st.error(
        "Sales data could not be loaded."
    )
    st.stop()

revenue = float(
    pd.to_numeric(
        sales["dashboard_revenue"],
        errors="coerce"
    )
    .fillna(0)
    .sum()
)

quantity = float(
    pd.to_numeric(
        sales["quantity"],
        errors="coerce"
    )
    .fillna(0)
    .sum()
)

transactions = len(
    sales
)

average_transaction = (
    revenue / transactions
    if transactions
    else 0
)

unique_skus = (
    int(
        sales["sku_id"]
        .astype(str)
        .nunique()
    )
    if "sku_id" in sales.columns
    else 0
)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(
        "💰 Revenue",
        f"₹{revenue:,.0f}"
    )

with c2:
    st.metric(
        "🧾 Transactions",
        f"{transactions:,}"
    )

with c3:
    st.metric(
        "📦 Units Sold",
        f"{quantity:,.0f}"
    )

with c4:
    st.metric(
        "💳 Avg Transaction",
        f"₹{average_transaction:,.0f}"
    )

with c5:
    st.metric(
        "🛍️ SKUs",
        f"{unique_skus:,}"
    )

st.divider()

if (
    "date" in sales.columns
    and sales["date"].notna().any()
):

    daily = (
        sales
        .dropna(
            subset=["date"]
        )
        .groupby(
            "date",
            as_index=False
        )["dashboard_revenue"]
        .sum()
        .sort_values("date")
    )

    st.subheader(
        "📈 Daily Revenue"
    )

    fig = px.line(
        daily,
        x="date",
        y="dashboard_revenue",
        title="Revenue Trend",
    )

    fig.update_yaxes(
        title="Revenue",
        tickprefix="₹"
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

left, right = st.columns(2)

with left:

    st.subheader(
        "🛒 Revenue by Sales Channel"
    )

    channel = get_channel_revenue()

    if channel.empty:

        st.info(
            "Sales-channel information unavailable."
        )

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

        fig.update_yaxes(
            tickprefix="₹"
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
        "📦 Units by Sales Channel"
    )

    if "channel" in sales.columns:

        channel_quantity = (
            sales
            .groupby(
                "channel",
                as_index=False
            )["quantity"]
            .sum()
            .sort_values(
                "quantity",
                ascending=False
            )
        )

    else:

        channel_quantity = pd.DataFrame()

    if channel_quantity.empty:

        st.info(
            "No sales-channel quantity data available."
        )

    else:

        fig = px.bar(
            channel_quantity,
            x="channel",
            y="quantity",
            title="Units Sold by Sales Channel",
            text="quantity",
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

st.divider()

st.header(
    "🏆 Top 20 Products"
)

top = get_top_products(
    20
)

if top.empty:

    st.info(
        "No SKU-level sales data available."
    )

else:

    st.dataframe(
        top,
        width="stretch",
        hide_index=True
    )

    fig = px.bar(
        top.head(10),
        x="Revenue",
        y="sku_id",
        orientation="h",
        title="Top 10 Revenue SKUs",
        text="Revenue",
    )

    fig.update_traces(
        texttemplate="₹%{text:,.0f}",
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

st.divider()

st.header(
    "🔍 Sales Data Quality"
)

q1, q2, q3 = st.columns(3)

with q1:

    st.metric(
        "Valid Dates",
        f"{sales['date'].notna().sum():,}"
    )

with q2:

    st.metric(
        "Positive Quantity Rows",
        f"{(sales['quantity'] > 0).sum():,}"
    )

with q3:

    st.metric(
        "Positive Revenue Rows",
        f"{(sales['dashboard_revenue'] > 0).sum():,}"
    )

footer()
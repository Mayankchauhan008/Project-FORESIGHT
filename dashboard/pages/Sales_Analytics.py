import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# COMMON STYLE
# ============================================================

from dashboard_utils import (
    apply_dashboard_style,
    load_sales_data,
    find_date_column,
    find_sales_column,
    find_quantity_column,
    find_product_column,
    find_store_column,
    numeric_series,
    chart_layout,
    footer
)

apply_dashboard_style()


# ============================================================
# PAGE CONFIG
# ============================================================

st.title(
    "📊 Sales Analytics"
)

st.write(
    "Analyze revenue, transactions, products and store performance."
)

st.divider()


# ============================================================
# LOAD DATA
# ============================================================

sales = load_sales_data()


if sales.empty:

    st.error(
        "Sales data could not be loaded."
    )

    st.stop()


# ============================================================
# DETECT COLUMNS
# ============================================================

date_col = find_date_column(
    sales
)

sales_col = find_sales_column(
    sales
)

quantity_col = find_quantity_column(
    sales
)

product_col = find_product_column(
    sales
)

store_col = find_store_column(
    sales
)


# ============================================================
# DATE CONVERSION
# ============================================================

if date_col:

    sales[date_col] = pd.to_datetime(
        sales[date_col],
        errors="coerce"
    )


# ============================================================
# FILTERS
# ============================================================

with st.expander(
    "🎛️ Filters"
):

    filtered = sales.copy()

    if product_col:

        product_values = sorted(
            filtered[product_col]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_products = st.multiselect(
            "Product / SKU",
            product_values
        )

        if selected_products:

            filtered = filtered[
                filtered[product_col]
                .astype(str)
                .isin(selected_products)
            ]


    if store_col:

        store_values = sorted(
            filtered[store_col]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_stores = st.multiselect(
            "Store",
            store_values
        )

        if selected_stores:

            filtered = filtered[
                filtered[store_col]
                .astype(str)
                .isin(selected_stores)
            ]


# ============================================================
# KPI
# ============================================================

if sales_col:

    sales_values = numeric_series(
        filtered,
        sales_col
    )

    total_revenue = sales_values.sum()

    average_transaction = sales_values.mean()

else:

    total_revenue = 0

    average_transaction = 0


transactions = len(filtered)


if quantity_col:

    units_sold = numeric_series(
        filtered,
        quantity_col
    ).sum()

else:

    units_sold = 0


# ============================================================
# KPI DISPLAY
# ============================================================

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
        "💵 Avg Transaction",
        f"₹{average_transaction:,.0f}"
    )


with c4:

    st.metric(
        "📦 Units Sold",
        f"{units_sold:,.0f}"
    )


st.divider()


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3 = st.tabs(
    [
        "📈 Revenue Trend",
        "🏆 Product Performance",
        "🏪 Store Performance"
    ]
)


# ============================================================
# REVENUE TREND
# ============================================================

with tab1:

    if date_col and sales_col:

        trend = (
            filtered
            .dropna(subset=[date_col])
            .groupby(date_col)[sales_col]
            .sum()
            .reset_index()
        )

        fig = px.line(
            trend,
            x=date_col,
            y=sales_col,
            markers=True,
            title="Revenue Trend"
        )

        chart_layout(
            fig,
            450
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )


        monthly = filtered.copy()

        monthly["Month"] = (
            monthly[date_col]
            .dt.to_period("M")
            .astype(str)
        )

        monthly = (
            monthly
            .groupby("Month")[sales_col]
            .sum()
            .reset_index()
        )

        fig2 = px.bar(
            monthly,
            x="Month",
            y=sales_col,
            title="Monthly Revenue"
        )

        chart_layout(
            fig2,
            400
        )

        st.plotly_chart(
            fig2,
            width="stretch"
        )

    else:

        st.warning(
            "Date or sales column was not detected."
        )


# ============================================================
# PRODUCT PERFORMANCE
# ============================================================

with tab2:

    if product_col and sales_col:

        product_data = (
            filtered
            .groupby(product_col)[sales_col]
            .sum()
            .reset_index()
            .sort_values(
                sales_col,
                ascending=False
            )
            .head(15)
        )

        fig = px.bar(
            product_data,
            x=sales_col,
            y=product_col,
            orientation="h",
            title="Top Products by Revenue"
        )

        chart_layout(
            fig,
            500
        )

        fig.update_layout(
            yaxis={
                "categoryorder": "total ascending"
            }
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    else:

        st.warning(
            "Product or sales column was not detected."
        )


# ============================================================
# STORE PERFORMANCE
# ============================================================

with tab3:

    if store_col and sales_col:

        store_data = (
            filtered
            .groupby(store_col)[sales_col]
            .sum()
            .reset_index()
            .sort_values(
                sales_col,
                ascending=False
            )
            .head(15)
        )

        fig = px.bar(
            store_data,
            x=store_col,
            y=sales_col,
            title="Top Stores by Revenue"
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

        st.warning(
            "Store or sales column was not detected."
        )


# ============================================================
# DATA TABLE
# ============================================================

with st.expander(
    "📋 View Sales Data"
):

    st.dataframe(
        filtered,
        width="stretch",
        height=400
    )


footer()
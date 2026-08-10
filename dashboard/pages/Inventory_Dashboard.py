import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# COMMON STYLE
# ============================================================

from dashboard_utils import (
    apply_dashboard_style,
    load_inventory_data,
    load_recommendation_data,
    find_product_column,
    find_store_column,
    find_inventory_column,
    numeric_series,
    chart_layout,
    footer
)

apply_dashboard_style()


# ============================================================
# HEADER
# ============================================================

st.title(
    "📦 Inventory Dashboard"
)

st.write(
    "Monitor stock health, shortages and replenishment opportunities."
)

st.divider()


# ============================================================
# LOAD DATA
# ============================================================

inventory = load_inventory_data()

recommendations = load_recommendation_data()


if inventory.empty:

    st.error(
        "Inventory data could not be loaded."
    )

    st.stop()


# ============================================================
# COLUMNS
# ============================================================

inventory_col = find_inventory_column(
    inventory
)

product_col = find_product_column(
    inventory
)

store_col = find_store_column(
    inventory
)


# ============================================================
# INVENTORY VALUE
# ============================================================

if inventory_col:

    inventory["Inventory_Value"] = numeric_series(
        inventory,
        inventory_col
    )

else:

    inventory["Inventory_Value"] = 0


# ============================================================
# INVENTORY STATUS
# ============================================================

inventory["Inventory_Status"] = pd.cut(
    inventory["Inventory_Value"],
    bins=[
        -1,
        0,
        10,
        50,
        float("inf")
    ],
    labels=[
        "Out of Stock",
        "Critical",
        "Low",
        "Healthy"
    ]
)


# ============================================================
# KPIs
# ============================================================

total_products = len(
    inventory
)

out_of_stock = (
    inventory["Inventory_Status"]
    ==
    "Out of Stock"
).sum()

critical = (
    inventory["Inventory_Status"]
    ==
    "Critical"
).sum()

low_stock = (
    inventory["Inventory_Status"]
    ==
    "Low"
).sum()

healthy = (
    inventory["Inventory_Status"]
    ==
    "Healthy"
).sum()


c1, c2, c3, c4 = st.columns(4)


with c1:

    st.metric(
        "🛍️ Products",
        f"{total_products:,}"
    )


with c2:

    st.metric(
        "🔴 Out of Stock",
        f"{out_of_stock:,}"
    )


with c3:

    st.metric(
        "🟠 Critical",
        f"{critical:,}"
    )


with c4:

    st.metric(
        "🟢 Healthy",
        f"{healthy:,}"
    )


st.divider()


# ============================================================
# INVENTORY HEALTH
# ============================================================

st.header(
    "📊 Inventory Health"
)


c1, c2 = st.columns(2)


with c1:

    status = (
        inventory["Inventory_Status"]
        .value_counts()
        .reset_index()
    )

    status.columns = [
        "Status",
        "Count"
    ]

    fig = px.pie(
        status,
        names="Status",
        values="Count",
        hole=0.5,
        title="Inventory Status Distribution"
    )

    chart_layout(
        fig,
        430
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


with c2:

    fig = px.histogram(
        inventory,
        x="Inventory_Value",
        nbins=30,
        title="Inventory Quantity Distribution"
    )

    chart_layout(
        fig,
        430
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


st.divider()


# ============================================================
# REPLENISHMENT
# ============================================================

st.header(
    "🚨 Replenishment"
)


if not recommendations.empty:

    st.dataframe(
        recommendations,
        width="stretch",
        height=400
    )

    st.download_button(
        "⬇️ Download Recommendations",
        recommendations.to_csv(
            index=False
        ),
        "inventory_recommendations.csv",
        "text/csv"
    )

else:

    critical_data = inventory[
        inventory["Inventory_Value"] <= 10
    ]

    st.dataframe(
        critical_data,
        width="stretch",
        height=400
    )


st.divider()


# ============================================================
# STORE INVENTORY
# ============================================================

st.header(
    "🏪 Store Inventory"
)


if store_col:

    store_data = (
        inventory
        .groupby(store_col)["Inventory_Value"]
        .sum()
        .reset_index()
        .sort_values(
            "Inventory_Value",
            ascending=False
        )
    )

    fig = px.bar(
        store_data,
        x=store_col,
        y="Inventory_Value",
        title="Inventory by Store"
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
        "Store column was not detected."
    )


# ============================================================
# INSIGHTS
# ============================================================

st.header(
    "💡 Inventory Insights"
)


if out_of_stock > 0:

    st.error(
        f"🔴 {out_of_stock} products are out of stock."
    )


if critical > 0:

    st.warning(
        f"🟠 {critical} products require immediate attention."
    )


if low_stock > 0:

    st.warning(
        f"🟡 {low_stock} products have low inventory."
    )


if healthy > 0:

    st.success(
        f"🟢 {healthy} products have healthy inventory."
    )


footer()
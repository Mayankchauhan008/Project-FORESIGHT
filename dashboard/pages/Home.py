import sys
from pathlib import Path

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

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
# STYLE
# ============================================================

apply_dashboard_style()


# ============================================================
# HEADER
# ============================================================

st.title(
    "🏠 Retail Operations Home"
)

st.write(
    """
    Monitor the current health of your retail operation,
    identify problems and focus on the actions that matter most.
    """
)

st.divider()


# ============================================================
# LOAD DATA
# ============================================================

sales = load_sales_data()

inventory = load_inventory_data()


if sales.empty and inventory.empty:

    st.error(
        "No retail data is available."
    )

    st.stop()


# ============================================================
# COLUMN DETECTION
# ============================================================

sales_col = find_sales_column(
    sales
) if not sales.empty else None


inventory_col = find_inventory_column(
    inventory
) if not inventory.empty else None


product_col = find_product_column(
    inventory
) if not inventory.empty else None


# ============================================================
# BASIC METRICS
# ============================================================

if sales_col:

    revenue = numeric_series(
        sales,
        sales_col
    ).sum()

else:

    revenue = 0


transactions = len(
    sales
)


products = len(
    inventory
)


if inventory_col:

    stock = numeric_series(
        inventory,
        inventory_col
    )

    total_stock = stock.sum()

    out_of_stock = (
        stock <= 0
    ).sum()

    critical_stock = (
        (stock > 0)
        &
        (stock <= 10)
    ).sum()

    low_stock = (
        (stock > 10)
        &
        (stock <= 50)
    ).sum()

    healthy_stock = (
        stock > 50
    ).sum()

else:

    total_stock = 0

    out_of_stock = 0

    critical_stock = 0

    low_stock = 0

    healthy_stock = 0


# ============================================================
# TODAY'S RETAIL SNAPSHOT
# ============================================================

st.header(
    "📌 Retail Snapshot"
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
        "🛍️ SKUs",
        f"{products:,}"
    )


with c4:

    st.metric(
        "📦 Stock Units",
        f"{total_stock:,.0f}"
    )


with c5:

    st.metric(
        "🔴 Stock Issues",
        f"{out_of_stock + critical_stock:,}"
    )


# ============================================================
# INVENTORY HEALTH
# ============================================================

st.divider()

st.header(
    "📦 Inventory Health"
)


left, right = st.columns(2)


# ============================================================
# INVENTORY STATUS
# ============================================================

with left:

    inventory_status = pd.DataFrame(

        {
            "Status": [
                "Healthy",
                "Low",
                "Critical",
                "Out of Stock"
            ],

            "Products": [
                healthy_stock,
                low_stock,
                critical_stock,
                out_of_stock
            ]
        }

    )


    fig = px.pie(

        inventory_status,

        names="Status",

        values="Products",

        hole=0.5,

        title="Current Inventory Health"

    )


    chart_layout(
        fig,
        420
    )


    st.plotly_chart(
        fig,
        width="stretch"
    )


# ============================================================
# STOCK DISTRIBUTION
# ============================================================

with right:

    if inventory_col:

        fig = px.histogram(

            stock,

            nbins=25,

            title="Stock Quantity Distribution"

        )


        chart_layout(
            fig,
            420
        )


        st.plotly_chart(
            fig,
            width="stretch"
        )

    else:

        st.info(
            "Inventory quantity column could not be detected."
        )


# ============================================================
# ATTENTION REQUIRED
# ============================================================

st.divider()

st.header(
    "🚨 Attention Required"
)


a1, a2, a3 = st.columns(3)


with a1:

    if out_of_stock > 0:

        st.error(
            f"""
            🔴 Out of Stock

            **{out_of_stock:,} products**

            Immediate replenishment may be required.
            """
        )

    else:

        st.success(
            """
            🟢 Out of Stock

            No products are currently out of stock.
            """
        )


with a2:

    if critical_stock > 0:

        st.warning(
            f"""
            🟠 Critical Stock

            **{critical_stock:,} products**

            Review these products for replenishment.
            """
        )

    else:

        st.success(
            """
            🟢 Critical Stock

            No critical stock levels detected.
            """
        )


with a3:

    if low_stock > 0:

        st.warning(
            f"""
            🟡 Low Stock

            **{low_stock:,} products**

            Monitor demand before inventory falls further.
            """
        )

    else:

        st.success(
            """
            🟢 Low Stock

            Inventory levels are currently healthy.
            """
        )


# ============================================================
# TOP PRODUCTS
# ============================================================

st.divider()

st.header(
    "🏆 Inventory Leaders"
)


if (
    inventory_col
    and product_col
    and not inventory.empty
):

    try:

        top_products = (

            inventory[[
                product_col,
                inventory_col
            ]]

            .copy()

        )


        top_products[
            inventory_col
        ] = pd.to_numeric(

            top_products[
                inventory_col
            ],

            errors="coerce"

        ).fillna(0)


        top_products = (

            top_products

            .sort_values(
                inventory_col,
                ascending=False
            )

            .head(10)

        )


        fig = px.bar(

            top_products,

            x=inventory_col,

            y=product_col,

            orientation="h",

            title="Products with Highest Available Stock"

        )


        chart_layout(
            fig,
            450
        )


        st.plotly_chart(
            fig,
            width="stretch"
        )


    except Exception:

        st.info(
            "Top product visualization is unavailable."
        )

else:

    st.info(
        "Product and inventory information is unavailable."
    )


# ============================================================
# OPERATIONAL CHECKLIST
# ============================================================

st.divider()

st.header(
    "✅ Operational Checklist"
)


check1, check2 = st.columns(2)


with check1:

    st.write(
        "### Data & Analytics"
    )

    st.success(
        "Sales data loaded"
    )

    st.success(
        "Inventory data loaded"
    )

    st.success(
        "Product intelligence available"
    )


with check2:

    st.write(
        "### Recommended Actions"
    )

    if out_of_stock > 0:

        st.error(
            "Review out-of-stock products"
        )

    if critical_stock > 0:

        st.warning(
            "Prioritize critical inventory"
        )

    if low_stock > 0:

        st.info(
            "Monitor low-stock products"
        )

    if (
        out_of_stock == 0
        and critical_stock == 0
        and low_stock == 0
    ):

        st.success(
            "No immediate inventory action required"
        )


# ============================================================
# NAVIGATION GUIDE
# ============================================================

st.divider()

st.header(
    "🧭 Continue Analysis"
)


n1, n2, n3, n4 = st.columns(4)


with n1:

    st.info(
        """
        📊 **Sales Analytics**

        Understand sales performance.
        """
    )


with n2:

    st.info(
        """
        📈 **Demand Forecast**

        Estimate future demand.
        """
    )


with n3:

    st.info(
        """
        ⚠️ **Risk Dashboard**

        Find high-risk products.
        """
    )


with n4:

    st.info(
        """
        🔎 **Product Details**

        Investigate individual SKUs.
        """
    )


# ============================================================
# FOOTER
# ============================================================

footer()
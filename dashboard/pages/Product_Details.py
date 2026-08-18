import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from auth import (
    require_login,
    render_user_sidebar,
)

from dashboard_utils import (
    apply_dashboard_style,
    load_sales_data,
    load_inventory_data,
    calculate_product_risk,
    chart_layout,
    footer,
)

require_login()
render_user_sidebar()

st.set_page_config(
    page_title="Product Details",
    page_icon="🔎",
    layout="wide",
)

apply_dashboard_style()

st.title(
    "🔎 Product Details"
)

st.caption(
    "Explore individual SKU performance, inventory health, demand and risk."
)

st.divider()

inventory = load_inventory_data()
sales = load_sales_data()

if inventory.empty:

    st.error(
        "Inventory data could not be loaded."
    )

    st.stop()

risk_df = calculate_product_risk(
    inventory,
    sales,
    demand_days=90
)

if (
    risk_df.empty
    or
    "sku_id" not in risk_df.columns
):

    st.error(
        "No product / SKU information was generated."
    )

    st.stop()

products = sorted(
    [
        x
        for x in risk_df["sku_id"]
        .astype(str)
        .unique()
        if x.strip()
        and x.lower() != "nan"
    ]
)

if not products:

    st.warning(
        "No products were found."
    )

    st.stop()

selected_product = st.selectbox(
    "🔍 Select Product / SKU",
    products
)

product_data = risk_df[
    risk_df["sku_id"]
    .astype(str)
    ==
    selected_product
].copy()

if product_data.empty:

    st.warning(
        "No data found for the selected product."
    )

    st.stop()

row = product_data.iloc[0]

def num(
    value,
    default=0.0
):

    try:

        value = float(value)

        if pd.notna(value):

            return value

        return default

    except (
        TypeError,
        ValueError,
    ):

        return default

stock = num(
    row.get(
        "stock_on_hand",
        0
    )
)

risk_score = max(
    0.0,
    min(
        100.0,
        num(
            row.get(
                "risk_score",
                0
            )
        )
    )
)

risk_level = str(
    row.get(
        "risk_level",
        "Low"
    )
).upper()

inventory_status = str(
    row.get(
        "inventory_status",
        "HEALTHY"
    )
)

recent_demand = num(
    row.get(
        "recent_demand",
        0
    )
)

days_of_cover = num(
    row.get(
        "days_of_cover",
        0
    )
)

reorder_point = num(
    row.get(
        "reorder_point",
        0
    )
)

safety_stock = num(
    row.get(
        "safety_stock",
        0
    )
)

st.header(
    f"🛍️ Product / SKU: {selected_product}"
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "📦 Current Stock",
        f"{stock:,.0f}"
    )

with c2:
    st.metric(
        "⚠️ Risk Score",
        f"{risk_score:.1f}/100"
    )

with c3:
    st.metric(
        "🎯 Risk Level",
        risk_level
    )

with c4:
    st.metric(
        "📊 Inventory Status",
        inventory_status
    )

st.divider()

st.subheader(
    "📈 Product Intelligence"
)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "📊 Recent Demand",
        f"{recent_demand:,.0f}"
    )

with m2:

    cover_text = (
        "1000+ days"
        if days_of_cover > 1000
        else f"{days_of_cover:.1f} days"
    )

    st.metric(
        "📅 Days of Cover",
        cover_text
    )

with m3:
    st.metric(
        "🔄 Reorder Point",
        f"{reorder_point:,.0f}"
    )

with m4:
    st.metric(
        "🛡️ Safety Stock",
        f"{safety_stock:,.0f}"
    )

st.divider()

st.header(
    "🎯 Risk Analysis"
)

left, right = st.columns(2)

with left:

    if risk_score >= 75:
        gauge_color = "#dc2626"
    elif risk_score >= 50:
        gauge_color = "#f97316"
    elif risk_score >= 25:
        gauge_color = "#eab308"
    else:
        gauge_color = "#22c55e"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=risk_score,
            title={
                "text": "Product Risk Score"
            },
            number={
                "suffix": "/100"
            },
            gauge={
                "axis": {
                    "range": [0, 100]
                },
                "bar": {
                    "color": gauge_color
                },
                "steps": [
                    {
                        "range": [0, 25],
                        "color": "#dcfce7"
                    },
                    {
                        "range": [25, 50],
                        "color": "#fef3c7"
                    },
                    {
                        "range": [50, 75],
                        "color": "#ffedd5"
                    },
                    {
                        "range": [75, 100],
                        "color": "#fee2e2"
                    },
                ],
            },
        )
    )

    fig.update_layout(
        height=400
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

with right:

    components = pd.DataFrame(
        {
            "Metric": [
                "Stock Risk",
                "Demand Risk",
                "Overall Risk"
            ],
            "Score": [
                num(
                    row.get(
                        "stock_risk_score",
                        0
                    )
                ),
                num(
                    row.get(
                        "demand_risk_score",
                        0
                    )
                ),
                risk_score,
            ],
        }
    )

    fig = px.bar(
        components,
        x="Metric",
        y="Score",
        range_y=[0, 100],
        title="Risk Components",
        text="Score",
    )

    fig.update_traces(
        texttemplate="%{text:.1f}",
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

st.header(
    "📦 Inventory Coverage"
)

coverage = pd.DataFrame(
    {
        "Metric": [
            "Current Stock",
            "Reorder Point",
            "Safety Stock"
        ],
        "Quantity": [
            stock,
            reorder_point,
            safety_stock
        ],
    }
)

fig = px.bar(
    coverage,
    x="Metric",
    y="Quantity",
    title="Stock vs Replenishment Levels",
    text="Quantity",
)

fig.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside"
)

chart_layout(
    fig,
    380
)

st.plotly_chart(
    fig,
    width="stretch"
)

st.divider()

st.header(
    "💡 Business Recommendation"
)

if risk_score >= 75:

    st.error(
        "🔴 URGENT: This SKU has critical risk. "
        "Immediate inventory intervention is recommended."
    )

elif risk_score >= 50:

    st.warning(
        "🟠 HIGH PRIORITY: Review demand, stock coverage "
        "and replenishment needs."
    )

elif risk_score >= 25:

    st.warning(
        "🟡 MONITOR: Continue monitoring demand and inventory."
    )

else:

    st.success(
        "🟢 HEALTHY: This SKU currently has low risk."
    )

if stock <= 0:

    st.error(
        "🚨 Stock is currently zero. "
        "Immediate replenishment should be considered."
    )

elif (
    reorder_point > 0
    and stock <= reorder_point
):

    st.warning(
        "🔄 Current stock is at or below the reorder point. "
        "Consider replenishment."
    )

elif (
    safety_stock > 0
    and stock <= safety_stock
):

    st.warning(
        "🛡️ Current stock is close to safety-stock levels."
    )

else:

    st.success(
        "✅ Current stock is above the immediate "
        "replenishment threshold."
    )

st.divider()

st.header(
    "📋 Product Data"
)

display_data = product_data.T.copy()

display_data.columns = [
    "Value"
]

st.dataframe(
    display_data,
    width="stretch",
    height=450
)

st.download_button(
    "⬇️ Download Product Data",
    product_data.to_csv(index=False),
    f"{selected_product}_details.csv",
    "text/csv"
)

footer()
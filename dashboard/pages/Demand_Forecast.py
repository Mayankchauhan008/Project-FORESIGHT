import streamlit as st
import pandas as pd
import plotly.express as px

from auth import (
    require_login,
    render_user_sidebar,
)

from dashboard_utils import (
    apply_dashboard_style,
    load_sales_data,
    chart_layout,
    footer,
)

require_login()
render_user_sidebar()

st.set_page_config(
    page_title="Demand Forecast",
    page_icon="🔮",
    layout="wide",
)

apply_dashboard_style()

st.title("🔮 Demand Forecast")

st.caption(
    "Historical demand, moving averages and a transparent baseline forecast."
)

st.divider()

sales = load_sales_data()

if sales.empty:
    st.error("Sales data is unavailable.")
    st.stop()

sales = sales.dropna(
    subset=["date"]
).copy()

if sales.empty:
    st.error(
        "A valid date column is required for demand forecasting."
    )
    st.stop()

daily = (
    sales
    .groupby(
        "date",
        as_index=False
    )["quantity"]
    .sum()
    .sort_values("date")
)

if daily.empty:
    st.warning(
        "No demand data is available."
    )
    st.stop()

total_demand = float(
    daily["quantity"].sum()
)

average_daily_demand = float(
    daily["quantity"].mean()
)

maximum_daily_demand = float(
    daily["quantity"].max()
)

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "📦 Total Demand",
        f"{total_demand:,.0f}"
    )

with c2:
    st.metric(
        "📊 Avg Daily Demand",
        f"{average_daily_demand:,.2f}"
    )

with c3:
    st.metric(
        "🚀 Peak Daily Demand",
        f"{maximum_daily_demand:,.0f}"
    )

st.divider()

valid_skus = []

if "sku_id" in sales.columns:

    valid_skus = sorted(
        [
            x
            for x in sales["sku_id"]
            .astype(str)
            .unique()
            if x.strip()
            and x.lower() != "nan"
        ]
    )

if valid_skus:

    selected_sku = st.selectbox(
        "🔍 Select SKU for detailed forecast",
        ["All SKUs"] + valid_skus
    )

else:

    selected_sku = "All SKUs"

if selected_sku != "All SKUs":

    filtered = sales[
        sales["sku_id"]
        .astype(str)
        ==
        selected_sku
    ].copy()

    sku_daily = (
        filtered
        .groupby(
            "date",
            as_index=False
        )["quantity"]
        .sum()
        .sort_values("date")
    )

else:

    sku_daily = daily.copy()

if sku_daily.empty:

    st.warning(
        "No demand history is available for the selected SKU."
    )

    st.stop()

st.subheader(
    "📈 Historical Demand"
)

fig = px.line(
    sku_daily,
    x="date",
    y="quantity",
    title=(
        f"Daily Demand - SKU {selected_sku}"
        if selected_sku != "All SKUs"
        else "Daily Demand - All SKUs"
    ),
)

fig.update_xaxes(
    title="Date"
)

fig.update_yaxes(
    title="Units"
)

chart_layout(
    fig,
    420
)

st.plotly_chart(
    fig,
    width="stretch"
)

sku_daily["7_Day_Moving_Average"] = (
    sku_daily["quantity"]
    .rolling(
        7,
        min_periods=1
    )
    .mean()
)

st.subheader(
    "📊 Demand + 7-Day Moving Average"
)

fig = px.line(
    sku_daily,
    x="date",
    y=[
        "quantity",
        "7_Day_Moving_Average"
    ],
    title="Demand Trend",
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
    "🔮 Simple 30-Day Baseline Forecast"
)

recent_window = min(
    7,
    len(sku_daily)
)

recent_average = float(
    sku_daily
    .tail(recent_window)["quantity"]
    .mean()
)

last_date = sku_daily["date"].max()

future_dates = pd.date_range(
    start=(
        last_date
        +
        pd.Timedelta(days=1)
    ),
    periods=30,
    freq="D"
)

forecast = pd.DataFrame(
    {
        "date": future_dates,
        "forecast_demand": recent_average
    }
)

fig = px.line(
    forecast,
    x="date",
    y="forecast_demand",
    title="30-Day Baseline Forecast"
)

fig.update_yaxes(
    title="Forecast Units"
)

chart_layout(
    fig,
    420
)

st.plotly_chart(
    fig,
    width="stretch"
)

f1, f2 = st.columns(2)

with f1:

    st.metric(
        "📅 Forecast Daily Baseline",
        f"{recent_average:,.2f}"
    )

with f2:

    st.metric(
        "📦 Forecast 30-Day Units",
        f"{recent_average * 30:,.0f}"
    )

st.info(
    "This page intentionally uses a transparent 7-day-average baseline. "
    "It is not presented as a trained ML forecast."
)

footer()
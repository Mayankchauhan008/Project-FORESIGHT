import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# COMMON STYLE
# ============================================================

from dashboard_utils import (
    apply_dashboard_style,
    load_prediction_data,
    load_model_summary,
    find_product_column,
    chart_layout,
    footer
)

apply_dashboard_style()


# ============================================================
# PAGE HEADER
# ============================================================

st.title(
    "📈 Demand Forecast"
)

st.write(
    "Forecast future demand using trained machine learning models."
)

st.divider()


# ============================================================
# LOAD DATA
# ============================================================

prediction = load_prediction_data()

model_summary = load_model_summary()


if prediction.empty:

    st.error(
        "prediction_report.csv could not be loaded."
    )

    st.stop()


# ============================================================
# COLUMN DETECTION
# ============================================================

numeric_cols = prediction.select_dtypes(
    include="number"
).columns.tolist()


product_col = find_product_column(
    prediction
)


# ============================================================
# KPIs
# ============================================================

forecast_records = len(
    prediction
)


if numeric_cols:

    first_numeric = numeric_cols[0]

    average_forecast = pd.to_numeric(
        prediction[first_numeric],
        errors="coerce"
    ).mean()

else:

    average_forecast = 0


c1, c2, c3, c4 = st.columns(4)


with c1:

    st.metric(
        "🔮 Forecast Records",
        f"{forecast_records:,}"
    )


with c2:

    st.metric(
        "📊 Numeric Features",
        len(numeric_cols)
    )


with c3:

    st.metric(
        "🤖 Models",
        "2"
    )


with c4:

    st.metric(
        "📈 Avg Forecast Value",
        f"{average_forecast:,.2f}"
    )


st.divider()


# ============================================================
# PRODUCT FILTER
# ============================================================

filtered = prediction.copy()


if product_col:

    products = sorted(
        filtered[product_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if products:

        selected_product = st.selectbox(
            "🔎 Select Product / SKU",
            ["All Products"] + products
        )

        if selected_product != "All Products":

            filtered = filtered[
                filtered[product_col]
                .astype(str)
                ==
                selected_product
            ]


# ============================================================
# FORECAST VISUALIZATION
# ============================================================

st.header(
    "📈 Forecast Visualization"
)


if not filtered.empty and numeric_cols:

    x_candidates = list(
        filtered.columns
    )

    x_col = st.selectbox(
        "X-axis",
        x_candidates
    )

    y_col = st.selectbox(
        "Forecast Metric",
        numeric_cols
    )

    try:

        fig = px.line(
            filtered,
            x=x_col,
            y=y_col,
            markers=True,
            title="Demand Forecast"
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

        st.warning(
            "The selected columns cannot be plotted."
        )


st.divider()


# ============================================================
# MODEL PERFORMANCE
# ============================================================

st.header(
    "🤖 Model Performance"
)


if not model_summary.empty:

    st.dataframe(
        model_summary,
        width="stretch"
    )

    model_numeric = model_summary.select_dtypes(
        include="number"
    ).columns.tolist()

    if model_numeric:

        metric = st.selectbox(
            "Performance Metric",
            model_numeric
        )

        fig = px.bar(
            model_summary,
            x=model_summary.columns[0],
            y=metric,
            title=f"Model Comparison — {metric}"
        )

        chart_layout(
            fig,
            400
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

else:

    st.info(
        "Model summary file is not available."
    )


# ============================================================
# FORECAST TABLE
# ============================================================

with st.expander(
    "📋 View Forecast Data"
):

    st.dataframe(
        filtered,
        width="stretch",
        height=450
    )


footer()
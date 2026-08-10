# ============================================================
# PROJECT FORESIGHT
# RISK DASHBOARD
# ============================================================

import sys
from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


# ============================================================
# IMPORTS
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px


from dashboard_utils import (
    apply_dashboard_style,
    load_inventory_data,
    load_sales_data,
    chart_layout,
    footer
)


from src.risk_scoring import (
    calculate_risk_score
)


# ============================================================
# STYLE
# ============================================================

apply_dashboard_style()


# ============================================================
# HEADER
# ============================================================

st.title(
    "⚠️ Risk Dashboard"
)

st.write(
    "Identify inventory shortage, overstock and demand-related risks."
)

st.divider()


# ============================================================
# LOAD DATA
# ============================================================

inventory = load_inventory_data()

sales = load_sales_data()


if inventory.empty:

    st.error(
        "Inventory data could not be loaded."
    )

    st.stop()


# ============================================================
# CALCULATE RISK
# ============================================================

try:

    risk_df = calculate_risk_score(

        inventory,

        sales,

        demand_days=90

    )

except Exception as e:

    st.error(
        "Risk calculation failed."
    )

    st.exception(e)

    st.stop()


if risk_df.empty:

    st.warning(
        "No risk records were generated."
    )

    st.stop()


# ============================================================
# RISK COUNTS
# ============================================================

critical = int(

    (
        risk_df[
            "risk_level"
        ]
        ==
        "CRITICAL"
    ).sum()

)


high = int(

    (
        risk_df[
            "risk_level"
        ]
        ==
        "HIGH"
    ).sum()

)


medium = int(

    (
        risk_df[
            "risk_level"
        ]
        ==
        "MEDIUM"
    ).sum()

)


low = int(

    (
        risk_df[
            "risk_level"
        ]
        ==
        "LOW"
    ).sum()

)


# ============================================================
# INVENTORY STATUS COUNTS
# ============================================================

out_of_stock = int(

    (
        risk_df[
            "inventory_status"
        ]
        ==
        "OUT OF STOCK"
    ).sum()

)


critical_stock = int(

    (
        risk_df[
            "inventory_status"
        ]
        ==
        "CRITICAL"
    ).sum()

)


low_stock = int(

    (
        risk_df[
            "inventory_status"
        ]
        ==
        "LOW STOCK"
    ).sum()

)


overstock = int(

    (
        risk_df[
            "inventory_status"
        ]
        ==
        "OVERSTOCK"
    ).sum()

)


healthy = int(

    (
        risk_df[
            "inventory_status"
        ]
        ==
        "HEALTHY"
    ).sum()

)


average_risk = float(

    risk_df[
        "risk_score"
    ].mean()

)


# ============================================================
# KPI
# ============================================================

c1, c2, c3, c4, c5 = st.columns(5)


with c1:

    st.metric(
        "🔴 Critical",
        critical
    )


with c2:

    st.metric(
        "🟠 High",
        high
    )


with c3:

    st.metric(
        "🟡 Medium",
        medium
    )


with c4:

    st.metric(
        "🟢 Low",
        low
    )


with c5:

    st.metric(
        "📦 SKUs",
        len(risk_df)
    )


st.divider()


# ============================================================
# IMPORTANT DATA VALIDATION
# ============================================================

st.header(
    "🔍 Risk Data Validation"
)


v1, v2, v3 = st.columns(3)


with v1:

    st.metric(

        "Inventory Rows",

        f"{len(inventory):,}"

    )


with v2:

    st.metric(

        "Unique SKUs",

        f"{len(risk_df):,}"

    )


with v3:

    st.metric(

        "Average Risk",

        f"{average_risk:.1f}/100"

    )


st.info(

    "Risk is calculated at SKU level. "
    "Multiple store inventory records are aggregated "
    "before assigning product risk."

)


st.divider()


# ============================================================
# RISK DISTRIBUTION
# ============================================================

st.header(
    "📊 Risk Distribution"
)


c1, c2 = st.columns(2)


# ============================================================
# PIE
# ============================================================

with c1:

    risk_counts = pd.DataFrame(

        {

            "Risk Level": [

                "CRITICAL",

                "HIGH",

                "MEDIUM",

                "LOW"

            ],

            "Count": [

                critical,

                high,

                medium,

                low

            ]

        }

    )


    risk_counts = risk_counts[
        risk_counts["Count"] > 0
    ]


    if not risk_counts.empty:

        fig = px.pie(

            risk_counts,

            names="Risk Level",

            values="Count",

            hole=0.55,

            title="Risk Level Distribution",

            color="Risk Level",

            color_discrete_map={

                "CRITICAL": "#DC2626",

                "HIGH": "#F97316",

                "MEDIUM": "#EAB308",

                "LOW": "#22C55E"

            }

        )


        chart_layout(
            fig,
            430
        )


        st.plotly_chart(

            fig,

            width="stretch"

        )

    else:

        st.info(
            "No risk records available."
        )


# ============================================================
# HISTOGRAM
# ============================================================

with c2:

    fig = px.histogram(

        risk_df,

        x="risk_score",

        nbins=15,

        title="Risk Score Distribution"

    )


    fig.update_xaxes(
        range=[0, 100]
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
# INVENTORY HEALTH
# ============================================================

st.header(
    "📦 Inventory Health"
)


health_data = pd.DataFrame(

    {

        "Status": [

            "Out of Stock",

            "Critical",

            "Low Stock",

            "Overstock",

            "Healthy"

        ],

        "Products": [

            out_of_stock,

            critical_stock,

            low_stock,

            overstock,

            healthy

        ]

    }

)


health_data = health_data[
    health_data["Products"] > 0
]


if not health_data.empty:

    fig = px.bar(

        health_data,

        x="Status",

        y="Products",

        title="Inventory Health by SKU",

        text="Products"

    )


    fig.update_traces(

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


# ============================================================
# PORTFOLIO RISK
# ============================================================

st.header(
    "🎯 Portfolio Risk"
)


st.metric(

    "Average Portfolio Risk",

    f"{average_risk:.1f}/100"

)


if average_risk >= 75:

    st.error(
        "🔴 Critical portfolio risk."
    )

elif average_risk >= 50:

    st.warning(
        "🟠 High portfolio risk."
    )

elif average_risk >= 25:

    st.warning(
        "🟡 Moderate portfolio risk."
    )

else:

    st.success(
        "🟢 Portfolio shortage risk is low."
    )


st.divider()


# ============================================================
# TOP RISK PRODUCTS
# ============================================================

st.header(
    "🚨 Highest Risk Products"
)


display_columns = [

    column

    for column in [

        "sku_id",

        "stock_on_hand",

        "reorder_point",

        "stock_to_reorder_ratio",

        "recent_demand",

        "days_of_cover",

        "stock_risk_score",

        "demand_risk_score",

        "risk_score",

        "risk_level",

        "inventory_status",

        "recommended_action"

    ]

    if column in risk_df.columns

]


top_risk = (

    risk_df

    .sort_values(

        "risk_score",

        ascending=False

    )

    .head(20)

)


st.dataframe(

    top_risk[
        display_columns
    ],

    width="stretch",

    height=500

)


# ============================================================
# OVERSTOCK PRODUCTS
# ============================================================

st.header(
    "📦 Overstock Products"
)


overstock_df = (

    risk_df[

        risk_df[
            "inventory_status"
        ]
        ==
        "OVERSTOCK"

    ]

    .sort_values(

        "stock_to_reorder_ratio",

        ascending=False

    )

    .head(20)

)


if not overstock_df.empty:

    st.dataframe(

        overstock_df[
            display_columns
        ],

        width="stretch",

        height=450

    )

else:

    st.success(
        "No significant overstock products detected."
    )


# ============================================================
# DOWNLOAD
# ============================================================

st.download_button(

    "⬇️ Download Risk Report",

    risk_df.to_csv(
        index=False
    ),

    "risk_report.csv",

    "text/csv"

)


# ============================================================
# FOOTER
# ============================================================

footer()
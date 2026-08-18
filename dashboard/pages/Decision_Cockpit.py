# ============================================================
# PROJECT FORESIGHT
# DECISION COCKPIT
# ============================================================

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

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

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
# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="FORESIGHT | Decision Cockpit",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# COMMON STYLE
# ============================================================

apply_dashboard_style()


# ============================================================
# LOAD DATA
# ============================================================

sales = load_sales_data()

inventory = load_inventory_data()


if inventory.empty:

    st.error(
        "Inventory data could not be loaded."
    )

    st.stop()


# ============================================================
# PRODUCT RISK
# ============================================================

try:

    risk = calculate_product_risk(
        inventory,
        sales,
        demand_days=90,
    )

except Exception as exc:

    st.error(
        "Product risk calculation failed."
    )

    st.exception(exc)

    st.stop()


if risk.empty:

    st.warning(
        "No SKU-level risk records were generated."
    )

    st.stop()


# ============================================================
# BASIC CLEANING
# ============================================================

risk = risk.copy()


if "sku_id" not in risk.columns:

    st.error(
        "SKU column is missing from the risk dataset."
    )

    st.stop()


risk["sku_id"] = (
    risk["sku_id"]
    .astype(str)
    .str.strip()
)


risk = risk[
    ~risk["sku_id"].isin(
        [
            "",
            "nan",
            "None",
            "NaN",
        ]
    )
].copy()


# ============================================================
# SAFE NUMBER HELPER
# ============================================================

def safe_number(
    value,
    default=0.0
):

    try:

        value = float(value)

        if np.isfinite(value):

            return value

        return default

    except (
        TypeError,
        ValueError,
    ):

        return default


# ============================================================
# NUMERIC COLUMNS
# ============================================================

numeric_columns = [

    "stock_on_hand",

    "reorder_point",

    "safety_stock",

    "recent_demand",

    "daily_demand",

    "days_of_cover",

    "risk_score",

    "stock_risk_score",

    "demand_risk_score",

    "stock_reorder_ratio",

]


for column in numeric_columns:

    if column in risk.columns:

        risk[column] = pd.to_numeric(
            risk[column],
            errors="coerce"
        ).fillna(0)


# ============================================================
# LOAD SKU MASTER FOR CATEGORY
# ============================================================

sku_master = pd.DataFrame()


sku_master_candidates = [

    PROJECT_ROOT / "Data" / "raw" / "bm_skus.csv",

    PROJECT_ROOT / "data" / "raw" / "bm_skus.csv",

    PROJECT_ROOT / "Data" / "bm_skus.csv",

    PROJECT_ROOT / "data" / "bm_skus.csv",

]


for sku_path in sku_master_candidates:

    if sku_path.exists():

        try:

            sku_master = pd.read_csv(
                sku_path,
                low_memory=False
            )

            sku_master.columns = (

                sku_master.columns
                .astype(str)
                .str.strip()

            )

            break

        except Exception:

            sku_master = pd.DataFrame()


# ============================================================
# FIND CATEGORY COLUMN IN SKU MASTER
# ============================================================

category_column = None


if not sku_master.empty:

    category_candidates = [

        "category",

        "product_category",

        "category_name",

        "item_category",

        "department",

        "segment",

    ]

    for candidate in category_candidates:

        if candidate in sku_master.columns:

            category_column = candidate

            break


# ============================================================
# MERGE CATEGORY
# ============================================================

if (
    not sku_master.empty
    and
    category_column is not None
):

    sku_master["sku_id"] = (
        sku_master["sku_id"]
        .astype(str)
        .str.strip()
    )

    category_lookup = (

        sku_master[
            [
                "sku_id",
                category_column,
            ]
        ]

        .drop_duplicates(
            subset=["sku_id"]
        )

        .rename(
            columns={
                category_column:
                "category"
            }
        )

    )

    risk = risk.merge(
        category_lookup,
        on="sku_id",
        how="left"
    )


# ============================================================
# FALLBACK CATEGORY FROM SALES
# ============================================================

if "category" not in risk.columns:

    if (
        not sales.empty
        and
        "sku_id" in sales.columns
        and
        "category" in sales.columns
    ):

        sales_category = sales[
            [
                "sku_id",
                "category"
            ]
        ].copy()

        sales_category["sku_id"] = (
            sales_category["sku_id"]
            .astype(str)
            .str.strip()
        )

        sales_category = (

            sales_category

            .dropna(
                subset=["category"]
            )

            .groupby(
                "sku_id",
                as_index=False
            )["category"]

            .first()

        )

        risk = risk.merge(
            sales_category,
            on="sku_id",
            how="left"
        )


# ============================================================
# CATEGORY CLEANUP
# ============================================================

if "category" not in risk.columns:

    risk["category"] = "Unknown"

else:

    risk["category"] = (

        risk["category"]

        .astype(str)

        .replace(
            {
                "nan": "Unknown",
                "None": "Unknown",
                "": "Unknown",
            }
        )

        .fillna(
            "Unknown"
        )

    )


# ============================================================
# SALES DATA BY SKU
# ============================================================

if not sales.empty and "sku_id" in sales.columns:

    sales_copy = sales.copy()

    sales_copy["sku_id"] = (

        sales_copy["sku_id"]
        .astype(str)
        .str.strip()

    )

    # --------------------------------------------------------
    # REVENUE
    # --------------------------------------------------------

    if "dashboard_revenue" in sales_copy.columns:

        sales_copy["dashboard_revenue"] = (
            pd.to_numeric(
                sales_copy[
                    "dashboard_revenue"
                ],
                errors="coerce"
            )
            .fillna(0)
        )

    else:

        sales_copy["dashboard_revenue"] = 0.0


    # --------------------------------------------------------
    # QUANTITY
    # --------------------------------------------------------

    if "quantity" in sales_copy.columns:

        sales_copy["quantity"] = (
            pd.to_numeric(
                sales_copy["quantity"],
                errors="coerce"
            )
            .fillna(0)
        )

    else:

        sales_copy["quantity"] = 0.0


    # --------------------------------------------------------
    # SKU AGGREGATION
    # --------------------------------------------------------

    sales_summary = (

        sales_copy

        .groupby(
            "sku_id",
            as_index=False
        )

        .agg(

            revenue=(
                "dashboard_revenue",
                "sum"
            ),

            sales_quantity=(
                "quantity",
                "sum"
            ),

            transactions=(
                "sku_id",
                "count"
            ),

        )

    )


    risk = risk.merge(
        sales_summary,
        on="sku_id",
        how="left"
    )

else:

    risk["revenue"] = 0.0

    risk["sales_quantity"] = 0.0

    risk["transactions"] = 0


# ============================================================
# NUMERIC SALES CLEANUP
# ============================================================

for column in [

    "revenue",

    "sales_quantity",

    "transactions",

]:

    risk[column] = pd.to_numeric(
        risk[column],
        errors="coerce"
    ).fillna(0)


# ============================================================
# SAFE DAYS OF COVER
# ============================================================

risk["days_of_cover_clean"] = (

    risk["days_of_cover"]

    .replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan
    )

)


# ============================================================
# IMPROVED DECISION ENGINE
# ============================================================
#
# The previous version classified everything as
# "Markdown / Clear" because a stock/reorder ratio >= 2
# alone triggered Markdown.
#
# This version requires stronger evidence.
# ============================================================

def classify_decision(row):

    stock = safe_number(
        row.get(
            "stock_on_hand",
            0
        )
    )

    reorder = safe_number(
        row.get(
            "reorder_point",
            0
        )
    )

    safety = safe_number(
        row.get(
            "safety_stock",
            0
        )
    )

    risk_score = safe_number(
        row.get(
            "risk_score",
            0
        )
    )

    ratio = safe_number(
        row.get(
            "stock_reorder_ratio",
            0
        )
    )

    days_cover = row.get(
        "days_of_cover_clean",
        np.nan
    )


    # --------------------------------------------------------
    # 1. REORDER NOW
    # --------------------------------------------------------

    if stock <= 0:

        return "Reorder Now"


    if (
        reorder > 0
        and stock <= reorder
    ):

        return "Reorder Now"


    if (
        pd.notna(days_cover)
        and days_cover <= 7
    ):

        return "Reorder Now"


    # --------------------------------------------------------
    # 2. WATCH / VOLATILE
    # --------------------------------------------------------

    if risk_score >= 50:

        return "Watch / Volatile"


    if (
        pd.notna(days_cover)
        and days_cover <= 30
    ):

        return "Watch / Volatile"


    # --------------------------------------------------------
    # 3. MARKDOWN / CLEAR
    # --------------------------------------------------------
    #
    # Require BOTH:
    #
    #   high inventory ratio
    #   AND very high coverage
    #
    # This prevents all SKUs from becoming Markdown.
    # --------------------------------------------------------

    excess_stock = (

        reorder > 0
        and stock > reorder * 3

    )


    excessive_coverage = (

        pd.notna(days_cover)
        and days_cover >= 120

    )


    if (
        excess_stock
        and
        excessive_coverage
    ):

        return "Markdown / Clear"


    # --------------------------------------------------------
    # 4. WATCH FOR MEDIUM RISK
    # --------------------------------------------------------

    if risk_score >= 25:

        return "Watch / Volatile"


    if (
        reorder > 0
        and stock <= reorder * 1.5
    ):

        return "Watch / Volatile"


    # --------------------------------------------------------
    # 5. HEALTHY
    # --------------------------------------------------------

    return "Healthy"


risk["decision"] = risk.apply(
    classify_decision,
    axis=1
)


# ============================================================
# DECISION PRIORITY
# ============================================================

decision_priority = {

    "Reorder Now": 1,

    "Watch / Volatile": 2,

    "Markdown / Clear": 3,

    "Healthy": 4,

}


risk["decision_priority"] = (

    risk["decision"]

    .map(
        decision_priority
    )

    .fillna(5)

)


# ============================================================
# INVENTORY VALUE
# ============================================================

# Use sales value as a proxy when actual unit cost
# is unavailable.

if "average_unit_price" in risk.columns:

    risk["value_per_unit"] = pd.to_numeric(
        risk[
            "average_unit_price"
        ],
        errors="coerce"
    ).fillna(0)

else:

    if (
        "revenue" in risk.columns
        and
        "sales_quantity" in risk.columns
    ):

        risk["value_per_unit"] = np.where(

            risk[
                "sales_quantity"
            ] > 0,

            risk[
                "revenue"
            ]
            /
            risk[
                "sales_quantity"
            ],

            0

        )

    else:

        risk["value_per_unit"] = 0.0


risk["inventory_value"] = (

    risk["stock_on_hand"]
    *
    risk["value_per_unit"]

)


# ============================================================
# EXCESS INVENTORY
# ============================================================

risk["excess_units"] = np.maximum(

    risk["stock_on_hand"]
    -
    (
        risk["reorder_point"]
        *
        2
    ),

    0

)


risk["capital_locked"] = (

    risk["excess_units"]
    *
    risk["value_per_unit"]

)


# ============================================================
# REVENUE AT RISK
# ============================================================

risk["expected_14_day_demand"] = (

    risk["daily_demand"]
    *
    14

)


risk["shortage_units_14d"] = np.maximum(

    risk[
        "expected_14_day_demand"
    ]
    -
    risk[
        "stock_on_hand"
    ],

    0

)


risk["revenue_at_risk"] = (

    risk["shortage_units_14d"]
    *
    risk["value_per_unit"]

)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header(
        "🎯 Decision Filters"
    )


    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    categories = sorted(

        risk[
            "category"
        ]

        .dropna()

        .astype(str)

        .unique()

        .tolist()

    )


    if len(categories) == 1:

        selected_category = categories[0]

    else:

        selected_category = st.selectbox(

            "Category",

            [
                "All Categories"
            ]
            +
            categories

        )


    # --------------------------------------------------------
    # SKU
    # --------------------------------------------------------

    sku_options = sorted(

        risk[
            "sku_id"
        ]

        .astype(str)

        .unique()

        .tolist()

    )


    selected_sku = st.selectbox(

        "SKU",

        [
            "All SKUs"
        ]
        +
        sku_options

    )


    # --------------------------------------------------------
    # DECISION
    # --------------------------------------------------------

    selected_decisions = st.multiselect(

        "Decision Quadrant",

        [
            "Reorder Now",
            "Watch / Volatile",
            "Markdown / Clear",
            "Healthy",
        ],

        default=[

            "Reorder Now",
            "Watch / Volatile",
            "Markdown / Clear",
            "Healthy",

        ]

    )


    # --------------------------------------------------------
    # INFORMATION
    # --------------------------------------------------------

    with st.expander(
        "ℹ️ Decision Rules"
    ):

        st.markdown(
            """
            **🔴 Reorder Now**

            Stock is zero, at/below the reorder point,
            or coverage is 7 days or less.

            **🟡 Watch / Volatile**

            Moderate/high risk or inventory coverage
            is relatively low.

            **🟠 Markdown / Clear**

            Used only when both excess inventory
            and very high inventory coverage exist.

            **🟢 Healthy**

            No immediate intervention is indicated.
            """
        )


# ============================================================
# FILTER DATA
# ============================================================

filtered = risk.copy()


if selected_category != "All Categories":

    filtered = filtered[
        filtered["category"]
        ==
        selected_category
    ]


if selected_sku != "All SKUs":

    filtered = filtered[
        filtered["sku_id"]
        ==
        selected_sku
    ]


if selected_decisions:

    filtered = filtered[
        filtered["decision"]
        .isin(
            selected_decisions
        )
    ]

else:

    filtered = filtered.iloc[0:0]


# ============================================================
# HEADER
# ============================================================

st.title(
    "📦 FORESIGHT — Demand & Inventory Intelligence"
)

st.caption(
    "Project Foresight · Decision Support Cockpit · "
    "Turn retail data into actionable inventory decisions."
)


st.divider()


# ============================================================
# KPI SECTION
# ============================================================

skus_in_view = len(
    filtered
)


revenue_at_risk = float(

    filtered[
        "revenue_at_risk"
    ].sum()

)


capital_locked = float(

    filtered[
        "capital_locked"
    ].sum()

)


average_risk = (

    float(
        filtered[
            "risk_score"
        ].mean()
    )

    if not filtered.empty

    else 0.0

)


k1, k2, k3, k4 = st.columns(4)


with k1:

    st.metric(
        "SKUs in View",
        f"{skus_in_view:,}"
    )


with k2:

    st.metric(
        "Revenue at Risk",
        f"₹{revenue_at_risk:,.0f}"
    )


with k3:

    st.metric(
        "Inventory Value",
        f"₹{capital_locked:,.0f}"
    )


with k4:

    st.metric(
        "Average Risk Score",
        f"{average_risk:.1f}/100"
    )


st.caption(
    "Revenue at risk is estimated from recent demand and "
    "current stock. Inventory value is a retail-value proxy "
    "when unit cost is unavailable."
)


st.divider()


# ============================================================
# DECISION COUNT
# ============================================================

decision_counts = (

    filtered[
        "decision"
    ]

    .value_counts()

    .reindex(

        [
            "Reorder Now",
            "Watch / Volatile",
            "Markdown / Clear",
            "Healthy",
        ],

        fill_value=0

    )

)


d1, d2, d3, d4 = st.columns(4)


with d1:

    st.metric(
        "🔴 Reorder Now",
        int(
            decision_counts[
                "Reorder Now"
            ]
        )
    )


with d2:

    st.metric(
        "🟡 Watch / Volatile",
        int(
            decision_counts[
                "Watch / Volatile"
            ]
        )
    )


with d3:

    st.metric(
        "🟠 Markdown / Clear",
        int(
            decision_counts[
                "Markdown / Clear"
            ]
        )
    )


with d4:

    st.metric(
        "🟢 Healthy",
        int(
            decision_counts[
                "Healthy"
            ]
        )
    )


st.divider()


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3 = st.tabs(

    [
        "🎯 Reorder / Markdown Priorities",

        "📈 Demand Coverage",

        "🧭 Decisioning Grid",

    ]

)


# ============================================================
# TAB 1
# ============================================================

with tab1:

    st.subheader(
        "🎯 Reorder / Markdown Priorities"
    )

    st.caption(
        "Prioritized operational queue for inventory action."
    )


    priority = (

        filtered

        .sort_values(

            [

                "decision_priority",

                "risk_score",

                "revenue_at_risk",

            ],

            ascending=[

                True,

                False,

                False,

            ]

        )

        .copy()

    )


    if priority.empty:

        st.info(
            "No SKUs match the current filters."
        )

    else:

        columns = [

            "sku_id",

            "category",

            "decision",

            "stock_on_hand",

            "reorder_point",

            "recent_demand",

            "days_of_cover_clean",

            "risk_score",

            "revenue_at_risk",

            "capital_locked",

        ]


        columns = [

            column

            for column in columns

            if column in priority.columns

        ]


        display = priority[
            columns
        ].copy()


        if "days_of_cover_clean" in display.columns:

            display[
                "days_of_cover_clean"
            ] = display[
                "days_of_cover_clean"
            ].round(1)


        for column in [

            "stock_on_hand",

            "reorder_point",

            "recent_demand",

            "risk_score",

            "revenue_at_risk",

            "capital_locked",

        ]:

            if column in display.columns:

                display[
                    column
                ] = display[
                    column
                ].round(1)


        st.dataframe(

            display,

            width="stretch",

            height=500,

            hide_index=True,

        )


        st.download_button(

            "⬇️ Download Decision Queue",

            priority[
                columns
            ].to_csv(
                index=False
            ),

            "decision_queue.csv",

            "text/csv"

        )


# ============================================================
# TAB 2
# ============================================================

with tab2:

    st.subheader(
        "📈 Demand Coverage"
    )

    if filtered.empty:

        st.info(
            "No SKUs match the current filters."
        )

    else:

        coverage = filtered.copy()


        coverage_display = [

            "sku_id",

            "category",

            "stock_on_hand",

            "recent_demand",

            "daily_demand",

            "days_of_cover_clean",

            "risk_score",

            "decision",

        ]


        coverage_display = [

            c

            for c in coverage_display

            if c in coverage.columns

        ]


        st.dataframe(

            coverage[
                coverage_display
            ]
            .sort_values(
                "risk_score",
                ascending=False
            ),

            width="stretch",

            height=400,

            hide_index=True

        )


        fig = px.scatter(

            filtered,

            x="daily_demand",

            y="stock_on_hand",

            size="inventory_value",

            color="decision",

            hover_name="sku_id",

            hover_data=[

                "category",

                "risk_score",

                "days_of_cover_clean",

                "reorder_point",

            ],

            title="Current Stock vs Daily Demand",

            color_discrete_map={

                "Reorder Now":
                    "#ef4444",

                "Watch / Volatile":
                    "#eab308",

                "Markdown / Clear":
                    "#f97316",

                "Healthy":
                    "#22c55e",

            }

        )


        chart_layout(
            fig,
            500
        )


        st.plotly_chart(

            fig,

            width="stretch"

        )


# ============================================================
# TAB 3
# ============================================================

with tab3:

    st.subheader(
        "🧭 Stockout vs Overstock Decision Grid"
    )

    st.caption(
        "X = inventory coverage · "
        "Y = risk score · "
        "bubble size = estimated inventory value."
    )


    if filtered.empty:

        st.info(
            "No SKUs match the current filters."
        )

    else:

        plot = filtered.copy()


        plot["cover_plot"] = (

            plot[
                "days_of_cover_clean"
            ]

            .fillna(180)

            .clip(
                0,
                180
            )

        )


        fig = px.scatter(

            plot,

            x="cover_plot",

            y="risk_score",

            size="inventory_value",

            color="decision",

            hover_name="sku_id",

            hover_data={

                "category":
                    True,

                "stock_on_hand":
                    ":.0f",

                "reorder_point":
                    ":.0f",

                "recent_demand":
                    ":.0f",

                "cover_plot":
                    ":.1f",

                "risk_score":
                    ":.1f",

                "inventory_value":
                    ":,.0f",

            },

            title=(
                "Inventory Decision Matrix"
            ),

            color_discrete_map={

                "Reorder Now":
                    "#ef4444",

                "Watch / Volatile":
                    "#eab308",

                "Markdown / Clear":
                    "#f97316",

                "Healthy":
                    "#22c55e",

            }

        )


        fig.add_vline(

            x=14,

            line_dash="dash",

            annotation_text="14 days",

            annotation_position="top"

        )


        fig.add_vline(

            x=60,

            line_dash="dash",

            annotation_text="60 days",

            annotation_position="top"

        )


        fig.add_hline(

            y=50,

            line_dash="dot",

            annotation_text="50 risk",

            annotation_position="right"

        )


        max_cover = max(

            30,

            float(
                plot[
                    "cover_plot"
                ].max()
            ) * 1.05

        )


        fig.update_xaxes(

            title="Days of Inventory Cover",

            range=[
                0,
                max_cover
            ]

        )


        fig.update_yaxes(

            title="Risk Score",

            range=[
                0,
                100
            ]

        )


        chart_layout(
            fig,
            580
        )


        st.plotly_chart(

            fig,

            width="stretch"

        )


        q1, q2, q3, q4 = st.columns(4)


        with q1:

            st.error(
                "🔴 **REORDER NOW**\n\n"
                "Immediate replenishment pressure."
            )


        with q2:

            st.warning(
                "🟡 **WATCH / VOLATILE**\n\n"
                "Monitor demand and coverage."
            )


        with q3:

            st.warning(
                "🟠 **MARKDOWN / CLEAR**\n\n"
                "Strong evidence of excess stock."
            )


        with q4:

            st.success(
                "🟢 **HEALTHY**\n\n"
                "No immediate intervention."
            )


# ============================================================
# EXECUTIVE ACTION SUMMARY
# ============================================================

st.divider()

st.header(
    "💡 Recommended Actions"
)


reorder_count = int(
    decision_counts[
        "Reorder Now"
    ]
)

watch_count = int(
    decision_counts[
        "Watch / Volatile"
    ]
)

markdown_count = int(
    decision_counts[
        "Markdown / Clear"
    ]
)

healthy_count = int(
    decision_counts[
        "Healthy"
    ]
)


a1, a2 = st.columns(2)


with a1:

    if reorder_count > 0:

        st.error(

            f"""
            **🔴 Replenishment Priority**

            {reorder_count:,} SKU(s) need
            replenishment review.
            """

        )

    else:

        st.success(

            """
            **✅ Replenishment**

            No SKU currently meets the
            immediate reorder rule.
            """

        )


with a2:

    if markdown_count > 0:

        st.warning(

            f"""
            **🟠 Excess Inventory**

            {markdown_count:,} SKU(s) show
            strong evidence of excess stock.
            """

        )

    else:

        st.success(

            """
            **✅ Excess Inventory**

            No SKU currently meets the
            stronger markdown rule.
            """

        )


st.info(

    f"""
    **Portfolio status:** {skus_in_view:,} SKUs in the current view ·
    {watch_count:,} watch candidates ·
    {healthy_count:,} healthy candidates.
    """

)


# ============================================================
# DATA QUALITY NOTE
# ============================================================

st.caption(

    "Decision Cockpit uses SKU-level inventory risk, "
    "recent 90-day demand, reorder thresholds and "
    "inventory coverage. Markdown is deliberately "
    "conservative so high stock alone does not classify "
    "every SKU as an excess-inventory candidate."

)


# ============================================================
# FOOTER
# ============================================================

footer()
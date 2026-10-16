
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Inventory Optimization ",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Inventory Optimization")
st.write("Monitor stock levels, reorder requirements, and store-wise inventory needs.")

# --------------------------------------------------
# 1. PROJECT ROOT AND DATASET PATH
# --------------------------------------------------
BASE_PATH = Path(__file__).resolve().parent.parent.parent
inventory_path = BASE_PATH / "cleaned_inventory_snapshot.csv"


# --------------------------------------------------
# 2. LOAD INVENTORY DATA
# --------------------------------------------------
@st.cache_data
def load_inventory(path):
    return pd.read_csv(path)


if not inventory_path.is_file():
    st.error(f"Inventory dataset not found: {inventory_path}")
    st.stop()

try:
    inventory = load_inventory(inventory_path)
except Exception as e:
    st.error(f"Unable to load inventory data: {e}")
    st.stop()

required_columns = [
    "sku_id",
    "store_id",
    "stock_on_hand",
    "reorder_point",
    "safety_stock"
]

missing_columns = [
    col for col in required_columns
    if col not in inventory.columns
]

if missing_columns:
    st.error(f"Inventory dataset is missing columns: {missing_columns}")
    st.stop()

if inventory.empty:
    st.warning("The inventory dataset contains no records.")
    st.stop()

inventory = inventory.copy()

for col in ["stock_on_hand", "reorder_point", "safety_stock"]:
    inventory[col] = pd.to_numeric(inventory[col], errors="coerce")

inventory = inventory.dropna(
    subset=["stock_on_hand", "reorder_point", "safety_stock"]
).copy()

if inventory.empty:
    st.warning("No valid numeric inventory records are available.")
    st.stop()

st.success("Inventory data loaded successfully.")

# --------------------------------------------------
# 3. INVENTORY OVERVIEW
# --------------------------------------------------
st.subheader("1. Inventory Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Inventory Records", f"{len(inventory):,}")
col2.metric("Unique Products", f"{inventory['sku_id'].nunique():,}")
col3.metric("Stores Covered", f"{inventory['store_id'].nunique():,}")

with st.expander("View Inventory Data"):
    st.dataframe(inventory.head(100), use_container_width=True)

# --------------------------------------------------
# 4. STOCK LEVEL ANALYSIS
# --------------------------------------------------
st.divider()
st.subheader("2. Stock Level Analysis")

low_stock = inventory[
    inventory["stock_on_hand"] <= inventory["reorder_point"]
].copy()

normal_stock = inventory[
    inventory["stock_on_hand"] > inventory["reorder_point"]
].copy()

col1, col2, col3 = st.columns(3)

col1.metric("Low Stock Items", f"{len(low_stock):,}")
col2.metric("Other Stock Items", f"{len(normal_stock):,}")
col3.metric(
    "Low Stock Percentage",
    f"{len(low_stock) / len(inventory) * 100:.1f}%"
)

# Add stock status for visualizations
inventory["stock_status"] = "Above Reorder Point"
inventory.loc[
    inventory["stock_on_hand"] <= inventory["reorder_point"],
    "stock_status"
] = "At or Below Reorder Point"

col1, col2 = st.columns(2)

with col1:
    stock_counts = (
        inventory["stock_status"]
        .value_counts()
        .rename_axis("Stock Status")
        .reset_index(name="Item Count")
    )

    fig_stock_bar = px.bar(
        stock_counts,
        x="Stock Status",
        y="Item Count",
        color="Stock Status",
        text="Item Count",
        title="Inventory Stock Status"
    )
    st.plotly_chart(fig_stock_bar, use_container_width=True)

with col2:
    fig_stock_pie = px.pie(
        stock_counts,
        names="Stock Status",
        values="Item Count",
        title="Stock Status Distribution"
    )
    st.plotly_chart(fig_stock_pie, use_container_width=True)

# --------------------------------------------------
# 5. REORDER RECOMMENDATIONS
# --------------------------------------------------
st.divider()
st.subheader("3. Reorder Recommendations")

reorder_recommendations = low_stock.copy()

reorder_recommendations["recommended_order_qty"] = (
    reorder_recommendations["reorder_point"]
    + reorder_recommendations["safety_stock"]
    - reorder_recommendations["stock_on_hand"]
).clip(lower=0)

reorder_recommendations = reorder_recommendations.sort_values(
    "recommended_order_qty",
    ascending=False
)

total_recommended_qty = reorder_recommendations[
    "recommended_order_qty"
].sum()

col1, col2 = st.columns(2)

col1.metric(
    "Items Requiring Reorder",
    f"{len(reorder_recommendations):,}"
)

col2.metric(
    "Recommended Order Quantity",
    f"{total_recommended_qty:,.0f} units"
)

reorder_columns = [
    "store_id",
    "sku_id",
    "stock_on_hand",
    "reorder_point",
    "safety_stock",
    "recommended_order_qty"
]

if reorder_recommendations.empty:
    st.success("No items currently meet the low-stock rule.")
else:
    with st.expander("View Reorder Recommendations"):
        st.dataframe(
            reorder_recommendations[reorder_columns].head(100),
            use_container_width=True
        )

# --------------------------------------------------
# 6. REORDER PRIORITY ANALYSIS
# --------------------------------------------------
st.divider()
st.subheader("4. Reorder Priority Analysis")

priority_data = reorder_recommendations.copy()

if not priority_data.empty:
    high_threshold = priority_data["recommended_order_qty"].quantile(0.75)
    low_threshold = priority_data["recommended_order_qty"].quantile(0.25)

    priority_data["reorder_priority"] = "Medium"

    priority_data.loc[
        priority_data["recommended_order_qty"] >= high_threshold,
        "reorder_priority"
    ] = "High"

    priority_data.loc[
        priority_data["recommended_order_qty"] <= low_threshold,
        "reorder_priority"
    ] = "Low"

    priority_order = ["High", "Medium", "Low"]

    priority_summary = (
        priority_data["reorder_priority"]
        .value_counts()
        .reindex(priority_order, fill_value=0)
        .rename_axis("Reorder Priority")
        .reset_index(name="Item Count")
    )

else:
    priority_data["reorder_priority"] = pd.Series(dtype="object")
    priority_order = ["High", "Medium", "Low"]
    priority_summary = pd.DataFrame({
        "Reorder Priority": priority_order,
        "Item Count": [0, 0, 0]
    })

col1, col2 = st.columns(2)

with col1:
    fig_priority_bar = px.bar(
        priority_summary,
        x="Reorder Priority",
        y="Item Count",
        color="Reorder Priority",
        text="Item Count",
        category_orders={"Reorder Priority": priority_order},
        title="Reorder Priority Distribution"
    )
    st.plotly_chart(fig_priority_bar, use_container_width=True)

with col2:
    fig_priority_donut = px.pie(
        priority_summary,
        names="Reorder Priority",
        values="Item Count",
        hole=0.55,
        title="Reorder Priority Share"
    )
    st.plotly_chart(fig_priority_donut, use_container_width=True)

with st.expander("View Priority Summary"):
    st.dataframe(priority_summary, use_container_width=True)

# --------------------------------------------------
# 7. INVENTORY SCATTER PLOT
# --------------------------------------------------
st.divider()
st.subheader("5. Stock Level vs Reorder Point")

scatter_data = inventory.copy()

if not priority_data.empty:
    scatter_data = scatter_data.merge(
        priority_data[
            ["store_id", "sku_id", "reorder_priority"]
        ],
        on=["store_id", "sku_id"],
        how="left"
    )

    scatter_data["reorder_priority"] = (
        scatter_data["reorder_priority"].fillna("No Reorder")
    )
else:
    scatter_data["reorder_priority"] = "No Reorder"

fig_scatter = px.scatter(
    scatter_data,
    x="reorder_point",
    y="stock_on_hand",
    color="reorder_priority",
    hover_data=["store_id", "sku_id", "safety_stock"],
    title="Current Stock vs Reorder Point",
    labels={
        "reorder_point": "Reorder Point (Units)",
        "stock_on_hand": "Current Stock (Units)",
        "reorder_priority": "Reorder Priority"
    },
    opacity=0.75
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.caption(
    "Points below or on the reorder-point level meet the low-stock rule. "
    "Each point represents an inventory record."
)

# --------------------------------------------------
# 8. STORE-WISE REORDER ANALYSIS
# --------------------------------------------------
st.divider()
st.subheader("6. Store-wise Reorder Analysis")

if not reorder_recommendations.empty:
    store_reorder_summary = (
        reorder_recommendations.groupby("store_id")
        .agg(
            Reorder_Items=("sku_id", "count"),
            Recommended_Order_Qty=("recommended_order_qty", "sum")
        )
        .reset_index()
        .sort_values("Recommended_Order_Qty", ascending=False)
    )

    col1, col2 = st.columns(2)

    with col1:
        fig_store_bar = px.bar(
            store_reorder_summary,
            x="store_id",
            y="Recommended_Order_Qty",
            color="Recommended_Order_Qty",
            title="Recommended Order Quantity by Store",
            labels={
                "store_id": "Store",
                "Recommended_Order_Qty": "Order Quantity"
            }
        )
        st.plotly_chart(fig_store_bar, use_container_width=True)

    with col2:
        fig_store_scatter = px.scatter(
            store_reorder_summary,
            x="Reorder_Items",
            y="Recommended_Order_Qty",
            hover_data=["store_id"],
            title="Store Reorder Items vs Order Quantity",
            labels={
                "Reorder_Items": "Number of Reorder Items",
                "Recommended_Order_Qty": "Recommended Order Quantity"
            }
        )
        st.plotly_chart(fig_store_scatter, use_container_width=True)

    with st.expander("View Store-wise Summary"):
        st.dataframe(store_reorder_summary, use_container_width=True)

else:
    store_reorder_summary = pd.DataFrame()
    st.info("No store currently has items meeting the low-stock rule.")

# --------------------------------------------------
# 9. SKU-WISE REORDER ANALYSIS
# --------------------------------------------------
st.divider()
st.subheader("7. SKU-wise Reorder Analysis")

if not reorder_recommendations.empty:
    sku_reorder_summary = (
        reorder_recommendations.groupby("sku_id")
        .agg(
            Reorder_Items=("store_id", "count"),
            Recommended_Order_Qty=("recommended_order_qty", "sum")
        )
        .reset_index()
        .sort_values("Recommended_Order_Qty", ascending=False)
    )

    top_skus = sku_reorder_summary.head(10)

    fig_sku_bar = px.bar(
        top_skus,
        x="sku_id",
        y="Recommended_Order_Qty",
        color="Recommended_Order_Qty",
        title="Top 10 SKUs by Reorder Quantity",
        labels={
            "sku_id": "SKU",
            "Recommended_Order_Qty": "Recommended Order Quantity"
        }
    )
    st.plotly_chart(fig_sku_bar, use_container_width=True)

    with st.expander("View SKU-wise Summary"):
        st.dataframe(sku_reorder_summary, use_container_width=True)

else:
    sku_reorder_summary = pd.DataFrame()
    st.info("No SKU currently requires reorder under the low-stock rule.")

# --------------------------------------------------
# 10. INVENTORY OPTIMIZATION SUMMARY
# --------------------------------------------------
st.divider()
st.subheader("8. Inventory Optimization Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Inventory Records", f"{len(inventory):,}")
col2.metric("Low Stock Items", f"{len(low_stock):,}")
col3.metric("Reorder Items", f"{len(reorder_recommendations):,}")
col4.metric("Recommended Order Qty", f"{total_recommended_qty:,.0f}")

# --------------------------------------------------
# 11. INVENTORY INSIGHTS
# --------------------------------------------------
st.divider()
st.subheader("9. Inventory Optimization Insights")

if not reorder_recommendations.empty:
    high_priority_items = priority_data[
        priority_data["reorder_priority"] == "High"
    ]
    medium_priority_items = priority_data[
        priority_data["reorder_priority"] == "Medium"
    ]
    low_priority_items = priority_data[
        priority_data["reorder_priority"] == "Low"
    ]

    col1, col2, col3 = st.columns(3)

    col1.metric("High Priority", f"{len(high_priority_items):,}")
    col2.metric("Medium Priority", f"{len(medium_priority_items):,}")
    col3.metric("Low Priority", f"{len(low_priority_items):,}")

    st.write(
        f"**Total reorder items:** {len(reorder_recommendations):,}"
    )
    st.write(
        f"**Total recommended order quantity:** "
        f"{total_recommended_qty:,.0f} units."
    )

    if not store_reorder_summary.empty:
        top_store = store_reorder_summary.iloc[0]
        st.write(
            f"**Highest reorder requirement store:** "
            f"{top_store['store_id']} "
            f"({top_store['Recommended_Order_Qty']:,.0f} units)."
        )

    if not sku_reorder_summary.empty:
        top_sku = sku_reorder_summary.iloc[0]
        st.write(
            f"**Highest reorder requirement SKU:** "
            f"{top_sku['sku_id']} "
            f"({top_sku['Recommended_Order_Qty']:,.0f} units)."
        )

    st.dataframe(
        high_priority_items[
            [
                "store_id",
                "sku_id",
                "stock_on_hand",
                "reorder_point",
                "safety_stock",
                "recommended_order_qty",
                "reorder_priority"
            ]
        ].head(30),
        use_container_width=True
    )

else:
    st.success(
        "No inventory records currently meet the low-stock reorder rule."
    )

st.info(
    "Reorder quantities are rule-based estimates calculated from stock on hand, "
    "reorder point, and safety stock. They are not demand-model predictions."
)

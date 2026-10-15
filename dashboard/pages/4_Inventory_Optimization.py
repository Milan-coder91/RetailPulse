# Day 18 - Step 1: Inventory Data Overview

import streamlit as st
import pandas as pd
from pathlib import Path

# Inventory Optimization Page

st.title("Inventory Optimization")
st.write("Monitor stock levels and inventory requirements.")

#BASE_PATH = Path(
 #   r"C:\Users\milan\Downloads\archive (3)\retail_clean_dataset")

BASE_PATH = Path(__file__).resolve().parent.parent.parent


inventory_path = BASE_PATH / "cleaned_inventory_snapshot.csv"

inventory = pd.read_csv(inventory_path)

st.subheader("Inventory Overview")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Inventory Records",
    f"{len(inventory):,}"
)

col2.metric(
    "Products in Inventory",
    f"{inventory['sku_id'].nunique():,}"
)

col3.metric(
    "Stores Covered",
    f"{inventory['store_id'].nunique():,}"
)

st.success("Inventory data loaded successfully.")

st.dataframe(
    inventory.head(30),
    width="stretch"
)

# Day 18 - Step 2: Stock Level Analysis

st.subheader("Stock Level Analysis")

low_stock = inventory[
    inventory["stock_on_hand"] <= inventory["reorder_point"]
].copy()

st.metric(
    "Low Stock Items",
    f"{len(low_stock):,}"
)

st.dataframe(
    low_stock.head(30),
    width="stretch"
)

# Day 18 - Step 3: Reorder Recommendations

st.subheader("Reorder Recommendations")

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

st.metric(
    "Items Requiring Reorder",
    f"{len(reorder_recommendations):,}"
)

st.dataframe(
    reorder_recommendations[
        [
            "store_id",
            "sku_id",
            "stock_on_hand",
            "reorder_point",
            "safety_stock",
            "recommended_order_qty"
        ]
    ].head(30),
    width="stretch"
)

# Day 18 - Step 4: Reorder Priority Analysis

st.subheader("Reorder Priority Analysis")

priority_data = reorder_recommendations.copy()

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

priority_summary = (
    priority_data["reorder_priority"]
    .value_counts()
    .reindex(["High", "Medium", "Low"], fill_value=0)
    .reset_index()
)

priority_summary.columns = [
    "Reorder Priority",
    "Item Count"
]

st.dataframe(
    priority_summary,
    width="stretch"
)

st.bar_chart(
    priority_summary.set_index("Reorder Priority")["Item Count"],
    x_label="Reorder Priority",
    y_label="Item Count"
)

# Day 18 - Step 5: Inventory Optimization Summary

st.subheader("Inventory Optimization Summary")

total_recommended_qty = reorder_recommendations[
    "recommended_order_qty"
].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Inventory Records",
    f"{len(inventory):,}"
)

col2.metric(
    "Low Stock Items",
    f"{len(low_stock):,}"
)

col3.metric(
    "Reorder Items",
    f"{len(reorder_recommendations):,}"
)

col4.metric(
    "Recommended Order Qty",
    f"{total_recommended_qty:,.0f}"
)

# Day 18 - Step 6: Inventory Reorder Insights

st.subheader("Inventory Reorder Insights")

high_priority_items = (
    priority_data[priority_data["reorder_priority"] == "High"]
)

medium_priority_items = (
    priority_data[priority_data["reorder_priority"] == "Medium"]
)

low_priority_items = (
    priority_data[priority_data["reorder_priority"] == "Low"]
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "High Priority Reorders",
    f"{len(high_priority_items):,}"
)

col2.metric(
    "Medium Priority Reorders",
    f"{len(medium_priority_items):,}"
)

col3.metric(
    "Low Priority Reorders",
    f"{len(low_priority_items):,}"
)

st.write(
    "High-priority items should be considered first for inventory replenishment."
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
    width="stretch"
)


# Day 18 - Step 7: Reorder Priority Visualization

st.subheader("Reorder Priority Distribution")

st.bar_chart(
    priority_summary.set_index("Reorder Priority")["Item Count"],
    x_label="Reorder Priority",
    y_label="Number of Items"
)

st.info(
    "High-priority reorder items should be replenished first "
    "to reduce the risk of stock shortages."
)

# Day 18 - Step 8: Store-wise Reorder Analysis

st.subheader("Store-wise Reorder Analysis")

store_reorder_summary = (
    reorder_recommendations
    .groupby("store_id")
    .agg(
        Reorder_Items=("sku_id", "count"),
        Recommended_Order_Qty=("recommended_order_qty", "sum")
    )
    .reset_index()
    .sort_values(
        "Recommended_Order_Qty",
        ascending=False
    )
)

st.dataframe(
    store_reorder_summary,
    width="stretch"
)

st.bar_chart(
    store_reorder_summary.set_index("store_id")[
        "Recommended_Order_Qty"
    ],
    x_label="Store",
    y_label="Recommended Order Quantity"
)

# Day 18 - Step 9: SKU-wise Reorder Analysis

st.subheader("SKU-wise Reorder Analysis")

sku_reorder_summary = (
    reorder_recommendations
    .groupby("sku_id")
    .agg(
        Reorder_Items=("store_id", "count"),
        Recommended_Order_Qty=("recommended_order_qty", "sum")
    )
    .reset_index()
    .sort_values(
        "Recommended_Order_Qty",
        ascending=False
    )
)

st.dataframe(
    sku_reorder_summary.head(30),
    width="stretch"
)

st.bar_chart(
    sku_reorder_summary.head(10).set_index("sku_id")[
        "Recommended_Order_Qty"
    ],
    x_label="SKU",
    y_label="Recommended Order Quantity"
)

# Day 18 - Step 10: Inventory Optimization Insights

st.subheader("Inventory Optimization Insights")

top_store = store_reorder_summary.iloc[0]

top_sku = sku_reorder_summary.iloc[0]

st.write(
    f"**Total reorder items:** {len(reorder_recommendations):,}"
)

st.write(
    f"**Total recommended order quantity:** "
    f"{reorder_recommendations['recommended_order_qty'].sum():,.0f} units."
)

st.write(
    f"**Highest reorder requirement store:** "
    f"{top_store['store_id']} "
    f"({top_store['Recommended_Order_Qty']:,.0f} units)."
)

st.write(
    f"**Highest reorder requirement SKU:** "
    f"{top_sku['sku_id']} "
    f"({top_sku['Recommended_Order_Qty']:,.0f} units)."
)

st.success(
    "Inventory optimization analysis completed using actual inventory data."
)
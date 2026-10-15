

# Step 24: Sales Analytics with Real Metrics

import streamlit as st
import pandas as pd
from pathlib import Path

st.title("Sales Analytics")

#BASE_PATH = Path(
  #  r"C:\Users\milan\Downloads\archive (3)\retail_clean_dataset"
#)

BASE_PATH = Path(__file__).resolve().parent.parent.parent



sales_path = BASE_PATH / "cleaned_sales_transactions.csv"

@st.cache_data
def load_sales(path):
    return pd.read_csv(path)

sales = load_sales(sales_path)

total_sales = sales["total_value"].sum()
total_transactions = sales["receipt_id"].nunique()
average_order_value = (
    sales.groupby("receipt_id")["total_value"].sum().mean()
)

col1, col2, col3 = st.columns(3)

col1.metric("Total Sales", f"₹{total_sales:,.2f}")
col2.metric("Total Orders", f"{total_transactions:,}")
col3.metric("Average Order Value", f"₹{average_order_value:,.2f}")

st.subheader("Sales Dataset Preview")
st.dataframe(sales.head(100), width="stretch")


# Step 26: Daily Sales Trend

st.subheader("Daily Sales Trend")

sales["date"] = pd.to_datetime(sales["date"])

daily_sales = (
    sales.groupby("date")["total_value"]
    .sum()
    .reset_index()
    .sort_values("date")
)

st.line_chart(
    daily_sales.set_index("date")["total_value"],
    x_label="Date",
    y_label="Sales Value"
)


# Step 28: Sales by Channel

st.subheader("Sales by Channel")

channel_sales = (
    sales.groupby("channel")["total_value"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(
    channel_sales,
    x_label="Channel",
    y_label="Total Sales"
)

st.write("Channel-wise sales totals:")
st.dataframe(
    channel_sales.reset_index(name="total_sales"),
    width="stretch"
)


# Step 30: Top 10 Stores by Sales

st.subheader("Top 10 Stores by Sales")

store_sales = (
    sales.groupby("store_id")["total_value"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(
    store_sales,
    x_label="Store ID",
    y_label="Total Sales"
)

st.dataframe(
    store_sales.reset_index(name="total_sales"),
    width="stretch"
)


# Step 32: Monthly Sales Trend

st.subheader("Monthly Sales Trend")

sales["month"] = sales["date"].dt.to_period("M").astype(str)

monthly_sales = (
    sales.groupby("month")["total_value"]
    .sum()
    .reset_index()
    .sort_values("month")
)

st.line_chart(
    monthly_sales.set_index("month")["total_value"],
    x_label="Month",
    y_label="Total Sales"
)

st.dataframe(monthly_sales, width="stretch")


# Step 34: Top 10 SKUs by Sales

st.subheader("Top 10 Products (SKU) by Sales")

sku_sales = (
    sales.groupby("sku_id")["total_value"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(
    sku_sales,
    x_label="SKU ID",
    y_label="Total Sales"
)

st.dataframe(
    sku_sales.reset_index(name="total_sales"),
    width="stretch"
)


# Step 36: Sales by Store and Channel

st.subheader("Store-wise Sales by Channel")

store_channel_sales = (
    sales.pivot_table(
        index="store_id",
        columns="channel",
        values="total_value",
        aggfunc="sum",
        fill_value=0
    )
)

st.bar_chart(store_channel_sales)

st.dataframe(
    store_channel_sales,
    width="stretch"
)


# Step 38: Sales by Discount Percentage

st.subheader("Sales by Discount Percentage")

discount_sales = (
    sales.groupby("discount_pct")["total_value"]
    .sum()
    .sort_index()
)

st.bar_chart(
    discount_sales,
    x_label="Discount Percentage",
    y_label="Total Sales"
)

st.dataframe(
    discount_sales.reset_index(name="total_sales"),
    width="stretch"
)


# Step 40: Sales by Quantity

st.subheader("Sales by Quantity")

quantity_sales = (
    sales.groupby("quantity")["total_value"]
    .sum()
    .sort_index()
)

st.bar_chart(
    quantity_sales,
    x_label="Quantity",
    y_label="Total Sales"
)

st.dataframe(
    quantity_sales.reset_index(name="total_sales"),
    width="stretch"
)


# Step 42: Sales by Year

st.subheader("Sales by Year")

sales["year"] = sales["date"].dt.year

yearly_sales = (
    sales.groupby("year")["total_value"]
    .sum()
    .sort_index()
)

st.bar_chart(
    yearly_sales,
    x_label="Year",
    y_label="Total Sales"
)

st.dataframe(
    yearly_sales.reset_index(name="total_sales"),
    width="stretch"
)

# Step 44: Top 10 Customers by Sales

st.subheader("Top 10 Customers by Sales")

customer_sales = (
    sales.groupby("customer_id")["total_value"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(
    customer_sales,
    x_label="Customer ID",
    y_label="Total Sales"
)

st.dataframe(
    customer_sales.reset_index(name="total_sales"),
    width="stretch"
)

# Step 46: Sales by Customer Segment

st.subheader("Sales by Customer Segment")

customer_path = BASE_PATH / "cleaned_customer_master.csv"

customers = pd.read_csv(customer_path)

segment_sales = (
    sales.merge(
        customers[["cust_id", "loyalty_segment"]],
        left_on="customer_id",
        right_on="cust_id",
        how="left"
    )
    .groupby("loyalty_segment")["total_value"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(
    segment_sales,
    x_label="Customer Segment",
    y_label="Total Sales"
)

st.dataframe(
    segment_sales.reset_index(name="total_sales"),
    width="stretch"
)

# Step 48: Sales by Preferred Channel

st.subheader("Sales by Preferred Channel")

preferred_channel_sales = (
    sales.merge(
        customers[["cust_id", "preferred_channel"]],
        left_on="customer_id",
        right_on="cust_id",
        how="left"
    )
    .groupby("preferred_channel")["total_value"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(
    preferred_channel_sales,
    x_label="Preferred Channel",
    y_label="Total Sales"
)

st.dataframe(
    preferred_channel_sales.reset_index(name="total_sales"),
    width="stretch"
)

# Step 50: Sales by Customer Gender

st.subheader("Sales by Customer Gender")

gender_sales = (
    sales.merge(
        customers[["cust_id", "gender"]],
        left_on="customer_id",
        right_on="cust_id",
        how="left"
    )
    .groupby("gender")["total_value"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(
    gender_sales,
    x_label="Gender",
    y_label="Total Sales"
)

st.dataframe(
    gender_sales.reset_index(name="total_sales"),
    width="stretch"
)

# Step 52: Sales by Customer City

st.subheader("Sales by Customer City")

city_sales = (
    sales.merge(
        customers[["cust_id", "city"]],
        left_on="customer_id",
        right_on="cust_id",
        how="left"
    )
    .groupby("city")["total_value"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(
    city_sales,
    x_label="City",
    y_label="Total Sales"
)

st.dataframe(
    city_sales.reset_index(name="total_sales"),
    width="stretch"
)

# Step 54: Sales by Customer Age Group

st.subheader("Sales by Customer Age Group")

customer_age_sales = sales.merge(
    customers[["cust_id", "age"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

customer_age_sales["age_group"] = pd.cut(
    customer_age_sales["age"],
    bins=[0, 18, 25, 35, 45, 55, 65, 100],
    labels=[
        "0-18",
        "19-25",
        "26-35",
        "36-45",
        "46-55",
        "56-65",
        "66+"
    ]
)

age_group_sales = (
    customer_age_sales
    .groupby("age_group", observed=False)["total_value"]
    .sum()
)

st.bar_chart(
    age_group_sales,
    x_label="Age Group",
    y_label="Total Sales"
)

st.dataframe(
    age_group_sales.reset_index(name="total_sales"),
    width="stretch"
)

# Step 56: Sales by Customer Preferred Channel & Age Group

st.subheader("Sales by Customer Preferred Channel & Age Group")

channel_age_sales = sales.merge(
    customers[["cust_id", "preferred_channel", "age"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

channel_age_sales["age_group"] = pd.cut(
    channel_age_sales["age"],
    bins=[0, 18, 25, 35, 45, 55, 65, 100],
    labels=[
        "0-18",
        "19-25",
        "26-35",
        "36-45",
        "46-55",
        "56-65",
        "66+"
    ]
)

channel_age_sales_summary = (
    channel_age_sales
    .groupby(
        ["preferred_channel", "age_group"],
        observed=False
    )["total_value"]
    .sum()
    .reset_index()
)

channel_age_pivot = channel_age_sales_summary.pivot(
    index="age_group",
    columns="preferred_channel",
    values="total_value"
).fillna(0)

st.bar_chart(
    channel_age_pivot,
    x_label="Age Group",
    y_label="Total Sales"
)

st.dataframe(
    channel_age_summary if False else channel_age_pivot,
    width="stretch"
)

# Step 58: Sales by Customer City & Age Group

st.subheader("Sales by Customer City & Age Group")

city_age_sales = sales.merge(
    customers[["cust_id", "city", "age"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

city_age_sales["age_group"] = pd.cut(
    city_age_sales["age"],
    bins=[0, 18, 25, 35, 45, 55, 65, 100],
    labels=[
        "0-18",
        "19-25",
        "26-35",
        "36-45",
        "46-55",
        "56-65",
        "66+"
    ]
)

city_age_summary = (
    city_age_sales
    .groupby(
        ["city", "age_group"],
        observed=False
    )["total_value"]
    .sum()
    .reset_index()
)

city_age_pivot = city_age_summary.pivot(
    index="age_group",
    columns="city",
    values="total_value"
).fillna(0)

st.bar_chart(
    city_age_pivot,
    x_label="Age Group",
    y_label="Total Sales"
)

st.dataframe(
    city_age_pivot,
    width="stretch"
)

# Step 60: Sales by Customer Gender & Age Group

st.subheader("Sales by Customer Gender & Age Group")

gender_age_sales = sales.merge(
    customers[["cust_id", "gender", "age"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

gender_age_sales["age_group"] = pd.cut(
    gender_age_sales["age"],
    bins=[0, 18, 25, 35, 45, 55, 65, 100],
    labels=[
        "0-18",
        "19-25",
        "26-35",
        "36-45",
        "46-55",
        "56-65",
        "66+"
    ]
)

gender_age_summary = (
    gender_age_sales
    .groupby(
        ["age_group", "gender"],
        observed=False
    )["total_value"]
    .sum()
    .reset_index()
)

gender_age_pivot = gender_age_summary.pivot(
    index="age_group",
    columns="gender",
    values="total_value"
).fillna(0)

st.bar_chart(
    gender_age_pivot,
    x_label="Age Group",
    y_label="Total Sales"
)

st.dataframe(
    gender_age_pivot,
    width="stretch"
)

# Step 62: Sales by Customer Loyalty Segment & Age Group

st.subheader("Sales by Customer Loyalty Segment & Age Group")

loyalty_age_sales = sales.merge(
    customers[["cust_id", "loyalty_segment", "age"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

loyalty_age_sales["age_group"] = pd.cut(
    loyalty_age_sales["age"],
    bins=[0, 18, 25, 35, 45, 55, 65, 100],
    labels=[
        "0-18",
        "19-25",
        "26-35",
        "36-45",
        "46-55",
        "56-65",
        "66+"
    ]
)

loyalty_age_summary = (
    loyalty_age_sales
    .groupby(
        ["age_group", "loyalty_segment"],
        observed=False
    )["total_value"]
    .sum()
    .reset_index()
)

loyalty_age_pivot = loyalty_age_summary.pivot(
    index="age_group",
    columns="loyalty_segment",
    values="total_value"
).fillna(0)

st.bar_chart(
    loyalty_age_pivot,
    x_label="Age Group",
    y_label="Total Sales"
)

st.dataframe(
    loyalty_age_pivot,
    width="stretch"
)

# Step 64: Sales by Customer Preferred Channel & Loyalty Segment

st.subheader("Sales by Customer Preferred Channel & Loyalty Segment")

channel_loyalty_sales = sales.merge(
    customers[["cust_id", "preferred_channel", "loyalty_segment"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

channel_loyalty_summary = (
    channel_loyalty_sales
    .groupby(
        ["preferred_channel", "loyalty_segment"]
    )["total_value"]
    .sum()
    .reset_index()
)

channel_loyalty_pivot = channel_loyalty_summary.pivot(
    index="loyalty_segment",
    columns="preferred_channel",
    values="total_value"
).fillna(0)

st.bar_chart(
    channel_loyalty_pivot,
    x_label="Loyalty Segment",
    y_label="Total Sales"
)

st.dataframe(
    channel_loyalty_pivot,
    width="stretch"
)

# Step 66: Sales by Customer Gender & Loyalty Segment

st.subheader("Sales by Customer Gender & Loyalty Segment")

gender_loyalty_sales = sales.merge(
    customers[["cust_id", "gender", "loyalty_segment"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

gender_loyalty_summary = (
    gender_loyalty_sales
    .groupby(
        ["loyalty_segment", "gender"]
    )["total_value"]
    .sum()
    .reset_index()
)

gender_loyalty_pivot = gender_loyalty_summary.pivot(
    index="loyalty_segment",
    columns="gender",
    values="total_value"
).fillna(0)

st.bar_chart(
    gender_loyalty_pivot,
    x_label="Loyalty Segment",
    y_label="Total Sales"
)

st.dataframe(
    gender_loyalty_pivot,
    width="stretch"
)

# Step 68: Sales by Customer City & Loyalty Segment

st.subheader("Sales by Customer City & Loyalty Segment")

city_loyalty_sales = sales.merge(
    customers[["cust_id", "city", "loyalty_segment"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

city_loyalty_summary = (
    city_loyalty_sales
    .groupby(
        ["loyalty_segment", "city"]
    )["total_value"]
    .sum()
    .reset_index()
)

city_loyalty_pivot = city_loyalty_summary.pivot(
    index="loyalty_segment",
    columns="city",
    values="total_value"
).fillna(0)

st.bar_chart(
    city_loyalty_pivot,
    x_label="Loyalty Segment",
    y_label="Total Sales"
)

st.dataframe(
    city_loyalty_pivot,
    width="stretch"
)

# Step 70: Sales by Customer Preferred Channel & Gender

st.subheader("Sales by Customer Preferred Channel & Gender")

channel_gender_sales = sales.merge(
    customers[["cust_id", "preferred_channel", "gender"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

channel_gender_summary = (
    channel_gender_sales
    .groupby(["preferred_channel", "gender"])["total_value"]
    .sum()
    .reset_index()
)

channel_gender_pivot = channel_gender_summary.pivot(
    index="preferred_channel",
    columns="gender",
    values="total_value"
).fillna(0)

st.bar_chart(
    channel_gender_pivot,
    x_label="Preferred Channel",
    y_label="Total Sales"
)

st.dataframe(
    channel_gender_pivot,
    width="stretch"
)

# Step 72: Sales by Customer City & Preferred Channel

st.subheader("Sales by Customer City & Preferred Channel")

city_channel_sales = sales.merge(
    customers[["cust_id", "city", "preferred_channel"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

city_channel_summary = (
    city_channel_sales
    .groupby(["city", "preferred_channel"])["total_value"]
    .sum()
    .reset_index()
)

city_channel_pivot = city_channel_summary.pivot(
    index="city",
    columns="preferred_channel",
    values="total_value"
).fillna(0)

st.bar_chart(
    city_channel_pivot,
    x_label="City",
    y_label="Total Sales"
)

st.dataframe(
    city_channel_pivot,
    width="stretch"
)

# Step 74: Sales by Customer City & Gender

st.subheader("Sales by Customer City & Gender")

city_gender_sales = sales.merge(
    customers[["cust_id", "city", "gender"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

city_gender_summary = (
    city_gender_sales
    .groupby(["city", "gender"])["total_value"]
    .sum()
    .reset_index()
)

city_gender_pivot = city_gender_summary.pivot(
    index="city",
    columns="gender",
    values="total_value"
).fillna(0)

st.bar_chart(
    city_gender_pivot,
    x_label="City",
    y_label="Total Sales"
)

st.dataframe(
    city_gender_pivot,
    width="stretch"
)



# Step 78: Sales by Customer Loyalty Segment & Gender

st.subheader("Sales by Customer Loyalty Segment & Gender")

loyalty_gender_sales = sales.merge(
    customers[["cust_id", "loyalty_segment", "gender"]],
    left_on="customer_id",
    right_on="cust_id",
    how="left"
)

loyalty_gender_summary = (
    loyalty_gender_sales
    .groupby(["loyalty_segment", "gender"])["total_value"]
    .sum()
    .reset_index()
)

loyalty_gender_pivot = loyalty_gender_summary.pivot(
    index="loyalty_segment",
    columns="gender",
    values="total_value"
).fillna(0)

st.bar_chart(
    loyalty_gender_pivot,
    x_label="Loyalty Segment",
    y_label="Total Sales"
)

st.dataframe(
    loyalty_gender_pivot,
    width="stretch"
)

import streamlit as st
import pandas as pd
from pathlib import Path

# Customer Analytics Page
st.title("Customer Segmentation")
st.write("Explore customer behavior and purchasing patterns.")

# Project root directory
BASE_PATH = Path(__file__).resolve().parent.parent.parent

# Dataset paths
customer_path = BASE_PATH / "cleaned_customer_master.csv"
sales_path = BASE_PATH / "cleaned_sales_transactions.zip"


# Load customer master CSV
@st.cache_data
def load_customers(path):
    return pd.read_csv(path)


# Load sales transactions from ZIP
@st.cache_data
def load_sales(path):
    return pd.read_csv(
        path,
        compression="zip",
        usecols=["customer_id", "date"]
    )


# Check that datasets exist
if not customer_path.exists():
    st.error(f"Customer dataset not found: {customer_path.name}")
    st.stop()

if not sales_path.exists():
    st.error(f"Sales dataset not found: {sales_path.name}")
    st.stop()


# Load datasets
try:
    customers = load_customers(customer_path)
    sales_data = load_sales(sales_path)
except Exception as e:
    st.error(f"Dataset loading failed: {e}")
    st.stop()


# Validate required columns
required_customer_columns = ["cust_id", "loyalty_segment"]
required_sales_columns = ["customer_id", "date"]

missing_customer_columns = [
    col for col in required_customer_columns
    if col not in customers.columns
]
missing_sales_columns = [
    col for col in required_sales_columns
    if col not in sales_data.columns
]

if missing_customer_columns:
    st.error(f"Customer CSV missing columns: {missing_customer_columns}")
    st.stop()

if missing_sales_columns:
    st.error(f"Sales ZIP missing columns: {missing_sales_columns}")
    st.stop()


# Clean required fields
customers = customers.dropna(subset=["cust_id"]).copy()
sales_data["date"] = pd.to_datetime(
    sales_data["date"],
    errors="coerce"
)
sales_data = sales_data.dropna(
    subset=["customer_id", "date"]
).copy()

st.success("Customer CSV and Sales ZIP loaded successfully.")


# --------------------------------------------------
# 1. CUSTOMER OVERVIEW
# --------------------------------------------------
st.subheader("Customer Overview")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Customers",
    f"{customers['cust_id'].nunique():,}"
)

col2.metric(
    "Customer Segments",
    customers["loyalty_segment"].nunique()
)

col3.metric(
    "Customer Records",
    f"{len(customers):,}"
)

st.dataframe(customers.head(30), width="stretch")


# --------------------------------------------------
# 2. CUSTOMER SEGMENTATION
# --------------------------------------------------
st.subheader("Customer Segmentation")

segment_summary = (
    customers["loyalty_segment"]
    .fillna("Unknown")
    .value_counts()
    .rename_axis("Customer Segment")
    .reset_index(name="Customer Count")
)

st.dataframe(segment_summary, width="stretch")

st.bar_chart(
    segment_summary.set_index("Customer Segment")["Customer Count"],
    x_label="Customer Segment",
    y_label="Customer Count"
)


# --------------------------------------------------
# 3. LAST PURCHASE AND CHURN RISK
# --------------------------------------------------
st.subheader("Churn Risk Analysis")

if sales_data.empty:
    st.warning("No valid sales transactions are available for churn analysis.")
    st.stop()

last_purchase = (
    sales_data
    .groupby("customer_id")["date"]
    .max()
    .reset_index()
)

last_purchase.columns = [
    "customer_id",
    "last_purchase_date"
]

analysis_date = sales_data["date"].max()

last_purchase["days_since_purchase"] = (
    analysis_date - last_purchase["last_purchase_date"]
).dt.days

last_purchase["churn_risk"] = pd.cut(
    last_purchase["days_since_purchase"],
    bins=[-1, 90, 180, float("inf")],
    labels=["Low", "Medium", "High"]
)

risk_order = ["Low", "Medium", "High"]

risk_summary = (
    last_purchase["churn_risk"]
    .value_counts()
    .reindex(risk_order, fill_value=0)
    .rename_axis("Churn Risk")
    .reset_index(name="Customer Count")
)

st.dataframe(risk_summary, width="stretch")

st.bar_chart(
    risk_summary.set_index("Churn Risk")["Customer Count"],
    x_label="Churn Risk",
    y_label="Customer Count"
)


# --------------------------------------------------
# 4. CUSTOMER SEGMENT AND CHURN RISK
# --------------------------------------------------
st.subheader("Customer Segment and Churn Risk")

customer_risk = customers[
    ["cust_id", "loyalty_segment"]
].copy()

customer_risk = customer_risk.merge(
    last_purchase,
    left_on="cust_id",
    right_on="customer_id",
    how="left"
)

# Customers without a matching sales record are not assigned
# a churn category because their last purchase is unknown.
segment_risk_summary = (
    customer_risk
    .groupby(
        ["loyalty_segment", "churn_risk"],
        observed=True,
        dropna=False
    )
    .size()
    .reset_index(name="Customer Count")
)

st.dataframe(segment_risk_summary, width="stretch")


# --------------------------------------------------
# 5. HIGH AND MEDIUM RISK CUSTOMER DETAILS
# --------------------------------------------------
st.subheader("Churn Risk Customer Details")

risk_customers = customer_risk[
    customer_risk["churn_risk"].isin(["High", "Medium"])
][
    [
        "cust_id",
        "loyalty_segment",
        "last_purchase_date",
        "days_since_purchase",
        "churn_risk"
    ]
].copy()

risk_customers = risk_customers.sort_values(
    "days_since_purchase",
    ascending=False
)

st.dataframe(risk_customers.head(30), width="stretch")


# --------------------------------------------------
# 6. CHURN RISK SUMMARY
# --------------------------------------------------
st.subheader("Churn Risk Summary")

total_customers_with_sales = last_purchase["customer_id"].nunique()

risk_summary["Risk Percentage"] = (
    risk_summary["Customer Count"]
    .div(max(total_customers_with_sales, 1))
    .mul(100)
    .round(2)
)

st.dataframe(risk_summary, width="stretch")


# --------------------------------------------------
# 7. CUSTOMER SEGMENT SUMMARY
# --------------------------------------------------
st.subheader("Customer Segmentation Summary")

segment_summary["Customer Percentage"] = (
    segment_summary["Customer Count"]
    .div(max(len(customers), 1))
    .mul(100)
    .round(2)
)

st.dataframe(segment_summary, width="stretch")


# --------------------------------------------------
# 8. CUSTOMER RISK OVERVIEW
# --------------------------------------------------
st.subheader("Customer Risk Overview")

st.bar_chart(
    risk_summary.set_index("Churn Risk")["Risk Percentage"],
    x_label="Churn Risk",
    y_label="Customer Percentage"
)


# --------------------------------------------------
# 9. CUSTOMER ANALYTICS SUMMARY
# --------------------------------------------------
st.subheader("Customer Analytics Summary")

high_risk_customers = int(
    risk_summary.loc[
        risk_summary["Churn Risk"] == "High",
        "Customer Count"
    ].iloc[0]
)

medium_risk_customers = int(
    risk_summary.loc[
        risk_summary["Churn Risk"] == "Medium",
        "Customer Count"
    ].iloc[0]
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Customers",
    f"{customers['cust_id'].nunique():,}"
)

col2.metric(
    "Customer Segments",
    f"{customers['loyalty_segment'].nunique():,}"
)

col3.metric(
    "High Risk Customers",
    f"{high_risk_customers:,}"
)

st.write(f"**Medium Risk Customers:** {medium_risk_customers:,}")


# --------------------------------------------------
# 10. CUSTOMER ANALYTICS INSIGHTS
# --------------------------------------------------
st.subheader("Customer Analytics Insights")

st.write(
    f"Total customer base analyzed: "
    f"**{customers['cust_id'].nunique():,} customers**."
)

st.write(
    f"Customer base is divided into "
    f"**{customers['loyalty_segment'].nunique()} loyalty segments**."
)

st.write(
    f"High churn risk customers identified: **{high_risk_customers:,}**."
)

st.write(
    f"Medium churn risk customers identified: **{medium_risk_customers:,}**."
)

st.info(
    "Customer segmentation and churn-risk analysis can support "
    "targeted retention and customer engagement decisions."
)

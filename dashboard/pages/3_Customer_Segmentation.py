
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Customer Segmentation | RetailPulse",
    page_icon="👥",
    layout="wide"
)

st.title("👥 Customer Segmentation")
st.write("Explore customer behavior, loyalty segments, and churn risk.")

# --------------------------------------------------
# 1. PROJECT ROOT AND DATASET PATHS
# --------------------------------------------------
BASE_PATH = Path(__file__).resolve().parent.parent.parent

customer_path = BASE_PATH / "cleaned_customer_master.csv"
sales_path = BASE_PATH / "cleaned_sales_transactions.zip"


# --------------------------------------------------
# 2. LOAD DATASETS
# --------------------------------------------------
@st.cache_data
def load_customers(path):
    return pd.read_csv(path)


@st.cache_data
def load_sales(path):
    return pd.read_csv(
        path,
        compression="zip",
        usecols=["customer_id", "date"]
    )


# Check files before loading
if not customer_path.is_file():
    st.error(f"Customer CSV not found: {customer_path}")
    st.stop()

if not sales_path.is_file():
    st.error(f"Sales ZIP not found: {sales_path}")
    st.stop()

try:
    customers = load_customers(customer_path)
    sales_data = load_sales(sales_path)
except Exception as e:
    st.error(f"Dataset loading failed: {e}")
    st.stop()


# --------------------------------------------------
# 3. VALIDATE REQUIRED COLUMNS
# --------------------------------------------------
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
    st.error(
        f"Customer CSV missing columns: {missing_customer_columns}"
    )
    st.stop()

if missing_sales_columns:
    st.error(
        f"Sales ZIP missing columns: {missing_sales_columns}"
    )
    st.stop()


# --------------------------------------------------
# 4. CLEAN DATA
# --------------------------------------------------
customers = customers.copy()
sales_data = sales_data.copy()

# Normalize customer IDs so joins work consistently.
customers["cust_id"] = (
    customers["cust_id"]
    .astype("string")
    .str.strip()
)

sales_data["customer_id"] = (
    sales_data["customer_id"]
    .astype("string")
    .str.strip()
)

customers = customers[
    customers["cust_id"].notna()
    & customers["cust_id"].ne("")
    & customers["cust_id"].ne("<NA>")
].copy()

customers["loyalty_segment"] = (
    customers["loyalty_segment"]
    .fillna("Unknown")
    .astype(str)
)

sales_data["date"] = pd.to_datetime(
    sales_data["date"],
    errors="coerce"
)

sales_data = sales_data.dropna(
    subset=["customer_id", "date"]
).copy()

sales_data = sales_data[
    sales_data["customer_id"].ne("")
    & sales_data["customer_id"].ne("<NA>")
].copy()

if customers.empty:
    st.warning("No valid customer records found.")
    st.stop()

if sales_data.empty:
    st.warning("No valid sales records found.")
    st.stop()

st.success("Customer CSV and Sales ZIP loaded successfully.")


# --------------------------------------------------
# 5. CUSTOMER OVERVIEW
# --------------------------------------------------
st.subheader("Customer Overview")

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
    "Customer Records",
    f"{len(customers):,}"
)

st.dataframe(customers.head(30), width="stretch")


# --------------------------------------------------
# 6. CUSTOMER SEGMENTATION
# --------------------------------------------------
st.subheader("Customer Segmentation")

segment_summary = (
    customers.groupby("loyalty_segment")
    .size()
    .reset_index(name="Customer Count")
    .rename(
        columns={"loyalty_segment": "Customer Segment"}
    )
    .sort_values("Customer Count", ascending=False)
)

segment_summary["Customer Percentage"] = (
    segment_summary["Customer Count"]
    .div(max(len(customers), 1))
    .mul(100)
    .round(2)
)

st.dataframe(segment_summary, width="stretch")

st.bar_chart(
    segment_summary.set_index("Customer Segment")[
        "Customer Count"
    ],
    x_label="Customer Segment",
    y_label="Customer Count"
)


# --------------------------------------------------
# 7. LAST PURCHASE AND CHURN RISK
# --------------------------------------------------
st.subheader("Churn Risk Analysis")

last_purchase = (
    sales_data.groupby("customer_id")["date"]
    .max()
    .reset_index()
    .rename(columns={"date": "last_purchase_date"})
)

# Use the latest available sales date as the analysis date.
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

total_customers_with_sales = (
    last_purchase["customer_id"].nunique()
)

risk_summary["Risk Percentage"] = (
    risk_summary["Customer Count"]
    .div(max(total_customers_with_sales, 1))
    .mul(100)
    .round(2)
)

st.caption(
    f"Analysis date: {analysis_date.strftime('%d %b %Y')}. "
    "Risk is estimated using days since the latest recorded purchase."
)

st.dataframe(risk_summary, width="stretch")

st.bar_chart(
    risk_summary.set_index("Churn Risk")["Customer Count"],
    x_label="Churn Risk",
    y_label="Customer Count"
)


# --------------------------------------------------
# 8. CUSTOMER SEGMENT AND CHURN RISK
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

# Customers with no matching sales record have unknown risk.
customer_risk["churn_risk"] = (
    customer_risk["churn_risk"].astype("object")
)

customer_risk.loc[
    customer_risk["last_purchase_date"].isna(),
    "churn_risk"
] = "Unknown"

segment_risk_summary = (
    customer_risk.groupby(
        ["loyalty_segment", "churn_risk"],
        dropna=False
    )
    .size()
    .reset_index(name="Customer Count")
    .rename(
        columns={"loyalty_segment": "Customer Segment"}
    )
)

st.dataframe(segment_risk_summary, width="stretch")


# --------------------------------------------------
# 9. MEDIUM AND HIGH RISK CUSTOMER DETAILS
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

if risk_customers.empty:
    st.info("No medium- or high-risk customers were identified.")
else:
    st.dataframe(
        risk_customers.head(30),
        width="stretch"
    )


# --------------------------------------------------
# 10. CUSTOMER RISK OVERVIEW
# --------------------------------------------------
st.subheader("Customer Risk Overview")

st.bar_chart(
    risk_summary.set_index("Churn Risk")["Risk Percentage"],
    x_label="Churn Risk",
    y_label="Customers with Sales (%)"
)


# --------------------------------------------------
# 11. CUSTOMER ANALYTICS SUMMARY
# --------------------------------------------------
st.subheader("Customer Analytics Summary")

risk_counts = risk_summary.set_index("Churn Risk")[
    "Customer Count"
]

high_risk_customers = int(risk_counts.get("High", 0))
medium_risk_customers = int(risk_counts.get("Medium", 0))
low_risk_customers = int(risk_counts.get("Low", 0))

customers_without_sales = int(
    customer_risk["last_purchase_date"].isna().sum()
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

col1, col2, col3 = st.columns(3)

col1.metric(
    "Low Risk Customers",
    f"{low_risk_customers:,}"
)

col2.metric(
    "Medium Risk Customers",
    f"{medium_risk_customers:,}"
)

col3.metric(
    "Customers Without Sales",
    f"{customers_without_sales:,}"
)


# --------------------------------------------------
# 12. CUSTOMER ANALYTICS INSIGHTS
# --------------------------------------------------
st.subheader("Customer Analytics Insights")

st.write(
    f"Total customer base analyzed: "
    f"**{customers['cust_id'].nunique():,} customers**."
)

st.write(
    f"Number of loyalty segments: "
    f"**{customers['loyalty_segment'].nunique()}**."
)

st.write(
    f"High churn-risk customers: **{high_risk_customers:,}**."
)

st.write(
    f"Medium churn-risk customers: **{medium_risk_customers:,}**."
)

st.write(
    f"Low churn-risk customers: **{low_risk_customers:,}**."
)

st.info(
    "Churn risk is estimated from days since the latest recorded "
    "purchase. These thresholds are analytical rules, not confirmed "
    "predictions that a customer will leave."
)


import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Customer Segmentation | RetailPulse",
    page_icon="👥",
    layout="wide"
)

st.title("👥 Customer Segmentation")
st.write("Explore customer behavior, loyalty segments, purchasing patterns, and churn risk.")

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
    st.error(f"Customer CSV missing columns: {missing_customer_columns}")
    st.stop()

if missing_sales_columns:
    st.error(f"Sales ZIP missing columns: {missing_sales_columns}")
    st.stop()


# --------------------------------------------------
# 4. CLEAN DATA
# --------------------------------------------------
customers = customers.copy()
sales_data = sales_data.copy()

customers["cust_id"] = (
    customers["cust_id"].astype("string").str.strip()
)

sales_data["customer_id"] = (
    sales_data["customer_id"].astype("string").str.strip()
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
    sales_data["date"], errors="coerce"
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

# Use strings for consistent joins.
customers["cust_id"] = customers["cust_id"].astype(str)
sales_data["customer_id"] = sales_data["customer_id"].astype(str)

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

with st.expander("View Customer Data"):
    st.dataframe(customers.head(30), use_container_width=True)


# --------------------------------------------------
# 6. CUSTOMER SEGMENTATION
# --------------------------------------------------
st.divider()
st.subheader("Customer Segmentation")

segment_summary = (
    customers.groupby("loyalty_segment")
    .size()
    .reset_index(name="Customer Count")
    .rename(columns={"loyalty_segment": "Customer Segment"})
    .sort_values("Customer Count", ascending=False)
)

segment_summary["Customer Percentage"] = (
    segment_summary["Customer Count"]
    .div(max(len(customers), 1))
    .mul(100)
    .round(2)
)

col1, col2 = st.columns(2)

with col1:
    fig_bar = px.bar(
        segment_summary,
        x="Customer Segment",
        y="Customer Count",
        color="Customer Segment",
        text="Customer Count",
        title="Customers by Segment"
    )
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    fig_pie = px.pie(
        segment_summary,
        names="Customer Segment",
        values="Customer Count",
        title="Customer Segment Distribution"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Donut chart
st.subheader("Customer Segment Share")

fig_donut = px.pie(
    segment_summary,
    names="Customer Segment",
    values="Customer Count",
    hole=0.55,
    title="Customer Loyalty Segment Share"
)
fig_donut.update_traces(textposition="inside", textinfo="percent+label")
st.plotly_chart(fig_donut, use_container_width=True)

with st.expander("View Segment Summary"):
    st.dataframe(segment_summary, use_container_width=True)


# --------------------------------------------------
# 7. CUSTOMER PURCHASE METRICS
# --------------------------------------------------
st.divider()
st.subheader("Customer Purchase Behaviour")

# One row per customer with purchase count and last purchase date.
customer_purchase = (
    sales_data.groupby("customer_id")
    .agg(
        purchase_frequency=("date", "size"),
        last_purchase_date=("date", "max")
    )
    .reset_index()
)

analysis_date = sales_data["date"].max()

customer_purchase["days_since_purchase"] = (
    analysis_date - customer_purchase["last_purchase_date"]
).dt.days

customer_analysis = customers[
    ["cust_id", "loyalty_segment"]
].merge(
    customer_purchase,
    left_on="cust_id",
    right_on="customer_id",
    how="left"
)

customer_analysis["purchase_frequency"] = (
    customer_analysis["purchase_frequency"].fillna(0)
)

customer_analysis["days_since_purchase"] = (
    customer_analysis["days_since_purchase"]
)

customer_analysis["customer_status"] = (
    customer_analysis["last_purchase_date"]
    .notna()
    .map({True: "Has Sales", False: "No Sales Record"})
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Customers with Sales",
    f"{customer_purchase['customer_id'].nunique():,}"
)

col2.metric(
    "Average Purchase Records",
    f"{customer_purchase['purchase_frequency'].mean():,.1f}"
)

col3.metric(
    "Customers Without Sales",
    f"{customer_analysis['last_purchase_date'].isna().sum():,}"
)

# Purchase frequency histogram
fig_hist = px.histogram(
    customer_analysis,
    x="purchase_frequency",
    color="loyalty_segment",
    nbins=25,
    title="Distribution of Purchase Frequency",
    labels={
        "purchase_frequency": "Number of Sales Records",
        "loyalty_segment": "Customer Segment"
    }
)
st.plotly_chart(fig_hist, use_container_width=True)

# Scatter plot: purchase frequency vs recency
scatter_data = customer_analysis.dropna(
    subset=["days_since_purchase"]
).copy()

if not scatter_data.empty:
    fig_scatter = px.scatter(
        scatter_data,
        x="purchase_frequency",
        y="days_since_purchase",
        color="loyalty_segment",
        hover_data=["cust_id"],
        title="Purchase Frequency vs Days Since Last Purchase",
        labels={
            "purchase_frequency": "Purchase Frequency (Sales Records)",
            "days_since_purchase": "Days Since Last Purchase",
            "loyalty_segment": "Customer Segment"
        },
        opacity=0.7
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("Scatter plot requires customers with valid sales records.")

st.caption(
    "Purchase frequency represents the number of sales records per customer, "
    "not necessarily the number of unique shopping visits."
)


# --------------------------------------------------
# 8. LAST PURCHASE AND CHURN RISK
# --------------------------------------------------
st.divider()
st.subheader("Churn Risk Analysis")

last_purchase = customer_purchase[
    ["customer_id", "last_purchase_date", "days_since_purchase"]
].copy()


def classify_risk(days):
    if pd.isna(days):
        return "Unknown"
    if days <= 90:
        return "Low"
    if days <= 180:
        return "Medium"
    return "High"


last_purchase["churn_risk"] = (
    last_purchase["days_since_purchase"].apply(classify_risk)
)

risk_order = ["Low", "Medium", "High", "Unknown"]

customer_risk = customers[
    ["cust_id", "loyalty_segment"]
].merge(
    last_purchase,
    left_on="cust_id",
    right_on="customer_id",
    how="left"
)

customer_risk["churn_risk"] = (
    customer_risk["churn_risk"].fillna("Unknown")
)

risk_summary = (
    customer_risk["churn_risk"]
    .value_counts()
    .reindex(risk_order, fill_value=0)
    .rename_axis("Churn Risk")
    .reset_index(name="Customer Count")
)

total_customers = len(customer_risk)

risk_summary["Risk Percentage"] = (
    risk_summary["Customer Count"]
    .div(max(total_customers, 1))
    .mul(100)
    .round(2)
)

st.caption(
    f"Analysis date: {analysis_date.strftime('%d %b %Y')}. "
    "Risk is estimated using days since the latest recorded purchase."
)

col1, col2 = st.columns(2)

with col1:
    fig_risk_bar = px.bar(
        risk_summary,
        x="Churn Risk",
        y="Customer Count",
        color="Churn Risk",
        text="Customer Count",
        title="Customers by Churn Risk",
        category_orders={"Churn Risk": risk_order}
    )
    st.plotly_chart(fig_risk_bar, use_container_width=True)

with col2:
    fig_risk_donut = px.pie(
        risk_summary,
        names="Churn Risk",
        values="Customer Count",
        hole=0.5,
        title="Churn Risk Distribution"
    )
    st.plotly_chart(fig_risk_donut, use_container_width=True)

col1, col2, col3 = st.columns(3)

risk_counts = risk_summary.set_index("Churn Risk")["Customer Count"]

col1.metric("Low Risk", f"{int(risk_counts.get('Low', 0)):,}")
col2.metric("Medium Risk", f"{int(risk_counts.get('Medium', 0)):,}")
col3.metric("High Risk", f"{int(risk_counts.get('High', 0)):,}")

with st.expander("View Risk Summary"):
    st.dataframe(risk_summary, use_container_width=True)


# --------------------------------------------------
# 9. CUSTOMER SEGMENT AND CHURN RISK
# --------------------------------------------------
st.divider()
st.subheader("Customer Segment vs Churn Risk")

segment_risk_summary = (
    customer_risk.groupby(
        ["loyalty_segment", "churn_risk"],
        dropna=False
    )
    .size()
    .reset_index(name="Customer Count")
    .rename(columns={"loyalty_segment": "Customer Segment"})
)

fig_segment_risk = px.bar(
    segment_risk_summary,
    x="Customer Segment",
    y="Customer Count",
    color="churn_risk",
    barmode="group",
    title="Churn Risk Across Loyalty Segments",
    labels={
        "loyalty_segment": "Customer Segment",
        "churn_risk": "Churn Risk"
    }
)
st.plotly_chart(fig_segment_risk, use_container_width=True)

with st.expander("View Segment and Risk Table"):
    st.dataframe(segment_risk_summary, use_container_width=True)


# --------------------------------------------------
# 10. MEDIUM AND HIGH RISK CUSTOMER DETAILS
# --------------------------------------------------
st.divider()
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
    ascending=False,
    na_position="last"
)

if risk_customers.empty:
    st.info("No medium- or high-risk customers were identified.")
else:
    st.dataframe(
        risk_customers.head(100),
        use_container_width=True
    )


# --------------------------------------------------
# 11. CUSTOMER ANALYTICS SUMMARY
# --------------------------------------------------
st.divider()
st.subheader("Customer Analytics Summary")

high_risk_customers = int(risk_counts.get("High", 0))
medium_risk_customers = int(risk_counts.get("Medium", 0))
low_risk_customers = int(risk_counts.get("Low", 0))
customers_without_sales = int(
    customer_risk["last_purchase_date"].isna().sum()
)

col1, col2, col3 = st.columns(3)

col1.metric("Total Customers", f"{customers['cust_id'].nunique():,}")
col2.metric("Customer Segments", f"{customers['loyalty_segment'].nunique():,}")
col3.metric("High Risk Customers", f"{high_risk_customers:,}")

col1, col2, col3 = st.columns(3)

col1.metric("Low Risk Customers", f"{low_risk_customers:,}")
col2.metric("Medium Risk Customers", f"{medium_risk_customers:,}")
col3.metric("Customers Without Sales", f"{customers_without_sales:,}")

st.info(
    "Churn risk is estimated from days since the latest recorded purchase. "
    "Low risk: up to 90 days; Medium risk: 91–180 days; "
    "High risk: more than 180 days. These are rule-based categories, "
    "not predictions from a trained churn model."
)

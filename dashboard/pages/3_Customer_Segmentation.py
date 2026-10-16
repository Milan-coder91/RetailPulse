

import streamlit as st
import pandas as pd
from pathlib import Path

# Customer Analytics Page

st.title("Customer Segmentation")
st.write("Explore customer behavior and purchasing patterns.")

#BASE_PATH = Path(
  #  r"C:\Users\milan\Downloads\archive (3)\retail_clean_dataset")

BASE_PATH = Path(__file__).resolve().parent.parent.parent



customer_path = BASE_PATH / "cleaned_customer_master.csv"

customers = pd.read_csv(customer_path)

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

st.success("Customer master data loaded successfully.")

st.dataframe(
    customers.head(30),
    width="stretch"
)



st.subheader("Customer Segmentation")

segment_summary = (
    customers["loyalty_segment"]
    .value_counts()
    .reset_index()
)

segment_summary.columns = [
    "Customer Segment",
    "Customer Count"
]

st.dataframe(
    segment_summary,
    width="stretch"
)

st.bar_chart(
    segment_summary.set_index("Customer Segment")["Customer Count"],
    x_label="Customer Segment",
    y_label="Customer Count"
)



st.subheader("Churn Risk Analysis")

sales_path = BASE_PATH / "cleaned_sales_transactions.zip"

sales_data = pd.read_csv(
    sales_path,
    compression="zip",
    usecols=["customer_id", "date"]
)

sales_data["date"] = pd.to_datetime(
    sales_data["date"]
)

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

risk_summary = (
    last_purchase["churn_risk"]
    .value_counts()
    .reindex(["Low", "Medium", "High"], fill_value=0)
    .reset_index()
)

risk_summary.columns = [
    "Churn Risk",
    "Customer Count"
]

st.dataframe(
    risk_summary,
    width="stretch"
)

st.bar_chart(
    risk_summary.set_index("Churn Risk")["Customer Count"],
    x_label="Churn Risk",
    y_label="Customer Count"
)



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

segment_risk_summary = (
    customer_risk
    .groupby(
        ["loyalty_segment", "churn_risk"],
        observed=True
    )
    .size()
    .reset_index(name="Customer Count")
)

st.dataframe(
    segment_risk_summary,
    width="stretch"
)




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

st.dataframe(
    risk_customers.head(30),
    width="stretch"
)


st.subheader("Churn Risk Summary")

total_customers = len(last_purchase)

risk_summary["Risk Percentage"] = (
    risk_summary["Customer Count"] / total_customers * 100
).round(2)

st.dataframe(
    risk_summary,
    width="stretch"
)


st.subheader("Customer Segmentation Summary")

segment_summary["Customer Percentage"] = (
    segment_summary["Customer Count"] / len(customers) * 100
).round(2)

st.dataframe(
    segment_summary,
    width="stretch"
)



st.subheader("Customer Risk Overview")

st.bar_chart(
    risk_summary.set_index("Churn Risk")["Risk Percentage"],
    x_label="Churn Risk",
    y_label="Customer Percentage"
)



st.subheader("Customer Analytics Summary")

high_risk_customers = (
    risk_summary.loc[
        risk_summary["Churn Risk"] == "High",
        "Customer Count"
    ].iloc[0]
)

medium_risk_customers = (
    risk_summary.loc[
        risk_summary["Churn Risk"] == "Medium",
        "Customer Count"
    ].iloc[0]
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Customers",
    f"{len(customers):,}"
)

col2.metric(
    "Customer Segments",
    f"{customers['loyalty_segment'].nunique():,}"
)

col3.metric(
    "High Risk Customers",
    f"{high_risk_customers:,}"
)

st.write(
    f"**Medium Risk Customers:** {medium_risk_customers:,}"
)



st.subheader("Customer Analytics Insights")

st.write(
    f"Total customer base analyzed: **{len(customers):,} customers**."
)

st.write(
    f"Customer base is divided into **"
    f"{customers['loyalty_segment'].nunique()} loyalty segments**."
)

st.write(
    f"High churn risk customers identified: **"
    f"{high_risk_customers:,}**."
)

st.write(
    f"Medium churn risk customers identified: **"
    f"{medium_risk_customers:,}**."
)

st.info(
    "Customer segmentation and churn-risk analysis can support "
    "targeted retention and customer engagement decisions."
)

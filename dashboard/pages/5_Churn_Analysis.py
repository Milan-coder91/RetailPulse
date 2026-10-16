
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Churn Analysis",
    page_icon="📉",
    layout="wide"
)

BASE_PATH = Path(__file__).resolve().parents[2]

sales_path = BASE_PATH / "cleaned_sales_transactions.zip"
customers_path = BASE_PATH / "cleaned_customer_master.csv"

st.title("📉 Customer Churn Analysis")
st.caption("RetailPulse — Customer Retention Analytics")

@st.cache_data
def load_data():
    sales = pd.read_csv(
        sales_path,
        compression="zip",
        usecols=["customer_id", "date", "total_value"]
    )
    customers = pd.read_csv(customers_path)
    sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
    return sales, customers

try:
    sales, customers = load_data()

    reference_date = sales["date"].max()
    last_purchase = sales.groupby("customer_id")["date"].max()

    churn = pd.DataFrame({
        "customer_id": last_purchase.index,
        "days_inactive": (
            reference_date - last_purchase
        ).dt.days.values
    })

    churn["Churn Risk"] = churn["days_inactive"].apply(
        lambda days: "High Risk" if days >= 90
        else "Medium Risk" if days >= 60
        else "Low Risk"
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Customers Analyzed", len(churn))
    col2.metric("High Risk", int((churn["Churn Risk"] == "High Risk").sum()))
    col3.metric("Medium Risk", int((churn["Churn Risk"] == "Medium Risk").sum()))

    st.subheader("Churn Risk Distribution")
    st.bar_chart(churn["Churn Risk"].value_counts())

    st.subheader("Customer Inactivity Details")
    st.dataframe(
        churn.sort_values("days_inactive", ascending=False),
        use_container_width=True
    )

except FileNotFoundError as e:
    st.error(f"Required dataset missing: {e.filename}")

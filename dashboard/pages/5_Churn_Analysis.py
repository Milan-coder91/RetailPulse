
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Customer Churn Analysis",
    page_icon="📉",
    layout="wide"
)

BASE_PATH = Path(__file__).resolve().parents[2]
sales_path = BASE_PATH / "cleaned_sales_transactions.zip"
customers_path = BASE_PATH / "cleaned_customer_master.csv"

st.title("📉 Customer Churn Analysis")
st.caption("RetailPulse | Customer Retention & Risk Intelligence")

@st.cache_data
def load_data():
    sales = pd.read_csv(
        sales_path,
        compression="zip",
        usecols=["customer_id", "date", "total_value"]
    )
    customers = pd.read_csv(customers_path)

    sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
    sales["total_value"] = pd.to_numeric(
        sales["total_value"], errors="coerce"
    )
    sales = sales.dropna(
        subset=["customer_id", "date", "total_value"]
    )
    return sales, customers

try:
    sales, customers = load_data()

    reference_date = sales["date"].max()
    if pd.isna(reference_date):
        st.error("Sales dataset mein valid dates nahi mili.")
        st.stop()

    customer_activity = (
        sales.groupby("customer_id")
        .agg(
            last_purchase=("date", "max"),
            total_orders=("date", "count"),
            total_spend=("total_value", "sum"),
            avg_order_value=("total_value", "mean")
        )
        .reset_index()
    )

    customer_activity["days_inactive"] = (
        reference_date - customer_activity["last_purchase"]
    ).dt.days

    customer_activity["Churn Risk"] = pd.cut(
        customer_activity["days_inactive"],
        bins=[-1, 29, 59, 89, float("inf")],
        labels=["Active", "Low Risk", "Medium Risk", "High Risk"]
    ).astype(str)

    # Merge customer profile details where possible
    if "customer_id" in customers.columns:
        customer_activity = customer_activity.merge(
            customers.drop_duplicates("customer_id"),
            on="customer_id",
            how="left",
            suffixes=("", "_profile")
        )

    total_customers = customer_activity["customer_id"].nunique()
    high_risk = int((customer_activity["Churn Risk"] == "High Risk").sum())
    medium_risk = int((customer_activity["Churn Risk"] == "Medium Risk").sum())
    active_customers = int((customer_activity["Churn Risk"] == "Active").sum())
    risk_customers = high_risk + medium_risk
    risk_pct = (
        risk_customers / total_customers * 100
        if total_customers else 0
    )
    sales_at_risk = customer_activity.loc[
        customer_activity["Churn Risk"].isin(["High Risk", "Medium Risk"]),
        "total_spend"
    ].sum()

    # Sidebar filters
    st.sidebar.subheader("Churn Filters")
    risk_options = ["Active", "Low Risk", "Medium Risk", "High Risk"]
    selected_risks = st.sidebar.multiselect(
        "Select customer risk",
        risk_options,
        default=["Medium Risk", "High Risk"]
    )
    min_inactive = st.sidebar.slider(
        "Minimum inactive days",
        min_value=0,
        max_value=max(90, int(customer_activity["days_inactive"].max())),
        value=0
    )

    # KPI cards
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Customers Analyzed", f"{total_customers:,}")
    k2.metric("High Risk", f"{high_risk:,}")
    k3.metric("Medium Risk", f"{medium_risk:,}")
    k4.metric("Customers at Risk", f"{risk_customers:,}", f"{risk_pct:.1f}%")

    k5, k6, k7 = st.columns(3)
    k5.metric("Active Customers", f"{active_customers:,}")
    k6.metric("Sales from At-Risk Customers", f"₹{sales_at_risk:,.0f}")
    k7.metric(
        "Average Inactive Days",
        f"{customer_activity['days_inactive'].mean():.1f}"
    )

    st.info(
        f"Analysis reference date: {reference_date:%d %b %Y}. "
        "Risk levels are estimated from days since last purchase, not verified churn labels."
    )

    # Risk distribution
    left, right = st.columns(2)

    with left:
        st.subheader("Customer Risk Distribution")
        risk_counts = (
            customer_activity["Churn Risk"]
            .value_counts()
            .reindex(risk_options, fill_value=0)
            .rename_axis("Risk Level")
            .reset_index(name="Customers")
        )
        fig = px.bar(
            risk_counts,
            x="Risk Level",
            y="Customers",
            color="Risk Level",
            text="Customers",
            title="Customers by Risk Level"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Customer Spending by Risk")
        spend_by_risk = (
            customer_activity.groupby("Churn Risk", observed=False)["total_spend"]
            .sum()
            .reindex(risk_options, fill_value=0)
            .rename_axis("Risk Level")
            .reset_index(name="Total Spend")
        )
        fig2 = px.pie(
            spend_by_risk,
            names="Risk Level",
            values="Total Spend",
            title="Historical Spend Share"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Inactivity distribution
    st.subheader("Days Since Last Purchase")
    fig3 = px.histogram(
        customer_activity,
        x="days_inactive",
        nbins=30,
        title="Customer Inactivity Distribution",
        labels={"days_inactive": "Inactive Days"}
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Filtered table
    filtered = customer_activity[
        customer_activity["Churn Risk"].isin(selected_risks)
        & (customer_activity["days_inactive"] >= min_inactive)
    ].copy()

    st.subheader("Customer Inactivity Details")
    st.caption(f"{len(filtered):,} customers match the selected filters.")

    display_columns = [
        "customer_id",
        "last_purchase",
        "days_inactive",
        "total_orders",
        "total_spend",
        "avg_order_value",
        "Churn Risk"
    ]
    st.dataframe(
        filtered[display_columns].sort_values(
            "days_inactive", ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

    csv_data = filtered[display_columns].to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Filtered Customer Report",
        data=csv_data,
        file_name="retailpulse_churn_risk_report.csv",
        mime="text/csv"
    )

    # Retention action recommendations
    st.subheader("🎯 Recommended Retention Actions")
    r1, r2, r3 = st.columns(3)

    with r1:
        st.markdown("**🔴 High Risk · 90+ days**")
        st.write("Review these customers for a win-back campaign or personalized offer.")

    with r2:
        st.markdown("**🟠 Medium Risk · 60–89 days**")
        st.write("Consider a re-engagement message or relevant product recommendation.")

    with r3:
        st.markdown("**🟢 Active · under 30 days**")
        st.write("Encourage repeat purchases through loyalty rewards and useful recommendations.")

except FileNotFoundError as e:
    st.error(f"Required dataset missing: {e.filename}")
    st.write(
        "Check that cleaned_sales_transactions.zip and "
        "cleaned_customer_master.csv are in the repository root."
    )
except Exception as e:
    st.error("Churn Analysis load karte waqt error aaya.")
    st.exception(e)

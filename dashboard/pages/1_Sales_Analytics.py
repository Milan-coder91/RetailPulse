
import plotly.express as px
from pathlib import Path
import pandas as pd
import streamlit as st


st.title("Sales Analytics")

#BASE_PATH = Path(
  #  r"C:\Users\milan\Downloads\archive (3)\retail_clean_dataset"
#)

BASE_PATH = Path(__file__).resolve().parents[2]
sales_path = BASE_PATH / "cleaned_sales_transactions.zip"
customer_path = BASE_PATH / "cleaned_customer_master.csv"

@st.cache_data
def load_sales(path):
    return pd.read_csv(path, compression="zip")

sales = load_sales(sales_path)

# ---------------- SALES FILTERS ----------------
st.sidebar.header("🔎 Sales Filters")

sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
sales = sales.dropna(subset=["date"])

# Date filter
min_date = sales["date"].min().date()
max_date = sales["date"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered_sales = sales.copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_sales = filtered_sales[
        filtered_sales["date"].dt.date.between(start_date, end_date)
    ]

# Channel filter
if "channel" in filtered_sales.columns:
    channels = sorted(
        filtered_sales["channel"].dropna().astype(str).unique().tolist()
    )
    selected_channels = st.sidebar.multiselect(
        "Sales Channel",
        channels,
        default=channels
    )
    filtered_sales = filtered_sales[
        filtered_sales["channel"].astype(str).isin(selected_channels)
    ]

# Store filter
if "store_id" in filtered_sales.columns:
    stores = sorted(
        filtered_sales["store_id"].dropna().astype(str).unique().tolist()
    )
    selected_stores = st.sidebar.multiselect(
        "Store",
        stores,
        default=stores
    )
    filtered_sales = filtered_sales[
        filtered_sales["store_id"].astype(str).isin(selected_stores)
    ]

# ---------------- FILTERED SALES KPIs ----------------
st.subheader("📊 Filtered Sales Overview")

c1, c2, c3 = st.columns(3)

c1.metric("Transactions", f"{len(filtered_sales):,}")
c2.metric(
    "Units Sold",
    f"{filtered_sales['quantity'].sum():,.0f}"
)
c3.metric(
    "Total Sales",
    f"₹{filtered_sales['total_value'].sum():,.2f}"
)

# ---------------- PIE & DONUT CHARTS ----------------
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("🥧 Sales by Channel")

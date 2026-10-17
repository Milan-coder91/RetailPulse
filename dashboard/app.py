import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="RetailPulse Dashboard", page_icon="📊", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebarNav"] {display:none;}
[data-testid="stSidebar"] .nav-title {font-size:18px;font-weight:700;margin-bottom:12px;}
[data-testid="stSidebar"] .nav-item {padding:8px 4px;margin-bottom:4px;}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="nav-title">RetailPulse</div>', unsafe_allow_html=True)
st.sidebar.page_link("app.py", label="Dashboard Overview", icon="🏠")
st.sidebar.page_link("pages/1_Sales_Analytics.py", label="Sales Analytics", icon="📊")
st.sidebar.page_link("pages/3_Customer_Segmentation.py", label="Customer Segmentation + Churn Risk", icon="👥")
st.sidebar.page_link("pages/2_Demand_Forecasting.py", label="Demand Forecasting", icon="📈")
st.sidebar.page_link("pages/4_Inventory_Optimization.py", label="Inventory Optimization", icon="📦")
st.sidebar.divider()

# Project root when this file is dashboard/app.py
BASE_PATH = Path(__file__).resolve().parent.parent
sales_path = BASE_PATH / "cleaned_sales_transactions.zip"
inventory_path = BASE_PATH / "cleaned_inventory_snapshot.csv"

if not sales_path.exists():
    st.error(f"Sales dataset missing: {sales_path}")
    st.stop()
if not inventory_path.exists():
    st.error(f"Inventory dataset missing: {inventory_path}")
    st.stop()

@st.cache_data
def load_sales(path):
    return pd.read_csv(path, compression="zip", usecols=["receipt_id", "date", "quantity", "total_value"])

@st.cache_data
def load_inventory(path):
    return pd.read_csv(path, usecols=["sku_id", "store_id", "stock_on_hand", "reorder_point"])

try:
    sales_data = load_sales(sales_path)
    inventory_data = load_inventory(inventory_path)
except Exception as error:
    st.error(f"Unable to load dashboard data: {error}")
    st.stop()

sales_data["date"] = pd.to_datetime(sales_data["date"], errors="coerce")
sales_data["quantity"] = pd.to_numeric(sales_data["quantity"], errors="coerce")
sales_data["total_value"] = pd.to_numeric(sales_data["total_value"], errors="coerce")
sales_data = sales_data.dropna(subset=["date", "quantity", "total_value"]).copy()
for col in ["stock_on_hand", "reorder_point"]:
    inventory_data[col] = pd.to_numeric(inventory_data[col], errors="coerce")
inventory_data = inventory_data.dropna(subset=["stock_on_hand", "reorder_point"]).copy()

if sales_data.empty:
    st.error("Sales dataset contains no valid records.")
    st.stop()

latest_date = sales_data["date"].max()
latest_sales = sales_data[sales_data["date"].dt.normalize() == latest_date.normalize()]
total_sales_latest = latest_sales["total_value"].sum()
total_units_latest = latest_sales["quantity"].sum()
total_orders_latest = latest_sales["receipt_id"].nunique()
low_stock_mask = inventory_data["stock_on_hand"] <= inventory_data["reorder_point"]
low_stock_items = int(low_stock_mask.sum())
daily_sales = sales_data.groupby(sales_data["date"].dt.normalize())["total_value"].sum().sort_index()
average_daily_sales = daily_sales.mean()
if pd.isna(average_daily_sales) or average_daily_sales == 0:
    st.error("Average daily sales could not be calculated.")
    st.stop()

# Header
st.title("🚀 RetailPulse AI Analytics Platform")
st.header("📌 Overview")
st.markdown("""**RetailPulse** is an AI-powered retail analytics platform designed to help businesses understand customers, forecast demand, manage inventory, and make data-driven decisions.""")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 📈 Demand Forecasting")
    st.write("30-day demand forecasting and scenario analysis. Check the Demand Forecasting page for the current model details.")
    st.markdown("### 👥 Customer Analytics")
    st.write("RFM analysis and customer segmentation using machine learning.")
    st.markdown("### ⚠️ Churn Prediction")
    st.write("Identify customers who may be at risk of churn.")
with col2:
    st.markdown("### 📦 Inventory Optimization")
    st.write("Reorder recommendations and stock monitoring.")
    st.markdown("### 📊 Business Intelligence")
    st.write("Interactive analytics, KPIs, alerts and downloadable reports.")

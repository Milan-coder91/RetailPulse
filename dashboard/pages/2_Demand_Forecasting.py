import streamlit as st

# Demand Forecasting Page

st.title("Demand Forecasting")
st.write("View future demand predictions for RetailPulse.")

st.subheader("Forecast Overview")

col1, col2 = st.columns(2)

col1.metric("Forecast Period", "30 Days")
col2.metric("Forecast Status", "Ready for Integration")

st.info("LSTM, Prophet, and Hybrid forecast data will be connected here.")


# Day 16 - Step 1: Load Sales Data

import pandas as pd
from pathlib import Path

#BASE_PATH = Path(
#    r"C:\Users\milan\Downloads\archive (3)\retail_clean_dataset")

BASE_PATH = Path(__file__).resolve().parent.parent.parent


sales_path = BASE_PATH / "cleaned_sales_transactions.zip"

@st.cache_data
def load_sales_data(path):
    return pd.read_csv(path, compression="zip")

sales = load_sales_data(sales_path)

sales["date"] = pd.to_datetime(sales["date"])

st.subheader("Forecasting Data Overview")

st.success("Sales transaction data loaded successfully.")

st.metric(
    "Total Sales Records",
    f"{len(sales):,}"
)

st.dataframe(
    sales.head(30),
    width="stretch"
)

## Day 16 - Step 2: Daily Demand Overview

st.subheader("Daily Demand Overview")

daily_demand = (
    sales
    .groupby("date")["quantity"]
    .sum()
    .reset_index()
    .sort_values("date")
)

daily_demand.columns = ["date", "demand"]

st.metric(
    "Total Days Available",
    f"{len(daily_demand):,}"
)

st.dataframe(
    daily_demand.head(30),
    width="stretch"
)

# Day 16 - Step 3: Historical Demand Visualization

st.subheader("Historical Demand Analysis")

st.line_chart(
    daily_demand.set_index("date")["demand"],
    x_label="Date",
    y_label="Units Sold"
)

# Day 16 - Step 4: 30-Day Forecast Overview

st.subheader("30-Day Forecast Overview")

forecast_days = 30

average_demand = daily_demand["demand"].tail(30).mean()

last_date = daily_demand["date"].max()

future_dates = pd.date_range(
    start=last_date + pd.Timedelta(days=1),
    periods=forecast_days,
    freq="D"
)

forecast = pd.DataFrame({
    "date": future_dates,
    "forecast_demand": round(average_demand)
})

st.metric(
    "Average Daily Forecast",
    f"{average_demand:,.0f}"
)

st.dataframe(
    forecast,
    width="stretch"
)

# Day 16 - Step 5: 30-Day Forecast Visualization

st.subheader("Forecast Trend Analysis")

st.line_chart(
    forecast.set_index("date")["forecast_demand"],
    x_label="Date",
    y_label="Forecasted Demand"
)

# Day 16 - Step 6: Demand Scenario Analysis

st.subheader("Demand Scenario Analysis")

demand_change = st.slider(
    "Expected Demand Adjustment (%)",
    min_value=-30,
    max_value=30,
    value=0,
    step=5
)

what_if_forecast = forecast.copy()

what_if_forecast["adjusted_demand"] = (
    what_if_forecast["forecast_demand"]
    * (1 + demand_change / 100)
).round()

st.metric(
    "Demand Adjustment",
    f"{demand_change:+d}%"
)

st.line_chart(
    what_if_forecast.set_index("date")["adjusted_demand"],
    x_label="Date",
    y_label="Adjusted Demand"
)

st.dataframe(
    what_if_forecast,
    width="stretch"
)

# Day 16 - Step 7: Forecast Comparison

st.subheader("Forecast Scenario Comparison")

comparison = what_if_forecast[
    ["date", "forecast_demand", "adjusted_demand"]
].copy()

comparison = comparison.set_index("date")

st.line_chart(
    comparison,
    x_label="Date",
    y_label="Demand"
)

st.dataframe(
    comparison,
    width="stretch"
)

# Day 16 - Step 8: Forecast Summary Metrics

st.subheader("Forecast Performance Summary")

forecast_avg = forecast["forecast_demand"].mean()
forecast_min = forecast["forecast_demand"].min()
forecast_max = forecast["forecast_demand"].max()

col1, col2, col3 = st.columns(3)

col1.metric(
    "30-Day Average Demand",
    f"{forecast_avg:,.0f}"
)

col2.metric(
    "Minimum Forecast",
    f"{forecast_min:,.0f}"
)

col3.metric(
    "Maximum Forecast",
    f"{forecast_max:,.0f}"
)

# Day 16 - Step 9: Demand Forecast

st.subheader("Demand Forecast")

recent_demand = daily_demand["demand"].tail(30).reset_index(drop=True)

forecast = pd.DataFrame({
    "date": future_dates,
    "forecast_demand": recent_demand.values
})

st.line_chart(
    forecast.set_index("date")["forecast_demand"],
    x_label="Date",
    y_label="Forecasted Demand"
)

st.dataframe(
    forecast,
    width="stretch"
)

# Day 16 - Step 10: Forecast Insights

st.subheader("Forecast Insights")

total_forecast_demand = forecast["forecast_demand"].sum()
average_forecast_demand = forecast["forecast_demand"].mean()

st.write(
    f"Expected demand over the next 30 days: "
    f"**{total_forecast_demand:,.0f} units**."
)

st.write(
    f"Average expected daily demand: "
    f"**{average_forecast_demand:,.0f} units**."
)

st.info(
    "These baseline forecast values can be used to support "
    "inventory planning and demand-based decision making."
)

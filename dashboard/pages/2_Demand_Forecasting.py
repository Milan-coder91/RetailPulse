
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="Demand Forecasting",
    page_icon="📈",
    layout="wide"
)

st.title("Demand Forecasting")
st.write(
    "View historical demand, baseline forecasts, and demand scenarios."
)

BASE_PATH = Path(__file__).resolve().parents[2]
sales_path = BASE_PATH / "cleaned_sales_transactions.zip"


# --------------------------------------------------
# LOAD SALES DATA
# --------------------------------------------------
@st.cache_data
def load_sales_data(path):
    if not path.exists():
        raise FileNotFoundError(f"Sales dataset not found: {path}")

    return pd.read_csv(path, compression="zip")


try:
    sales = load_sales_data(sales_path)

    required_columns = ["date", "quantity"]
    missing_columns = [
        column for column in required_columns
        if column not in sales.columns
    ]

    if missing_columns:
        st.error(f"Missing required columns: {missing_columns}")
        st.stop()

    sales["date"] = pd.to_datetime(
        sales["date"], errors="coerce"
    )
    sales["quantity"] = pd.to_numeric(
        sales["quantity"], errors="coerce"
    )

    sales = sales.dropna(
        subset=["date", "quantity"]
    ).copy()

    for column in ["store_id", "sku_id"]:
        if column in sales.columns:
            sales[column] = (
                sales[column]
                .astype("string")
                .fillna("Unknown")
            )

except Exception as error:
    st.error(f"Unable to load sales data: {error}")
    st.stop()


if sales.empty:
    st.error("No valid sales data is available for forecasting.")
    st.stop()


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("Demand Forecast Filters")
st.sidebar.caption("Choose filters to update the analysis.")

min_date = sales["date"].min().date()
max_date = sales["date"].max().date()

# Date filter
date_range = st.sidebar.date_input(
    "Historical Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key="forecast_date_range"
)

# Store filter
if "store_id" in sales.columns:
    stores = sorted(sales["store_id"].unique().tolist())

    selected_stores = st.sidebar.multiselect(
        "Select Stores",
        options=stores,
        default=stores,
        key="forecast_stores"
    )
else:
    stores = []
    selected_stores = None
    st.sidebar.caption("Store filter unavailable in this dataset.")

# SKU filter
if "sku_id" in sales.columns:
    skus = sorted(sales["sku_id"].unique().tolist())

    selected_skus = st.sidebar.multiselect(
        "Select SKUs",
        options=skus,
        default=skus,
        key="forecast_skus"
    )
else:
    skus = []
    selected_skus = None
    st.sidebar.caption("SKU filter unavailable in this dataset.")

# Reset filters
if st.sidebar.button("Reset Filters", use_container_width=True):
    st.session_state["forecast_date_range"] = (
        min_date,
        max_date
    )

    if "store_id" in sales.columns:
        st.session_state["forecast_stores"] = stores

    if "sku_id" in sales.columns:
        st.session_state["forecast_skus"] = skus

    st.rerun()


# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------
if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
    st.info("Please select both a start date and an end date.")
    st.stop()

start_date, end_date = date_range

if start_date > end_date:
    st.error("Start date must be before end date.")
    st.stop()

filtered_sales = sales[
    sales["date"].dt.date.between(start_date, end_date)
].copy()

if selected_stores is not None:
    filtered_sales = filtered_sales[
        filtered_sales["store_id"].isin(selected_stores)
    ]

if selected_skus is not None:
    filtered_sales = filtered_sales[
        filtered_sales["sku_id"].isin(selected_skus)
    ]

if filtered_sales.empty:
    st.warning(
        "No sales data matches the selected filters. "
        "Please change the date, store, or SKU selection."
    )
    st.stop()

st.sidebar.success(
    f"{len(filtered_sales):,} sales records selected"
)


# --------------------------------------------------
# DAILY DEMAND OVERVIEW
# --------------------------------------------------
st.subheader("Daily Demand Overview")

daily_demand = (
    filtered_sales.groupby("date", as_index=False)["quantity"]
    .sum()
    .sort_values("date")
    .reset_index(drop=True)
)

daily_demand.columns = ["date", "demand"]

col1, col2, col3 = st.columns(3)

col1.metric(
    "Filtered Sales Records",
    f"{len(filtered_sales):,}"
)
col2.metric(
    "Daily Observations",
    f"{len(daily_demand):,}"
)
col3.metric(
    "Total Units Sold",
    f"{daily_demand['demand'].sum():,.0f}"
)

with st.expander("View Filtered Sales Data"):
    st.dataframe(
        filtered_sales.head(100),
        use_container_width=True
    )

with st.expander("View Daily Demand Data"):
    st.dataframe(
        daily_demand,
        use_container_width=True
    )


# --------------------------------------------------
# HISTORICAL DEMAND ANALYSIS
# --------------------------------------------------
st.subheader("Historical Demand Analysis")

fig_history = px.line(
    daily_demand,
    x="date",
    y="demand",
    title="Historical Daily Demand",
    labels={
        "date": "Date",
        "demand": "Units Sold"
    }
)

fig_history.update_layout(
    hovermode="x unified"
)

st.plotly_chart(
    fig_history,
    use_container_width=True
)


# --------------------------------------------------
# 30-DAY BASELINE FORECAST
# --------------------------------------------------
st.subheader("30-Day Demand Forecast")

forecast_days = 30

# Use up to 30 available daily observations
recent_demand = (
    daily_demand["demand"]
    .tail(30)
    .reset_index(drop=True)
)

last_date = daily_demand["date"].max()

future_dates = pd.date_range(
    start=last_date + pd.Timedelta(days=1),
    periods=forecast_days,
    freq="D"
)

# Pattern-based baseline; not a trained ML model
forecast_values = []

for day in range(forecast_days):
    base_demand = recent_demand.iloc[
        day % len(recent_demand)
    ]

    trend_factor = 1 + (0.002 * day)

    forecast_values.append(
        max(0, round(base_demand * trend_factor))
    )

forecast = pd.DataFrame({
    "date": future_dates,
    "forecast_demand": forecast_values
})

forecast_avg = forecast["forecast_demand"].mean()
forecast_min = forecast["forecast_demand"].min()
forecast_max = forecast["forecast_demand"].max()
total_forecast_demand = forecast["forecast_demand"].sum()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Average Daily Forecast",
    f"{forecast_avg:,.0f} units"
)
col2.metric(
    "Minimum Daily Forecast",
    f"{forecast_min:,.0f} units"
)
col3.metric(
    "Maximum Daily Forecast",
    f"{forecast_max:,.0f} units"
)

fig_forecast = px.line(
    forecast,
    x="date",
    y="forecast_demand",
    title="Baseline Forecast — Next 30 Days",
    labels={
        "date": "Date",
        "forecast_demand": "Forecast Units"
    }
)

st.plotly_chart(
    fig_forecast,
    use_container_width=True
)

with st.expander("View Baseline Forecast Data"):
    st.dataframe(
        forecast,
        use_container_width=True
    )


# --------------------------------------------------
# DEMAND SCENARIO ANALYSIS
# --------------------------------------------------
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
).round().clip(lower=0)

adjusted_total = what_if_forecast["adjusted_demand"].sum()

col1, col2 = st.columns(2)

col1.metric(
    "Demand Adjustment",
    f"{demand_change:+d}%"
)

col2.metric(
    "Adjusted 30-Day Demand",
    f"{adjusted_total:,.0f} units",
    delta=(
        f"{adjusted_total - total_forecast_demand:+,.0f} units"
    )
)

fig_scenario = px.line(
    what_if_forecast,
    x="date",
    y=["forecast_demand", "adjusted_demand"],
    title="Baseline vs Adjusted Demand",
    labels={
        "date": "Date",
        "value": "Demand (Units)",
        "variable": "Scenario"
    }
)

st.plotly_chart(
    fig_scenario,
    use_container_width=True
)

with st.expander("View Scenario Data"):
    st.dataframe(
        what_if_forecast,
        use_container_width=True
    )


# --------------------------------------------------
# FORECAST SUMMARY
# --------------------------------------------------
st.subheader("Forecast Summary")

col1, col2, col3 = st.columns(3)

col1.metric(
    "30-Day Average",
    f"{forecast_avg:,.0f} units"
)
col2.metric(
    "30-Day Minimum",
    f"{forecast_min:,.0f} units"
)
col3.metric(
    "30-Day Maximum",
    f"{forecast_max:,.0f} units"
)

st.write(
    f"Baseline 30-day demand: "
    f"**{total_forecast_demand:,.0f} units**."
)

st.write(
    f"Adjusted scenario demand: "
    f"**{adjusted_total:,.0f} units**."
)

st.info(
    "This is a pattern-based baseline using recent daily demand "
    "and a small trend adjustment. It is not a trained LSTM, "
    "Prophet, or Hybrid model prediction."
)


# --------------------------------------------------
# RETAILPULSE FORECAST ASSISTANT
# --------------------------------------------------
st.divider()

st.header("RetailPulse Forecast Assistant")

st.caption(
    "Rule-based assistant using the filtered data and "
    "forecast calculations available on this page."
)


def answer_question(question):
    q = question.lower().strip()

    if any(word in q for word in [
        "hello", "hi", "hey", "greetings"
    ]):
        return (
            "Hello! I am the RetailPulse Forecast Assistant. "
            "Ask me about historical demand, forecasts, "
            "or demand scenarios."
        )

    if any(word in q for word in [
        "accuracy", "mape", "rmse", "mae", "performance"
    ]):
        return (
            "MAE, RMSE, and MAPE are not calculated on this page. "
            "Accuracy requires comparing predictions with actual "
            "observed demand."
        )

    if any(word in q for word in [
        "lstm", "prophet", "hybrid", "trained model"
    ]):
        return (
            "Trained LSTM, Prophet, and Hybrid predictions are not "
            "connected to this page. The current forecast is a "
            "pattern-based baseline."
        )

    if any(word in q for word in [
        "maximum", "max", "highest", "peak"
    ]):
        row = forecast.loc[
            forecast["forecast_demand"].idxmax()
        ]

        return (
            f"Maximum daily forecast: "
            f"{row['forecast_demand']:,.0f} units "
            f"on {row['date'].date()}."
        )

    if any(word in q for word in [
        "minimum", "min", "lowest"
    ]):
        row = forecast.loc[
            forecast["forecast_demand"].idxmin()
        ]

        return (
            f"Minimum daily forecast: "
            f"{row['forecast_demand']:,.0f} units "
            f"on {row['date'].date()}."
        )

    if any(word in q for word in ["average", "mean"]):
        return (
            f"Average daily forecast: "
            f"{forecast_avg:,.0f} units."
        )

    if any(word in q for word in [
        "total", "sum", "30-day", "30 day", "next month"
    ]):
        return (
            f"Baseline 30-day forecast: "
            f"{total_forecast_demand:,.0f} units."
        )

    if any(word in q for word in [
        "adjust", "scenario", "what if", "what-if",
        "increase", "decrease"
    ]):
        return (
            f"Selected adjustment: {demand_change:+d}%. "
            f"Adjusted 30-day demand: {adjusted_total:,.0f} units."
        )

    if any(word in q for word in [
        "historical", "past demand", "history"
    ]):
        return (
            f"Filtered historical demand covers "
            f"{daily_demand['date'].min().date()} to "
            f"{daily_demand['date'].max().date()}, with "
            f"{len(daily_demand):,} daily observations."
        )

    if any(word in q for word in [
        "record", "transaction", "sales data"
    ]):
        return (
            f"There are {len(filtered_sales):,} valid sales "
            "records after filtering."
        )

    if any(word in q for word in [
        "inventory", "stock", "reorder"
    ]):
        return (
            "This page forecasts demand. Inventory and reorder "
            "recommendations are handled on the Inventory "
            "Optimization page."
        )

    return (
        "Try asking: 'What is the maximum forecast?', "
        "'What is the average demand?', or "
        "'What is the adjusted scenario total?'"
    )


if "forecast_chat_history" not in st.session_state:
    st.session_state.forecast_chat_history = []

for message in st.session_state.forecast_chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_question = st.chat_input(
    "Ask a question about demand forecasting..."
)

if user_question:
    st.session_state.forecast_chat_history.append({
        "role": "user",
        "content": user_question
    })

    with st.chat_message("user"):
        st.markdown(user_question)

    response = answer_question(user_question)

    st.session_state.forecast_chat_history.append({
        "role": "assistant",
        "content": response
    })

    with st.chat_message("assistant"):
        st.markdown(response)

if st.button("Clear Chat History"):
    st.session_state.forecast_chat_history = []
    st.rerun()

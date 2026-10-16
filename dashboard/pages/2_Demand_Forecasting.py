
from pathlib import Path
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Demand Forecasting", layout="wide")

st.title("Demand Forecasting")
st.write("View historical demand, baseline forecasts, and demand scenarios.")

BASE_PATH = Path(__file__).resolve().parents[2]
sales_path = BASE_PATH / "cleaned_sales_transactions.zip"


@st.cache_data
def load_sales_data(path):
    if not path.exists():
        raise FileNotFoundError(f"Sales dataset not found: {path}")
    return pd.read_csv(path, compression="zip")


try:
    sales = load_sales_data(sales_path)
    sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
    sales["quantity"] = pd.to_numeric(sales["quantity"], errors="coerce")
    sales = sales.dropna(subset=["date", "quantity"])
except Exception as e:
    st.error(f"Unable to load sales data: {e}")
    st.stop()

if sales.empty:
    st.error("No valid sales data is available for forecasting.")
    st.stop()


# Step 1: Daily Demand
st.subheader("Daily Demand Overview")

daily_demand = (
    sales.groupby("date", as_index=False)["quantity"]
    .sum()
    .sort_values("date")
    .reset_index(drop=True)
)
daily_demand.columns = ["date", "demand"]

col1, col2 = st.columns(2)
col1.metric("Total Sales Records", f"{len(sales):,}")
col2.metric("Available Daily Observations", f"{len(daily_demand):,}")

with st.expander("View Sales Data"):
    st.dataframe(sales.head(30), use_container_width=True)

with st.expander("View Daily Demand Data"):
    st.dataframe(daily_demand.head(30), use_container_width=True)


# Step 2: Historical Demand
st.subheader("Historical Demand Analysis")

st.line_chart(
    daily_demand.set_index("date")["demand"],
    x_label="Date",
    y_label="Units Sold"
)


# Step 3: 30-Day Baseline Forecast
st.subheader("30-Day Demand Forecast")

forecast_days = 30
recent_demand = daily_demand["demand"].tail(30).reset_index(drop=True)

last_date = daily_demand["date"].max()

future_dates = pd.date_range(
    start=last_date + pd.Timedelta(days=1),
    periods=forecast_days,
    freq="D"
)

# Use recent day-wise demand patterns with a small trend adjustment.
# This is a pattern-based baseline, not a trained ML model.
forecast_values = []

for day in range(forecast_days):
    base_demand = recent_demand.iloc[day % len(recent_demand)]
    trend_factor = 1 + (0.002 * day)
    forecast_values.append(max(0, round(base_demand * trend_factor)))

forecast = pd.DataFrame({
    "date": future_dates,
    "forecast_demand": forecast_values
})

forecast_avg = forecast["forecast_demand"].mean()
forecast_min = forecast["forecast_demand"].min()
forecast_max = forecast["forecast_demand"].max()
total_forecast_demand = forecast["forecast_demand"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Average Daily Forecast", f"{forecast_avg:,.0f} units")
col2.metric("Minimum Daily Forecast", f"{forecast_min:,.0f} units")
col3.metric("Maximum Daily Forecast", f"{forecast_max:,.0f} units")

st.line_chart(
    forecast.set_index("date")["forecast_demand"],
    x_label="Date",
    y_label="Forecasted Units"
)

st.dataframe(forecast, use_container_width=True)


# Step 4: Demand Scenario Analysis
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
    what_if_forecast["forecast_demand"] *
    (1 + demand_change / 100)
).round().clip(lower=0)

adjusted_total = what_if_forecast["adjusted_demand"].sum()

st.metric("Demand Adjustment", f"{demand_change:+d}%")

st.line_chart(
    what_if_forecast.set_index("date")[
        ["forecast_demand", "adjusted_demand"]
    ],
    x_label="Date",
    y_label="Demand (Units)"
)

st.dataframe(what_if_forecast, use_container_width=True)


# Step 5: Forecast Summary
st.subheader("Forecast Summary")

col1, col2, col3 = st.columns(3)
col1.metric("30-Day Average", f"{forecast_avg:,.0f} units")
col2.metric("30-Day Minimum", f"{forecast_min:,.0f} units")
col3.metric("30-Day Maximum", f"{forecast_max:,.0f} units")

st.write(f"Baseline 30-day demand: **{total_forecast_demand:,.0f} units**.")
st.write(f"Adjusted scenario demand: **{adjusted_total:,.0f} units**.")

st.info(
    "This is a pattern-based baseline using recent daily demand and a small trend adjustment. "
    "It is not a trained LSTM, Prophet, or Hybrid model prediction."
)


# Step 6: RetailPulse Forecast Assistant
st.divider()
st.header("RetailPulse Forecast Assistant")
st.caption(
    "Rule-based assistant that answers questions using the data and calculations "
    "available on this page. It is not an external AI/LLM chatbot."
)


def answer_question(question):
    q = question.lower().strip()

    if any(word in q for word in ["hello", "hi", "hey", "greetings"]):
        return (
            "Hello! I am the RetailPulse Forecast Assistant. "
            "You can ask me about historical demand, forecast values, or demand scenarios."
        )

    if any(word in q for word in ["accuracy", "mape", "rmse", "mae", "performance"]):
        return (
            "Forecast accuracy metrics such as MAE, RMSE, and MAPE are not calculated "
            "or displayed on this page. Actual model performance cannot be confirmed "
            "without comparing predictions against observed demand."
        )

    if any(word in q for word in ["lstm", "prophet", "hybrid", "machine learning", "trained model"]):
        return (
            "Trained LSTM, Prophet, and Hybrid model predictions are not connected to "
            "this page yet. The current forecast is a pattern-based baseline, not a "
            "trained machine-learning prediction."
        )

    if any(word in q for word in ["maximum", "max", "highest", "peak"]):
        max_row = forecast.loc[forecast["forecast_demand"].idxmax()]
        return (
            f"The maximum daily forecast is {max_row['forecast_demand']:,.0f} units, "
            f"expected on {max_row['date'].date()}."
        )

    if any(word in q for word in ["minimum", "min", "lowest"]):
        min_row = forecast.loc[forecast["forecast_demand"].idxmin()]
        return (
            f"The minimum daily forecast is {min_row['forecast_demand']:,.0f} units, "
            f"expected on {min_row['date'].date()}."
        )

    if any(word in q for word in ["average", "mean"]):
        return (
            f"The average forecast demand is {forecast_avg:,.0f} units per day "
            f"over the next {forecast_days} days."
        )

    if any(word in q for word in ["total", "sum", "30-day", "30 day", "next month"]):
        return (
            f"The total baseline demand forecast for the next {forecast_days} days "
            f"is {total_forecast_demand:,.0f} units."
        )

    if any(word in q for word in ["adjust", "scenario", "what if", "what-if", "increase", "decrease"]):
        return (
            f"The selected demand adjustment is {demand_change:+d}%. "
            f"The adjusted total for the next {forecast_days} days is "
            f"{adjusted_total:,.0f} units."
        )

    if any(word in q for word in ["historical", "past demand", "history"]):
        return (
            f"Historical daily demand is available from "
            f"{daily_demand['date'].min().date()} to "
            f"{daily_demand['date'].max().date()}, covering "
            f"{len(daily_demand):,} daily observations."
        )

    if any(word in q for word in ["record", "transaction", "sales data"]):
        return (
            f"The loaded dataset contains {len(sales):,} valid records "
            "with usable dates and numeric quantities."
        )

    if any(word in q for word in ["inventory", "stock", "reorder"]):
        return (
            "An exact reorder recommendation requires current inventory levels, "
            "supplier lead times, and target safety stock. Those details are not "
            "calculated by this demand forecasting page."
        )

    return (
        "I can answer questions about average demand, minimum forecast, maximum forecast, "
        "total 30-day demand, historical demand, demand adjustments, and model accuracy. "
        "Try asking: 'What is the maximum forecast?'"
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

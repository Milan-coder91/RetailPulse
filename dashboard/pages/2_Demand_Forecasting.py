
from pathlib import Path
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Demand Forecasting", layout="wide")

st.title("Demand Forecasting")
st.write("View future demand predictions for RetailPulse.")

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
    st.error(f"Sales dataset load nahi hua: {e}")
    st.stop()


# Forecast Overview
st.subheader("Forecast Overview")
col1, col2 = st.columns(2)
col1.metric("Forecast Period", "30 Days")
col2.metric("Forecast Status", "Baseline Forecast Ready")

st.success("Sales transaction data loaded successfully.")
st.metric("Total Sales Records", f"{len(sales):,}")

with st.expander("View Sales Data"):
    st.dataframe(sales.head(30), use_container_width=True)


# Step 1: Daily Demand
st.subheader("Daily Demand Overview")

daily_demand = (
    sales.groupby("date", as_index=False)["quantity"]
    .sum()
    .sort_values("date")
)
daily_demand.columns = ["date", "demand"]

st.metric("Total Days Available", f"{len(daily_demand):,}")

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
st.subheader("30-Day Forecast Overview")

forecast_days = 30
recent_demand = daily_demand["demand"].tail(30)

if recent_demand.empty:
    st.warning("Forecast banane ke liye demand data available nahi hai.")
    st.stop()

average_demand = recent_demand.mean()
last_date = daily_demand["date"].max()

future_dates = pd.date_range(
    start=last_date + pd.Timedelta(days=1),
    periods=forecast_days,
    freq="D"
)

# Baseline: recent 30-day average
forecast = pd.DataFrame({
    "date": future_dates,
    "forecast_demand": [round(average_demand)] * forecast_days
})

st.metric("Average Daily Forecast", f"{average_demand:,.0f}")
st.line_chart(
    forecast.set_index("date")["forecast_demand"],
    x_label="Date",
    y_label="Forecasted Demand"
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
).round()

st.metric("Demand Adjustment", f"{demand_change:+d}%")

st.line_chart(
    what_if_forecast.set_index("date")[
        ["forecast_demand", "adjusted_demand"]
    ],
    x_label="Date",
    y_label="Demand"
)

st.dataframe(what_if_forecast, use_container_width=True)


# Step 5: Forecast Summary
st.subheader("Forecast Performance Summary")

forecast_avg = forecast["forecast_demand"].mean()
forecast_min = forecast["forecast_demand"].min()
forecast_max = forecast["forecast_demand"].max()

col1, col2, col3 = st.columns(3)
col1.metric("30-Day Average Demand", f"{forecast_avg:,.0f}")
col2.metric("Minimum Forecast", f"{forecast_min:,.0f}")
col3.metric("Maximum Forecast", f"{forecast_max:,.0f}")

total_forecast_demand = forecast["forecast_demand"].sum()
adjusted_total = what_if_forecast["adjusted_demand"].sum()

st.write(
    f"Expected demand over the next 30 days: "
    f"**{total_forecast_demand:,.0f} units**."
)
st.write(
    f"Average expected daily demand: **{forecast_avg:,.0f} units**."
)
st.info(
    "This is a baseline forecast using the recent 30-day average, "
    "not a trained LSTM, Prophet, or Hybrid model prediction."
)


# Step 6: RetailPulse Forecast Chatbot
st.divider()
st.header("RetailPulse Forecast Assistant")
st.write(
    "Sales, demand forecast aur scenario analysis ke baare mein "
    "apne questions poochho."
)

def answer_question(question):
    q = question.lower()

    if any(word in q for word in ["hello", "hi", "hey", "namaste"]):
        return (
            "Namaste bhai! Main RetailPulse Forecast Assistant hoon. "
            "Sales aur demand forecast ke baare mein poochho."
        )

    if "lstm" in q or "prophet" in q or "hybrid" in q:
        return (
            "Is page par abhi LSTM, Prophet aur Hybrid models connected "
            "nahi hain. Current displayed forecast recent 30-day average "
            "par based baseline forecast hai."
        )

    if "record" in q or "transaction" in q or "sales data" in q:
        return f"Loaded sales dataset mein {len(sales):,} valid dated quantity records hain."

    if "historical" in q or "past demand" in q:
        return (
            f"Historical daily demand {daily_demand['date'].min().date()} "
            f"se {daily_demand['date'].max().date()} tak available hai. "
            f"Total daily observations: {len(daily_demand):,}."
        )

    if "adjust" in q or "scenario" in q or "what if" in q:
        return (
            f"Current scenario adjustment {demand_change:+d}% hai. "
            f"Adjusted 30-day demand approximately {adjusted_total:,.0f} units hai."
        )

    if "minimum" in q or "lowest" in q:
        return f"Minimum daily demand forecast: {forecast_min:,.0f} units."

    if "maximum" in q or "highest" in q:
        return f"Maximum daily demand forecast: {forecast_max:,.0f} units."

    if "average" in q or "daily demand" in q:
        return f"Average forecast demand: {forecast_avg:,.0f} units per day."

    if "total" in q or "30 day" in q or "30-day" in q or "next month" in q:
        return (
            f"Next 30 days ka baseline forecast {total_forecast_demand:,.0f} units hai. "
            f"Current adjusted scenario {adjusted_total:,.0f} units hai."
        )

    if "inventory" in q or "stock" in q or "reorder" in q:
        return (
            "Inventory recommendation ke liye current stock aur supplier lead-time "
            "data bhi chahiye. Sirf demand forecast se exact reorder quantity "
            "confirm nahi ki ja sakti."
        )

    return (
        "Main abhi loaded sales data aur baseline forecast par answer de sakta hoon. "
        "Try karo: average demand, total 30-day forecast, historical demand, "
        "minimum forecast, maximum forecast, ya what-if scenario."
    )


if "forecast_chat_history" not in st.session_state:
    st.session_state.forecast_chat_history = []

for message in st.session_state.forecast_chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_question = st.chat_input(
    "Ask about sales, demand, or the 30-day forecast..."
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

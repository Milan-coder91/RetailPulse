
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px

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
    sales = sales.dropna(subset=["date", "quantity"]).copy()

    for col in ["store_id", "sku_id"]:
        if col in sales.columns:
            sales[col] = sales[col].astype("string").fillna("Unknown")

except Exception as e:
    st.error(f"Unable to load sales data: {e}")
    st.stop()

if sales.empty:
    st.error("No valid sales data is available for forecasting.")
    st.stop()


# --------------------------------------------------
# FILTERS
# --------------------------------------------------
st.subheader("Forecast Filters")

with st.container(border=True):
    f1, f2, f3 = st.columns(3)

    min_date = sales["date"].min().date()
    max_date = sales["date"].max().date()

    with f1:
        date_range = st.date_input(
            "Historical Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="forecast_date_range"
        )

    with f2:
        if "store_id" in sales.columns:
            stores = sorted(sales["store_id"].unique().tolist())
            selected_stores = st.multiselect(
                "Select Stores",
                stores,
                default=stores,
                key="forecast_stores"
            )
        else:
            selected_stores = None
            st.caption("Store filter unavailable.")

    with f3:
        if "sku_id" in sales.columns:
            skus = sorted(sales["sku_id"].unique().tolist())
            selected_skus = st.multiselect(
                "Select SKUs",
                skus,
                default=skus,
                key="forecast_skus"
            )
        else:
            selected_skus = None
            st.caption("SKU filter unavailable.")

    st.button(
        "Reset Filters",
        on_click=lambda: st.session_state.update({
            "forecast_date_range": (min_date, max_date),
            "forecast_stores": (
                sorted(sales["store_id"].unique().tolist())
                if "store_id" in sales.columns else []
            ),
            "forecast_skus": (
                sorted(sales["sku_id"].unique().tolist())
                if "sku_id" in sales.columns else []
            ),
        }),
        key="reset_forecast_filters"
    )


# Date range selection validation
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
    st.warning("No sales data matches the selected filters. Please change the filters.")
    st.stop()


# --------------------------------------------------
# DAILY DEMAND
# --------------------------------------------------
st.subheader("Daily Demand Overview")

daily_demand = (
    filtered_sales.groupby("date", as_index=False)["quantity"]
    .sum()
    .sort_values("date")
    .reset_index(drop=True)
)
daily_demand.columns = ["date", "demand"]

c1, c2, c3 = st.columns(3)
c1.metric("Filtered Sales Records", f"{len(filtered_sales):,}")
c2.metric("Daily Observations", f"{len(daily_demand):,}")
c3.metric("Total Units Sold", f"{daily_demand['demand'].sum():,.0f}")

with st.expander("View Filtered Sales Data"):
    st.dataframe(filtered_sales.head(100), use_container_width=True)

with st.expander("View Daily Demand Data"):
    st.dataframe(daily_demand, use_container_width=True)


# --------------------------------------------------
# HISTORICAL DEMAND
# --------------------------------------------------
st.subheader("Historical Demand Analysis")

fig_history = px.line(
    daily_demand,
    x="date",
    y="demand",
    title="Historical Daily Demand",
    labels={"date": "Date", "demand": "Units Sold"}
)
st.plotly_chart(fig_history, use_container_width=True)


# --------------------------------------------------
# BASELINE FORECAST
# --------------------------------------------------
st.subheader("30-Day Demand Forecast")

forecast_days = 30
recent_demand = daily_demand["demand"].tail(30).reset_index(drop=True)
last_date = daily_demand["date"].max()

future_dates = pd.date_range(
    start=last_date + pd.Timedelta(days=1),
    periods=forecast_days,
    freq="D"
)

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

c1, c2, c3 = st.columns(3)
c1.metric("Average Daily Forecast", f"{forecast_avg:,.0f} units")
c2.metric("Minimum Daily Forecast", f"{forecast_min:,.0f} units")
c3.metric("Maximum Daily Forecast", f"{forecast_max:,.0f} units")

fig_forecast = px.line(
    forecast,
    x="date",
    y="forecast_demand",
    title="Baseline Forecast for Next 30 Days",
    labels={"date": "Date", "forecast_demand": "Forecast Units"}
)
st.plotly_chart(fig_forecast, use_container_width=True)

with st.expander("View Baseline Forecast Data"):
    st.dataframe(forecast, use_container_width=True)


# --------------------------------------------------
# DEMAND SCENARIO
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
    what_if_forecast["forecast_demand"] *
    (1 + demand_change / 100)
).round().clip(lower=0)

adjusted_total = what_if_forecast["adjusted_demand"].sum()

c1, c2 = st.columns(2)
c1.metric("Demand Adjustment", f"{demand_change:+d}%")
c2.metric(
    "Adjusted 30-Day Demand",
    f"{adjusted_total:,.0f} units",
    delta=f"{adjusted_total - total_forecast_demand:+,.0f} units"
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
st.plotly_chart(fig_scenario, use_container_width=True)

with st.expander("View Scenario Data"):
    st.dataframe(what_if_forecast, use_container_width=True)


# --------------------------------------------------
# FORECAST SUMMARY
# --------------------------------------------------
st.subheader("Forecast Summary")

c1, c2, c3 = st.columns(3)
c1.metric("30-Day Average", f"{forecast_avg:,.0f} units")
c2.metric("30-Day Minimum", f"{forecast_min:,.0f} units")
c3.metric("30-Day Maximum", f"{forecast_max:,.0f} units")

st.write(f"Baseline 30-day demand: **{total_forecast_demand:,.0f} units**.")
st.write(f"Adjusted scenario demand: **{adjusted_total:,.0f} units**.")

st.info(
    "This is a pattern-based baseline using recent daily demand and a small "
    "trend adjustment. It is not a trained LSTM, Prophet, or Hybrid model prediction."
)


# --------------------------------------------------
# FORECAST ASSISTANT
# --------------------------------------------------
st.divider()
st.header("RetailPulse Forecast Assistant")
st.caption(
    "Rule-based assistant using the filtered data and forecast calculations."
)


def answer_question(question):
    q = question.lower().strip()

    if any(w in q for w in ["hello", "hi", "hey", "greetings"]):
        return (
            "Hello! I am the RetailPulse Forecast Assistant. "
            "Ask me about historical demand, forecasts, or demand scenarios."
        )

    if any(w in q for w in ["accuracy", "mape", "rmse", "mae", "performance"]):
        return (
            "MAE, RMSE, and MAPE are not calculated on this page. "
            "Accuracy requires comparing predictions with actual observed demand."
        )

    if any(w in q for w in ["lstm", "prophet", "hybrid", "trained model"]):
        return (
            "Trained LSTM, Prophet, and Hybrid predictions are not connected to this page. "
            "The current forecast is a pattern-based baseline."
        )

    if any(w in q for w in ["maximum", "max", "highest", "peak"]):
        row = forecast.loc[forecast["forecast_demand"].idxmax()]
        return (
            f"Maximum daily forecast: {row['forecast_demand']:,.0f} units "
            f"on {row['date'].date()}."
        )

    if any(w in q for w in ["minimum", "min", "lowest"]):
        row = forecast.loc[forecast["forecast_demand"].idxmin()]
        return (
            f"Minimum daily forecast: {row['forecast_demand']:,.0f} units "
            f"on {row['date'].date()}."
        )

    if any(w in q for w in ["average", "mean"]):
        return f"Average daily forecast: {forecast_avg:,.0f} units."

    if any(w in q for w in ["total", "sum", "30-day", "30 day", "next month"]):
        return f"Baseline 30-day forecast: {total_forecast_demand:,.0f} units."

    if any(w in q for w in ["adjust", "scenario", "what if", "what-if", "increase", "decrease"]):
        return (
            f"Selected adjustment: {demand_change:+d}%. "
            f"Adjusted 30-day demand: {adjusted_total:,.0f} units."
        )

    if any(w in q for w in ["historical", "past demand", "history"]):
        return (
            f"Filtered historical demand covers {daily_demand['date'].min().date()} "
            f"to {daily_demand['date'].max().date()}, with "
            f"{len(daily_demand):,} daily observations."
        )

    if any(w in q for w in ["record", "transaction", "sales data"]):
        return f"There are {len(filtered_sales):,} valid sales records after filtering."

    if any(w in q for w in ["inventory", "stock", "reorder"]):
        return (
            "This page forecasts demand. Inventory and reorder recommendations "
            "are handled on the Inventory Optimization page."
        )

    return (
        "Try asking: 'What is the maximum forecast?', 'What is the average demand?', "
        "or 'What is the adjusted scenario total?'"
    )


if "forecast_chat_history" not in st.session_state:
    st.session_state.forecast_chat_history = []

for message in st.session_state.forecast_chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_question = st.chat_input("Ask a question about demand forecasting...")

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

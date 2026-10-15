# ==============================
# Stage 1: Build Dependencies
# ==============================
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ==============================
# Stage 2: Production Application
# ==============================
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY dashboard ./dashboard

COPY cleaned_sales_transactions.csv .
COPY cleaned_customer_master.csv .
COPY cleaned_inventory_snapshot.csv .
COPY cleaned_sku_master.csv .
COPY cleaned_store_master.csv .
COPY cleaned_promotions.csv .
COPY cleaned_sku_inventory_flags.csv .

# Create a non-root application user
RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8501


CMD ["streamlit", "run", "dashboard/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
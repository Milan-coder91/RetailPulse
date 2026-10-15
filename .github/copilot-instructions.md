# RetailPulse Project Instructions

## Build and validation

- Use Python 3.11, matching the CI workflow and Docker image.
- Install the dashboard dependencies with `python -m pip install -r requirements.txt`.
- Run the dashboard from the repository root with `streamlit run dashboard/app.py`.
- Build and run the dashboard container with `docker build -t retailpulse-dashboard .` and `docker run --rm -p 8501:8501 retailpulse-dashboard`.
- The CI workflow validates Python syntax across the repository; for a single file, run `python -m py_compile dashboard/app.py` (substitute the file to check). There is no separate test or lint command configured.
- Start the Airflow stack from the repository root with `docker compose -f airflow/docker-compose.yaml up`.

## Architecture

- `RetailPulse_AI_Powered_Customer_Analytics_and_Demand_Forecasting_Platform.ipynb` is the analytical workflow: it cleans retail data, performs customer segmentation and forecasting/churn/inventory analysis, and writes CSV, model, and report artifacts into the repository root.
- `dashboard/app.py` is the Streamlit overview and navigation entry point. Pages in `dashboard/pages/` read the root-level `cleaned_*.csv` datasets and build sales, customer/churn, demand, and inventory views.
- The dashboard container in `Dockerfile` packages the Streamlit app and its cleaned CSV inputs. `k8s/` contains its Deployment and NodePort Service manifests.
- Airflow runs as a CeleryExecutor stack defined in `airflow/docker-compose.yaml`; its DAGs are in `airflow/dags/`. The project root is mounted at `/opt/airflow/project`. The current `retailpulse_automated_retraining` DAG checks for Day 13 model/report artifacts and validates the pipeline report; it does not run the notebook or retrain models.

## Repository conventions

- Resolve data paths from the source file with `Path(__file__).resolve()` rather than hard-coding a machine-specific path. Dashboard pages locate the repository root by walking up from their own directory.
- Keep the cleaned dataset names and schemas stable: the dashboard reads `cleaned_sales_transactions.csv`, `cleaned_customer_master.csv`, and `cleaned_inventory_snapshot.csv`, while the Dockerfile explicitly copies these and the other cleaned master datasets.
- Add Streamlit pages under `dashboard/pages/` and add their navigation links in `dashboard/app.py`.
- Keep dashboard runtime dependencies in the root `requirements.txt`. The Airflow services use the Airflow image version configured in `airflow/docker-compose.yaml`.
- `.gitignore` excludes CSV datasets, model/checkpoint artifacts, and MLflow output. When changing artifact producers or consumers, keep filenames and formats aligned across the notebook, dashboard, Dockerfile, and Airflow DAG.

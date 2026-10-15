
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator


BASE_PATH = "/opt/airflow/project"


def check_pipeline_files():
    from pathlib import Path
    import json

    base_path = Path(BASE_PATH)

    required_files = [
        "day13_retrained_churn_model.json",
        "day13_retraining_report.json",
        "day13_pipeline_model.json",
        "day13_pipeline_run_report.json",
    ]

    missing_files = [
        file_name
        for file_name in required_files
        if not (base_path / file_name).exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            f"Missing Day 13 files: {missing_files}"
        )

    print("All Day 13 pipeline files are available.")


def validate_pipeline_report():
    from pathlib import Path
    import json

    report_path = (
        Path(BASE_PATH) / "day13_pipeline_run_report.json"
    )

    with report_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    print("Pipeline report loaded successfully.")
    print("Report keys:", list(report.keys()))


default_args = {
    "owner": "retailpulse",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="retailpulse_automated_retraining",
    default_args=default_args,
    description="Automated retraining pipeline for RetailPulse",
    start_date=datetime(2026, 1, 1),
    schedule="0 2 * * 1",
    catchup=False,
    tags=["RetailPulse", "Retraining", "Day13"],
) as dag:

    check_files = PythonOperator(
        task_id="check_pipeline_files",
        python_callable=check_pipeline_files,
    )

    validate_report = PythonOperator(
        task_id="validate_pipeline_report",
        python_callable=validate_pipeline_report,
    )

    check_files >> validate_report
# RetailPulse – AI-Powered Customer Analytics & Demand Forecasting Platform

RetailPulse is a data science and analytics project designed to explore retail sales, understand customer segments, analyze inventory, and support demand forecasting using data-driven insights.

## Project Objectives

- Analyze retail sales and business performance.
- Understand customer behavior and customer segments.
- Forecast future product demand.
- Explore inventory trends and optimization opportunities.
- Build an interactive dashboard for retail analytics.

## Key Features

- **Sales Analytics:** Explore sales trends and performance.
- **Demand Forecasting:** Analyze historical data to estimate future demand.
- **Customer Segmentation:** Group customers based on behavioral patterns.
- **Inventory Optimization:** Support inventory analysis and planning.
- **Machine Learning:** Experiment with predictive models and analytics workflows.
- **CI Workflow:** GitHub Actions checks Python file syntax on repository updates.

## Technology Stack

- Python
- Pandas and NumPy
- Scikit-learn
- Streamlit
- Machine Learning and Time-Series Forecasting
- Docker
- Kubernetes
- Apache Airflow
- Git and GitHub Actions

## Project Structure

```text
RetailPulse/
├── .github/
│   ├── copilot-instructions.md
│   └── workflows/
│       └── ci-cd.yml
├── airflow/
│   └── dags/
│       └── retailpulse_retraining_dag.py
├── dashboard/
│   ├── app.py
│   └── pages/
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── Dockerfile
├── requirements.txt
└── RetailPulse_AI_Powered_Customer_Analytics_and_Demand_Forecasting_Platform.ipynb
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Milan-coder91/RetailPulse.git
cd RetailPulse
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
streamlit run dashboard/app.py
```

Make sure the required datasets and dependencies are available before running the application.

## CI Workflow

The GitHub Actions workflow is located at `.github/workflows/ci-cd.yml`. It checks Python syntax and installs dependencies when configured. The workflow passing does not by itself mean the application has been deployed.

## Project Status

The project includes analytics dashboard code, a forecasting notebook, Docker configuration, Kubernetes manifests, an Airflow DAG, and a GitHub Actions CI workflow.

## Author

**Milan Kumar **

GitHub: [Milan-coder91](https://github.com/Milan-coder91)

## Disclaimer

This project is intended for learning, development, and demonstration of retail analytics and machine learning workflows.
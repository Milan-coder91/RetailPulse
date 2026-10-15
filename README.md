# RetailPulse – AI-Powered Customer Analytics & Demand Forecasting Platform

RetailPulse is a data science and analytics project designed to analyze retail sales, understand customer behavior, forecast product demand, and support inventory optimization through data-driven insights.

The project combines data analysis, machine learning, time-series forecasting, interactive dashboards, workflow automation, containerization, cloud deployment, and monitoring into a structured 28-day development workflow.

## Project Objectives

- Analyze retail sales trends and business performance.
- Understand customer purchasing behavior and customer segments.
- Forecast future product demand using machine learning and time-series models.
- Analyze inventory levels and identify potential stockout risks.
- Build an interactive dashboard for retail analytics.
- Automate model retraining and experiment tracking.
- Prepare the application for containerization, cloud deployment, and monitoring.

## Key Features

### 1. Sales Analytics
Analyze sales trends, revenue patterns, product performance, and business KPIs to support data-driven decisions.

### 2. Demand Forecasting
Use forecasting approaches such as Prophet and LSTM to study historical demand and estimate future sales or demand.

### 3. Customer Segmentation
Apply RFM analysis and customer segmentation techniques to understand customer purchasing patterns and identify meaningful customer groups.

### 4. Inventory Optimization
Analyze inventory snapshots, product availability, and stock-related indicators to support inventory planning.

### 5. Machine Learning and Model Evaluation
Evaluate forecasting and predictive models using suitable metrics such as MAE, RMSE, and MAPE.

### 6. Interactive Dashboard
Use Streamlit to present sales analytics, demand forecasts, customer segmentation, and inventory insights.

### 7. Experiment Tracking and Automation
Use MLflow for experiment tracking and Apache Airflow for workflow orchestration and model retraining automation.

### 8. DevOps and Deployment
Prepare Docker and Kubernetes configurations, automate code checks using GitHub Actions, and plan cloud deployment and monitoring.

## Technology Stack

- **Programming Language:** Python
- **Data Analysis:** Pandas, NumPy
- **Machine Learning:** Scikit-learn, XGBoost
- **Forecasting:** Prophet, LSTM
- **Model Explainability:** SHAP
- **Visualization and Dashboard:** Streamlit, Matplotlib
- **Experiment Tracking:** MLflow
- **Workflow Automation:** Apache Airflow
- **Containerization:** Docker
- **Orchestration:** Kubernetes
- **CI/CD:** GitHub Actions
- **Cloud Platform:** AWS or Google Cloud Platform (GCP)
- **Monitoring:** Prometheus and Grafana
- **Version Control:** Git and GitHub

## Dataset Overview

The project uses retail datasets to analyze sales, customers, products, inventory, stores, and promotions.

| Dataset | Purpose |
|---|---|
| `sales_transactions.csv` | Analyze sales transactions and revenue |
| `customer_master.csv` | Study customer information and behavior |
| `sku_master.csv` | Analyze product and SKU information |
| `store_master.csv` | Understand store-level information |
| `inventory_snapshot.csv` | Analyze inventory levels and availability |
| `promotions.csv` | Study promotional activities |
| `sku_inventory_flags.csv` | Support inventory-related analysis |

Dataset availability and column names may vary depending on the local data files.

## 28-Day Project Development Roadmap

### Week 1: Data Preparation and Baseline Models

**Day 1 – Project Setup**
- Understand the project objectives and requirements.
- Review the project workflow and available datasets.
- Set up the development environment and project folders.

**Day 2 – Data Understanding**
- Load the available retail datasets.
- Inspect dataset dimensions, column names, and data types.
- Identify important relationships between sales, customers, products, and inventory.

**Day 3 – Data Cleaning and Preprocessing**
- Handle missing values and inconsistent records.
- Check for duplicate records.
- Prepare cleaned datasets for analysis and modeling.

**Day 4 – Exploratory Data Analysis (EDA)**
- Analyze sales and revenue trends.
- Explore product and store performance.
- Study time-series patterns and relevant business insights.

**Day 5 – Customer Analytics**
- Perform RFM (Recency, Frequency, Monetary) analysis.
- Apply customer segmentation techniques.
- Summarize customer groups and purchasing behavior.

**Day 6 – Baseline Demand Forecasting**
- Prepare time-series data for forecasting.
- Experiment with Prophet and LSTM models.
- Evaluate model performance using suitable metrics.

**Day 7 – Week 1 Checkpoint**
- Prepare the EDA report.
- Save cleaned and processed datasets.
- Log baseline model experiments using MLflow.
- Review the results achieved during the first week.

### Week 2: Advanced Analytics and Automation

**Day 8 – Forecasting Improvements**
- Explore improvements to demand forecasting.
- Compare forecasting approaches using consistent evaluation metrics.
- Record relevant model results.

**Day 9 – Customer Churn Analysis**
- Prepare data for customer churn prediction.
- Explore an XGBoost-based predictive workflow.
- Use SHAP to interpret model predictions where applicable.

**Day 10 – Inventory Optimization**
- Analyze inventory availability and stock levels.
- Identify potential stockout and overstock risks.
- Develop inventory-related indicators to support planning.

**Day 11 – Model Tuning and Evaluation**
- Evaluate model configurations.
- Apply hyperparameter tuning where appropriate.
- Compare results and record model performance.

**Day 12 – Data Validation and Reporting**
- Add data and model validation checks.
- Review evaluation results and potential issues.
- Prepare validation reports and supporting outputs.

**Day 13 – Workflow Automation with Apache Airflow**
- Configure an Airflow DAG for the retraining workflow.
- Organize workflow tasks and dependencies.
- Validate the DAG configuration and execution where the environment permits.

**Day 14 – Week 2 Checkpoint**
- Review customer analytics and forecasting workflows.
- Review inventory analysis and automation.
- Document completed work and outstanding issues.

### Week 3: Dashboard and Application Development

**Day 15 – Dashboard Foundation**
- Set up the Streamlit application.
- Organize the application structure and navigation.
- Prepare reusable components where appropriate.

**Day 16 – Sales Analytics Dashboard**
- Display sales trends and key performance indicators.
- Present product and store performance.
- Add relevant charts and summary metrics.

**Day 17 – Demand Forecasting Dashboard**
- Present historical demand and forecast results.
- Display model evaluation metrics.
- Improve the readability of forecasting visualizations.

**Day 18 – Customer Segmentation Dashboard**
- Display customer segments and RFM insights.
- Summarize customer behavior.
- Present relevant charts and segment-level information.

**Day 19 – Inventory Optimization Dashboard**
- Display inventory-related indicators.
- Present stock availability and potential risks.
- Organize inventory insights for easier interpretation.

**Day 20 – Dashboard Integration**
- Connect the available analytics pages.
- Integrate processed data and model outputs.
- Review navigation and consistency across pages.

**Day 21 – Application Review**
- Review dashboard functionality.
- Check data loading and visualizations.
- Improve usability and resolve identified issues.

### Week 4: Containerization, Cloud Deployment, Monitoring, and Final Delivery

**Day 22 – Docker Multi-Stage Build**
- Create or refine a multi-stage Dockerfile.
- Separate build-time and runtime dependencies where appropriate.
- Build and validate the Docker image.

**Day 23 – Kubernetes Deployment**
- Prepare Kubernetes Deployment and Service manifests.
- Configure application container settings.
- Validate Kubernetes configuration and deployment where a suitable cluster is available.

**Day 24 – GitHub Actions CI/CD**
- Configure a GitHub Actions workflow.
- Automate Python syntax checks and relevant validation steps.
- Verify workflow execution on GitHub Actions.

**Day 25 – Cloud Deployment on AWS or GCP**
- Select a suitable cloud platform: Amazon Web Services (AWS) or Google Cloud Platform (GCP).
- Prepare the application and deployment configuration for the selected platform.
- Deploy the RetailPulse application.
- Verify application accessibility and deployment functionality.

**Day 26 – Monitoring Setup with Prometheus and Grafana**
- Set up Prometheus to collect relevant application or infrastructure metrics.
- Configure Grafana dashboards to visualize monitoring data.
- Review available metrics and identify performance issues.

**Day 27 – Load Testing and Model Accuracy Validation**
- Perform load testing to evaluate application performance under different workloads.
- Review response times, resource usage, and errors.
- Validate demand forecasting model accuracy using appropriate metrics such as MAE, RMSE, and MAPE.
- Document test results and identified issues.

**Day 28 – Final QA, README Polishing, Demo Video, and PDF Export**
- Perform final quality assurance (QA) across the project.
- Review the application, dashboard, and available outputs.
- Polish the README documentation.
- Record a demonstration video of the project.
- Export the final project report as a PDF.
- Review the GitHub repository and organize the final deliverables.

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
│       ├── 1_Sales_Analytics.py
│       ├── 2_Demand_Forecasting.py
│       ├── 3_Customer_Segmentation.py
│       └── 4_Inventory_Optimization.py
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── Dockerfile
├── requirements.txt
├── .dockerignore
├── .gitignore
└── RetailPulse_AI_Powered_Customer_Analytics_and_Demand_Forecasting_Platform.ipynb
```

*Note: This structure represents the main project files. Additional datasets, generated reports, model artifacts, and local configuration files may be present in the development environment.*

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Milan-coder91/RetailPulse.git
cd RetailPulse
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Make sure the required Python version and dependencies are compatible with the project environment.

### 4. Run the Streamlit Dashboard

```bash
streamlit run dashboard/app.py
```

Ensure that the required datasets and model artifacts are available at the paths expected by the application.

## GitHub Actions CI Workflow

The GitHub Actions workflow is located at:

`.github/workflows/ci-cd.yml`

The configured workflow checks out the repository, sets up Python, installs dependencies when configured, and performs Python syntax checks.

A successful CI workflow confirms that the configured checks passed. It does not, by itself, confirm cloud deployment or production readiness.

## Project Deliverables

The planned project deliverables include:

- Cleaned retail datasets and EDA report.
- Customer RFM analysis and segmentation results.
- Demand forecasting models and evaluation results.
- Inventory analytics and optimization outputs.
- Interactive Streamlit dashboard.
- MLflow experiment tracking.
- Apache Airflow retraining workflow.
- Docker multi-stage build.
- Kubernetes deployment and service manifests.
- GitHub Actions CI/CD workflow.
- Cloud deployment on AWS or GCP.
- Prometheus and Grafana monitoring setup.
- Load testing and model accuracy validation results.
- Final polished README documentation.
- Project demonstration video.
- Final project report exported as PDF.

## Project Status

RetailPulse is being developed through a structured 28-day workflow. The completion status of individual tasks depends on their actual implementation and verification.

The presence of configuration files does not necessarily mean that the corresponding service has been deployed, executed successfully, or tested in a production environment.

## Author

**Milan Kumar **

GitHub: [Milan-coder91](https://github.com/Milan-coder91)

Project Repository: [RetailPulse on GitHub](https://github.com/Milan-coder91/RetailPulse)

## Disclaimer

This project is intended for learning, development, and demonstration of retail analytics, machine learning, forecasting, and deployment workflows. Model outputs and business insights should be validated before being used for real-world business decisions.
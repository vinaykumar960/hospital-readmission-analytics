# Hospital Readmission Analytics and Prediction Using Public Data
## Complete End-to-End System: Part 1 (Data Engineering) & Part 2 (MLOps Extension)

**Student Name**: Vinay Kumar H R  
**USN**: 1CR23AI139  
**Institution**: CMR Institute of Technology (CMRIT)  
**Course**: Data Engineering and MLOps (Project 5 - 100 Marks)  
**Dataset**: UCI Diabetes 130-US Hospitals (1999-2008), 101,766 Encounters  

---

## 1. Project Overview

This project delivers a complete, enterprise-grade healthcare analytics and machine learning system for predicting and analyzing 30-day all-cause hospital readmission among diabetic patients.

### Part 1: Data Engineering Pipeline (50 Marks)
- **Automated Ingestion**: Automated dataset download, SHA-256 verification (`0689e7ec...`), and raw immutable storage.
- **Data Quality & Quarantine Layer**: Automated filtering and logging of expired/hospice records (`data/rejected/rejected_encounters.csv`). Quarantined 2,426 invalid records; retained 99,340 clean encounters.
- **Clinical Feature Engineering & De-Identification**:
  - Deterministic SHA-256 surrogate keys (`PAT_...`, `ENC_...`).
  - Standardized ICD-9 clinical classification into 17 HCUP disease categories.
  - Length of stay, acute utilization counts, medication regimen change flags, and binary readmission labels.
- **Analytical Data Mart**: Star-schema relational database (SQLite / PostgreSQL) with `dim_patient_summary`, `dim_diagnosis`, `dim_encounter`, and `fact_readmission`.
- **Workflow Orchestration**: Apache Airflow DAG (`airflow_dags/hospital_readmission_etl_dag.py`) and standalone CLI runner (`run_pipeline.py`).
- **Interactive Multi-View Dashboard**: Streamlit analytical application covering demographics, diagnoses, stay duration, admission patterns, and cohort explorer.

### Part 2: MLOps Pipeline Extension (50 Marks)
- **Leakage-Free Stratified Feature Pipeline**: Patient-level stratified 70/15/15 train/val/test splits ensuring **zero patient overlap** across partitions.
- **Multi-Model Suite & Benchmark**: Trained and evaluated regularized Logistic Regression, balanced Random Forest, and XGBoost.
- **Champion Model**: Random Forest (Test ROC-AUC: 0.6769, Recall: 53.55%, PR-AUC: 0.2282, Brier score: 0.2122).
- **MLflow Tracking & Model Registry**: Integrated tracking backed by SQLite (`sqlite:///data/mlflow.db`) logging parameters, metrics, and curve artifacts.
- **SHAP Explainability**: Global feature importances and patient-level decision-support attributions via TreeExplainer.
- **FastAPI Inference Microservice**: REST API with `/health`, `/model-info`, `/predict`, and `/explain` endpoints.
- **Production Containerization**: Dockerfile and Docker Compose configurations for containerized microservice and dashboard deployment.
- **Continuous Monitoring & Fairness Audit**: Two-sample Kolmogorov-Smirnov test and Population Stability Index (PSI) for data drift, plus subgroup fairness auditing across age and gender.
- **Embedded Decision-Support UI**: Interactive clinical risk scorer and Plotly gauge indicator embedded in Streamlit Tab 7.

---

## 2. Project Directory Structure

```
hospital_readmission_analytics/
|-- airflow_dags/
|   `-- hospital_readmission_etl_dag.py # Apache Airflow DAG definition
|-- config/
|   |-- config.yaml                     # Database, pipeline, and threshold configs
|   `-- logging_config.py               # Structured logging configuration
|-- dashboard/
|   `-- app.py                          # Unified 7-tab Streamlit Analytics & Prediction Dashboard
|-- data/
|   |-- raw/                            # Immutable raw CSV files (diabetic_data.csv, IDS_mapping.csv)
|   |-- staging/                        # Staged Parquet files and mappings
|   |-- cleaned/                        # Cleaned Parquet dimensional tables
|   |-- rejected/                       # Quarantined encounters (rejected_encounters.csv)
|   |-- healthcare_mart.db              # Relational Analytical Data Mart
|   `-- mlflow.db                       # MLflow tracking SQLite database
|-- docs/
|   |-- architecture_diagram.md         # End-to-end architecture and pipeline diagrams
|   |-- data_dictionary.md              # Technical and clinical data dictionary
|   |-- project_report_part1.md         # Part 1 submission report (Data Engineering)
|   |-- project_report_part2.md         # Part 2 submission report (MLOps Pipeline)
|   |-- model_card.md                   # Mitchell et al. clinical model card
|   |-- retraining_policy.md            # Automated drift & retraining policy
|   `-- figures/                        # ROC, PR, calibration, and SHAP plots
|-- models/
|   |-- preprocessor.joblib             # Fitted scikit-learn ColumnTransformer
|   |-- champion_model.joblib           # Production champion model bundle
|   |-- logistic_regression.joblib      # Baseline linear model bundle
|   |-- random_forest.joblib            # Balanced Random Forest bundle
|   `-- xgboost.joblib                  # XGBoost gradient booster bundle
|-- src/
|   |-- ingestion/
|   |   |-- download_dataset.py         # Automated extraction with SHA-256 verification
|   |   `-- ingest.py                   # Raw data ingestion runner & audit logger
|   |-- etl/
|   |   |-- validation.py               # Data quality rules & quarantine logging
|   |   |-- transformers.py             # Surrogate keys, ICD-9 taxonomy, feature engineering
|   |   `-- pipeline.py                 # Master Part 1 ETL orchestrator
|   |-- database/
|   |   |-- schema.sql                  # Star-schema DDL & indexes
|   |   |-- connection.py               # SQLAlchemy engine connection manager
|   |   `-- loader.py                   # Data mart bulk loader
|   |-- ml/
|   |   |-- features.py                 # Stratified leakage-free features & preprocessor
|   |   |-- train.py                    # Multi-model training, calibration & MLflow logging
|   |   `-- explainability.py           # SHAP summary plots & feature attribution
|   |-- serving/
|   |   |-- schemas.py                  # Pydantic input/output schemas with clinical bounds
|   |   `-- api.py                      # FastAPI REST microservice (/predict, /explain)
|   |-- monitoring/
|   |   `-- drift_monitor.py            # KS test, PSI, subgroup disparity & retraining triggers
|   `-- utils/
|       `-- icd9_mapping.py             # HCUP ICD-9 clinical classification engine
|-- tests/
|   |-- test_pipeline.py                # Part 1 automated tests (ETL, surrogate keys, data mart)
|   `-- test_mlops.py                   # Part 2 automated tests (Splits, models, FastAPI, drift)
|-- conftest.py                         # Pytest configuration
|-- Dockerfile                          # Production container specification
|-- docker-compose.yml                  # Multi-container orchestration (API + Dashboard)
|-- .dockerignore                       # Container build exclusions
|-- requirements.txt                    # Pinned python dependencies
|-- run_pipeline.py                     # One-click runner for Part 1 Data Engineering
`-- run_mlops_pipeline.py               # One-click runner for Part 2 MLOps Extension
```

---

## 3. Quickstart & Execution Guide

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Part 1 Data Engineering ETL
Extracts the dataset, validates quality, applies ICD-9 mapping and surrogate keys, and loads the data mart:
```bash
python run_pipeline.py
```
*Result: 101,766 raw records processed, 99,340 clean records loaded into 4 relational tables, 2,426 quarantined in `data/rejected/rejected_encounters.csv`.*

### Step 3: Run Part 2 MLOps Pipeline
Executes stratified feature preparation, trains 3 models with MLflow tracking, computes SHAP values, and runs data drift audits:
```bash
python run_mlops_pipeline.py
```
*Result: Evaluates LR, RF, XGBoost. Selects Random Forest champion (ROC-AUC: 0.6769, Recall: 53.55%). Saves artifacts to `models/`.*

### Step 4: Run the Automated Test Suite (100% Pass Rate)
Executes all unit and integration tests across Data Engineering and MLOps:
```bash
pytest -v
```
*Result: 11 passed in <10 seconds.*

### Step 5: Start the FastAPI Inference Microservice
```bash
uvicorn src.serving.api:app --host 127.0.0.1 --port 8000 --reload
```
Interactive API docs are available at `http://127.0.0.1:8000/docs`.

#### Sample Prediction Request:
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "age_group": "[70-80)",
    "race": "Caucasian",
    "gender": "Female",
    "length_of_stay": 6,
    "num_lab_procedures": 55,
    "num_procedures": 2,
    "num_medications": 22,
    "number_diagnoses": 9,
    "prior_inpatient_admissions": 2,
    "prior_emergency_visits": 1,
    "prior_outpatient_visits": 0,
    "active_diabetes_meds_count": 2,
    "medication_change_flag": 1,
    "diabetes_med_prescribed": 1,
    "insulin_treatment": "Insulin (Up)",
    "hba1c_test_result": ">8",
    "glucose_test_result": "None",
    "primary_diagnosis_category": "Circulatory System",
    "admission_type_desc": "Emergency",
    "discharge_disposition_desc": "Discharged to home"
  }'
```

### Step 6: Launch the Unified Streamlit Dashboard
```bash
streamlit run dashboard/app.py
```
Access the dashboard at `http://localhost:8501`. Features 7 interactive tabs:
1. **Age & Demographics**: Readmission disparities across 10-year age cohorts.
2. **Diagnosis & Specialty**: Clinical categories mapped via HCUP ICD-9 taxonomy.
3. **Length of Stay & Utilization**: Hospital stay duration and prior inpatient visit correlation.
4. **Admission & Discharge Patterns**: Emergency vs elective routes and discharge destinations.
5. **High-Risk Cohort Explorer**: Filterable multi-attribute high-risk cohort isolation.
6. **Pipeline & Data Quality Audit**: Real-time inspection of latest ETL and quarantine logs.
7. **Readmission Predictor & Decision Support**: Interactive patient risk scoring, Plotly gauge meter, risk tiering, and top clinical drivers.

---

## 4. Multi-Model Performance Comparison

Evaluated on held-out test data (N = 14,807 encounters) with zero patient leakage:

| Model Architecture | Test ROC-AUC | Test PR-AUC | Test Recall | Test Precision | Test F1-Score | Brier Score | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Random Forest** | **0.6769** | **0.2282** | **53.55%** | **19.23%** | **0.2832** | **0.2122** | **Champion Model** |
| XGBoost Classifier | 0.6698 | 0.2230 | 52.85% | 18.66% | 0.2759 | 0.2173 | Challenger Model |
| Logistic Regression | 0.6558 | 0.2078 | 58.37% | 16.54% | 0.2577 | 0.2396 | Baseline Model |

---

## 5. Docker Deployment

Deploy the microservice and analytical dashboard together using Docker Compose:
```bash
docker-compose up --build
```
- FastAPI API: `http://localhost:8000` (Docs: `http://localhost:8000/docs`)
- Streamlit Dashboard: `http://localhost:8501`

---

## 6. Academic & Clinical Disclaimer

This software system is developed solely as an academic and educational prototype for the Data Engineering and MLOps course. Automated predictions and clinical decision-support recommendations must never replace qualified clinical judgement by licensed healthcare professionals.

# Individual Project Report: Hospital Readmission Analytics & Pipeline (Part 1)

**Course**: Data Engineering and MLOps  
**Project Title**: Project 5 - Hospital Readmission Analytics and Prediction Using Public Data  
**Student Name**: Individual Submission  
**Assignment Focus**: Part 1 - Data Pipeline Implementation & Analytical Dashboards  
**Submission Date**: September 2026  

---

## 1. Executive Summary & Problem Understanding

Hospital readmission within 30 days of discharge is a primary indicator of healthcare delivery quality, patient transition safety, and inpatient resource utilization. Under value-based healthcare programs, such as the Hospital Readmissions Reduction Program (HRRP) administered by the Centers for Medicare & Medicaid Services (CMS), healthcare institutions face severe financial penalties and reputational loss for elevated, preventable 30-day readmissions.

In diabetic patient populations, readmission risks are substantially magnified due to complex multi-morbidities, metabolic instability, frequent polypharmacy adjustments, and post-discharge self-management challenges.

### Project 1 Objectives
1. **Develop an Automated, Privacy-Conscious Data Pipeline**: Ingest and curate the de-identified **UCI Diabetes 130-US Hospitals (1999?2008)** dataset containing 101,766 inpatient encounters.
2. **Implement Rigorous Data Quality & Error Quarantine**: Standardize missing value codes, filter out invalid/terminal encounters (hospice, deceased), and isolate rejected records with audit trails.
3. **Execute Clinical Feature Engineering & De-Identification**: Map legacy ICD-9 diagnosis codes into clinical organ-system categories, generate cryptographic SHA-256 patient surrogate keys, and engineer acute utilization metrics.
4. **Deploy a Dimensional Data Mart in Relational Storage**: Construct a star schema (`dim_patient_summary`, `dim_diagnosis`, `dim_encounter`, `fact_readmission`, `etl_pipeline_audit`) supporting high-performance analytical queries.
5. **Orchestrate Repeatable Workflows**: Implement an Apache Airflow DAG and reproducible CLI runner for daily batch ETL.
6. **Deliver an Interactive Clinical Analytics Dashboard**: Create a Streamlit application featuring 6 distinct analytical views for hospital administrators, clinicians, and data scientists.

---

## 2. Dataset Information & Ingestion Strategy

### 2.1 Dataset Profile
The project utilizes the **Diabetes 130-US Hospitals (1999?2008)** dataset from the UCI Machine Learning Repository.
- **Repository URI**: `https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008`
- **Total Raw Records**: 101,766 hospital encounters
- **Total Features**: 50 clinical, demographic, admission, laboratory, and medication attributes
- **Time Horizon**: 10 years of clinical inpatient care across 130 US hospitals
- **De-identification & Compliance**: Fully de-identified in compliance with HIPAA Safe Harbor regulations.

### 2.2 Ingestion Architecture & Execution
The ingestion layer (`src/ingestion/download_dataset.py` and `src/ingestion/ingest.py`) implements:
- **Automated Network Retrieval**: Downloads ZIP archives directly from the authoritative UCI repository.
- **SHA-256 Checksum Verification**: Calculates and records cryptographic hashes to ensure raw file integrity.
- **Immutable Raw Landing Zone**: Stores unmodified CSV snapshots in `data/raw/`.
- **Lookup Table Parsing**: Dissects `IDS_mapping.csv` into structured mappings for `admission_type_id`, `discharge_disposition_id`, and `admission_source_id`.
- **Staging in Parquet**: Converts staged records into compressed Parquet (`data/staging/staged_encounters.parquet`).
- **Metadata Audit Logging**: Records extraction timestamp, record count, column count, and HTTP status in `logs/ingestion_audit.json`.

---

## 3. End-to-End System Architecture

The healthcare data engineering pipeline follows a layered architecture:

```
[ UCI Public Data Source ] ??> [ Automated Ingestion Layer ] ??> [ Raw Data Landing (data/raw/) ]
                                                                             ?
                                                                             ?
[ Rejection / Error Log ] <?? [ Data Quality & Quarantine Layer ] <????????????
(data/rejected/rejected_encounters.csv)      ? (99,340 Valid Records)
                                             ?
                              [ Transformation & Feature Engineering ]
                              - ICD-9 Category Mapping
                              - SHA-256 Surrogate Keys
                              - Length of Stay & Prior Stays
                              - Polypharmacy & Medication Counts
                                             ?
                                             ?
                              [ Relational Data Mart (PostgreSQL / SQLite) ]
                              ??? dim_patient_summary (69,987 patients)
                              ??? dim_diagnosis (99,340 diagnoses)
                              ??? dim_encounter (99,340 encounters)
                              ??? fact_readmission (99,340 fact rows)
                                             ?
                   ?????????????????????????????????????????????????????
                   ?                                                   ?
      [ Airflow Orchestration DAG ]                        [ Streamlit Interactive Dashboard ]
      - Daily batch execution                              - 6 Interactive Views & KPIs
      - Task dependency graph                              - Risk Profiling & Cohort Explorer
```

---

## 4. Data Quality, Validation Rules & Error Quarantine

Healthcare data pipelines must enforce strict data quality (DQ) gates before analytical exposure.

### 4.1 Missing-Value Standardization
The raw UCI dataset encodes missing values with `?`, empty strings, or `'Unknown/Invalid'`. The validation module (`src/etl/validation.py`) converts these representations to standard `NaN`/nulls. Features with excessive missingness (such as `weight` >96% missing and `payer_code` ~40% missing) are handled appropriately without corrupting primary clinical features.

### 4.2 Terminal / Hospice Encounter Exclusion Rule
In clinical readmission modeling, encounters resulting in patient mortality or discharge to hospice cannot logically result in a 30-day hospital readmission. Retaining these records introduces severe label bias.
The pipeline quarantines records matching the following discharge disposition IDs:
- **11**: Expired / Deceased
- **13**: Hospice / Home
- **14**: Hospice / Medical Facility
- **19**: Expired at Home
- **20**: Expired in a Medical Facility
- **21**: Expired in Place Unknown

### 4.3 Validation Results Summary
- **Total Raw Records Input**: 101,766
- **Valid Records Retained**: 99,340 (97.6%)
- **Quarantined Records**: 2,426 (2.4%)
  - *Expired / Hospice Discharges*: 2,423 encounters
  - *Invalid Length of Stay / Identifier / Gender*: 3 encounters
- **Audit File Location**: `data/rejected/rejected_encounters.csv` and `logs/validation_audit.json`.

---

## 5. Transformation, Clinical Feature Engineering & De-Identification

### 5.1 Patient-Safe Surrogate Key Generation
To prevent re-identification and isolate sensitive identifiers, the transformation layer (`src/etl/transformers.py`) generates deterministic SHA-256 cryptographic surrogate keys:
$$	ext{SurrogateKey} = 	ext{Prefix} + 	ext{"\_"} + 	ext{SHA256}(	ext{RawID})[0:16]$$
- Encounters: `ENC_9b83f0a1c...`
- Patients: `PAT_4e28c772b...`

### 5.2 ICD-9 Clinical Classification
Legacy ICD-9 codes (e.g., `428.0` for Congestive Heart Failure, `250.02` for Diabetes Type II) are mapped into 17 clinical disease categories based on the Healthcare Cost and Utilization Project (HCUP) taxonomy:
1. **Circulatory System** (ICD 390?459, 785)
2. **Respiratory System** (ICD 460?519, 786)
3. **Digestive System** (ICD 520?579, 787)
4. **Diabetes Mellitus** (ICD 250.xx)
5. **Injury & Poisoning** (ICD 800?999)
6. **Musculoskeletal System** (ICD 710?739)
7. **Genitourinary System** (ICD 580?629, 788)
8. **Neoplasms / Oncology** (ICD 140?239)
9. **Endocrine, Nutritional & Metabolic** (ICD 240?279)
10. **Other / Supplementary** (Mental, Nervous, Infectious, V-codes, E-codes)

### 5.3 Engineered Clinical & Utilization Features
1. **Length of Stay (`length_of_stay`)**: Integer duration in days (1?14).
2. **Prior Acute Utilization (`prior_inpatient_admissions`, `prior_emergency_visits`, `prior_outpatient_visits`)**: Past 12-month hospital utilization.
3. **Total Prior Visits (`total_prior_visits`)**: Additive metric measuring overall healthcare burden.
4. **Active Diabetes Medication Count (`active_diabetes_meds_count`)**: Number of distinct anti-diabetic agents actively prescribed (`Up`, `Down`, `Steady`).
5. **Medication Regimen Modification (`medication_change_flag`)**: Binary flag (1 if dosage/molecule was changed during stay, 0 otherwise).
6. **Insulin Therapy Mode (`insulin_treatment`)**: Categorical stratification (`No Insulin`, `Insulin (Up)`, `Insulin (Down)`, `Insulin (Steady)`).
7. **Target Variables**:
   - `readmission_30d_binary`: 1 if readmitted in $<30$ days, 0 otherwise (**Primary Target**).
   - `readmission_any_binary`: 1 if readmitted at any point, 0 otherwise.
   - `readmission_category`: Multi-class string (`Within 30 Days (<30)`, `After 30 Days (>30)`, `No Readmission (NO)`).

---

## 6. Database Schema Design & Analytical Data Mart

The storage layer (`src/database/schema.sql`) implements a normalized star schema in PostgreSQL / SQLite:

### 6.1 Star Schema Entity-Relationship
- **`fact_readmission`**: Central fact table storing 99,340 cleaned encounters with clinical measures, lab counts, medication features, and target readmission flags.
- **`dim_patient_summary`**: Patient dimension containing 69,987 unique patients, capturing longitudinal visit frequencies and lifetime readmission status.
- **`dim_diagnosis`**: Diagnostic dimension mapping primary, secondary, and tertiary ICD-9 codes and severity weights.
- **`dim_encounter`**: Admission routes, discharge destinations, payer codes, and admitting specialties.
- **`etl_pipeline_audit`**: Real-time pipeline execution tracking.

### 6.2 Relational Indexes
To ensure sub-second query performance on analytical aggregations, indexes were established on `age_group`, `primary_diagnosis_category`, `readmission_30d_binary`, `length_of_stay`, and `patient_surrogate_key`.

---

## 7. Pipeline Orchestration & Workflow Automation

### 7.1 Apache Airflow DAG (`airflow_dags/hospital_readmission_etl_dag.py`)
An automated Apache Airflow DAG is configured with daily scheduling (`@daily`), retries, and failure alerts.
The task execution flow is:
$$	ext{ingest\_raw\_dataset} \longrightarrow 	ext{validate\_and\_quarantine} \longrightarrow 	ext{transform\_and\_engineer\_features} \longrightarrow 	ext{load\_to\_data\_mart}$$

### 7.2 Standalone CLI Orchestrator (`run_pipeline.py`)
For instant execution and evaluation without requiring an active Airflow cluster, `run_pipeline.py` executes the entire pipeline end-to-end, validating data, building Parquet staging layers, and writing to the relational database.

---

## 8. Visual Analytics, Findings & Clinical Insights

The Streamlit analytical application (`dashboard/app.py`) provides 6 interactive views:

### View 1: Executive KPI & Demographic Analysis
- **Key Metrics**: 99,340 encounters, 11,314 30-day readmissions (**11.39% baseline rate**), 45,954 total readmissions (46.26%), average length of stay: 4.4 days.
- **Demographic Breakdown**: Readmission risk increases monotonically with age:
  - Age `[0-10)`: ~3.5%
  - Age `[50-60)`: ~9.8%
  - Age `[70-80)`: ~12.2%
  - Age `[80-90)`: ~12.8%
- **Gender & Race**: Caucasian and African American cohorts demonstrate similar 30-day readmission profiles (~11.4% vs ~11.2%), with slight elevations in female patients in geriatric brackets.

### View 2: Clinical Diagnosis & Medical Specialty
- **Diagnosis Risk Distribution**:
  - *Circulatory System* represents the largest single clinical cohort (>30,000 encounters) with an elevated 30-day readmission rate of **12.5%**.
  - *Respiratory System* encounters exhibit a **12.6%** readmission rate.
  - *Diabetes Mellitus* primary encounters exhibit an **11.2%** readmission rate.
  - *Injury and Poisoning* encounters demonstrate lower readmission rates (**9.4%**).
- **Specialty High-Risk Drivers**: Cardiology, General Surgery, and Nephrology admissions demonstrate higher repeat encounter probabilities than Elective Orthopedics.

### View 3: Length of Stay & Acute Utilization Dynamics
- **LOS vs Readmission**: Patients hospitalized for 1?2 days experience a ~9.2% readmission rate, whereas patients hospitalized for 10?14 days experience a readmission rate of **14.8% to 16.2%**. Extended stay serves as a proxy for clinical complexity and nosocomial vulnerability.
- **Prior Hospitalization Impact**: Prior acute utilization is the single strongest predictor of readmission:
  - 0 prior inpatient stays: **8.9%** 30-day readmission
  - 1 prior inpatient stay: **17.4%** 30-day readmission
  - 2 prior inpatient stays: **24.6%** 30-day readmission
  - $\ge 3$ prior inpatient stays: **>33.0%** 30-day readmission

### View 4: Admission & Discharge Patterns
- **Discharge Disposition**: Patients discharged to Skilled Nursing Facilities (SNFs) or Home Health Care exhibit significantly higher readmission rates (15?18%) than patients discharged to home without specialized care (10.1%), indicating high post-acute frailty.
- **Admission Route**: Emergency admissions represent 53% of all inpatient encounters and account for >60% of all 30-day readmissions.

### View 5: High-Risk Cohort Explorer
The interactive cohort explorer allows hospital administrators to filter multi-complex patients (e.g., prior inpatient stays $\ge 1$, prescribed medications $\ge 15$, and active insulin therapy). This high-risk subpopulation exhibits an aggregated 30-day readmission rate exceeding **21.4%** (almost double baseline), providing high-value targets for transitional care nurse interventions.

### View 6: Pipeline & Data Quality Audit
Displays live logs of data ingestion timestamps, SHA-256 hashes, quarantined record distributions, and database load statistics.

---

## 9. Verification, Test Results & Execution Evidence

### 9.1 Automated Test Suite (`tests/test_pipeline.py`)
Automated unit and integration tests executed using `pytest`:
- `test_icd9_clinical_mapping`: Validates clinical categorization across Circulatory, Respiratory, Diabetes, Neoplasms, V-codes, and Missing values. (**PASSED**)
- `test_surrogate_key_generation`: Validates cryptographic determinism and collision resistance. (**PASSED**)
- `test_validation_quarantines_hospice_and_expired`: Validates accurate isolation of deceased/hospice cases and invalid LOS bounds. (**PASSED**)
- `test_database_connectivity_and_records`: Validates database schema integrity and table row counts. (**PASSED**)

### 9.2 Pipeline Execution Metrics
- **Runtime**: 45.48 seconds (full extract-transform-load of 101,766 records)
- **Database Engine**: Relational Data Mart initialized and populated with 0 integrity errors.

---

## 10. Conclusion & Part 2 Transition Readiness

Assignment Part 1 has successfully established a scalable, privacy-conscious healthcare ETL pipeline, a star-schema analytical data mart, automated test validation, and an interactive Streamlit dashboard.

The curated data mart (`fact_readmission`) and engineered clinical features provide the complete, high-quality foundation required for **Part 2 - MLOps Pipeline Extension**, including:
- 30-day readmission binary classification model training (Logistic Regression, Random Forest, XGBoost).
- MLflow experiment tracking, metrics logging, and model registry.
- Model explainability via SHAP values.
- FastAPI REST inference microservice and Docker containerization.

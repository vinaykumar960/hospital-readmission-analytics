# Healthcare Readmission ETL & Analytics Architecture

## 1. End-to-End System Architecture

```mermaid
flowchart TD
    subgraph "1. Source Data Layer"
        UCI["UCI Machine Learning Repository<br/>Diabetes 130-US Hospitals (1999-2008)<br/>101,766 Raw Encounters"]
        IDS["IDS_mapping.csv<br/>Admission / Discharge / Source Dictionaries"]
    end

    subgraph "2. Automated Ingestion Layer"
        DL["Python Ingestion Service<br/>(src/ingestion/download_dataset.py)"]
        RAW_CSV["Immutable Raw Landing<br/>(data/raw/diabetic_data.csv)<br/>SHA-256 Checksum Verification"]
        AUDIT_ING["Ingestion Audit Log<br/>(logs/ingestion_audit.json)"]
    end

    subgraph "3. Data Quality & Quarantine Layer"
        DQ["DQ Validation Engine<br/>(src/etl/validation.py)<br/>- Special code normalization (?)<br/>- Expired/Hospice filtering (IDs 11,13,14,19,20,21)<br/>- Boundary & constraint validation"]
        REJ["Quarantined Error Log<br/>(data/rejected/rejected_encounters.csv)<br/>2,426 Quarantined Records"]
        VAL_AUD["Validation Audit Log<br/>(logs/validation_audit.json)"]
    end

    subgraph "4. Transformation & Feature Engineering"
        TRANS["Transformer Engine<br/>(src/etl/transformers.py)<br/>- De-identification (SHA-256 Surrogate Keys)<br/>- ICD-9 Clinical Classification<br/>- Feature Engineering (LOS, Priors, Polypharmacy)<br/>- Dimensional Splitting"]
        PARQUET["Optimized Staging Parquet<br/>(data/cleaned/*.parquet)"]
    end

    subgraph "5. Storage Layer (Analytical Data Mart)"
        DB[("PostgreSQL / SQLite Analytical Data Mart<br/>(data/healthcare_mart.db)")]
        DIM_P["dim_patient_summary (69,987 rows)"]
        DIM_D["dim_diagnosis (99,340 rows)"]
        DIM_E["dim_encounter (99,340 rows)"]
        FACT_R["fact_readmission (99,340 rows)"]
        AUD_T["etl_pipeline_audit"]
    end

    subgraph "6. Orchestration Layer"
        AIRFLOW["Apache Airflow DAG<br/>(airflow_dags/hospital_readmission_etl_dag.py)<br/>Daily Scheduled Pipeline"]
        RUNNER["Python CLI Runner<br/>(run_pipeline.py)"]
    end

    subgraph "7. Analytics & Visualization Layer"
        DASH["Streamlit Interactive Dashboard<br/>(dashboard/app.py)<br/>- Age & Demographics<br/>- Diagnosis & Specialty<br/>- Length of Stay & Utilization<br/>- Admission/Discharge Patterns<br/>- High-Risk Cohort Explorer<br/>- Pipeline & DQ Audit View"]
    end

    UCI --> DL
    IDS --> DL
    DL --> RAW_CSV
    DL --> AUDIT_ING
    RAW_CSV --> DQ
    DQ -->|Quarantine| REJ
    DQ -->|Log| VAL_AUD
    DQ -->|99,340 Valid| TRANS
    TRANS --> PARQUET
    PARQUET --> DB
    DB --> DIM_P
    DB --> DIM_D
    DB --> DIM_E
    DB --> FACT_R
    DB --> AUD_T

    AIRFLOW -.-> DL
    AIRFLOW -.-> DQ
    AIRFLOW -.-> TRANS
    AIRFLOW -.-> DB
    RUNNER -.-> DB

    DB --> DASH
```

---

## 2. Pipeline Execution Layers

1. **Source Layer**: Acquires 101,766 de-identified clinical encounter records across 130 US hospitals spanning 10 years (1999?2008).
2. **Ingestion Layer**: Downloads, verifies file SHA-256 signatures, preserves immutable raw CSV snapshots, and parses lookup tables.
3. **Validation & Quality Layer**: Filters 2,426 invalid/hospice/expired records where 30-day readmission is clinically impossible, recording explicit rejection reasons in `data/rejected/rejected_encounters.csv`.
4. **Transformation Layer**:
   - Generates privacy-preserving SHA-256 surrogate keys (`PAT_...`, `ENC_...`).
   - Translates ICD-9 codes into 17 high-level clinical categories.
   - Computes utilization metrics, medication change flags, and 30-day readmission indicators.
5. **Storage Layer**: Star-schema data mart (`dim_patient_summary`, `dim_diagnosis`, `dim_encounter`, `fact_readmission`) hosted in PostgreSQL / SQLite.
6. **Orchestration Layer**: Airflow DAG + one-click Python runner (`run_pipeline.py`).
7. **Visualization Layer**: Multi-view Streamlit dashboard with interactive filtering and cohort drill-downs.

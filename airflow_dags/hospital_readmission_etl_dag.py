"""
Apache Airflow DAG for Healthcare Hospital Readmission ETL Pipeline.
Orchestrates scheduled batch ingestion, data validation, feature engineering, and data mart loading.
"""
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# In Airflow environment, DAGs folder will point to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Optional Airflow imports with standalone fallback
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from airflow.operators.bash import BashOperator
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False

default_args = {
    'owner': 'healthcare_data_team',
    'depends_on_past': False,
    'start_date': datetime(2026, 9, 1),
    'email': ['data-eng@hospital-analytics.org'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

def task_extract_ingest(**kwargs):
    from src.ingestion.ingest import ingest_raw_data
    return ingest_raw_data()

def task_validate_quarantine(**kwargs):
    import pandas as pd
    from src.etl.validation import validate_and_clean_data
    staging_file = PROJECT_ROOT / "data" / "staging" / "staged_encounters.parquet"
    df_raw = pd.read_parquet(staging_file)
    valid_df, rejected_df, summary = validate_and_clean_data(df_raw)
    return summary

def task_transform_features(**kwargs):
    import json
    import pandas as pd
    from src.etl.transformers import transform_healthcare_data
    staging_file = PROJECT_ROOT / "data" / "staging" / "staged_encounters.parquet"
    mapping_file = PROJECT_ROOT / "data" / "staging" / "ids_mapping.json"
    
    with open(mapping_file, "r", encoding="utf-8") as f:
        mappings = json.load(f)
    
    df_raw = pd.read_parquet(staging_file)
    from src.etl.validation import validate_and_clean_data
    valid_df, _, _ = validate_and_clean_data(df_raw)
    
    transformed_tables = transform_healthcare_data(valid_df, mappings)
    return {k: len(v) for k, v in transformed_tables.items()}

def task_load_datamart(**kwargs):
    import pandas as pd
    from src.database.connection import get_database_engine
    from src.database.loader import load_tables_to_database
    
    cleaned_dir = PROJECT_ROOT / "data" / "cleaned"
    tables = {
        "dim_patient_summary": pd.read_parquet(cleaned_dir / "dim_patient_summary.parquet"),
        "dim_diagnosis": pd.read_parquet(cleaned_dir / "dim_diagnosis.parquet"),
        "dim_encounter": pd.read_parquet(cleaned_dir / "dim_encounter.parquet"),
        "fact_readmission": pd.read_parquet(cleaned_dir / "fact_readmission.parquet"),
    }
    engine = get_database_engine()
    return load_tables_to_database(tables, engine)

if AIRFLOW_AVAILABLE:
    dag = DAG(
        'hospital_readmission_etl_pipeline',
        default_args=default_args,
        description='Daily ETL pipeline for hospital encounter readmission analytics',
        schedule_interval='@daily',
        catchup=False,
        tags=['healthcare', 'etl', 'readmission', 'part1']
    )

    t1_ingest = PythonOperator(
        task_id='ingest_raw_dataset',
        python_callable=task_extract_ingest,
        dag=dag,
    )

    t2_validate = PythonOperator(
        task_id='validate_and_quarantine',
        python_callable=task_validate_quarantine,
        dag=dag,
    )

    t3_transform = PythonOperator(
        task_id='transform_and_engineer_features',
        python_callable=task_transform_features,
        dag=dag,
    )

    t4_load = PythonOperator(
        task_id='load_to_data_mart',
        python_callable=task_load_datamart,
        dag=dag,
    )

    t1_ingest >> t2_validate >> t3_transform >> t4_load

if __name__ == "__main__":
    print("[*] Testing Airflow DAG tasks in standalone execution mode...")
    print("Executing Task 1: Ingest...")
    r1 = task_extract_ingest()
    print("Executing Task 2: Validate...")
    r2 = task_validate_quarantine()
    print("Executing Task 3: Transform...")
    r3 = task_transform_features()
    print("Executing Task 4: Load...")
    r4 = task_load_datamart()
    print("[+] Airflow standalone test passed successfully!")

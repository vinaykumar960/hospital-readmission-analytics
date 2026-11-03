"""
Master End-to-End ETL Pipeline Orchestrator.
Coordinates:
1. Ingestion of raw dataset & mapping parsing
2. Data Quality validation, cleaning, and rejection quarantine
3. Transformation, surrogate keys, ICD-9 mapping, and feature engineering
4. Analytical Data Mart loading into Database (PostgreSQL / SQLite)
5. Execution metrics and audit logging
"""
import os
import sys
import json
import time
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.logging_config import setup_logger
from src.ingestion.ingest import ingest_raw_data, parse_ids_mapping
from src.etl.validation import validate_and_clean_data
from src.etl.transformers import transform_healthcare_data
from src.database.connection import get_database_engine
from src.database.loader import load_tables_to_database

logger = setup_logger("etl_pipeline")

def run_pipeline() -> dict:
    start_time = time.time()
    logger.info("==================================================================")
    logger.info("Starting Healthcare Readmission ETL Pipeline Execution (Part 1)")
    logger.info("==================================================================")

    # Step 1: Ingestion
    logger.info("[Step 1/4] Running Raw Data Ingestion...")
    ingestion_summary = ingest_raw_data()
    raw_df = pd.read_parquet(ingestion_summary["staged_parquet"])
    
    with open(BASE_DIR / "data" / "staging" / "ids_mapping.json", "r", encoding="utf-8") as f:
        mappings = json.load(f)

    # Step 2: Validation & Quarantine
    logger.info("[Step 2/4] Running Data Quality Validation & Error Quarantine...")
    valid_df, rejected_df, validation_summary = validate_and_clean_data(raw_df)

    # Step 3: Transformation & Feature Engineering
    logger.info("[Step 3/4] Transforming Data & Engineering Clinical Features...")
    transformed_tables = transform_healthcare_data(valid_df, mappings)

    # Step 4: Loading into Analytical Data Mart
    logger.info("[Step 4/4] Loading Tables into Data Mart...")
    db_engine = get_database_engine()
    load_summary = load_tables_to_database(transformed_tables, db_engine)

    elapsed_time = time.time() - start_time
    logger.info(f"ETL Pipeline completed successfully in {elapsed_time:.2f} seconds!")

    summary = {
        "pipeline_execution_id": f"RUN_{int(start_time)}",
        "timestamp": datetime.now().isoformat(),
        "elapsed_seconds": round(elapsed_time, 2),
        "raw_records_extracted": len(raw_df),
        "valid_records_processed": len(valid_df),
        "quarantined_rejected_records": len(rejected_df),
        "data_mart_tables_loaded": load_summary,
        "database_url": str(db_engine.url),
        "status": "SUCCESS"
    }

    summary_file = BASE_DIR / "logs" / "latest_pipeline_run.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Execution report saved to {summary_file}")
    return summary

if __name__ == "__main__":
    res = run_pipeline()
    print("Pipeline Execution Summary:")
    print(json.dumps(res, indent=2))

"""
Database Loader Module.
Bulk loads transformed dimensional and fact tables into the healthcare analytical data mart.
"""
import os
import sys
import pandas as pd
from pathlib import Path
from sqlalchemy import Engine, text

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.logging_config import setup_logger
from src.database.connection import get_database_engine, init_database

logger = setup_logger("db_loader")

def load_tables_to_database(tables: dict[str, pd.DataFrame], engine: Engine = None) -> dict:
    """
    Loads DataFrames into their respective tables in the database.
    """
    if engine is None:
        engine = get_database_engine()

    init_database(engine)
    results = {}

    for table_name, df in tables.items():
        logger.info(f"Loading {len(df)} records into table '{table_name}'...")
        # Write to SQL (replace to ensure fresh reproducible load)
        df.to_sql(table_name, engine, if_exists="replace", index=False)
        results[table_name] = len(df)
        logger.info(f"[+] Successfully loaded '{table_name}' ({len(df)} rows).")

    # Record pipeline audit record
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                INSERT INTO etl_pipeline_audit (step_name, records_input, records_output, records_rejected, status, details)
                VALUES (:step, :input_cnt, :out_cnt, :rej_cnt, :status, :details)
                """),
                {
                    "step": "Full Pipeline Load",
                    "input_cnt": results.get("fact_readmission", 0),
                    "out_cnt": results.get("fact_readmission", 0),
                    "rej_cnt": 0,
                    "status": "SUCCESS",
                    "details": f"Loaded tables: {', '.join(results.keys())}"
                }
            )
    except Exception as e:
        logger.warning(f"Audit table logging warning: {e}")

    return results

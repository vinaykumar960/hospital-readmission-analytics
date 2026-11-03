"""
Data Ingestion and Raw Storage Layer
Extracts CSV data, parses dictionary mappings, logs metadata, and writes staging snapshots.
"""
import os
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.logging_config import setup_logger
from src.ingestion.download_dataset import download_and_extract

logger = setup_logger("ingestion")

def parse_ids_mapping(ids_file: Path) -> dict:
    """
    Parses IDS_mapping.csv which contains 3 sections:
    1. admission_type_id
    2. discharge_disposition_id
    3. admission_source_id
    """
    sections = {}
    current_section = None
    admission_types = {}
    discharge_dispositions = {}
    admission_sources = {}

    with open(ids_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "admission_type_id" in line:
                current_section = "admission_type"
                continue
            elif "discharge_disposition_id" in line:
                current_section = "discharge_disposition"
                continue
            elif "admission_source_id" in line:
                current_section = "admission_source"
                continue
            
            parts = [p.strip() for p in line.split(",", 1)]
            if len(parts) == 2:
                try:
                    k = int(parts[0])
                    v = parts[1].replace('"', '')
                    if current_section == "admission_type":
                        admission_types[k] = v
                    elif current_section == "discharge_disposition":
                        discharge_dispositions[k] = v
                    elif current_section == "admission_source":
                        admission_sources[k] = v
                except ValueError:
                    pass

    return {
        "admission_type": admission_types,
        "discharge_disposition": discharge_dispositions,
        "admission_source": admission_sources
    }

def ingest_raw_data() -> dict:
    """
    Executes raw extraction, records metadata audit log, and creates staged raw data.
    """
    meta = download_and_extract()
    raw_csv = Path(meta["diabetic_csv_path"])
    ids_csv = Path(meta["ids_csv_path"])
    staging_dir = BASE_DIR / "data" / "staging"
    staging_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Ingesting raw encounter data from {raw_csv}...")
    df_raw = pd.read_csv(raw_csv, low_memory=False)
    
    # Save staged snapshot
    staged_encounter_path = staging_dir / "staged_encounters.parquet"
    df_raw.to_parquet(staged_encounter_path, index=False)
    
    mappings = parse_ids_mapping(ids_csv)
    mapping_json_path = staging_dir / "ids_mapping.json"
    with open(mapping_json_path, "w", encoding="utf-8") as f:
        json.dump(mappings, f, indent=2)

    ingestion_summary = {
        "ingestion_timestamp": datetime.utcnow().isoformat(),
        "source": meta["source"],
        "raw_file": str(raw_csv),
        "raw_sha256": meta["sha256_hash"],
        "raw_record_count": len(df_raw),
        "raw_column_count": len(df_raw.columns),
        "staged_parquet": str(staged_encounter_path),
        "admission_types_count": len(mappings["admission_type"]),
        "discharge_dispositions_count": len(mappings["discharge_disposition"]),
        "admission_sources_count": len(mappings["admission_source"]),
        "status": "SUCCESS"
    }

    audit_log_path = BASE_DIR / "logs" / "ingestion_audit.json"
    with open(audit_log_path, "w", encoding="utf-8") as f:
        json.dump(ingestion_summary, f, indent=2)

    logger.info(f"Ingestion successful! Records loaded: {len(df_raw)}. Metadata written to {audit_log_path}")
    return ingestion_summary

if __name__ == "__main__":
    ingest_raw_data()

"""
Data Quality Validation and Rejection Quarantine Module.
Applies rigorous validation rules, isolates malformed records, and logs rejection audits.
"""
import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.logging_config import setup_logger

logger = setup_logger("validation")

HOSPICE_EXPIRED_DISCHARGE_IDS = [11, 13, 14, 19, 20, 21]

def validate_and_clean_data(df_raw: pd.DataFrame, save_audit: bool = True) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Performs data quality checks, missing value resolution, and rejection logging.
    Returns (valid_df, rejected_df, audit_summary).
    """
    logger.info(f"Starting data validation on {len(df_raw)} records...")
    df = df_raw.copy()
    
    # 1. Normalize missing value representations
    logger.info("Replacing special missing value codes ('?', 'Unknown/Invalid', empty strings)...")
    df.replace("?", np.nan, inplace=True)
    df.replace("Unknown/Invalid", np.nan, inplace=True)
    df.replace("", np.nan, inplace=True)
    
    rejected_reasons = []
    
    # Create mask for invalid / expired / hospice records
    # Discharge dispositions: 11 (Expired), 13 (Hospice/home), 14 (Hospice/medical), 19/20/21 (Expired at facility)
    mask_hospice_expired = df["discharge_disposition_id"].isin(HOSPICE_EXPIRED_DISCHARGE_IDS)
    
    # Check invalid length of stay
    mask_invalid_los = (df["time_in_hospital"] <= 0) | (df["time_in_hospital"] > 14) | df["time_in_hospital"].isna()
    
    # Check invalid patient/encounter IDs
    mask_invalid_ids = df["encounter_id"].isna() | df["patient_nbr"].isna()
    
    # Check invalid gender (e.g. Unknown/Invalid)
    mask_invalid_gender = df["gender"].isna()
    
    # Duplicate encounters
    mask_duplicates = df.duplicated(subset=["encounter_id"], keep="first")
    
    # Aggregate rejection flags
    is_rejected = mask_hospice_expired | mask_invalid_los | mask_invalid_ids | mask_invalid_gender | mask_duplicates
    
    df_rejected = df[is_rejected].copy()
    
    # Assign specific reason
    def get_rejection_reason(row):
        reasons = []
        if row["discharge_disposition_id"] in HOSPICE_EXPIRED_DISCHARGE_IDS:
            reasons.append(f"Discharge disposition {row['discharge_disposition_id']} (Expired/Hospice: Readmission N/A)")
        if row["time_in_hospital"] <= 0 or row["time_in_hospital"] > 14 or pd.isna(row["time_in_hospital"]):
            reasons.append("Invalid time in hospital")
        if pd.isna(row["encounter_id"]) or pd.isna(row["patient_nbr"]):
            reasons.append("Missing primary identifiers")
        if pd.isna(row["gender"]):
            reasons.append("Unknown/Invalid gender")
        return "; ".join(reasons) if reasons else "Duplicate encounter"

    if not df_rejected.empty:
        df_rejected["rejection_reason"] = df_rejected.apply(get_rejection_reason, axis=1)
        df_rejected["quarantine_timestamp"] = datetime.utcnow().isoformat()

    df_valid = df[~is_rejected].copy()

    rejected_path = None
    if save_audit:
        # Log rejection outputs
        rejected_dir = BASE_DIR / "data" / "rejected"
        rejected_dir.mkdir(parents=True, exist_ok=True)
        rejected_path = rejected_dir / "rejected_encounters.csv"
        df_rejected.to_csv(rejected_path, index=False)
    
    audit_summary = {
        "total_records_processed": len(df),
        "valid_records_retained": len(df_valid),
        "rejected_records_count": len(df_rejected),
        "rejection_breakdown": {
            "hospice_expired_count": int(mask_hospice_expired.sum()),
            "invalid_los_count": int(mask_invalid_los.sum()),
            "invalid_gender_count": int(mask_invalid_gender.sum()),
            "duplicate_encounters_count": int(mask_duplicates.sum()),
        },
        "rejected_log_path": str(rejected_path) if rejected_path else "In-memory test run",
        "validation_timestamp": datetime.utcnow().isoformat(),
        "status": "PASSED"
    }

    if save_audit:
        audit_path = BASE_DIR / "logs" / "validation_audit.json"
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(audit_summary, f, indent=2)

    logger.info(f"Validation complete: {len(df_valid)} valid records retained, {len(df_rejected)} quarantined.")
    return df_valid, df_rejected, audit_summary

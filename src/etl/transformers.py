"""
Feature Engineering, De-Identification, and Dimensional Modeling Module.
Generates surrogate keys, standardizes ICD-9 codes, encodes clinical metrics,
and models admission, diagnosis, patient summary, and fact tables.
"""
import os
import sys
import hashlib
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.logging_config import setup_logger
from src.utils.icd9_mapping import map_icd9_code, get_category_severity_weight

logger = setup_logger("transformers")

MEDICATION_COLUMNS = [
    "metformin", "repaglinide", "nateglinide", "chlorpropamide", "glimepiride",
    "acetohexamide", "glipizide", "glyburide", "tolbutamide", "pioglitazone",
    "rosiglitazone", "acarbose", "miglitol", "troglitazone", "tolazamide",
    "examide", "citoglipton", "insulin", "glyburide-metformin", "glipizide-metformin",
    "glimepiride-pioglitazone", "metformin-rosiglitazone", "metformin-pioglitazone"
]

def generate_surrogate_key(prefix: str, val: str) -> str:
    raw = f"{prefix}_{str(val)}"
    return f"{prefix}_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"

def transform_healthcare_data(df_valid: pd.DataFrame, mappings: dict) -> dict[str, pd.DataFrame]:
    logger.info("Starting transformation & feature engineering...")
    df = df_valid.copy()

    # 1. Patient & Encounter Surrogate Keys (De-identification)
    # Fast unique lookup mapping for surrogate keys
    unique_pats = df["patient_nbr"].unique()
    pat_map = {p: generate_surrogate_key("PAT", p) for p in unique_pats}
    df["patient_surrogate_key"] = df["patient_nbr"].map(pat_map)

    unique_encs = df["encounter_id"].unique()
    enc_map = {e: generate_surrogate_key("ENC", e) for e in unique_encs}
    df["encounter_surrogate_key"] = df["encounter_id"].map(enc_map)

    # 2. Map Admission & Discharge IDs to human-readable labels
    adm_types = {int(k): v for k, v in mappings.get("admission_type", {}).items()}
    disch_disp = {int(k): v for k, v in mappings.get("discharge_disposition", {}).items()}
    adm_src = {int(k): v for k, v in mappings.get("admission_source", {}).items()}

    df["admission_type_desc"] = df["admission_type_id"].map(adm_types).fillna("Unknown / Other")
    df["discharge_disposition_desc"] = df["discharge_disposition_id"].map(disch_disp).fillna("Unknown / Other")
    df["admission_source_desc"] = df["admission_source_id"].map(adm_src).fillna("Unknown / Other")

    # 3. ICD-9 Clinical Classification
    # Cache mapping for speed
    all_icd9 = pd.concat([df["diag_1"], df["diag_2"], df["diag_3"]]).dropna().unique()
    icd9_cache = {c: map_icd9_code(c) for c in all_icd9}
    
    df["primary_diagnosis_category"] = df["diag_1"].map(icd9_cache).fillna("Unknown / Missing")
    df["secondary_diagnosis_category"] = df["diag_2"].map(icd9_cache).fillna("Unknown / Missing")
    df["tertiary_diagnosis_category"] = df["diag_3"].map(icd9_cache).fillna("Unknown / Missing")

    df["primary_diagnosis_severity"] = df["primary_diagnosis_category"].apply(get_category_severity_weight)

    # 4. Feature Engineering
    df["length_of_stay"] = df["time_in_hospital"].astype(int)
    df["prior_inpatient_admissions"] = df["number_inpatient"].fillna(0).astype(int)
    df["prior_emergency_visits"] = df["number_emergency"].fillna(0).astype(int)
    df["prior_outpatient_visits"] = df["number_outpatient"].fillna(0).astype(int)
    df["total_prior_visits"] = df["prior_inpatient_admissions"] + df["prior_emergency_visits"] + df["prior_outpatient_visits"]
    
    df["num_lab_procedures"] = df["num_lab_procedures"].fillna(0).astype(int)
    df["num_procedures"] = df["num_procedures"].fillna(0).astype(int)
    df["num_medications"] = df["num_medications"].fillna(0).astype(int)
    df["number_diagnoses"] = df["number_diagnoses"].fillna(0).astype(int)

    # Vectorized active diabetic medications count
    avail_meds = [m for m in MEDICATION_COLUMNS if m in df.columns]
    med_df = df[avail_meds].isin(["Up", "Down", "Steady"])
    df["active_diabetes_meds_count"] = med_df.sum(axis=1)
    
    df["medication_change_flag"] = (df["change"].astype(str).str.strip() == "Ch").astype(int)
    df["diabetes_med_prescribed"] = (df["diabetesMed"].astype(str).str.strip() == "Yes").astype(int)

    df["insulin_treatment"] = df["insulin"].apply(
        lambda x: "No Insulin" if str(x).strip() in ["No", "nan", "None"] else f"Insulin ({str(x).strip()})"
    )

    df["hba1c_test_result"] = df["A1Cresult"].fillna("None")
    df["glucose_test_result"] = df["max_glu_serum"].fillna("None")

    # Readmission Target Labels
    df["readmitted_raw"] = df["readmitted"].astype(str).str.strip()
    df["readmission_30d_binary"] = (df["readmitted_raw"] == "<30").astype(int)
    df["readmission_any_binary"] = (df["readmitted_raw"] != "NO").astype(int)
    
    readm_cat_map = {
        "<30": "Within 30 Days (<30)",
        ">30": "After 30 Days (>30)",
        "NO": "No Readmission (NO)"
    }
    df["readmission_category"] = df["readmitted_raw"].map(readm_cat_map).fillna("No Readmission (NO)")

    df["medical_specialty"] = df["medical_specialty"].fillna("Missing / Unspecified")
    df["race"] = df["race"].fillna("Unknown / Missing")
    df["age_group"] = df["age"].astype(str)

    # ----------------------------------------------------
    # Dimensional Modeling
    # ----------------------------------------------------

    # 1. dim_patient_summary (Fast aggregation)
    dim_patient_summary = df.groupby("patient_surrogate_key", as_index=False).agg(
        race=("race", "first"),
        gender=("gender", "first"),
        primary_age_group=("age_group", "last"),
        total_encounters_count=("encounter_surrogate_key", "count"),
        total_inpatient_stays=("prior_inpatient_admissions", "sum"),
        total_emergency_visits=("prior_emergency_visits", "sum"),
        total_outpatient_visits=("prior_outpatient_visits", "sum"),
        has_30d_readmission=("readmission_30d_binary", "max"),
        has_any_readmission=("readmission_any_binary", "max")
    )

    # 2. dim_diagnosis
    dim_diagnosis = df[[
        "encounter_surrogate_key", "diag_1", "diag_2", "diag_3",
        "primary_diagnosis_category", "secondary_diagnosis_category", "tertiary_diagnosis_category",
        "primary_diagnosis_severity"
    ]].rename(columns={
        "diag_1": "primary_icd9_code",
        "diag_2": "secondary_icd9_code",
        "diag_3": "tertiary_icd9_code"
    }).drop_duplicates(subset=["encounter_surrogate_key"])

    # 3. dim_encounter
    dim_encounter = df[[
        "encounter_surrogate_key", "patient_surrogate_key",
        "admission_type_id", "admission_type_desc",
        "discharge_disposition_id", "discharge_disposition_desc",
        "admission_source_id", "admission_source_desc",
        "medical_specialty", "payer_code"
    ]].drop_duplicates(subset=["encounter_surrogate_key"])

    # 4. fact_readmission
    fact_readmission = df[[
        "encounter_surrogate_key", "patient_surrogate_key",
        "age_group", "race", "gender",
        "length_of_stay",
        "num_lab_procedures", "num_procedures", "num_medications",
        "number_diagnoses", "active_diabetes_meds_count",
        "prior_inpatient_admissions", "prior_emergency_visits", "prior_outpatient_visits", "total_prior_visits",
        "medication_change_flag", "diabetes_med_prescribed", "insulin_treatment",
        "hba1c_test_result", "glucose_test_result",
        "primary_diagnosis_category", "admission_type_desc", "discharge_disposition_desc", "medical_specialty",
        "readmission_30d_binary", "readmission_any_binary", "readmission_category"
    ]]

    # Save cleaned Parquet tables to data/cleaned/
    cleaned_dir = BASE_DIR / "data" / "cleaned"
    cleaned_dir.mkdir(parents=True, exist_ok=True)
    
    dim_patient_summary.to_parquet(cleaned_dir / "dim_patient_summary.parquet", index=False)
    dim_diagnosis.to_parquet(cleaned_dir / "dim_diagnosis.parquet", index=False)
    dim_encounter.to_parquet(cleaned_dir / "dim_encounter.parquet", index=False)
    fact_readmission.to_parquet(cleaned_dir / "fact_readmission.parquet", index=False)

    logger.info(f"Transformation complete. Generated {len(fact_readmission)} fact records and {len(dim_patient_summary)} unique patient records.")

    return {
        "dim_patient_summary": dim_patient_summary,
        "dim_diagnosis": dim_diagnosis,
        "dim_encounter": dim_encounter,
        "fact_readmission": fact_readmission
    }

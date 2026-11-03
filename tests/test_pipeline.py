"""
Comprehensive Test Suite for Hospital Readmission Pipeline (Part 1).
Tests Ingestion, ICD-9 Mapping, Validation rules, Transformer logic, and Data Mart integrity.
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.utils.icd9_mapping import map_icd9_code, get_category_severity_weight
from src.etl.validation import validate_and_clean_data
from src.etl.transformers import generate_surrogate_key, transform_healthcare_data
from src.database.connection import get_database_engine

def test_icd9_clinical_mapping():
    # Circulatory
    assert map_icd9_code("410.1") == "Circulatory System"
    assert map_icd9_code("428") == "Circulatory System"
    assert map_icd9_code("785") == "Circulatory System"
    
    # Respiratory
    assert map_icd9_code("493.9") == "Respiratory System"
    assert map_icd9_code("786") == "Respiratory System"
    
    # Diabetes
    assert map_icd9_code("250.02") == "Diabetes Mellitus"
    
    # Neoplasms
    assert map_icd9_code("174") == "Neoplasms"
    
    # V and E codes
    assert map_icd9_code("V45.1") == "Supplementary (V-codes)"
    assert map_icd9_code("E876") == "External Causes of Injury (E-codes)"
    
    # Unknown / Null
    assert map_icd9_code("?") == "Unknown / Missing"
    assert map_icd9_code(None) == "Unknown / Missing"

def test_surrogate_key_generation():
    key1 = generate_surrogate_key("PAT", "12345")
    key2 = generate_surrogate_key("PAT", "12345")
    key3 = generate_surrogate_key("PAT", "67890")
    
    assert key1.startswith("PAT_")
    assert key1 == key2, "Surrogate keys must be deterministic"
    assert key1 != key3, "Surrogate keys for different IDs must be distinct"

def test_validation_quarantines_hospice_and_expired():
    sample_df = pd.DataFrame([
        {
            "encounter_id": 1,
            "patient_nbr": 100,
            "discharge_disposition_id": 1, # Normal discharge
            "time_in_hospital": 3,
            "gender": "Female",
            "readmitted": "NO"
        },
        {
            "encounter_id": 2,
            "patient_nbr": 101,
            "discharge_disposition_id": 11, # Expired
            "time_in_hospital": 4,
            "gender": "Male",
            "readmitted": "NO"
        },
        {
            "encounter_id": 3,
            "patient_nbr": 102,
            "discharge_disposition_id": 13, # Hospice
            "time_in_hospital": 2,
            "gender": "Female",
            "readmitted": "NO"
        },
        {
            "encounter_id": 4,
            "patient_nbr": 103,
            "discharge_disposition_id": 1,
            "time_in_hospital": 0, # Invalid LOS
            "gender": "Female",
            "readmitted": "NO"
        }
    ])
    
    valid_df, rejected_df, audit = validate_and_clean_data(sample_df, save_audit=False)
    assert len(valid_df) == 1
    assert len(rejected_df) == 3
    assert audit["rejection_breakdown"]["hospice_expired_count"] == 2
    assert audit["rejection_breakdown"]["invalid_los_count"] == 1

def test_database_connectivity_and_records():
    engine = get_database_engine()
    with engine.connect() as conn:
        res = pd.read_sql("SELECT COUNT(*) as cnt FROM fact_readmission", conn)
        assert res["cnt"].iloc[0] > 0
        
        patient_res = pd.read_sql("SELECT COUNT(*) as cnt FROM dim_patient_summary", conn)
        assert patient_res["cnt"].iloc[0] > 0

"""
Comprehensive Automated Test Suite for Part 2 MLOps Pipeline Extension.
Covers:
- Feature engineering, split integrity, and leakage prevention
- Model artifacts and probability prediction
- FastAPI serving endpoints (/health, /model-info, /predict, /explain)
- Statistical drift monitoring and PSI calculations
"""
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from starlette.testclient import TestClient

from src.ml.features import (
    load_analytical_dataset,
    prepare_train_val_test_data,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES
)
from src.serving.api import app, get_model_and_preprocessor
from src.monitoring.drift_monitor import compute_drift_metrics

@pytest.fixture(scope="module")
def api_client():
    return TestClient(app)

def test_feature_preparation_and_split_integrity():
    """Verify train/val/test splits, dimensions, and zero patient leakage across sets."""
    split_data = prepare_train_val_test_data()
    
    assert "X_train" in split_data
    assert "X_val" in split_data
    assert "X_test" in split_data
    assert "y_train" in split_data
    assert "train_pats" in split_data
    assert "test_pats" in split_data
    
    train_patients = set(split_data["train_pats"]["patient_surrogate_key"])
    val_patients = set(split_data["val_pats"]["patient_surrogate_key"])
    test_patients = set(split_data["test_pats"]["patient_surrogate_key"])
    
    # Zero patient overlap between train, val, and test splits
    assert len(train_patients.intersection(test_patients)) == 0, "Patient leakage detected between train and test sets!"
    assert len(train_patients.intersection(val_patients)) == 0, "Patient leakage detected between train and val sets!"
    assert len(val_patients.intersection(test_patients)) == 0, "Patient leakage detected between val and test sets!"
    
    # Verify feature columns match
    expected_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    assert list(split_data["X_train_raw"].columns) == expected_cols
    assert len(split_data["y_train"]) == len(split_data["X_train"])
    assert split_data["X_train"].shape[1] == len(split_data["feature_names"])

def test_champion_model_and_inference():
    """Verify champion model artifact loads and outputs calibrated probabilities."""
    mb, pb = get_model_and_preprocessor()
    assert mb is not None
    assert pb is not None
    
    model = mb["model"]
    preprocessor = pb["preprocessor"]
    
    # Generate dummy input matching schema
    dummy_input = pd.DataFrame([{
        "length_of_stay": 4,
        "num_lab_procedures": 40,
        "num_procedures": 1,
        "num_medications": 15,
        "number_diagnoses": 7,
        "active_diabetes_meds_count": 1,
        "prior_inpatient_admissions": 1,
        "prior_emergency_visits": 0,
        "prior_outpatient_visits": 0,
        "total_prior_visits": 1,
        "age_group": "[60-70)",
        "race": "Caucasian",
        "gender": "Female",
        "primary_diagnosis_category": "Circulatory System",
        "admission_type_desc": "Emergency",
        "discharge_disposition_desc": "Discharged to home",
        "insulin_treatment": "No Insulin",
        "hba1c_test_result": "None",
        "glucose_test_result": "None",
        "medication_change_flag": 0,
        "diabetes_med_prescribed": 1
    }])
    
    X_trans = preprocessor.transform(dummy_input)
    assert X_trans.shape[0] == 1
    assert X_trans.shape[1] > 50  # Encoded feature dimensions
    
    probs = model.predict_proba(X_trans)
    assert probs.shape == (1, 2)
    p = float(probs[0, 1])
    assert 0.0 <= p <= 1.0, f"Probability {p} out of bounds [0, 1]"

def test_fastapi_health_endpoint(api_client):
    """Verify /health endpoint returns healthy status and model information."""
    response = api_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["model_loaded"] is True
    assert "champion_model" in data

def test_fastapi_model_info_endpoint(api_client):
    """Verify /model-info endpoint returns champion metadata and performance metrics."""
    response = api_client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "model_name" in data
    assert "test_metrics" in data
    assert data["test_metrics"]["roc_auc"] > 0.60
    assert "intended_use" in data

def test_fastapi_predict_endpoint(api_client):
    """Verify /predict returns valid risk score, probability, and clinical recommendation."""
    payload = {
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
    }
    response = api_client.post("/predict", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["readmission_30d_prediction"] in [0, 1]
    assert 0.0 <= res_data["readmission_probability"] <= 1.0
    assert res_data["risk_tier"] in ["Low Risk", "Moderate Risk", "High Risk"]
    assert len(res_data["clinical_recommendation"]) > 10
    assert "disclaimer" in res_data

def test_fastapi_explain_endpoint(api_client):
    """Verify /explain endpoint returns top feature contributors and risk level."""
    payload = {
        "age_group": "[60-70)",
        "race": "AfricanAmerican",
        "gender": "Male",
        "length_of_stay": 3,
        "num_lab_procedures": 40,
        "num_procedures": 1,
        "num_medications": 14,
        "number_diagnoses": 6,
        "prior_inpatient_admissions": 0,
        "prior_emergency_visits": 0,
        "prior_outpatient_visits": 0,
        "active_diabetes_meds_count": 1,
        "medication_change_flag": 0,
        "diabetes_med_prescribed": 1,
        "insulin_treatment": "No Insulin",
        "hba1c_test_result": "None",
        "glucose_test_result": "None",
        "primary_diagnosis_category": "Endocrine/Nutritional/Metabolic",
        "admission_type_desc": "Emergency",
        "discharge_disposition_desc": "Discharged to home"
    }
    response = api_client.post("/explain", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert "top_risk_contributors" in res_data
    assert len(res_data["top_risk_contributors"]) > 0
    assert "risk_tier" in res_data
    assert "clinical_decision_support" in res_data

def test_drift_monitoring_metrics():
    """Verify Kolmogorov-Smirnov test and PSI calculations run without errors."""
    ref_data = np.random.normal(loc=5.0, scale=2.0, size=500)
    curr_data = np.random.normal(loc=5.2, scale=2.1, size=500)
    
    drift_res = compute_drift_metrics(ref_data, curr_data)
    assert "ks_statistic" in drift_res
    assert "p_value" in drift_res
    assert "psi" in drift_res
    assert "drift_detected" in drift_res
    assert 0.0 <= drift_res["ks_statistic"] <= 1.0
    assert 0.0 <= drift_res["p_value"] <= 1.0

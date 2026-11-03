"""
Feature Engineering, Selection, and Stratified Preprocessing Pipeline for Part 2.
Prevents patient data leakage, implements ColumnTransformer, and saves preprocessing artifacts.
"""
import os
import sys
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.logging_config import setup_logger
from src.database.connection import get_database_engine

logger = setup_logger("ml_features")

NUMERICAL_FEATURES = [
    "length_of_stay",
    "num_lab_procedures",
    "num_procedures",
    "num_medications",
    "number_diagnoses",
    "active_diabetes_meds_count",
    "prior_inpatient_admissions",
    "prior_emergency_visits",
    "prior_outpatient_visits",
    "total_prior_visits"
]

CATEGORICAL_FEATURES = [
    "age_group",
    "race",
    "gender",
    "primary_diagnosis_category",
    "admission_type_desc",
    "discharge_disposition_desc",
    "insulin_treatment",
    "hba1c_test_result",
    "glucose_test_result",
    "medication_change_flag",
    "diabetes_med_prescribed"
]

TARGET_COL = "readmission_30d_binary"

def load_analytical_dataset() -> pd.DataFrame:
    engine = get_database_engine()
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM fact_readmission", conn)
    logger.info(f"Loaded {len(df)} records from fact_readmission table.")
    return df

def build_preprocessor() -> ColumnTransformer:
    # Use sparse_output=False for dense matrix compatibility
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERICAL_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES)
        ],
        remainder="drop"
    )
    return preprocessor

def prepare_train_val_test_data(
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42
) -> dict:
    df = load_analytical_dataset()

    # Features and target
    feature_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    X = df[feature_cols].copy()
    y = df[TARGET_COL].copy().astype(int)
    patient_ids = df["patient_surrogate_key"].copy()

    # Stratified split by patient or target to ensure no patient leakage across splits
    # GroupSplit by patient_surrogate_key with stratification on patient-level label
    unique_patients = df.groupby("patient_surrogate_key").agg(
        has_30d=(TARGET_COL, "max")
    ).reset_index()

    train_val_pats, test_pats = train_test_split(
        unique_patients,
        test_size=test_size,
        stratify=unique_patients["has_30d"],
        random_state=random_state
    )

    val_relative_size = val_size / (1.0 - test_size)
    train_pats, val_pats = train_test_split(
        train_val_pats,
        test_size=val_relative_size,
        stratify=train_val_pats["has_30d"],
        random_state=random_state
    )

    train_set = set(train_pats["patient_surrogate_key"])
    val_set = set(val_pats["patient_surrogate_key"])
    test_set = set(test_pats["patient_surrogate_key"])

    # Map back to encounters
    train_mask = patient_ids.isin(train_set)
    val_mask = patient_ids.isin(val_set)
    test_mask = patient_ids.isin(test_set)

    X_train, y_train = X[train_mask], y[train_mask]
    X_val, y_val = X[val_mask], y[val_mask]
    X_test, y_test = X[test_mask], y[test_mask]

    logger.info(f"Split sizes (Encounters): Train={len(X_train)} (Positive: {y_train.sum()} / {y_train.mean():.3%}), "
                f"Val={len(X_val)} (Positive: {y_val.sum()} / {y_val.mean():.3%}), "
                f"Test={len(X_test)} (Positive: {y_test.sum()} / {y_test.mean():.3%})")

    # Fit preprocessor strictly on training data
    preprocessor = build_preprocessor()
    preprocessor.fit(X_train)

    # Get feature names after one-hot encoding
    cat_encoder = preprocessor.named_transformers_["cat"]
    cat_feature_names = cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
    all_feature_names = NUMERICAL_FEATURES + cat_feature_names

    X_train_trans = preprocessor.transform(X_train)
    X_val_trans = preprocessor.transform(X_val)
    X_test_trans = preprocessor.transform(X_test)

    models_dir = BASE_DIR / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Save preprocessor artifact
    preprocessor_path = models_dir / "preprocessor.joblib"
    joblib.dump({
        "preprocessor": preprocessor,
        "feature_names": all_feature_names,
        "numerical_features": NUMERICAL_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "target_col": TARGET_COL
    }, preprocessor_path)
    logger.info(f"Saved preprocessor artifact to {preprocessor_path}")

    return {
        "X_train": X_train_trans,
        "y_train": y_train.values,
        "X_val": X_val_trans,
        "y_val": y_val.values,
        "X_test": X_test_trans,
        "y_test": y_test.values,
        "X_train_raw": X_train,
        "X_test_raw": X_test,
        "train_pats": train_pats,
        "val_pats": val_pats,
        "test_pats": test_pats,
        "feature_names": all_feature_names,
        "preprocessor": preprocessor
    }

if __name__ == "__main__":
    data = prepare_train_val_test_data()
    print("Feature preparation complete! Total encoded features:", len(data["feature_names"]))

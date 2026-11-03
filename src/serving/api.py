"""
FastAPI Real-Time Inference Microservice for 30-Day Hospital Readmission Risk.
Serves:
- GET  /health (Service & Model Liveness)
- GET  /model-info (Champion model metadata & performance)
- POST /predict (Real-time readmission risk scoring with clinical stratification)
- POST /explain (Clinical decision-support factor attribution)
"""
import os
import sys
import time
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.logging_config import setup_logger
from src.serving.schemas import (
    PatientEncounterInput,
    PredictionResponse,
    ExplanationResponse
)

logger = setup_logger("fastapi_serving")

app = FastAPI(
    title="Hospital Readmission Prediction API",
    description="Academic Decision-Support Prototype for 30-Day Hospital Readmission Risk Scoring",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODELS_DIR = BASE_DIR / "models"
CHAMPION_PATH = MODELS_DIR / "champion_model.joblib"
PREPROCESSOR_PATH = MODELS_DIR / "preprocessor.joblib"

# Global lazy model loader
model_bundle = None
preprocessor_bundle = None

def get_model_and_preprocessor():
    global model_bundle, preprocessor_bundle
    if model_bundle is None or preprocessor_bundle is None:
        if not CHAMPION_PATH.exists() or not PREPROCESSOR_PATH.exists():
            raise RuntimeError("Model or Preprocessor artifact missing. Execute training pipeline first.")
        logger.info("Loading Champion Model and Preprocessor artifacts...")
        model_bundle = joblib.load(CHAMPION_PATH)
        preprocessor_bundle = joblib.load(PREPROCESSOR_PATH)
    return model_bundle, preprocessor_bundle

@app.on_event("startup")
def startup_event():
    try:
        get_model_and_preprocessor()
        logger.info("Model service successfully initialized.")
    except Exception as e:
        logger.warning(f"Startup warning: {e}")

@app.get("/health", tags=["Health"])
def health_check():
    try:
        mb, pb = get_model_and_preprocessor()
        return {
            "status": "HEALTHY",
            "model_loaded": True,
            "champion_model": mb.get("model_name", "Unknown"),
            "features_count": len(mb.get("feature_names", [])),
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "DEGRADED",
            "model_loaded": False,
            "error": str(e)
        }

@app.get("/model-info", tags=["Metadata"])
def get_model_info():
    try:
        mb, _ = get_model_and_preprocessor()
        return {
            "model_name": mb.get("model_name"),
            "test_metrics": mb.get("test_metrics"),
            "features": mb.get("feature_names", [])[:20],
            "total_features": len(mb.get("feature_names", [])),
            "intended_use": "Academic Decision-Support Prototype. Not certified for sole diagnostic use."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def convert_input_to_df(patient: PatientEncounterInput) -> pd.DataFrame:
    data_dict = patient.model_dump() if hasattr(patient, "model_dump") else patient.dict()
    if data_dict.get("total_prior_visits") is None:
        data_dict["total_prior_visits"] = (
            data_dict["prior_inpatient_admissions"] +
            data_dict["prior_emergency_visits"] +
            data_dict["prior_outpatient_visits"]
        )
    return pd.DataFrame([data_dict])

@app.post("/predict", response_model=PredictionResponse, tags=["Inference"])
def predict_readmission(patient: PatientEncounterInput):
    try:
        mb, pb = get_model_and_preprocessor()
        model = mb["model"]
        preprocessor = pb["preprocessor"]

        df_input = convert_input_to_df(patient)
        X_trans = preprocessor.transform(df_input)

        prob = float(model.predict_proba(X_trans)[0, 1])
        prediction = 1 if prob >= 0.5 else 0

        # Clinical Risk Tiering
        if prob >= 0.35:
            tier = "High Risk"
            recom = "High readmission vulnerability. Recommend transitional care nurse coordination, 48-hour post-discharge telephone check, and medication reconciliation."
        elif prob >= 0.18:
            tier = "Moderate Risk"
            recom = "Moderate readmission risk. Schedule 7-day primary care follow-up and review discharge prescription instructions."
        else:
            tier = "Low Risk"
            recom = "Low readmission likelihood. Standard post-discharge outpatient care plan indicated."

        return PredictionResponse(
            model_name=mb["model_name"],
            readmission_30d_prediction=prediction,
            readmission_probability=round(prob, 4),
            risk_tier=tier,
            clinical_recommendation=recom,
            disclaimer="RESEARCH PROTOTYPE ONLY: This decision-support tool is an academic prototype and must not replace professional clinical judgement."
        )
    except Exception as e:
        logger.error(f"Inference error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/explain", response_model=ExplanationResponse, tags=["Inference"])
def explain_prediction(patient: PatientEncounterInput):
    try:
        mb, pb = get_model_and_preprocessor()
        model = mb["model"]
        preprocessor = pb["preprocessor"]
        feature_names = mb["feature_names"]

        df_input = convert_input_to_df(patient)
        X_trans = preprocessor.transform(df_input)
        prob = float(model.predict_proba(X_trans)[0, 1])

        # Feature level attribution proxy via model feature importances
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        else:
            importances = np.abs(model.coef_[0])

        top_indices = np.argsort(importances)[::-1][:6]
        contributors = []
        for idx in top_indices:
            feat = feature_names[idx]
            val = float(X_trans[0, idx])
            contributors.append({
                "feature": feat.replace("_", " ").title(),
                "relative_importance": f"{importances[idx]:.4f}",
                "standardized_patient_value": f"{val:.2f}"
            })

        tier = "High Risk" if prob >= 0.35 else ("Moderate Risk" if prob >= 0.18 else "Low Risk")
        return ExplanationResponse(
            readmission_probability=round(prob, 4),
            risk_tier=tier,
            top_risk_contributors=contributors,
            clinical_decision_support="Key drivers reflect acute prior admissions, stay duration, and complex pharmacotherapy."
        )
    except Exception as e:
        logger.error(f"Explanation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

"""
Model Explainability Module with SHAP (SHapley Additive exPlanations) & Feature Importance.
Generates:
1. Global Feature Importance summary (bar plot & beeswarm plot)
2. Local Patient-Level attribution (waterfall explanation)
3. Interpretable Clinical Attribution outputs
"""
import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.logging_config import setup_logger
from src.ml.features import prepare_train_val_test_data

logger = setup_logger("ml_explainability")

def generate_shap_explanations(sample_size: int = 500) -> dict:
    models_dir = BASE_DIR / "models"
    figures_dir = BASE_DIR / "docs" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    champion_path = models_dir / "champion_model.joblib"
    if not champion_path.exists():
        raise FileNotFoundError("Champion model not found! Run src/ml/train.py first.")

    champion_data = joblib.load(champion_path)
    model = champion_data["model"]
    model_name = champion_data["model_name"]
    feature_names = champion_data["feature_names"]

    logger.info(f"Loaded Champion Model: {model_name}. Preparing evaluation samples for SHAP...")
    data = prepare_train_val_test_data()
    X_test = data["X_test"]
    X_test_raw = data["X_test_raw"]

    # Sample a manageable subset for SHAP computation
    np.random.seed(42)
    sample_indices = np.random.choice(len(X_test), size=min(sample_size, len(X_test)), replace=False)
    X_sample = X_test[sample_indices]

    import shap
    logger.info("Computing SHAP values using TreeExplainer...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    # In binary classification, shap_values is a list [class_0, class_1] or an array
    if isinstance(shap_values, list):
        shap_vals_pos = shap_values[1]
    elif len(shap_values.shape) == 3:
        shap_vals_pos = shap_values[:, :, 1]
    else:
        shap_vals_pos = shap_values

    # 1. Global Feature Importance (Top 15 Features)
    mean_abs_shap = np.abs(shap_vals_pos).mean(axis=0)
    top_indices = np.argsort(mean_abs_shap)[::-1][:15]

    top_features = [feature_names[i] for i in top_indices]
    top_scores = [float(mean_abs_shap[i]) for i in top_indices]

    plt.figure(figsize=(10, 6))
    y_pos = np.arange(len(top_features))
    plt.barh(y_pos, top_scores[::-1], color="#2563EB", align="center")
    plt.yticks(y_pos, [f.replace("_", " ").title() for f in top_features[::-1]])
    plt.xlabel("Mean |SHAP Value| (Impact on Readmission Risk)")
    plt.title(f"Top 15 Global Risk Drivers - {model_name} (SHAP)")
    plt.tight_layout()
    summary_path = figures_dir / "shap_global_feature_importance.png"
    plt.savefig(summary_path, dpi=150)
    plt.close()
    logger.info(f"Saved global SHAP plot to {summary_path}")

    # 2. Local Patient Explanation (Case Example)
    # Pick a high-risk sample
    sample_probs = model.predict_proba(X_sample)[:, 1]
    high_risk_idx = int(np.argmax(sample_probs))
    patient_shap = shap_vals_pos[high_risk_idx]
    patient_prob = float(sample_probs[high_risk_idx])

    # Top positive risk factors for this patient
    patient_top_idx = np.argsort(patient_shap)[::-1][:5]
    top_patient_factors = [
        {
            "feature": feature_names[i],
            "shap_contribution": round(float(patient_shap[i]), 4),
            "feature_value": float(X_sample[high_risk_idx, i])
        }
        for i in patient_top_idx
    ]

    # Save explanation metadata
    explainability_metadata = {
        "model_name": model_name,
        "sample_size": len(X_sample),
        "top_global_features": list(zip(top_features, [round(s, 4) for s in top_scores])),
        "sample_patient_case": {
            "predicted_readmission_probability": round(patient_prob, 4),
            "top_risk_factors": top_patient_factors
        },
        "plot_path": str(summary_path)
    }

    meta_file = BASE_DIR / "logs" / "shap_explainability.json"
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(explainability_metadata, f, indent=2)

    logger.info(f"Explainability metadata successfully written to {meta_file}")
    return explainability_metadata

if __name__ == "__main__":
    generate_shap_explanations()

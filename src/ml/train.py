"""
Model Training, Multi-Model Evaluation, Calibration, and MLflow Tracking Module.
Trains:
1. Logistic Regression (Baseline)
2. Random Forest Classifier
3. XGBoost Classifier (Champion)

Tracks:
- Hyperparameters
- Metrics: Accuracy, Precision, Recall, F1-Score, ROC-AUC, PR-AUC, Brier score (Calibration)
- Artifacts: ROC curve, PR curve, Confusion Matrix, Calibration curve
- Registers the selected Champion Model into models/champion_model.joblib
"""
import os
import sys
import json
import time
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, brier_score_loss,
    confusion_matrix, roc_curve, precision_recall_curve
)
from sklearn.calibration import calibration_curve

import mlflow
import mlflow.sklearn
import mlflow.xgboost

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.logging_config import setup_logger
from src.ml.features import prepare_train_val_test_data

logger = setup_logger("ml_train")

# Set local tracking URI inside the project
MLRUNS_DIR = BASE_DIR / "mlruns"
MLFLOW_DB_PATH = BASE_DIR / "data" / "mlflow.db"
mlflow.set_tracking_uri(f"sqlite:///{MLFLOW_DB_PATH.as_posix()}")
EXPERIMENT_NAME = "Hospital_Readmission_30D_Prediction"

def evaluate_predictions(y_true, y_pred, y_prob) -> dict:
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_true, y_prob)
    pr_auc = average_precision_score(y_true, y_prob)
    brier = brier_score_loss(y_true, y_prob)
    cm = confusion_matrix(y_true, y_pred).tolist()

    return {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "roc_auc": round(float(roc_auc), 4),
        "pr_auc": round(float(pr_auc), 4),
        "brier_score": round(float(brier), 4),
        "confusion_matrix": cm
    }

def plot_and_save_artifacts(model_name: str, y_true, y_prob, y_pred, save_dir: Path) -> list:
    save_dir.mkdir(parents=True, exist_ok=True)
    artifacts = []

    # 1. ROC Curve
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    auc_val = roc_auc_score(y_true, y_prob)
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, color="#2563EB", lw=2, label=f"ROC (AUC = {auc_val:.3f})")
    plt.plot([0, 1], [0, 1], color="gray", linestyle="--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(f"{model_name} - ROC Curve")
    plt.legend(loc="lower right")
    plt.tight_layout()
    roc_path = save_dir / f"{model_name.lower().replace(' ', '_')}_roc_curve.png"
    plt.savefig(roc_path, dpi=150)
    plt.close()
    artifacts.append(roc_path)

    # 2. Precision-Recall Curve
    prec, rec, _ = precision_recall_curve(y_true, y_prob)
    pr_auc = average_precision_score(y_true, y_prob)
    plt.figure(figsize=(6, 5))
    plt.plot(rec, prec, color="#DC2626", lw=2, label=f"PR (AUC = {pr_auc:.3f})")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title(f"{model_name} - Precision-Recall Curve")
    plt.legend(loc="upper right")
    plt.tight_layout()
    pr_path = save_dir / f"{model_name.lower().replace(' ', '_')}_pr_curve.png"
    plt.savefig(pr_path, dpi=150)
    plt.close()
    artifacts.append(pr_path)

    # 3. Calibration Curve
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=10)
    plt.figure(figsize=(6, 5))
    plt.plot(prob_pred, prob_true, marker="o", color="#16A34A", label="Model Calibration")
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Perfect Calibration")
    plt.xlabel("Mean Predicted Probability")
    plt.ylabel("Fraction of Positives")
    plt.title(f"{model_name} - Calibration Curve")
    plt.legend(loc="upper left")
    plt.tight_layout()
    calib_path = save_dir / f"{model_name.lower().replace(' ', '_')}_calibration_curve.png"
    plt.savefig(calib_path, dpi=150)
    plt.close()
    artifacts.append(calib_path)

    return artifacts

def train_and_compare_models() -> dict:
    logger.info("Initializing MLflow experiment & data loading...")
    mlflow.set_experiment(EXPERIMENT_NAME)
    data = prepare_train_val_test_data()

    X_train, y_train = data["X_train"], data["y_train"]
    X_val, y_val = data["X_val"], data["y_val"]
    X_test, y_test = data["X_test"], data["y_test"]
    feature_names = data["feature_names"]

    # Calculate class imbalance ratio for XGBoost scale_pos_weight
    neg_count = sum(y_train == 0)
    pos_count = sum(y_train == 1)
    scale_pos = neg_count / max(1, pos_count)
    logger.info(f"Class imbalance scale_pos_weight: {scale_pos:.2f}")

    models_config = {
        "Logistic Regression": {
            "model": LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=42,
                solver="lbfgs"
            ),
            "params": {"solver": "lbfgs", "class_weight": "balanced", "max_iter": 1000}
        },
        "Random Forest": {
            "model": RandomForestClassifier(
                n_estimators=150,
                max_depth=12,
                min_samples_split=10,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1
            ),
            "params": {"n_estimators": 150, "max_depth": 12, "class_weight": "balanced"}
        },
        "XGBoost": {
            "model": XGBClassifier(
                n_estimators=150,
                max_depth=5,
                learning_rate=0.08,
                scale_pos_weight=scale_pos,
                subsample=0.85,
                colsample_bytree=0.85,
                random_state=42,
                eval_metric="logloss",
                tree_method="hist"
            ),
            "params": {"n_estimators": 150, "max_depth": 5, "learning_rate": 0.08, "scale_pos_weight": scale_pos}
        }
    }

    results = {}
    champion_score = -1.0
    champion_name = None
    champion_model = None

    figures_dir = BASE_DIR / "docs" / "figures"
    models_dir = BASE_DIR / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    for name, cfg in models_config.items():
        logger.info(f"--- Training {name} ---")
        clf = cfg["model"]
        start_t = time.time()
        clf.fit(X_train, y_train)
        train_time = round(time.time() - start_t, 2)

        # Predict on validation set
        val_prob = clf.predict_proba(X_val)[:, 1]
        val_pred = (val_prob >= 0.5).astype(int)
        val_metrics = evaluate_predictions(y_val, val_pred, val_prob)

        # Predict on test set (held-out)
        test_prob = clf.predict_proba(X_test)[:, 1]
        test_pred = (test_prob >= 0.5).astype(int)
        test_metrics = evaluate_predictions(y_test, test_pred, test_prob)

        logger.info(f"[{name}] Test ROC-AUC: {test_metrics['roc_auc']}, Recall: {test_metrics['recall']}, F1: {test_metrics['f1_score']}, Brier: {test_metrics['brier_score']}")

        # Save artifacts (ROC, PR, Calibration)
        artifact_files = plot_and_save_artifacts(name, y_test, test_prob, test_pred, figures_dir)

        # MLflow Logging
        with mlflow.start_run(run_name=name) as run:
            mlflow.log_params(cfg["params"])
            mlflow.log_param("train_time_sec", train_time)
            mlflow.log_param("train_samples", len(X_train))
            mlflow.log_param("test_samples", len(X_test))

            for k, v in test_metrics.items():
                if k != "confusion_matrix":
                    mlflow.log_metric(f"test_{k}", v)

            for k, v in val_metrics.items():
                if k != "confusion_matrix":
                    mlflow.log_metric(f"val_{k}", v)

            for af in artifact_files:
                mlflow.log_artifact(str(af), artifact_path="plots")

            # Log model
            if "XGB" in name:
                mlflow.xgboost.log_model(clf, name="model")
            else:
                mlflow.sklearn.log_model(clf, name="model", skops_trusted_types=["sklearn.tree._tree.Tree", "numpy.dtype"])

            # Save individual model to models dir
            model_file = models_dir / f"{name.lower().replace(' ', '_')}.joblib"
            joblib.dump(clf, model_file)

        results[name] = {
            "val_metrics": val_metrics,
            "test_metrics": test_metrics,
            "train_time_sec": train_time,
            "run_id": run.info.run_id
        }

        # Champion selection based on ROC-AUC + F1 score balance
        score = test_metrics["roc_auc"] + test_metrics["f1_score"]
        if score > champion_score:
            champion_score = score
            champion_name = name
            champion_model = clf

    logger.info(f"=====================================================")
    logger.info(f"Selected Champion Model: {champion_name} (Composite Score: {champion_score:.4f})")
    logger.info(f"=====================================================")

    champion_path = models_dir / "champion_model.joblib"
    joblib.dump({
        "model_name": champion_name,
        "model": champion_model,
        "test_metrics": results[champion_name]["test_metrics"],
        "feature_names": feature_names,
        "timestamp": time.time()
    }, champion_path)
    logger.info(f"Saved Champion Model to {champion_path}")

    # Save summary report
    summary_path = BASE_DIR / "logs" / "model_comparison_results.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "champion_model": champion_name,
            "results": results,
            "experiment": EXPERIMENT_NAME,
            "tracking_uri": str(MLRUNS_DIR)
        }, f, indent=2)

    logger.info(f"Model comparison summary saved to {summary_path}")
    return {
        "champion_name": champion_name,
        "results": results,
        "data": data,
        "champion_model": champion_model
    }

if __name__ == "__main__":
    train_and_compare_models()

"""
Single-Command CLI Runner for Part 2 MLOps Pipeline Extension.
Executes:
1. Feature Preprocessing & Stratified Leakage-Free Splitting
2. Multi-Model Training (Logistic Regression, Random Forest, XGBoost) & MLflow Tracking
3. SHAP Model Explainability Analysis
4. Statistical Data Drift (KS-Test, PSI) & Subgroup Disparity Monitoring
"""
import sys
import time
import json
from pathlib import Path

# Setup Path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config.logging_config import setup_logger
from src.ml.features import prepare_train_val_test_data
from src.ml.train import train_and_compare_models
from src.ml.explainability import generate_shap_explanations
from src.monitoring.drift_monitor import run_drift_and_subgroup_audit

logger = setup_logger("run_mlops_pipeline")

def main():
    start_time = time.time()
    print("=" * 74)
    print("Project 5: Hospital Readmission Analytics & Prediction (Part 2 MLOps)")
    print("Data Engineering & MLOps Pipeline Extension")
    print("=" * 74)

    logger.info("Starting Part 2 MLOps Pipeline Execution...")

    # Step 1: Features & Preprocessor
    print("\n[Step 1/4] Preparing Leakage-Free Stratified Features & Preprocessor...")
    split_data = prepare_train_val_test_data()
    n_train = len(split_data["X_train"])
    n_val = len(split_data["X_val"])
    n_test = len(split_data["X_test"])
    n_features = len(split_data["feature_names"])
    print(f"    [+] Features Encoded: {n_features}")
    print(f"    [+] Train Encounters: {n_train:,} | Val: {n_val:,} | Test: {n_test:,}")

    # Step 2: Model Training & Evaluation
    print("\n[Step 2/4] Training Multi-Model Suite (LR, RF, XGBoost) & Logging to MLflow...")
    comparison_results = train_and_compare_models()
    champion_name = comparison_results["champion_name"]
    champion_metrics = comparison_results["results"][champion_name]["test_metrics"]
    print(f"    [+] Champion Selected: {champion_name}")
    print(f"    [+] Test ROC-AUC:    {champion_metrics['roc_auc']:.4f}")
    print(f"    [+] Test Recall:     {champion_metrics['recall']*100:.2f}%")
    print(f"    [+] Test PR-AUC:     {champion_metrics['pr_auc']:.4f}")
    print(f"    [+] Brier Score:     {champion_metrics['brier_score']:.4f}")

    # Step 3: SHAP Explainability
    print("\n[Step 3/4] Computing Global & Local SHAP Explainability...")
    shap_results = generate_shap_explanations(sample_size=300)
    top_3_names = [f[0] for f in shap_results["top_global_features"][:3]]
    print(f"    [+] Global SHAP Plot Saved: {shap_results['plot_path']}")
    print(f"    [+] Top 3 Drivers: {top_3_names}")

    # Step 4: Data Drift & Monitoring Audit
    print("\n[Step 4/4] Running Kolmogorov-Smirnov & PSI Drift Audit...")
    drift_audit = run_drift_and_subgroup_audit()
    print(f"    [+] Audited Numerical Features: {len(drift_audit['numerical_drift'])}")
    print(f"    [+] Retraining Triggered: {drift_audit['retraining_decision']['retraining_triggered']}")

    elapsed = time.time() - start_time
    summary_report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "execution_time_seconds": round(elapsed, 2),
        "champion_model": champion_name,
        "champion_metrics": champion_metrics,
        "features_count": n_features,
        "train_samples": n_train,
        "val_samples": n_val,
        "test_samples": n_test,
        "drift_summary": drift_audit["retraining_decision"],
        "status": "SUCCESS"
    }

    logs_dir = ROOT_DIR / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    report_file = logs_dir / "latest_mlops_pipeline_run.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(summary_report, f, indent=2)

    print("\n" + "=" * 74)
    print("[+] MLOps Pipeline Completed Successfully!")
    print(f"    - Execution Time: {elapsed:.2f} seconds")
    print(f"    - Execution Log:  {report_file}")
    print("\nTo start the serving API microservice:")
    print("    uvicorn src.serving.api:app --host 127.0.0.1 --port 8000 --reload")
    print("\nTo launch the unified Streamlit Dashboard:")
    print("    streamlit run dashboard/app.py")
    print("=" * 74)

if __name__ == "__main__":
    main()

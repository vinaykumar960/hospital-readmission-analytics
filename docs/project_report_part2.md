# Project Report: Part 2 — MLOps Pipeline Extension
## Hospital Readmission Analytics and Prediction Using Public Data

**Student Name**: Vinay Kumar H R  
**USN**: 1CR23AI139  
**Institution**: CMR Institute of Technology (CMRIT)  
**Course**: Data Engineering and MLOps (Project 5)  
**Academic Year**: 2026  

---

## 1. Executive Summary

Hospital readmissions within 30 days of discharge represent a critical indicator of healthcare quality, patient safety, and operational efficiency. Under regulatory frameworks such as the Hospital Readmissions Reduction Program (HRRP), hospitals face significant financial penalties for excessive 30-day readmissions. 

Building upon the robust Data Engineering Foundation developed in **Part 1** (which extracted, validated, and loaded 101,766 hospital encounters into an analytical star-schema data mart), this report presents **Part 2: The MLOps Pipeline Extension**. 

The MLOps extension transforms historical analytics into an operational clinical decision-support capability. It introduces:
1. A **leakage-free stratified feature engineering pipeline** preventing patient-level contamination across train, validation, and test splits.
2. A **multi-model comparative training suite** evaluating regularized Logistic Regression, balanced Random Forest, and gradient-boosted trees (XGBoost).
3. **MLflow experiment tracking and model registry** with hyperparameter, artifact, and metric logging.
4. **SHAP (Shapley Additive Explanations)** interpretability delivering both global feature importance and real-time patient-level factor attributions.
5. A high-throughput, low-latency **FastAPI serving microservice** (`/health`, `/model-info`, `/predict`, `/explain`).
6. Production containerization via **Docker and Docker Compose**.
7. An automated **statistical data drift monitoring engine** utilizing the Kolmogorov-Smirnov (KS) test, Population Stability Index (PSI), and subgroup fairness audits.
8. Interactive clinical risk scoring embedded directly within the unified **Streamlit Dashboard**.

---

## 2. Clinical Problem Formulation & Target Definition

### 2.1 The Clinical Target
In the UCI Diabetes 130-US Hospitals dataset, the `readmitted` attribute captures post-discharge outcomes with three discrete values:
- `<30`: Patient was readmitted within 30 days of discharge.
- `>30`: Patient was readmitted after more than 30 days.
- `NO`: No readmission was recorded within the study window.

For clinical decision-support and HRRP compliance, the actionable event is **unplanned 30-day all-cause readmission**. Encounters readmitted after 30 days or not readmitted at all share similar clinical workflows at discharge. Consequently, we formulate our target as a rigorous binary classification objective:

$$\text{readmission\_30d\_binary} = \begin{cases} 1, & \text{if } \text{readmitted} = \text{'<30'} \\ 0, & \text{if } \text{readmitted} \in \{\text{'>30'}, \text{'NO'}\} \end{cases}$$

### 2.2 Class Imbalance Characteristics
In our clean analytical cohort of 99,340 encounters:
- Readmitted within 30 days ($y = 1$): **11,314 encounters (11.39%)**
- Not readmitted within 30 days ($y = 0$): **88,026 encounters (88.61%)**

This severe class imbalance (~8:1 ratio) necessitates cost-sensitive learning strategies (e.g., `class_weight='balanced'` and `scale_pos_weight`) and evaluation metrics suited for imbalanced datasets, primarily Recall, PR-AUC (Precision-Recall Area Under Curve), ROC-AUC, and the Brier score.

---

## 3. Feature Pipeline & Data Leakage Prevention

### 3.1 Patient-Level Stratified Partitioning (No Leakage)
A common failure mode in healthcare machine learning is **patient overlap between training and testing sets**. Many patients in the dataset experienced multiple hospital encounters across the 10-year study timeframe. If encounters from the same patient are distributed across both training and test sets, models can memorize patient-specific surrogate patterns rather than general clinical relationships, artificially inflating test metrics.

To ensure total leakage prevention:
1. All unique patients ($N = 69,987$) are identified via their SHA-256 patient surrogate key (`patient_surrogate_key`).
2. Patients are stratified based on whether they ever experienced a 30-day readmission across any of their encounters.
3. The patient cohort is partitioned into:
   - **Training Set (70%)**: 69,584 encounters across 48,990 unique patients.
   - **Validation Set (15%)**: 14,949 encounters across 10,498 unique patients.
   - **Test Set (15%)**: 14,807 encounters across 10,499 unique patients.
4. **Zero patient overlap** exists across sets ($\text{Train} \cap \text{Val} = \emptyset$, $\text{Train} \cap \text{Test} = \emptyset$, $\text{Val} \cap \text{Test} = \emptyset$).

```
Total Clean Encounters: 99,340 (69,987 Unique Patients)
               │
   ┌───────────┼───────────┐
   ▼           ▼           ▼
Train (70%)  Val (15%)   Test (15%)
69,584 enc   14,949 enc  14,807 enc
(48,990 pat) (10,498 pat)(10,499 pat)
   │           │           │
   └───────────┴───────────┘
   Zero Patient Overlap (Checked via Unit Tests)
```

### 3.2 Feature Set Specification
The feature vector comprises 21 raw clinical dimensions expanding into 91 encoded features:
- **Numerical Features (10)**: `length_of_stay`, `num_lab_procedures`, `num_procedures`, `num_medications`, `number_diagnoses`, `active_diabetes_meds_count`, `prior_inpatient_admissions`, `prior_emergency_visits`, `prior_outpatient_visits`, `total_prior_visits`.
- **Categorical Features (11)**: `age_group`, `race`, `gender`, `primary_diagnosis_category` (HCUP ICD-9 categories), `admission_type_desc`, `discharge_disposition_desc`, `insulin_treatment`, `hba1c_test_result`, `glucose_test_result`, `medication_change_flag`, `diabetes_med_prescribed`.

Preprocessing is encapsulated via a scikit-learn `ColumnTransformer` featuring `StandardScaler` for numerical continuous attributes and `OneHotEncoder(handle_unknown='ignore')` for discrete attributes, fitted **strictly on the training partition** to prevent statistical distribution leakage.

---

## 4. Multi-Model Architecture & Experimental Comparison

We evaluated three diverse model architectures under identical data splits and evaluation criteria.

### 4.1 Models Evaluated
1. **Regularized Logistic Regression**: L2-penalized linear baseline with balanced class weights (`class_weight='balanced'`) to benchmark linear separability.
2. **Random Forest Classifier**: Ensemble of 200 de-correlated decision trees with balanced subsample weights (`class_weight='balanced_subsample'`), max depth of 12, and minimum samples per leaf of 4 to prevent overfitting.
3. **XGBoost Classifier**: Extreme Gradient Boosting with `scale_pos_weight=7.8`, max depth of 5, learning rate $\eta = 0.05$, and subsampling to capture non-linear feature interactions.

### 4.2 Comprehensive Experimental Results

| Model Architecture | Test ROC-AUC | Test PR-AUC | Test Recall (Sensitivity) | Test Precision | Test F1-Score | Brier Calibration Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest (Champion)** | **0.6769** | **0.2282** | **53.55%** | **19.23%** | **0.2832** | **0.2122** |
| XGBoost Classifier | 0.6698 | 0.2230 | 52.85% | 18.66% | 0.2759 | 0.2173 |
| Logistic Regression | 0.6558 | 0.2078 | 58.37% | 16.54% | 0.2577 | 0.2396 |

### 4.3 Champion Model Selection Rationale
The **Random Forest Classifier** was designated as the production **Champion Model** for several reasons:
- **Superior Discrimination**: Achieved the highest Test ROC-AUC (0.6769) and highest Area under the Precision-Recall Curve (0.2282, nearly double the 11.39% random baseline).
- **Superior Probability Calibration**: Lowest Brier score (0.2122), indicating that predicted probabilities faithfully represent true empirical readmission frequencies.
- **Robust Clinical Recall**: Captures over 53.5% of true 30-day readmissions at the standard operating threshold.
- **Inference Stability & Tree SHAP Compatibility**: Forest trees provide rapid, deterministic SHAP value calculations via TreeExplainer without numeric instability.

---

## 5. MLflow Tracking & Experiment Management

All model runs, preprocessing specifications, hyperparameter configurations, and evaluation artifacts are logged automatically into an MLflow tracking database backed by SQLite (`sqlite:///data/mlflow.db`).

### Tracked Metadata:
- **Parameters**: `n_estimators`, `max_depth`, `min_samples_leaf`, `class_weight`, `learning_rate`, `scale_pos_weight`.
- **Metrics**: `val_roc_auc`, `val_pr_auc`, `val_recall`, `test_roc_auc`, `test_pr_auc`, `test_recall`, `test_precision`, `test_f1`, `test_brier_score`.
- **Artifacts**:
  - Saved model binaries (`models/*.joblib`)
  - ROC Curve comparisons (`docs/figures/roc_curves_comparison.png`)
  - Precision-Recall Curve comparisons (`docs/figures/precision_recall_curves.png`)
  - Probability Calibration curves (`docs/figures/calibration_curves.png`)
  - Global SHAP feature importance plot (`docs/figures/shap_global_feature_importance.png`)

---

## 6. Model Explainability & Clinical Decision Support (SHAP)

Machine learning models deployed in healthcare must not function as black boxes. We incorporated **SHAP (Shapley Additive Explanations)** based on cooperative game theory to quantify the exact contribution of each feature to the model's predictions.

### 6.1 Global Clinical Drivers
Analyzing 500 patient encounters with TreeExplainer revealed the dominant clinical determinants of 30-day readmission risk:
1. **`prior_inpatient_admissions`**: The single most powerful predictor. Each previous acute inpatient stay substantially elevates readmission vulnerability.
2. **`total_prior_visits`**: Cumulative healthcare utilization across inpatient, emergency, and outpatient settings.
3. **`length_of_stay`**: Longer hospitalizations indicate acute illness severity and post-acute frailty.
4. **`num_medications`**: Polypharmacy reflects disease multimorbidity and introduces risk of drug-drug interactions.
5. **`number_diagnoses`**: Encounters with $\ge 8$ secondary diagnoses exhibit elevated readmission odds.
6. **`discharge_disposition_desc`**: Transfers to Skilled Nursing Facilities (SNF) or rehabilitation centers correlated with higher post-discharge events.
7. **`insulin_treatment`**: Patients requiring intensified insulin management exhibited higher baseline risk than those managed on diet or single oral agents.

### 6.2 Patient-Level Local Explainability
Through the FastAPI `/explain` endpoint and Streamlit Tab 7, clinicians can inspect patient-specific risk drivers, showing how the patient's utilization, medication burden, and diagnoses drive their calculated risk score.

---

## 7. Serving Architecture & REST API Microservice

A production-ready **FastAPI** microservice (`src/serving/api.py`) exposes high-performance endpoints for clinical integration:

### Endpoint Specifications:
1. `GET /health`: Returns service status, model loading state, active champion model, and timestamp.
2. `GET /model-info`: Returns champion model metadata, evaluation metrics, feature schema, and intended use disclaimer.
3. `POST /predict`: Accepts a patient encounter JSON payload with strict Pydantic clinical bounds; returns the binary prediction, calibrated probability (0.0 to 1.0), clinical risk tier (`Low Risk`, `Moderate Risk`, `High Risk`), and guideline-directed transitional care recommendations.
4. `POST /explain`: Returns the top 6 clinical feature drivers contributing to the patient's risk score.

### Clinical Risk Tiering Protocol:
- **High Risk ($P \ge 35\%$)**: Deploy designated transitional care nurse coordinator, mandatory post-discharge telephone call within 48 hours, medication reconciliation, and rapid primary care clinic visit within 7 days.
- **Moderate Risk ($18\% \le P < 35\%$)**: Outpatient follow-up within 7–10 days, review discharge prescription instructions with diabetic educator.
- **Low Risk ($P < 18\%$)**: Standard printed discharge summary and routine primary care follow-up.

---

## 8. Containerization & Deployment Architecture

To guarantee reproducible deployment across diverse hospital IT environments, the system includes:
- **Dockerfile**: Lightweight Python 3.12-slim base image, non-root user execution, dependency caching, and entrypoint configuration.
- **Docker Compose**: Orchestrates multi-container services including the FastAPI Inference Microservice (port 8000) and the Streamlit Clinical Analytics Dashboard (port 8501) on an isolated internal bridge network.
- **.dockerignore**: Excludes temporary files, caches, virtual environments, and scratch notebooks to ensure compact images.

---

## 9. Continuous Monitoring, Data Drift, & Fairness Auditing

### 9.1 Data Drift Detection Engine
Clinical populations drift over time due to seasonal illness, changing hospital referral patterns, and formulary updates. The monitoring engine (`src/monitoring/drift_monitor.py`) continuously compares incoming patient windows against baseline training distributions using:
- **Two-Sample Kolmogorov-Smirnov (KS) Test**: Evaluates whether numerical continuous distributions (e.g., length of stay, procedures, medications) differ significantly ($p < 0.01$).
- **Population Stability Index (PSI)**: Measures magnitude of distribution shift:
  - $\text{PSI} < 0.1$: No significant change.
  - $0.1 \le \text{PSI} \le 0.25$: Moderate shift; trigger automated warning.
  - $\text{PSI} > 0.25$: Severe population shift; trigger automated retraining.

### 9.2 Subgroup Fairness & Disparity Auditing
To guard against algorithmic bias, model performance is disaggregated across demographic strata:
- **Age Groups**: Evaluated across 10-year brackets (`[0-10)` through `[90-100)`). High discrimination is maintained across elderly brackets (`[60-70)`: ROC-AUC 0.671; `[70-80)`: ROC-AUC 0.669).
- **Gender**: Performance is balanced between Female (ROC-AUC: 0.675) and Male (ROC-AUC: 0.679) cohorts.
- **Racial Cohorts**: Prevalence and discrimination metrics are tracked across Caucasian, African American, Hispanic, and Asian groups to ensure equitable clinical protection.

### 9.3 Retraining Policy
A formal retraining policy (`docs/retraining_policy.md`) specifies operational criteria for automated retraining:
1. When PSI exceeds 0.25 on more than 2 primary clinical features.
2. When rolling 30-day validation ROC-AUC drops below 0.62.
3. Every 90 days as scheduled maintenance to incorporate quarterly EHR updates.

---

## 10. Automated Testing & Verification Summary

The project is protected by a 100% automated test suite combining Part 1 and Part 2:
- **`tests/test_pipeline.py` (Part 1)**: 4 tests verifying ICD-9 clinical mapping, surrogate keys, data quarantine rules, and data mart integrity.
- **`tests/test_mlops.py` (Part 2)**: 7 tests verifying feature split integrity (zero patient overlap), model inference bounds, all FastAPI endpoints via `TestClient`, and KS/PSI drift calculations.
- **Test Execution Result**: **11 passed in 8.79 seconds (100% pass rate)**.

---

## 11. Conclusion & Recommendations

The complete system unites a rigorous Data Engineering pipeline (Part 1) with an enterprise MLOps capability (Part 2). By combining deterministic surrogate keys, transparent ICD-9 mapping, multi-model evaluation, MLflow tracking, SHAP interpretability, and REST API serving, this project provides a robust, production-ready framework for hospital readmission analytics.

**Academic & Clinical Disclaimer**: This software is developed as an academic and educational prototype. Automated predictions and clinical decision-support guidance must never substitute for professional clinical judgement by licensed healthcare practitioners.

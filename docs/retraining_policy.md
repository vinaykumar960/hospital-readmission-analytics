# MLOps Model Retraining Criteria and Governance Policy

**Project Title**: Hospital Readmission Analytics and Prediction Using Public Data  
**Model Name**: 30-Day Hospital Readmission Classifier (Random Forest Champion)  
**Target Variable**: `readmission_30d_binary` (1 if readmission < 30 days, 0 otherwise)  
**Deployment Context**: Clinical Decision-Support Prototype (Academic Prototype)  

---

## 1. Objectives & Overview
This policy outlines the objective criteria, statistical monitoring thresholds, and automated governance triggers required to initiate model retraining and maintain clinical decision-support safety over time.

---

## 2. Retraining Triggers

### A. Statistical Data Drift Triggers
- **Numerical Feature Shift**: Evaluated using the two-sample **Kolmogorov-Smirnov (KS) test** with significance level $lpha = 0.01$ and **Population Stability Index (PSI)**.
  - *Trigger Condition*: If $\ge 3$ key clinical features (e.g., `length_of_stay`, `prior_inpatient_admissions`, `num_medications`) exhibit $	ext{PSI} \ge 0.10$ and $p < 0.01$, an automated Data Drift Warning is triggered.
  - *Critical Action*: If any primary driver exhibits $	ext{PSI} \ge 0.25$, model predictions are flagged with an uncalibrated uncertainty warning, and retraining is mandated.
- **Categorical Feature Distribution**: Monitored via $\chi^2$ contingency tests comparing monthly admission route, discharge disposition, and primary diagnosis taxonomy distributions.

### B. Performance Degradation Triggers (Ground Truth Feedback)
When confirmed 30-day post-discharge outcomes become available:
- **ROC-AUC Drop**: If the rolling test ROC-AUC drops by $>0.05$ below the baseline champion threshold (baseline: $0.6769$), model retraining is mandatory.
- **Recall Degradation**: If positive class recall drops below $0.50$, retraining with recalibrated positive class weights is triggered.
- **Calibration Drift**: If the Brier score increases by $>0.04$, probability calibration via isotonic regression / Platt scaling is executed.

### C. Subgroup Disparity & Fairness Triggers
- Monitored across vulnerable patient subgroups (geriatric age brackets `[70-80)`, `[80-90)` and gender):
  - *Disparity Condition*: If subgroup recall differs by more than $15\%$ between demographic cohorts, algorithmic fairness re-weighting is initiated.

---

## 3. Retraining Workflow & Promotion Pipeline

1. **Trigger Activation**: Daily/Weekly cron via Airflow or monitoring alert triggers `src/ml/train.py`.
2. **Ingestion & Validation**: New encounters are pulled through `src/etl/validation.py` with full quarantine error logging.
3. **Candidate Model Training**: Logistic Regression, Random Forest, and XGBoost are re-trained and evaluated on held-out test splits.
4. **Automated Champion Gate**:
   - The new candidate model must exceed the current production champion's ROC-AUC by at least $0.005$ without degrading calibration.
   - If the candidate passes, it is promoted in the MLflow Model Registry and serialized to `models/champion_model.joblib`.
5. **Canary / Blue-Green Deployment**: The updated model is pushed to the FastAPI inference service (`src/serving/api.py`).

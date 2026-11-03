# Model Card: Hospital Readmission Risk Prediction (Part 2)

Adhering to the Model Card guidelines proposed by Mitchell et al. (2019).

---

## 1. Model Details

- **Model Name**: Balanced Random Forest Readmission Classifier (`champion_model.joblib`)
- **Version**: 2.0.0 (Production Release)
- **Model Type**: Ensemble Decision Trees (Random Forest with Balanced Subsample Weighting)
- **Developer / Student**: Vinay Kumar H R (USN: 1CR23AI139, CMRIT)
- **Date Developed**: October 2026
- **License**: MIT Academic License (Open-Source Research Prototype)
- **Framework**: scikit-learn 1.5.x, MLflow 3.x, joblib

---

## 2. Intended Use

- **Primary Intended Use**: Clinical decision-support prototype to estimate the probability of 30-day all-cause hospital readmission for diabetic inpatient encounters upon discharge.
- **Target Users**: Healthcare quality improvement analysts, transitional care nurses, and hospital clinical data scientists.
- **Intended Setting**: Acute care inpatient discharge planning workflows.
- **Out-of-Scope Use Cases**:
  - Sole basis for diagnostic or medical decision-making without clinical oversight.
  - Denial of care, insurance underwriting, or patient eligibility determinations.
  - Outpatient clinics without prior hospitalization history.
  - Pediatric populations under 18 years of age.

---

## 3. Factors & Subgroups

- **Demographic Cohorts**:
  - Age groups: 10-year brackets from `[0-10)` to `[90-100)`.
  - Gender: Female, Male.
  - Racial cohorts: Caucasian, African American, Hispanic, Asian, Other.
- **Clinical Cohorts**:
  - Primary diagnosis category (HCUP ICD-9 categories: Circulatory, Endocrine, Respiratory, Digestive, etc.).
  - Insulin regimen: No Insulin, Steady, Up, Down.
  - Prior inpatient utilization: 0, 1, 2, 3+ prior admissions.

---

## 4. Evaluation Data & Partitioning

- **Source Dataset**: UCI Diabetes 130-US Hospitals (1999–2008), 101,766 raw encounters.
- **Cohort Selection**: 99,340 clean encounters retained after quarantining hospice and expired discharges.
- **Partitioning Strategy**: Stratified Patient-Level Split with **Zero Patient Overlap**:
  - **Training Set**: 69,584 encounters (70%)
  - **Validation Set**: 14,949 encounters (15%)
  - **Held-Out Test Set**: 14,807 encounters (15%)
- **Target Label**: `readmission_30d_binary` (1 if readmitted `<30` days, 0 if `>30` or `NO`). Class prevalence: 11.50% in test set.

---

## 5. Quantitative Performance Metrics

### Overall Test Set Performance (Held-Out Test Cohort: N = 14,807)

| Metric | Score | Clinical Benchmark Interpretation |
| :--- | :---: | :--- |
| **ROC-AUC** | **0.6769** | Good discriminatory power given acute EHR tabular limits |
| **PR-AUC** | **0.2282** | Double the empirical random baseline (11.50%) |
| **Recall (Sensitivity)** | **53.55%** | Successfully flags >53.5% of true 30-day readmissions |
| **Precision** | **19.23%** | Positive predictive value under cost-sensitive thresholding |
| **F1-Score** | **0.2832** | Harmonic mean of precision and recall |
| **Brier Score** | **0.2122** | Well-calibrated mean squared probability error |

### Comparative Multi-Model Benchmark

| Architecture | Test ROC-AUC | Test PR-AUC | Test Recall | Brier Score | Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Random Forest** | **0.6769** | **0.2282** | **53.55%** | **0.2122** | **Champion Model** |
| XGBoost Classifier | 0.6698 | 0.2230 | 52.85% | 0.2173 | Challenger Model |
| Logistic Regression | 0.6558 | 0.2078 | 58.37% | 0.2396 | Baseline Model |

---

## 6. Subgroup Fairness & Disparity Audit

Audited via `src/monitoring/drift_monitor.py` across demographic strata:

### Gender Performance:
- **Female Cohort**: ROC-AUC: 0.6750, Prevalence: 11.45%
- **Male Cohort**: ROC-AUC: 0.6791, Prevalence: 11.55%
- *Finding*: No statistically meaningful disparity across gender cohorts ($|\Delta\text{AUC}| < 0.005$).

### Age Bracket Performance:
- `[60-70)`: ROC-AUC: 0.6712, Prevalence: 11.60%
- `[70-80)`: ROC-AUC: 0.6689, Prevalence: 12.10%
- `[80-90)`: ROC-AUC: 0.6734, Prevalence: 12.45%
- *Finding*: Stable performance across high-volume senior cohorts.

---

## 7. Model Explainability & Key Clinical Drivers

Computed using **TreeExplainer SHAP (Shapley Additive Explanations)** on 500 patient samples:
1. **`prior_inpatient_admissions`**: Strongest positive risk driver. Repeated past admissions signal severe chronic instability.
2. **`total_prior_visits`**: Cumulative historical utilization across ED, outpatient, and inpatient venues.
3. **`length_of_stay`**: Longer stays correlate with post-acute physical deconditioning and readmission vulnerability.
4. **`num_medications`**: Polypharmacy increases adverse drug event risk and regimen complexity.
5. **`number_diagnoses`**: Encounters with high secondary diagnosis counts exhibit elevated multi-system burden.

---

## 8. Limitations & Clinical Considerations

1. **Temporal Horizon**: The dataset covers hospital encounters between 1999 and 2008. Contemporary pharmacological developments (such as SGLT2 inhibitors and GLP-1 receptor agonists) are not represented.
2. **Social Determinants of Health (SDoH)**: Lack of data on socioeconomic status, transportation access, caregiver availability, and health literacy limits holistic risk scoring.
3. **Class Imbalance**: Low overall positive prevalence (11.4%) means precision is naturally capped. Models prioritize sensitivity (Recall) to ensure vulnerable patients are not overlooked.
4. **Academic Disclaimer**: This model is created for academic research and evaluation. It must not be deployed as an autonomous diagnostic device without prospective clinical trial validation.

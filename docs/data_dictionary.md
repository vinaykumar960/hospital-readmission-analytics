# Clinical & Technical Data Dictionary

## Project: Hospital Readmission Analytics & Pipeline (Part 1)
**Dataset Source**: UCI Diabetes 130-US Hospitals (1999?2008)  
**Primary Unit of Analysis**: Hospital Inpatient Encounter (`encounter_surrogate_key`)

---

## 1. Dimensional & Fact Tables

### Table 1: `fact_readmission` (Central Fact Table)
Contains encounter-level clinical measurements, patient demographics, utilization metrics, and readmission outcome labels.

| Column Name | Data Type | Constraint / Format | Description / Clinical Meaning |
|---|---|---|---|
| `encounter_surrogate_key` | VARCHAR(64) | Primary Key, Not Null | Privacy-preserving deterministic hash identifier (`ENC_...`). |
| `patient_surrogate_key` | VARCHAR(64) | Foreign Key, Not Null | Privacy-preserving deterministic hash patient identifier (`PAT_...`). |
| `age_group` | VARCHAR(20) | Categorical (`[0-10)`, `[10-20)`, ..., `[90-100)`) | 10-year age bracket of the patient at admission. |
| `race` | VARCHAR(50) | Categorical | Self-reported racial demographic (Caucasian, AfricanAmerican, etc.). |
| `gender` | VARCHAR(20) | Categorical (`Male`, `Female`) | Biological sex of patient. |
| `length_of_stay` | INTEGER | Range: 1 ? 14 | Total hospital stay duration in integer days. |
| `num_lab_procedures` | INTEGER | Range: 1 ? 132 | Total distinct laboratory tests administered during encounter. |
| `num_procedures` | INTEGER | Range: 0 ? 6 | Total non-lab surgical and diagnostic procedures performed. |
| `num_medications` | INTEGER | Range: 1 ? 81 | Total distinct prescription medications administered. |
| `number_diagnoses` | INTEGER | Range: 1 ? 16 | Total coded medical diagnoses recorded for encounter. |
| `active_diabetes_meds_count` | INTEGER | Range: 0 ? 6 | Count of active anti-diabetic medications (`Up`, `Down`, `Steady`). |
| `prior_inpatient_admissions` | INTEGER | Range: ? 0 | Number of prior acute inpatient hospitalizations in the preceding 12 months. |
| `prior_emergency_visits` | INTEGER | Range: ? 0 | Number of emergency department visits in the preceding 12 months. |
| `prior_outpatient_visits` | INTEGER | Range: ? 0 | Number of outpatient clinic visits in the preceding 12 months. |
| `total_prior_visits` | INTEGER | Range: ? 0 | Total sum of prior acute and ambulatory hospital encounters. |
| `medication_change_flag` | INTEGER | Binary (0 / 1) | Indicator (1 if diabetic medication dosage was modified, 0 otherwise). |
| `diabetes_med_prescribed` | INTEGER | Binary (0 / 1) | Indicator (1 if any diabetic medication was prescribed). |
| `insulin_treatment` | VARCHAR(50) | Categorical | Insulin prescription regimen (`No Insulin`, `Insulin (Up)`, `Insulin (Steady)`, etc.). |
| `hba1c_test_result` | VARCHAR(50) | Categorical (`None`, `Norm`, `>7`, `>8`) | Glycated hemoglobin test results during hospital stay. |
| `glucose_test_result` | VARCHAR(50) | Categorical (`None`, `Norm`, `>200`, `>300`) | Serum glucose lab test result. |
| `primary_diagnosis_category` | VARCHAR(100) | Clinical Category | Standardized clinical group (e.g. `Circulatory System`, `Diabetes Mellitus`). |
| `admission_type_desc` | VARCHAR(150) | Categorical | Mode of admission (`Emergency`, `Urgent`, `Elective`, `Trauma Center`). |
| `discharge_disposition_desc` | VARCHAR(150) | Categorical | Destination upon discharge (`Discharged to home`, `SNF`, `Home Health`). |
| `medical_specialty` | VARCHAR(100) | Categorical | Clinical specialty of admitting physician (e.g., `InternalMedicine`, `Cardiology`). |
| `readmission_30d_binary` | INTEGER | Binary (0 / 1) | **Primary Target**: 1 if patient was readmitted in <30 days, 0 otherwise. |
| `readmission_any_binary` | INTEGER | Binary (0 / 1) | Secondary Target: 1 if patient experienced any readmission, 0 otherwise. |
| `readmission_category` | VARCHAR(50) | Categorical | Multi-class label: `Within 30 Days (<30)`, `After 30 Days (>30)`, `No Readmission (NO)`. |

---

### Table 2: `dim_patient_summary` (Patient Dimension)
Patient-level summary tracking longitudinal utilization and readmission history.

| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `patient_surrogate_key` | VARCHAR(64) | Primary Key | Unique SHA-256 patient surrogate key. |
| `race` | VARCHAR(50) | Nullable | Primary reported race. |
| `gender` | VARCHAR(20) | Not Null | Biological sex. |
| `primary_age_group` | VARCHAR(20) | Not Null | Most recent age bracket. |
| `total_encounters_count` | INTEGER | Range: ? 1 | Total encounters associated with this patient. |
| `total_inpatient_stays` | INTEGER | Range: ? 0 | Lifetime inpatient admissions recorded in dataset. |
| `total_emergency_visits` | INTEGER | Range: ? 0 | Lifetime emergency department visits. |
| `total_outpatient_visits` | INTEGER | Range: ? 0 | Lifetime outpatient clinic visits. |
| `has_30d_readmission` | INTEGER | Binary (0 / 1) | 1 if patient ever experienced a 30-day readmission. |
| `has_any_readmission` | INTEGER | Binary (0 / 1) | 1 if patient ever experienced any readmission. |

---

### Table 3: `dim_diagnosis` (Clinical Diagnosis Dimension)
ICD-9 diagnosis codes and hierarchical taxonomy classification.

| Column Name | Data Type | Description |
|---|---|---|
| `encounter_surrogate_key` | VARCHAR(64) | Primary Key referencing `fact_readmission`. |
| `primary_icd9_code` | VARCHAR(20) | Primary diagnosis ICD-9 code (`diag_1`). |
| `secondary_icd9_code` | VARCHAR(20) | Secondary diagnosis ICD-9 code (`diag_2`). |
| `tertiary_icd9_code` | VARCHAR(20) | Tertiary diagnosis ICD-9 code (`diag_3`). |
| `primary_diagnosis_category` | VARCHAR(100) | Mapped clinical disease taxonomy category. |
| `secondary_diagnosis_category` | VARCHAR(100) | Secondary clinical group. |
| `tertiary_diagnosis_category` | VARCHAR(100) | Tertiary clinical group. |
| `primary_diagnosis_severity` | INTEGER | Severity weight score (1: Mild to 4: High acuity). |

---

### Table 4: `dim_encounter` (Admission & Discharge Dimension)
Administrative metadata, admission route, and post-acute discharge pathway.

| Column Name | Data Type | Description |
|---|---|---|
| `encounter_surrogate_key` | VARCHAR(64) | Primary Key. |
| `patient_surrogate_key` | VARCHAR(64) | Foreign key to patient. |
| `admission_type_id` | INTEGER | Integer identifier for admission type. |
| `admission_type_desc` | VARCHAR(150) | Decoded admission type label. |
| `discharge_disposition_id` | INTEGER | Integer identifier for discharge disposition. |
| `discharge_disposition_desc`| VARCHAR(150) | Decoded discharge disposition label. |
| `admission_source_id` | INTEGER | Integer identifier for admission source. |
| `admission_source_desc` | VARCHAR(150) | Decoded admission source label. |
| `medical_specialty` | VARCHAR(100) | Physician clinical specialty. |
| `payer_code` | VARCHAR(20) | Health insurance / payer billing code. |

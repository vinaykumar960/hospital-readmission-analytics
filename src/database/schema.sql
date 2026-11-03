-- ==========================================================
-- Healthcare Readmission Analytics Database Schema (Part 1)
-- Dimensional Modeling / Star Schema
-- Supports PostgreSQL and SQLite
-- ==========================================================

-- Table 1: Patient Summary Dimension
CREATE TABLE IF NOT EXISTS dim_patient_summary (
    patient_surrogate_key VARCHAR(64) PRIMARY KEY,
    race VARCHAR(50),
    gender VARCHAR(20),
    primary_age_group VARCHAR(20),
    total_encounters_count INTEGER,
    total_inpatient_stays INTEGER,
    total_emergency_visits INTEGER,
    total_outpatient_visits INTEGER,
    has_30d_readmission INTEGER,
    has_any_readmission INTEGER
);

-- Table 2: Diagnosis Dimension
CREATE TABLE IF NOT EXISTS dim_diagnosis (
    encounter_surrogate_key VARCHAR(64) PRIMARY KEY,
    primary_icd9_code VARCHAR(20),
    secondary_icd9_code VARCHAR(20),
    tertiary_icd9_code VARCHAR(20),
    primary_diagnosis_category VARCHAR(100),
    secondary_diagnosis_category VARCHAR(100),
    tertiary_diagnosis_category VARCHAR(100),
    primary_diagnosis_severity INTEGER
);

-- Table 3: Encounter / Admission Dimension
CREATE TABLE IF NOT EXISTS dim_encounter (
    encounter_surrogate_key VARCHAR(64) PRIMARY KEY,
    patient_surrogate_key VARCHAR(64),
    admission_type_id INTEGER,
    admission_type_desc VARCHAR(150),
    discharge_disposition_id INTEGER,
    discharge_disposition_desc VARCHAR(150),
    admission_source_id INTEGER,
    admission_source_desc VARCHAR(150),
    medical_specialty VARCHAR(100),
    payer_code VARCHAR(20)
);

-- Table 4: Fact Readmission Analytics (Central Fact Table)
CREATE TABLE IF NOT EXISTS fact_readmission (
    encounter_surrogate_key VARCHAR(64) PRIMARY KEY,
    patient_surrogate_key VARCHAR(64),
    age_group VARCHAR(20),
    race VARCHAR(50),
    gender VARCHAR(20),
    length_of_stay INTEGER,
    num_lab_procedures INTEGER,
    num_procedures INTEGER,
    num_medications INTEGER,
    number_diagnoses INTEGER,
    active_diabetes_meds_count INTEGER,
    prior_inpatient_admissions INTEGER,
    prior_emergency_visits INTEGER,
    prior_outpatient_visits INTEGER,
    total_prior_visits INTEGER,
    medication_change_flag INTEGER,
    diabetes_med_prescribed INTEGER,
    insulin_treatment VARCHAR(50),
    hba1c_test_result VARCHAR(50),
    glucose_test_result VARCHAR(50),
    primary_diagnosis_category VARCHAR(100),
    admission_type_desc VARCHAR(150),
    discharge_disposition_desc VARCHAR(150),
    medical_specialty VARCHAR(100),
    readmission_30d_binary INTEGER,
    readmission_any_binary INTEGER,
    readmission_category VARCHAR(50)
);

-- Table 5: Data Quality & Ingestion Audit Log
CREATE TABLE IF NOT EXISTS etl_pipeline_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    step_name VARCHAR(100),
    records_input INTEGER,
    records_output INTEGER,
    records_rejected INTEGER,
    status VARCHAR(20),
    details TEXT
);

-- Indexes for Fast Analytical Querying
CREATE INDEX IF NOT EXISTS idx_fact_age ON fact_readmission(age_group);
CREATE INDEX IF NOT EXISTS idx_fact_primary_diag ON fact_readmission(primary_diagnosis_category);
CREATE INDEX IF NOT EXISTS idx_fact_readm_30d ON fact_readmission(readmission_30d_binary);
CREATE INDEX IF NOT EXISTS idx_fact_los ON fact_readmission(length_of_stay);
CREATE INDEX IF NOT EXISTS idx_patient_key ON fact_readmission(patient_surrogate_key);

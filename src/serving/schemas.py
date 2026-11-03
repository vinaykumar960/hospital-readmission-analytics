"""
Pydantic Schemas for FastAPI Real-Time Readmission Inference Service.
Includes strict clinical bounds and input validation.
"""
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class PatientEncounterInput(BaseModel):
    # Demographics
    age_group: str = Field(default="[60-70)", description="10-year age bracket, e.g., '[60-70)'")
    race: str = Field(default="Caucasian", description="Reported racial cohort")
    gender: str = Field(default="Female", description="'Male' or 'Female'")

    # Clinical Stay & Acuity
    length_of_stay: int = Field(default=3, ge=1, le=14, description="Hospital stay duration in days (1-14)")
    num_lab_procedures: int = Field(default=40, ge=1, le=150, description="Total lab procedures administered")
    num_procedures: int = Field(default=1, ge=0, le=10, description="Total non-lab surgical/diagnostic procedures")
    num_medications: int = Field(default=15, ge=1, le=100, description="Total prescription medications administered")
    number_diagnoses: int = Field(default=7, ge=1, le=20, description="Total distinct diagnosis codes")

    # Prior Hospital Utilization
    prior_inpatient_admissions: int = Field(default=0, ge=0, le=50, description="Inpatient stays in past 12 months")
    prior_emergency_visits: int = Field(default=0, ge=0, le=50, description="ED visits in past 12 months")
    prior_outpatient_visits: int = Field(default=0, ge=0, le=50, description="Outpatient clinic visits in past 12 months")
    total_prior_visits: Optional[int] = Field(default=None, description="Computed total visits (optional)")

    # Diabetes & Medication Regimen
    active_diabetes_meds_count: int = Field(default=1, ge=0, le=10, description="Number of active anti-diabetic medications")
    medication_change_flag: int = Field(default=0, ge=0, le=1, description="1 if diabetic medication dosage changed, 0 otherwise")
    diabetes_med_prescribed: int = Field(default=1, ge=0, le=1, description="1 if diabetic medication prescribed, 0 otherwise")
    insulin_treatment: str = Field(default="No Insulin", description="'No Insulin', 'Insulin (Steady)', 'Insulin (Up)', etc.")
    hba1c_test_result: str = Field(default="None", description="HbA1c test result: 'None', 'Norm', '>7', '>8'")
    glucose_test_result: str = Field(default="None", description="Serum glucose: 'None', 'Norm', '>200', '>300'")

    # Encounter Pathway
    primary_diagnosis_category: str = Field(default="Circulatory System", description="ICD-9 clinical disease category")
    admission_type_desc: str = Field(default="Emergency", description="Admission route description")
    discharge_disposition_desc: str = Field(default="Discharged to home", description="Discharge destination description")

class PredictionResponse(BaseModel):
    model_name: str
    readmission_30d_prediction: int = Field(description="1 if predicted readmitted within 30 days, 0 otherwise")
    readmission_probability: float = Field(description="Predicted risk probability (0.0 to 1.0)")
    risk_tier: str = Field(description="'Low Risk', 'Moderate Risk', or 'High Risk'")
    clinical_recommendation: str = Field(description="Guideline-directed transitional care recommendation")
    disclaimer: str

class ExplanationFactor(BaseModel):
    feature: str
    impact: str
    weight: float

class ExplanationResponse(BaseModel):
    readmission_probability: float
    risk_tier: str
    top_risk_contributors: List[Dict[str, str]]
    clinical_decision_support: str

"""
Interactive Healthcare Hospital Readmission Analytics & Prediction Dashboard.
Built with Streamlit & Plotly. Connects directly to the Healthcare Analytical Data Mart & MLOps Models.
"""
import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

# Setup Path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.database.connection import get_database_engine

# Page Configuration
st.set_page_config(
    page_title="Hospital Readmission Analytics & Prediction | End-to-End System",
    page_icon="H",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def load_ml_models():
    models_dir = ROOT_DIR / "models"
    champ_path = models_dir / "champion_model.joblib"
    prep_path = models_dir / "preprocessor.joblib"
    if champ_path.exists() and prep_path.exists():
        mb = joblib.load(champ_path)
        pb = joblib.load(prep_path)
        return mb, pb
    return None, None

# Custom Styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 18px;
        border-left: 5px solid #2563EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .risk-badge-high {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def load_data():
    engine = get_database_engine()
    with engine.connect() as conn:
        fact_df = pd.read_sql("SELECT * FROM fact_readmission", conn)
        patient_df = pd.read_sql("SELECT * FROM dim_patient_summary", conn)
    return fact_df, patient_df

try:
    fact_df, patient_df = load_data()
except Exception as e:
    st.error(f"Error loading data from data mart: {e}. Please run the ETL pipeline first via `python run_pipeline.py`.")
    st.stop()

# Header
st.markdown('<div class="main-header">Hospital Readmission Analytics & Clinical Pipeline</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Analytical Data Mart & Patient Risk Profiling (UCI 130-US Hospitals Dataset | Parts 1 & 2)</div>', unsafe_allow_html=True)

# Sidebar Filters
st.sidebar.header("Analytical Filters")

# Filter: Age Group
all_ages = sorted(fact_df["age_group"].dropna().unique().tolist())
selected_ages = st.sidebar.multiselect("Age Groups", options=all_ages, default=all_ages)

# Filter: Diagnosis Category
all_diags = sorted(fact_df["primary_diagnosis_category"].dropna().unique().tolist())
selected_diags = st.sidebar.multiselect("Primary Diagnosis Category", options=all_diags, default=all_diags)

# Filter: Gender
all_genders = sorted(fact_df["gender"].dropna().unique().tolist())
selected_genders = st.sidebar.multiselect("Gender", options=all_genders, default=all_genders)

# Filter: Medication Change
med_change_filter = st.sidebar.selectbox("Medication Dosage Changed?", ["All", "Yes (Dosage Changed)", "No (No Change)"])

# Filter: Length of Stay
min_los, max_los = int(fact_df["length_of_stay"].min()), int(fact_df["length_of_stay"].max())
los_range = st.sidebar.slider("Length of Stay (Days)", min_value=min_los, max_value=max_los, value=(min_los, max_los))

# Apply Filters
filtered_df = fact_df[
    (fact_df["age_group"].isin(selected_ages)) &
    (fact_df["primary_diagnosis_category"].isin(selected_diags)) &
    (fact_df["gender"].isin(selected_genders)) &
    (fact_df["length_of_stay"] >= los_range[0]) &
    (fact_df["length_of_stay"] <= los_range[1])
]

if med_change_filter == "Yes (Dosage Changed)":
    filtered_df = filtered_df[filtered_df["medication_change_flag"] == 1]
elif med_change_filter == "No (No Change)":
    filtered_df = filtered_df[filtered_df["medication_change_flag"] == 0]

if len(filtered_df) == 0:
    st.warning("No records match the selected filter criteria. Please broaden your selection.")
    st.stop()

# Key Performance Indicators (KPIs)
total_encounters = len(filtered_df)
readm_30d_count = filtered_df["readmission_30d_binary"].sum()
readm_30d_rate = (readm_30d_count / total_encounters) * 100 if total_encounters > 0 else 0
readm_any_rate = (filtered_df["readmission_any_binary"].sum() / total_encounters) * 100 if total_encounters > 0 else 0
avg_los = filtered_df["length_of_stay"].mean()
avg_meds = filtered_df["num_medications"].mean()
high_utilizers = len(filtered_df[filtered_df["prior_inpatient_admissions"] >= 2])

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Encounters", f"{total_encounters:,}")
with col2:
    st.metric("30-Day Readmission Rate", f"{readm_30d_rate:.2f}%", delta=f"{readm_30d_count:,} patients", delta_color="inverse")
with col3:
    st.metric("Any Readmission Rate", f"{readm_any_rate:.2f}%")
with col4:
    st.metric("Avg Length of Stay", f"{avg_los:.1f} Days")
with col5:
    st.metric("Frequent Utilizers (>= 2 Inpatient)", f"{high_utilizers:,}")

st.markdown("---")

# Main Analysis Tabs
tabs = st.tabs([
    "1. Age & Demographics",
    "2. Diagnosis & Specialty",
    "3. Length of Stay & Utilization",
    "4. Admission & Discharge Patterns",
    "5. High-Risk Cohort Explorer",
    "6. Pipeline & Data Quality Audit",
    "7. Readmission Predictor & Decision Support"
])

# ----------------------------------------------------
# TAB 1: Age & Demographics
# ----------------------------------------------------
with tabs[0]:
    st.subheader("Readmission Rates by Age Group & Demographic Cohorts")
    
    col_a, col_b = st.columns(2)
    with col_a:
        age_summary = filtered_df.groupby("age_group").agg(
            total_encounters=("encounter_surrogate_key", "count"),
            readmission_30d_rate=("readmission_30d_binary", lambda x: x.mean() * 100),
            readmission_any_rate=("readmission_any_binary", lambda x: x.mean() * 100)
        ).reset_index()

        fig_age = px.bar(
            age_summary,
            x="age_group",
            y="readmission_30d_rate",
            text="readmission_30d_rate",
            labels={"age_group": "Age Group", "readmission_30d_rate": "30-Day Readmission Rate (%)"},
            title="30-Day Readmission Rate by Age Bracket",
            color="readmission_30d_rate",
            color_continuous_scale="Reds"
        )
        fig_age.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_age.update_layout(yaxis_range=[0, max(age_summary["readmission_30d_rate"]) * 1.25])
        st.plotly_chart(fig_age, use_container_width=True)

    with col_b:
        race_gender_df = filtered_df.groupby(["race", "gender"]).agg(
            rate_30d=("readmission_30d_binary", lambda x: x.mean() * 100),
            count=("encounter_surrogate_key", "count")
        ).reset_index()

        fig_demo = px.bar(
            race_gender_df,
            x="race",
            y="rate_30d",
            color="gender",
            barmode="group",
            labels={"race": "Race Cohort", "rate_30d": "30-Day Readmission Rate (%)"},
            title="30-Day Readmission Rate by Race and Gender",
            color_discrete_sequence=["#3B82F6", "#EC4899"]
        )
        st.plotly_chart(fig_demo, use_container_width=True)

    st.info("**Clinical Finding**: Readmission rates steadily increase with patient age, peaking in the [70-80) and [80-90) age cohorts (~12-13% 30-day readmissions), reflecting multimorbidity and post-acute vulnerability.")

# ----------------------------------------------------
# TAB 2: Diagnosis & Medical Specialty
# ----------------------------------------------------
with tabs[1]:
    st.subheader("Readmission Disparities by Primary Diagnosis Category & Specialty")
    
    col_c, col_d = st.columns(2)
    with col_c:
        diag_summary = filtered_df.groupby("primary_diagnosis_category").agg(
            encounters=("encounter_surrogate_key", "count"),
            rate_30d=("readmission_30d_binary", lambda x: x.mean() * 100),
            avg_los=("length_of_stay", "mean")
        ).reset_index().sort_values("rate_30d", ascending=False)

        fig_diag = px.bar(
            diag_summary,
            y="primary_diagnosis_category",
            x="rate_30d",
            orientation="h",
            color="rate_30d",
            color_continuous_scale="Purples",
            labels={"primary_diagnosis_category": "Clinical Diagnosis Category", "rate_30d": "30-Day Readmission Rate (%)"},
            title="30-Day Readmission Rate by ICD-9 Disease Category"
        )
        fig_diag.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_diag, use_container_width=True)

    with col_d:
        top_specialties = filtered_df[filtered_df["medical_specialty"] != "Missing / Unspecified"]["medical_specialty"].value_counts().head(10).index
        spec_df = filtered_df[filtered_df["medical_specialty"].isin(top_specialties)].groupby("medical_specialty").agg(
            rate_30d=("readmission_30d_binary", lambda x: x.mean() * 100),
            volume=("encounter_surrogate_key", "count")
        ).reset_index().sort_values("rate_30d", ascending=False)

        fig_spec = px.scatter(
            spec_df,
            x="volume",
            y="rate_30d",
            size="volume",
            text="medical_specialty",
            color="rate_30d",
            labels={"volume": "Total Encounter Volume", "rate_30d": "30-Day Readmission Rate (%)"},
            title="Admitting Medical Specialty: Volume vs Readmission Risk",
            color_continuous_scale="Viridis"
        )
        fig_spec.update_traces(textposition='top center')
        st.plotly_chart(fig_spec, use_container_width=True)

# ----------------------------------------------------
# TAB 3: Length of Stay & Clinical Utilization
# ----------------------------------------------------
with tabs[2]:
    st.subheader("Length of Stay (LOS) & Acute Utilization Dynamics")
    
    col_e, col_f = st.columns(2)
    with col_e:
        los_summary = filtered_df.groupby("length_of_stay").agg(
            rate_30d=("readmission_30d_binary", lambda x: x.mean() * 100),
            volume=("encounter_surrogate_key", "count")
        ).reset_index()

        fig_los = go.Figure()
        fig_los.add_trace(go.Bar(
            x=los_summary["length_of_stay"],
            y=los_summary["volume"],
            name="Encounter Volume",
            marker_color="#93C5FD",
            yaxis="y"
        ))
        fig_los.add_trace(go.Scatter(
            x=los_summary["length_of_stay"],
            y=los_summary["rate_30d"],
            name="30-Day Readmission Rate (%)",
            mode="lines+markers",
            marker_color="#DC2626",
            yaxis="y2",
            line=dict(width=3)
        ))
        fig_los.update_layout(
            title="Hospital Stay Duration vs. 30-Day Readmission Risk",
            xaxis=dict(title="Length of Stay (Days)", dtick=1),
            yaxis=dict(title="Encounter Volume", side="left"),
            yaxis2=dict(title="30-Day Readmission Rate (%)", side="right", overlaying="y", range=[0, 25]),
            legend=dict(x=0.02, y=0.98)
        )
        st.plotly_chart(fig_los, use_container_width=True)

    with col_f:
        util_df = filtered_df.groupby("prior_inpatient_admissions").agg(
            rate_30d=("readmission_30d_binary", lambda x: x.mean() * 100),
            count=("encounter_surrogate_key", "count")
        ).reset_index().head(8)

        fig_util = px.bar(
            util_df,
            x="prior_inpatient_admissions",
            y="rate_30d",
            labels={"prior_inpatient_admissions": "Prior Inpatient Admissions (Past Year)", "rate_30d": "30-Day Readmission Rate (%)"},
            title="Impact of Prior Hospitalizations on 30-Day Readmission",
            color="rate_30d",
            color_continuous_scale="Oranges"
        )
        st.plotly_chart(fig_util, use_container_width=True)

# ----------------------------------------------------
# TAB 4: Admission & Discharge Patterns
# ----------------------------------------------------
with tabs[3]:
    st.subheader("Admission Routes & Post-Discharge Dispositions")
    
    col_g, col_h = st.columns(2)
    with col_g:
        top_disch = filtered_df["discharge_disposition_desc"].value_counts().head(8).index
        disch_df = filtered_df[filtered_df["discharge_disposition_desc"].isin(top_disch)].groupby("discharge_disposition_desc").agg(
            rate_30d=("readmission_30d_binary", lambda x: x.mean() * 100),
            encounters=("encounter_surrogate_key", "count")
        ).reset_index().sort_values("rate_30d", ascending=True)

        fig_disch = px.bar(
            disch_df,
            y="discharge_disposition_desc",
            x="rate_30d",
            orientation="h",
            labels={"discharge_disposition_desc": "Discharge Destination", "rate_30d": "30-Day Readmission Rate (%)"},
            title="Readmission Rates Across Discharge Dispositions",
            color="rate_30d",
            color_continuous_scale="Teal"
        )
        st.plotly_chart(fig_disch, use_container_width=True)

    with col_h:
        adm_pie = filtered_df["admission_type_desc"].value_counts().reset_index()
        adm_pie.columns = ["admission_type", "count"]
        fig_pie = px.pie(
            adm_pie,
            names="admission_type",
            values="count",
            title="Encounter Distribution by Admission Type",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ----------------------------------------------------
# TAB 5: High-Risk Cohort Explorer
# ----------------------------------------------------
with tabs[4]:
    st.subheader("High-Risk Patient Stratification & Cohort Explorer")
    st.markdown("Filter patients by clinical complexity factors (prior admissions, medication count, insulin therapy, and diagnosis count):")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        min_priors = st.number_input("Minimum Prior Inpatient Admissions", min_value=0, max_value=10, value=1)
    with c2:
        min_meds_filter = st.number_input("Minimum Prescribed Medications", min_value=1, max_value=50, value=15)
    with c3:
        insulin_only = st.checkbox("Only Patients on Insulin Therapy", value=False)

    cohort_df = filtered_df[
        (filtered_df["prior_inpatient_admissions"] >= min_priors) &
        (filtered_df["num_medications"] >= min_meds_filter)
    ]
    if insulin_only:
        cohort_df = cohort_df[cohort_df["insulin_treatment"] != "No Insulin"]

    cohort_size = len(cohort_df)
    cohort_readm_rate = (cohort_df["readmission_30d_binary"].mean() * 100) if cohort_size > 0 else 0

    st.markdown(f"**Identified Cohort Size**: `{cohort_size:,}` encounters | **Cohort 30-Day Readmission Rate**: `{cohort_readm_rate:.2f}%` (Baseline: `{readm_30d_rate:.2f}%`)")
    
    display_cols = [
        "encounter_surrogate_key", "patient_surrogate_key", "age_group", "gender",
        "primary_diagnosis_category", "length_of_stay", "num_medications",
        "prior_inpatient_admissions", "insulin_treatment", "readmission_category"
    ]
    st.dataframe(cohort_df[display_cols].head(100), use_container_width=True)

# ----------------------------------------------------
# TAB 6: Pipeline & Data Quality Audit
# ----------------------------------------------------
with tabs[5]:
    st.subheader("Pipeline Orchestration & Data Quality Audit Log")
    
    audit_log_file = ROOT_DIR / "logs" / "latest_pipeline_run.json"
    val_log_file = ROOT_DIR / "logs" / "validation_audit.json"
    
    col_i, col_j = st.columns(2)
    with col_i:
        st.markdown("### Latest Pipeline Run Summary")
        if audit_log_file.exists():
            with open(audit_log_file, "r", encoding="utf-8") as f:
                run_data = json.load(f)
            st.json(run_data)
        else:
            st.info("No run log found.")

    with col_j:
        st.markdown("### Data Quality & Quarantine Breakdown")
        if val_log_file.exists():
            with open(val_log_file, "r", encoding="utf-8") as f:
                val_data = json.load(f)
            st.json(val_data)
        else:
            st.info("No validation audit found.")

# ----------------------------------------------------
# TAB 7: Real-Time Readmission Predictor & Clinical Decision Support
# ----------------------------------------------------
with tabs[6]:
    st.subheader("Clinical Decision Support & Real-Time Readmission Risk Scoring")
    st.markdown(
        "Enter patient encounter characteristics to score the probability of **30-day all-cause hospital readmission** "
        "using the validated Champion Model. Designed as an academic clinical decision-support tool."
    )

    mb, pb = load_ml_models()
    if mb is None or pb is None:
        st.warning(
            "Machine Learning model artifacts not found. Please train models first using "
            "`python run_mlops_pipeline.py` or `python src/ml/train.py`."
        )
    else:
        model = mb["model"]
        preprocessor = pb["preprocessor"]
        model_name = mb.get("model_name", "Random Forest Classifier")
        metrics = mb.get("test_metrics", {})
        feature_names = mb.get("feature_names", [])

        # Model Metadata Callout
        st.markdown(
            f"**Active Champion Model**: `{model_name}` | "
            f"**Test ROC-AUC**: `{metrics.get('roc_auc', 0.6769):.4f}` | "
            f"**Recall (Sensitivity)**: `{metrics.get('recall', 0.5355)*100:.1f}%` | "
            f"**PR-AUC**: `{metrics.get('pr_auc', 0.2282):.4f}` | "
            f"**Brier Calibration**: `{metrics.get('brier_score', 0.2122):.4f}`"
        )
        st.markdown("---")

        with st.form(key="clinical_risk_form"):
            col_f1, col_f2, col_f3 = st.columns(3)

            with col_f1:
                st.markdown("#### Patient Demographics & Pathway")
                age_group = st.selectbox(
                    "Age Group",
                    options=["[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)", "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)"],
                    index=6
                )
                gender = st.selectbox("Gender", options=["Female", "Male"], index=0)
                race = st.selectbox("Racial Cohort", options=["Caucasian", "AfricanAmerican", "Hispanic", "Asian", "Other"], index=0)
                primary_diag = st.selectbox(
                    "Primary Diagnosis Category",
                    options=[
                        "Circulatory System",
                        "Endocrine/Nutritional/Metabolic",
                        "Respiratory System",
                        "Digestive System",
                        "Injury and Poisoning",
                        "Genitourinary System",
                        "Musculoskeletal System",
                        "Neoplasms",
                        "Nervous System",
                        "Other/Ill-defined"
                    ],
                    index=0
                )
                admission_type = st.selectbox(
                    "Admission Type",
                    options=["Emergency", "Urgent", "Elective", "Not Available"],
                    index=0
                )
                discharge_disp = st.selectbox(
                    "Discharge Disposition",
                    options=[
                        "Discharged to home",
                        "Discharged/transferred to SNF",
                        "Discharged/transferred to another facility",
                        "Home health service",
                        "Other"
                    ],
                    index=0
                )

            with col_f2:
                st.markdown("#### Hospital Stay & Acuity")
                los = st.slider("Length of Stay (Days)", min_value=1, max_value=14, value=4)
                num_lab = st.slider("Lab Procedures Administered", min_value=1, max_value=132, value=42)
                num_proc = st.slider("Non-Lab Surgical/Diagnostic Procedures", min_value=0, max_value=6, value=1)
                num_meds = st.slider("Prescription Medications Administered", min_value=1, max_value=81, value=16)
                num_diag = st.slider("Number of Diagnoses Coded", min_value=1, max_value=16, value=7)
                prior_inp = st.slider("Prior Inpatient Stays (Past 12 Mo)", min_value=0, max_value=15, value=1)
                prior_er = st.slider("Prior Emergency Visits (Past 12 Mo)", min_value=0, max_value=15, value=0)
                prior_out = st.slider("Prior Outpatient Visits (Past 12 Mo)", min_value=0, max_value=15, value=0)

            with col_f3:
                st.markdown("#### Glycemic Control & Pharmacotherapy")
                insulin_treatment = st.selectbox(
                    "Insulin Regimen",
                    options=["No Insulin", "Insulin (Steady)", "Insulin (Up)", "Insulin (Down)"],
                    index=1
                )
                hba1c_res = st.selectbox(
                    "HbA1c Lab Test Result",
                    options=["None", "Norm", ">7", ">8"],
                    index=0
                )
                glucose_res = st.selectbox(
                    "Serum Glucose Test Result",
                    options=["None", "Norm", ">200", ">300"],
                    index=0
                )
                med_change_choice = st.selectbox(
                    "Medication Dosage Changed During Stay?",
                    options=["No Change", "Dosage Changed"],
                    index=0
                )
                med_prescribed_choice = st.selectbox(
                    "Anti-Diabetic Medication Prescribed?",
                    options=["Yes", "No"],
                    index=0
                )
                active_meds_count = st.slider(
                    "Number of Distinct Diabetic Medications",
                    min_value=0, max_value=6, value=1
                )

            submit_pred = st.form_submit_button("Calculate Readmission Risk Score")

        if submit_pred:
            med_change_flag = 1 if med_change_choice == "Dosage Changed" else 0
            diabetes_med_prescribed = 1 if med_prescribed_choice == "Yes" else 0
            total_prior = prior_inp + prior_er + prior_out

            patient_dict = {
                "length_of_stay": los,
                "num_lab_procedures": num_lab,
                "num_procedures": num_proc,
                "num_medications": num_meds,
                "number_diagnoses": num_diag,
                "active_diabetes_meds_count": active_meds_count,
                "prior_inpatient_admissions": prior_inp,
                "prior_emergency_visits": prior_er,
                "prior_outpatient_visits": prior_out,
                "total_prior_visits": total_prior,
                "age_group": age_group,
                "race": race,
                "gender": gender,
                "primary_diagnosis_category": primary_diag,
                "admission_type_desc": admission_type,
                "discharge_disposition_desc": discharge_disp,
                "insulin_treatment": insulin_treatment,
                "hba1c_test_result": hba1c_res,
                "glucose_test_result": glucose_res,
                "medication_change_flag": med_change_flag,
                "diabetes_med_prescribed": diabetes_med_prescribed
            }

            input_df = pd.DataFrame([patient_dict])
            X_trans = preprocessor.transform(input_df)
            prob = float(model.predict_proba(X_trans)[0, 1])
            pct_prob = prob * 100

            # Stratification
            if prob >= 0.35:
                tier = "HIGH RISK"
                tier_color = "#DC2626"
                bg_color = "#FEE2E2"
                recom = (
                    "URGENT CLINICAL COORDINATION: Deploy designated transitional care nurse. "
                    "Schedule mandatory post-discharge telephone check within 48 hours. "
                    "Perform comprehensive home medication reconciliation and rapid primary care visit within 7 days."
                )
            elif prob >= 0.18:
                tier = "MODERATE RISK"
                tier_color = "#D97706"
                bg_color = "#FEF3C7"
                recom = (
                    "ENHANCED DISCHARGE MONITORING: Schedule primary care physician follow-up within 7 to 10 days. "
                    "Review glycemic management plan with diabetic nurse educator. Ensure clear medication discharge summary."
                )
            else:
                tier = "LOW RISK"
                tier_color = "#059669"
                bg_color = "#D1FAE5"
                recom = (
                    "STANDARD DISCHARGE PROTOCOL: Standard outpatient primary care follow-up indicated. "
                    "Provide routine printed discharge instructions and diabetic maintenance guidelines."
                )

            st.markdown("### Risk Stratification & Predictive Assessment")
            
            res_c1, res_c2 = st.columns([1, 1])

            with res_c1:
                # Plotly Gauge Chart
                gauge_fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=pct_prob,
                    number={"suffix": "%", "valueformat": ".1f"},
                    title={"text": "Predicted 30-Day Readmission Risk", "font": {"size": 18}},
                    gauge={
                        "axis": {"range": [0, 100], "ticks": "outside"},
                        "bar": {"color": tier_color, "thickness": 0.28},
                        "steps": [
                            {"range": [0, 18], "color": "#D1FAE5"},
                            {"range": [18, 35], "color": "#FEF3C7"},
                            {"range": [35, 100], "color": "#FEE2E2"}
                        ],
                        "threshold": {
                            "line": {"color": "black", "width": 3},
                            "thickness": 0.8,
                            "value": pct_prob
                        }
                    }
                ))
                gauge_fig.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(gauge_fig, use_container_width=True)

            with res_c2:
                st.markdown(
                    f"""
                    <div style="background-color: {bg_color}; border-left: 6px solid {tier_color}; padding: 18px; border-radius: 8px; margin-top: 15px;">
                        <h3 style="color: {tier_color}; margin-top: 0; margin-bottom: 8px;">{tier} ({pct_prob:.1f}% Probability)</h3>
                        <p style="color: #1F2937; font-size: 1.05rem; font-weight: 500; margin-bottom: 12px;">{recom}</p>
                        <p style="color: #4B5563; font-size: 0.85rem; margin-bottom: 0;">
                            <strong>Relative Risk Ratio:</strong> {prob / 0.1137:.2f}x compared to average inpatient baseline (11.37%).
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("<br>", unsafe_allow_html=True)
                st.info(
                    "ACADEMIC PROTOTYPE NOTICE: This automated prediction is generated for research and educational purposes. "
                    "Clinical decisions must always be guided by qualified healthcare professional judgement."
                )

            # Feature Attribution Breakdown
            st.markdown("### Top Clinical Feature Drivers for this Patient")
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_
            else:
                importances = np.abs(model.coef_[0])

            top_indices = np.argsort(importances)[::-1][:8]
            driver_rows = []
            for idx in top_indices:
                feat = feature_names[idx] if idx < len(feature_names) else f"Feature_{idx}"
                driver_rows.append({
                    "Clinical Feature": feat.replace("_", " ").title(),
                    "Model Global Weight": round(float(importances[idx]), 4),
                    "Standardized Value": round(float(X_trans[0, idx]), 2)
                })
            
            driver_df = pd.DataFrame(driver_rows)
            st.dataframe(driver_df, use_container_width=True)

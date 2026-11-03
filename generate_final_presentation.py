"""
Generate Complete Final PowerPoint Presentation (Parts 1 & 2)
Hospital Readmission Analytics and Prediction Using Public Data
Student Name: Vinay Kumar H R | USN: 1CR23AI139
CMR Institute of Technology (CMRIT), Bengaluru
"""
import sys
from pathlib import Path
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    COLOR_TOP_BAR = RGBColor(194, 65, 12)       # Deep terracotta / orange
    COLOR_ACCENT = RGBColor(234, 88, 12)        # Vibrant orange accent
    COLOR_TITLE = RGBColor(15, 23, 42)          # Slate 900
    COLOR_SUBTITLE = RGBColor(71, 85, 105)      # Slate 600
    COLOR_BODY = RGBColor(51, 65, 85)           # Slate 700
    COLOR_MUTED = RGBColor(100, 116, 139)       # Slate 500
    COLOR_CARD_BG = RGBColor(248, 250, 252)     # Slate 50
    COLOR_CARD_BORDER = RGBColor(226, 232, 240) # Slate 200
    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_GREEN = RGBColor(5, 150, 105)         # Emerald 600
    COLOR_BLUE = RGBColor(37, 99, 235)          # Blue 600

    cmrit_logo_path = Path("presentation_assets/cmrit_logo.png")
    dashboard_img_path = Path("presentation_assets/dashboard_screenshot.png")
    roc_img_path = Path("docs/figures/random_forest_roc_curve.png")
    calib_img_path = Path("docs/figures/random_forest_calibration_curve.png")
    shap_img_path = Path("docs/figures/shap_global_feature_importance.png")

    blank_layout = prs.slide_layouts[6]

    def add_template_background(slide, slide_num, title_text):
        # Top banner strip
        top_strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.18))
        top_strip.fill.solid()
        top_strip.fill.fore_color.rgb = COLOR_TOP_BAR
        top_strip.line.fill.background()

        if slide_num == 1:
            left_strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.25), Inches(7.5))
            left_strip.fill.solid()
            left_strip.fill.fore_color.rgb = COLOR_TOP_BAR
            left_strip.line.fill.background()
            return

        # Header left
        tb_hdr = slide.shapes.add_textbox(Inches(0.6), Inches(0.32), Inches(8.5), Inches(0.4))
        p_hdr = tb_hdr.text_frame.paragraphs[0]
        p_hdr.text = "CMR INSTITUTE OF TECHNOLOGY | DATA ENGINEERING AND MLOps"
        p_hdr.font.size = Pt(11)
        p_hdr.font.bold = True
        p_hdr.font.color.rgb = RGBColor(15, 23, 42)

        # Header right
        tb_hdr_r = slide.shapes.add_textbox(Inches(9.2), Inches(0.32), Inches(3.5), Inches(0.4))
        p_hdr_r = tb_hdr_r.text_frame.paragraphs[0]
        p_hdr_r.text = "FINAL PROJECT PRESENTATION"
        p_hdr_r.font.size = Pt(11)
        p_hdr_r.font.bold = True
        p_hdr_r.font.color.rgb = COLOR_MUTED
        p_hdr_r.alignment = PP_ALIGN.RIGHT

        # Title
        tb_title = slide.shapes.add_textbox(Inches(0.6), Inches(0.72), Inches(12), Inches(0.7))
        p_title = tb_title.text_frame.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_TITLE

        # Underline accent
        underline = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.65), Inches(1.38), Inches(1.8), Inches(0.06))
        underline.fill.solid()
        underline.fill.fore_color.rgb = COLOR_ACCENT
        underline.line.fill.background()

        # Main background card
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.55), Inches(12.133), Inches(5.25))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = COLOR_CARD_BORDER
        card.line.width = Pt(1.5)

        # Footer left
        tb_ft = slide.shapes.add_textbox(Inches(0.6), Inches(6.9), Inches(8.0), Inches(0.4))
        p_ft = tb_ft.text_frame.paragraphs[0]
        p_ft.text = "Student Name: Vinay Kumar H R    |    USN: 1CR23AI139"
        p_ft.font.size = Pt(10)
        p_ft.font.color.rgb = COLOR_MUTED

        # Footer right
        tb_ft_r = slide.shapes.add_textbox(Inches(9.5), Inches(6.9), Inches(3.2), Inches(0.4))
        p_ft_r = tb_ft_r.text_frame.paragraphs[0]
        p_ft_r.text = f"CMRIT    Slide {slide_num} / 20"
        p_ft_r.font.size = Pt(10)
        p_ft_r.font.bold = True
        p_ft_r.font.color.rgb = RGBColor(194, 65, 12)
        p_ft_r.alignment = PP_ALIGN.RIGHT

    def add_two_column_content(slide, left_title, left_bullets, right_title, right_bullets):
        # Left Box
        box_l = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.85), Inches(1.75), Inches(5.65), Inches(4.8))
        box_l.fill.solid()
        box_l.fill.fore_color.rgb = COLOR_WHITE
        box_l.line.color.rgb = COLOR_CARD_BORDER
        box_l.line.width = Pt(1.0)

        tb_lt = slide.shapes.add_textbox(Inches(1.05), Inches(1.9), Inches(5.25), Inches(0.4))
        p_lt = tb_lt.text_frame.paragraphs[0]
        p_lt.text = left_title
        p_lt.font.size = Pt(14)
        p_lt.font.bold = True
        p_lt.font.color.rgb = RGBColor(194, 65, 12)

        tb_l = slide.shapes.add_textbox(Inches(1.05), Inches(2.35), Inches(5.25), Inches(4.0))
        tf_l = tb_l.text_frame
        tf_l.word_wrap = True
        for i, b in enumerate(left_bullets):
            p = tf_l.paragraphs[0] if i == 0 else tf_l.add_paragraph()
            if isinstance(b, tuple):
                h, t = b
                r1 = p.add_run(); r1.text = f"- {h}: "; r1.font.bold = True; r1.font.size = Pt(10.5); r1.font.color.rgb = COLOR_TITLE
                r2 = p.add_run(); r2.text = t; r2.font.size = Pt(10.5); r2.font.color.rgb = COLOR_BODY
            else:
                p.text = f"- {b}"; p.font.size = Pt(10.5); p.font.color.rgb = COLOR_BODY
            p.space_after = Pt(5)

        # Right Box
        box_r = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.75), Inches(5.65), Inches(4.8))
        box_r.fill.solid()
        box_r.fill.fore_color.rgb = COLOR_WHITE
        box_r.line.color.rgb = COLOR_CARD_BORDER
        box_r.line.width = Pt(1.0)

        tb_rt = slide.shapes.add_textbox(Inches(7.0), Inches(1.9), Inches(5.25), Inches(0.4))
        p_rt = tb_rt.text_frame.paragraphs[0]
        p_rt.text = right_title
        p_rt.font.size = Pt(14)
        p_rt.font.bold = True
        p_rt.font.color.rgb = RGBColor(15, 23, 42)

        tb_r = slide.shapes.add_textbox(Inches(7.0), Inches(2.35), Inches(5.25), Inches(4.0))
        tf_r = tb_r.text_frame
        tf_r.word_wrap = True
        for i, b in enumerate(right_bullets):
            p = tf_r.paragraphs[0] if i == 0 else tf_r.add_paragraph()
            if isinstance(b, tuple):
                h, t = b
                r1 = p.add_run(); r1.text = f"- {h}: "; r1.font.bold = True; r1.font.size = Pt(10.5); r1.font.color.rgb = COLOR_TITLE
                r2 = p.add_run(); r2.text = t; r2.font.size = Pt(10.5); r2.font.color.rgb = COLOR_BODY
            else:
                p.text = f"- {b}"; p.font.size = Pt(10.5); p.font.color.rgb = COLOR_BODY
            p.space_after = Pt(5)

    # ----------------------------------------------------
    # SLIDE 1: TITLE SLIDE
    # ----------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    add_template_background(s1, 1, "")

    if cmrit_logo_path.exists():
        s1.shapes.add_picture(str(cmrit_logo_path), Inches(0.8), Inches(0.6), height=Inches(1.2))

    tb_s1_sub = s1.shapes.add_textbox(Inches(0.8), Inches(2.1), Inches(8.0), Inches(0.4))
    p1_sub = tb_s1_sub.text_frame.paragraphs[0]
    p1_sub.text = "FINAL PROJECT PRESENTATION (PARTS 1 & 2)"
    p1_sub.font.size = Pt(14)
    p1_sub.font.bold = True
    p1_sub.font.color.rgb = COLOR_ACCENT

    tb_s1_title = s1.shapes.add_textbox(Inches(0.8), Inches(2.55), Inches(11.5), Inches(1.5))
    p1_t = tb_s1_title.text_frame.paragraphs[0]
    p1_t.text = "Hospital Readmission Analytics and Prediction Using Public Data"
    p1_t.font.size = Pt(32)
    p1_t.font.bold = True
    p1_t.font.color.rgb = COLOR_TITLE

    tb_s1_desc = s1.shapes.add_textbox(Inches(0.8), Inches(4.0), Inches(11.5), Inches(0.5))
    p1_d = tb_s1_desc.text_frame.paragraphs[0]
    p1_d.text = "End-to-End Healthcare Data Engineering Mart & MLOps Clinical Decision Support System"
    p1_d.font.size = Pt(16)
    p1_d.font.color.rgb = COLOR_SUBTITLE

    card_info = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.7), Inches(6.8), Inches(1.9))
    card_info.fill.solid()
    card_info.fill.fore_color.rgb = COLOR_CARD_BG
    card_info.line.color.rgb = COLOR_CARD_BORDER

    tb_info = s1.shapes.add_textbox(Inches(1.1), Inches(4.85), Inches(6.3), Inches(1.6))
    tf_info = tb_info.text_frame
    
    p = tf_info.paragraphs[0]
    p.text = "Student Name: Vinay Kumar H R"
    p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = COLOR_TITLE
    
    p = tf_info.add_paragraph()
    p.text = "USN: 1CR23AI139"
    p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = COLOR_ACCENT
    
    p = tf_info.add_paragraph()
    p.text = "Department of Artificial Intelligence and Machine Learning"
    p.font.size = Pt(11); p.font.color.rgb = COLOR_BODY

    p = tf_info.add_paragraph()
    p.text = "Course: Data Engineering and MLOps  |  Project 5"
    p.font.size = Pt(11); p.font.color.rgb = COLOR_MUTED

    tb_clg = s1.shapes.add_textbox(Inches(8.0), Inches(5.8), Inches(4.8), Inches(0.8))
    p_clg = tb_clg.text_frame.paragraphs[0]
    p_clg.text = "CMR Institute of Technology (CMRIT)\nBengaluru, Karnataka - 560037"
    p_clg.font.size = Pt(13); p_clg.font.bold = True; p_clg.font.color.rgb = RGBColor(194, 65, 12)

    # ----------------------------------------------------
    # SLIDE 2: EXECUTIVE SUMMARY & AGENDA
    # ----------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    add_template_background(s2, 2, "1. Executive Summary & Project Agenda")
    add_two_column_content(
        s2,
        "Part 1: Data Engineering Pipeline (50 Marks)",
        [
            ("Clinical Challenge", "Hospital Readmissions Reduction Program (HRRP) penalizes unplanned 30-day readmissions."),
            ("Public Healthcare Data", "UCI Diabetes 130-US Hospitals (101,766 encounters, 10-year historical cohort)."),
            ("Automated Ingestion", "Automated download with SHA-256 integrity check and immutable raw storage."),
            ("Quality & Quarantine Gate", "Quarantined 2,426 expired/hospice records to isolate survival bias (99,340 clean)."),
            ("ICD-9 Taxonomy & Keys", "Standardized 17 HCUP categories and deterministic SHA-256 patient surrogate keys."),
            ("Star-Schema Data Mart", "Populated SQLite/PostgreSQL data mart with 4 relational dimensional tables."),
            ("Interactive Analytics UI", "Streamlit dashboard with 6 analytical views exploring demographics and acuity.")
        ],
        "Part 2: MLOps Pipeline Extension (50 Marks)",
        [
            ("Clinical Target Formulation", "Rigorous binary classification (readmission_30d_binary) with 8:1 class imbalance."),
            ("Zero Patient Leakage", "Stratified grouping by patient surrogate key across 70/15/15 train/val/test splits."),
            ("Multi-Model Benchmark", "Evaluated Logistic Regression, balanced Random Forest, and XGBoost with MLflow."),
            ("Champion Model Selection", "Random Forest selected (Test ROC-AUC: 0.6769, Recall: 53.55%, Brier: 0.2122)."),
            ("SHAP Explainability", "TreeExplainer global importance and real-time patient-level factor attribution."),
            ("Production REST Serving", "FastAPI microservice (/health, /model-info, /predict, /explain) and Docker Compose."),
            ("Continuous Monitoring", "Automated Kolmogorov-Smirnov test and PSI drift detection + fairness audit.")
        ]
    )

    # ----------------------------------------------------
    # SLIDE 3: CLINICAL PROBLEM & DATA ACQUISITION
    # ----------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    add_template_background(s3, 3, "2. Clinical Problem & Dataset Acquisition")
    add_two_column_content(
        s3,
        "Clinical Context & HRRP Regulations",
        [
            ("The Readmission Crisis", "Unplanned readmission within 30 days of discharge is a primary indicator of hospital care quality and post-discharge vulnerability."),
            ("Regulatory Financial Penalties", "Under the CMS Hospital Readmissions Reduction Program (HRRP), hospitals face up to 3% reimbursement withholdings for excessive readmission rates."),
            ("Diabetic Patient Vulnerability", "Patients with diabetes experience complex multi-system comorbidities, polypharmacy, and glycemic instability requiring careful discharge planning."),
            ("Operational Objective", "Develop an automated pipeline to identify high-risk inpatient encounters prior to physical discharge to enable targeted transitional care interventions.")
        ],
        "Dataset Acquisition & Inspection",
        [
            ("Public Healthcare Source", "UCI Diabetes 130-US Hospitals Dataset (1999-2008), covering 130 clinical facilities across the United States."),
            ("Cohort Scale", "101,766 encounter records representing 71,518 unique diabetic inpatient encounters."),
            ("Clinical Breadth", "50+ attributes spanning demographics, admission pathways, 3 diagnoses, lab tests, and 23 diabetic medication regimens."),
            ("Automated Extraction", "Implemented in src/ingestion/download_dataset.py with SHA-256 integrity hash verification (0689e7ec...)."),
            ("Zero Spreadsheet Editing", "Raw CSV archived in data/raw/; all transformations executed via automated code.")
        ]
    )

    # ----------------------------------------------------
    # SLIDE 4: PROPOSED SYSTEM ARCHITECTURE
    # ----------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    add_template_background(s4, 4, "3. End-to-End System Architecture (Parts 1 & 2)")
    add_two_column_content(
        s4,
        "Data Engineering Layer (Part 1)",
        [
            ("Raw Landing & Ingestion", "Automated ingestion runner with timestamped metadata and row-count auditing."),
            ("Data Quality Gate", "Validates schema types, normalizes '?' missing codes, and isolates invalid cases."),
            ("Quarantine Quarantine Layer", "Extracts expired and hospice cases to data/rejected/rejected_encounters.csv."),
            ("Transformation Engine", "Generates SHA-256 surrogate keys, HCUP clinical categories, and utilization metrics."),
            ("Star-Schema Storage", "Loads fact_readmission and 3 dimension tables into relational database."),
            ("Orchestration Workflow", "Apache Airflow DAG and reproducible CLI runner (run_pipeline.py).")
        ],
        "MLOps Platform Layer (Part 2)",
        [
            ("Leakage-Free Feature Store", "Stratified patient-level partitioner with ColumnTransformer feature encoding."),
            ("Model Training & Tuning", "Trains multi-model suite (LR, RF, XGB) with cost-sensitive class balancing."),
            ("MLflow Experiment Tracker", "SQLite-backed tracking database logging parameters, metrics, and curve artifacts."),
            ("Explainable AI (SHAP)", "TreeExplainer deriving global feature rankings and patient-specific risk drivers."),
            ("FastAPI Inference Service", "Asynchronous microservice delivering low-latency clinical scoring."),
            ("Drift & Fairness Monitor", "Automated KS-test, PSI drift detection, and subgroup fairness evaluations.")
        ]
    )

    # ----------------------------------------------------
    # SLIDE 5: DATA QUALITY GATE & QUARANTINE
    # ----------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    add_template_background(s5, 5, "4. Data Quality Gate & Quarantine Layer (Part 1)")
    add_two_column_content(
        s5,
        "Quality Validation Rules & Clinical Logic",
        [
            ("Survival Bias Elimination", "Discharge disposition IDs 11, 13, 14, 19, 20, 21 designate expired patients or hospice transfers who cannot be readmitted."),
            ("Clinical Impact", "Retaining deceased patients artificially suppresses readmission rates and biases machine learning risk calibration."),
            ("Length of Stay Bounds", "Enforced valid hospitalization duration: 1 <= time_in_hospital <= 14 days."),
            ("Missing Value Standardization", "Replaced '?', 'Unknown/Invalid', and empty strings with typed null values."),
            ("Integrity Verification", "Enforced uniqueness of encounter IDs and foreign-key relationships across dimensions.")
        ],
        "Quarantine & Retention Results",
        [
            ("Total Records Processed", "101,766 raw hospital encounters."),
            ("Clean Retained Encounters", "99,340 validated encounters passed to analytical layer (97.6% retention)."),
            ("Quarantined Records", "2,426 invalid records isolated to data/rejected/rejected_encounters.csv."),
            ("Quarantine Breakdown", "2,423 expired / hospice encounters; 3 invalid encounters."),
            ("Audit Logging", "Structured summary logged to logs/validation_audit.json with rejection reasons."),
            ("Zero Data Loss", "Quarantined records remain inspectable for compliance without corrupting downstream analytics.")
        ]
    )

    # ----------------------------------------------------
    # SLIDE 6: ETL, FEATURE ENGINEERING & ICD-9 TAXONOMY
    # ----------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    add_template_background(s6, 6, "5. ETL, Feature Engineering & ICD-9 Taxonomy (Part 1)")
    add_two_column_content(
        s6,
        "Clinical Feature Engineering",
        [
            ("Length of Stay (length_of_stay)", "Hospitalization duration (1-14 days) reflecting acute clinical complexity."),
            ("Prior Inpatient Admissions", "Total acute hospital stays in preceding 12 months (dominant readmission driver)."),
            ("Prior ED & Outpatient Visits", "Measures ambulatory instability and emergency department reliance."),
            ("Total Prior Visits", "Cumulative prior encounter contacts (inpatient + emergency + outpatient)."),
            ("Medication Change Flag", "Binary indicator (1/0) indicating diabetic drug dosage titration during stay."),
            ("Polypharmacy Count", "Total prescription medications administered (num_medications: 1-81).")
        ],
        "HCUP ICD-9 Clinical Classification",
        [
            ("High-Cardinality Resolution", "Over 700 raw ICD-9 codes grouped into 17 standardized HCUP disease categories."),
            ("Circulatory System (390-459)", "Top diagnosis: 30,437 encounters (30.6% of cohort; CHF, CAD, hypertension)."),
            ("Endocrine / Diabetes (250.xx)", "Second largest: 22,607 encounters (22.8% of cohort; ketoacidosis, diabetes)."),
            ("Respiratory System (460-519)", "Third largest: 14,424 encounters (14.5% of cohort; pneumonia, COPD)."),
            ("Patient Privacy & De-ID", "Deterministic SHA-256 surrogate keys (PAT_..., ENC_...) replace raw MRNs.")
        ]
    )

    # ----------------------------------------------------
    # SLIDE 7: DATABASE & STAR SCHEMA DATA MART
    # ----------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    add_template_background(s7, 7, "6. Database & Star Schema Data Mart (Part 1)")
    add_two_column_content(
        s7,
        "Relational Star-Schema Architecture",
        [
            ("Fact Table: fact_readmission", "99,340 rows. Central table containing clinical metrics, surrogate foreign keys, stay duration, and 30-day readmission labels."),
            ("Dim Table: dim_patient_summary", "69,987 rows. Patient-level dimension capturing demographics, lifetime visits, and chronic risk tier."),
            ("Dim Table: dim_diagnosis", "99,340 rows. Contains primary, secondary, and tertiary ICD-9 codes mapped to HCUP categories."),
            ("Dim Table: dim_encounter", "99,340 rows. Admission source, discharge destination, and admission type classifications.")
        ],
        "Database Loading & Orchestration",
        [
            ("Database Engine", "SQLite / PostgreSQL with relational integrity constraints and indexed foreign keys."),
            ("Atomic Bulk Loading", "Idempotent staging and batch insertion implemented via src/database/loader.py."),
            ("Apache Airflow DAG", "airflow_dags/hospital_readmission_etl_dag.py orchestrates ingestion, validation, and mart loading."),
            ("One-Click Execution", "python run_pipeline.py executes entire pipeline and populates database in 22.8 seconds."),
            ("Audit Trail", "Execution timestamps, row counts, and table status logged to logs/latest_pipeline_run.json.")
        ]
    )

    # ----------------------------------------------------
    # SLIDE 8: STREAMLIT ANALYTICS DASHBOARD (PART 1)
    # ----------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    add_template_background(s8, 8, "7. Streamlit Clinical Analytics Dashboard (Part 1)")

    # Left text box
    box_l8 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.85), Inches(1.75), Inches(5.65), Inches(4.8))
    box_l8.fill.solid()
    box_l8.fill.fore_color.rgb = COLOR_WHITE
    box_l8.line.color.rgb = COLOR_CARD_BORDER

    tb_lt8 = s8.shapes.add_textbox(Inches(1.05), Inches(1.9), Inches(5.25), Inches(0.4))
    p_lt8 = tb_lt8.text_frame.paragraphs[0]
    p_lt8.text = "6 Core Analytical Views & Clinical Insights"
    p_lt8.font.size = Pt(14); p_lt8.font.bold = True; p_lt8.font.color.rgb = RGBColor(194, 65, 12)

    tb_l8 = s8.shapes.add_textbox(Inches(1.05), Inches(2.35), Inches(5.25), Inches(4.0))
    tf_l8 = tb_l8.text_frame
    tf_l8.word_wrap = True
    b8_items = [
        ("1. Age & Demographics", "Visualizes readmission rates across 10-year age brackets (peaks in 70-80 cohort at 12.1%)."),
        ("2. Diagnosis & Specialty", "Analyzes readmission incidence across 17 HCUP categories (Circulatory and Respiratory lead)."),
        ("3. Length of Stay & Acuity", "Evaluates stay duration correlation; stays >7 days exhibit 1.8x higher readmission probability."),
        ("4. Admission & Discharge", "Compares Emergency vs Elective routes and high-risk discharge to Skilled Nursing Facilities (SNF)."),
        ("5. High-Risk Cohort Explorer", "Interactive multi-attribute filter isolating complex, frequent-utilizer patients."),
        ("6. Pipeline & Quality Audit", "Live inspection of latest ETL run metrics, table row counts, and quarantined records.")
    ]
    for i, (h, t) in enumerate(b8_items):
        p = tf_l8.paragraphs[0] if i == 0 else tf_l8.add_paragraph()
        r1 = p.add_run(); r1.text = f"- {h}: "; r1.font.bold = True; r1.font.size = Pt(10); r1.font.color.rgb = COLOR_TITLE
        r2 = p.add_run(); r2.text = t; r2.font.size = Pt(10); r2.font.color.rgb = COLOR_BODY
        p.space_after = Pt(4)

    # Right image box
    box_r8 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.75), Inches(5.65), Inches(4.8))
    box_r8.fill.solid()
    box_r8.fill.fore_color.rgb = COLOR_WHITE
    box_r8.line.color.rgb = COLOR_CARD_BORDER

    if dashboard_img_path.exists():
        s8.shapes.add_picture(str(dashboard_img_path), Inches(6.9), Inches(1.9), width=Inches(5.45))

    # ----------------------------------------------------
    # SLIDE 9: MLOps TARGET & LEAKAGE PREVENTION (PART 2)
    # ----------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    add_template_background(s9, 9, "8. MLOps Target Formulation & Leakage Prevention (Part 2)")
    add_two_column_content(
        s9,
        "Target Formulation & Class Imbalance",
        [
            ("The Clinical Target", "Binary 30-day readmission indicator (readmission_30d_binary: 1 if '<30', 0 if '>30' or 'NO')."),
            ("Regulatory Alignment", "Strictly mirrors HRRP reimbursement policy focusing on readmissions occurring within 30 days."),
            ("Severe Class Imbalance", "11,314 positive encounters (11.39%) vs 88,026 negative encounters (88.61%) - ~8:1 ratio."),
            ("Cost-Sensitive Learning", "Applied balanced subsample weighting (Random Forest) and scale_pos_weight=7.84 (XGBoost)."),
            ("Clinical Metric Selection", "Prioritized Recall (Sensitivity) and PR-AUC over raw accuracy to prevent false negatives.")
        ],
        "Zero Patient Leakage Stratification",
        [
            ("The Patient Overlap Hazard", "Random encounter-level splitting places visits from the same patient into both train and test, leaking patient-specific patterns."),
            ("Stratified Group Split", "Grouped encounters strictly by patient_surrogate_key with stratification on patient-level readmission history."),
            ("Training Partition (70%)", "69,584 encounters across 48,990 unique patients (11.31% positive)."),
            ("Validation Partition (15%)", "14,949 encounters across 10,498 unique patients (11.63% positive)."),
            ("Held-Out Test Set (15%)", "14,807 encounters across 10,499 unique patients (11.50% positive)."),
            ("Zero Overlap Verified", "Train, validation, and test patient sets are strictly disjoint (Train n Test = 0).")
        ]
    )

    # ----------------------------------------------------
    # SLIDE 10: MULTI-MODEL ARCHITECTURE & BENCHMARK
    # ----------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    add_template_background(s10, 10, "9. Multi-Model Architecture & Experimental Benchmark (Part 2)")

    # Full card table + bullet points
    table_shape = s10.shapes.add_table(4, 7, Inches(0.85), Inches(1.8), Inches(11.6), Inches(1.8))
    table = table_shape.table
    col_widths = [Inches(2.4), Inches(1.5), Inches(1.5), Inches(1.5), Inches(1.5), Inches(1.5), Inches(1.7)]
    for ci, w in enumerate(col_widths):
        table.columns[ci].width = w

    headers = ["Model Architecture", "Test ROC-AUC", "Test PR-AUC", "Test Recall", "Test Precision", "Brier Score", "Model Role"]
    for ci, h in enumerate(headers):
        cell = table.cell(0, ci)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(194, 65, 12)
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = COLOR_WHITE; p.alignment = PP_ALIGN.CENTER

    data_rows = [
        ["Random Forest (200 Trees)", "0.6769", "0.2313", "53.55%", "19.23%", "0.2122", "CHAMPION"],
        ["XGBoost Classifier", "0.6722", "0.2230", "56.08%", "18.66%", "0.2143", "CHALLENGER"],
        ["Logistic Regression (L2)", "0.6649", "0.2078", "52.50%", "16.54%", "0.2252", "BASELINE"]
    ]
    for ri, row in enumerate(data_rows):
        for ci, val in enumerate(row):
            cell = table.cell(ri + 1, ci)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(255, 255, 255) if ri % 2 == 0 else RGBColor(241, 245, 249)
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10.5)
                p.alignment = PP_ALIGN.CENTER if ci > 0 else PP_ALIGN.LEFT
                if ci == 6 and val == "CHAMPION":
                    p.font.bold = True; p.font.color.rgb = COLOR_GREEN
                elif ci == 0:
                    p.font.bold = True; p.font.color.rgb = COLOR_TITLE
                else:
                    p.font.color.rgb = COLOR_BODY

    # Bullet points below table
    tb_b10 = s10.shapes.add_textbox(Inches(0.85), Inches(3.8), Inches(11.6), Inches(2.8))
    tf_b10 = tb_b10.text_frame
    tf_b10.word_wrap = True
    pts10 = [
        ("Champion Model Justification", "Random Forest achieved the highest discrimination (ROC-AUC: 0.6769), highest PR-AUC (0.2313), and superior probability calibration (Brier: 0.2122)."),
        ("PR-AUC Outperforms Baseline", "Achieved PR-AUC of 0.2313, more than double the random baseline prevalence (11.39%), demonstrating significant predictive power."),
        ("High Clinical Sensitivity", "Recovers 53.55% of true 30-day readmissions at operational threshold, ensuring the majority of vulnerable patients receive discharge interventions."),
        ("Tree-SHAP Determinism", "Random Forest decision trees provide deterministic, rapid Shapley attributions via TreeExplainer without numeric instabilities.")
    ]
    for i, (h, t) in enumerate(pts10):
        p = tf_b10.paragraphs[0] if i == 0 else tf_b10.add_paragraph()
        r1 = p.add_run(); r1.text = f"- {h}: "; r1.font.bold = True; r1.font.size = Pt(11); r1.font.color.rgb = COLOR_TITLE
        r2 = p.add_run(); r2.text = t; r2.font.size = Pt(11); r2.font.color.rgb = COLOR_BODY
        p.space_after = Pt(6)

    # ----------------------------------------------------
    # SLIDE 11: CHAMPION MODEL & MLFLOW TRACKING
    # ----------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    add_template_background(s11, 11, "10. Champion Model & MLflow Tracking (Part 2)")

    # Left text box
    box_l11 = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.85), Inches(1.75), Inches(5.65), Inches(4.8))
    box_l11.fill.solid()
    box_l11.fill.fore_color.rgb = COLOR_WHITE
    box_l11.line.color.rgb = COLOR_CARD_BORDER

    tb_lt11 = s11.shapes.add_textbox(Inches(1.05), Inches(1.9), Inches(5.25), Inches(0.4))
    p_lt11 = tb_lt11.text_frame.paragraphs[0]
    p_lt11.text = "MLflow Experiment Tracking & Registry"
    p_lt11.font.size = Pt(14); p_lt11.font.bold = True; p_lt11.font.color.rgb = RGBColor(194, 65, 12)

    tb_l11 = s11.shapes.add_textbox(Inches(1.05), Inches(2.35), Inches(5.25), Inches(4.0))
    tf_l11 = tb_l11.text_frame
    tf_l11.word_wrap = True
    b11_items = [
        ("Tracking Backend", "Configured MLflow tracking with SQLite database backend (sqlite:///data/mlflow.db)."),
        ("Tracked Hyperparameters", "Logged n_estimators (200), max_depth (12), min_samples_leaf (4), and subsample class weights."),
        ("Tracked Evaluation Metrics", "Logged validation & test ROC-AUC, PR-AUC, Recall, Precision, F1, and Brier score."),
        ("Artifact Persistence", "Saved ROC curves, PR curves, calibration plots, and serialized joblib model artifacts."),
        ("Model Packaging", "Champion model exported to models/champion_model.joblib with preprocessing metadata.")
    ]
    for i, (h, t) in enumerate(b11_items):
        p = tf_l11.paragraphs[0] if i == 0 else tf_l11.add_paragraph()
        r1 = p.add_run(); r1.text = f"- {h}: "; r1.font.bold = True; r1.font.size = Pt(10.5); r1.font.color.rgb = COLOR_TITLE
        r2 = p.add_run(); r2.text = t; r2.font.size = Pt(10.5); r2.font.color.rgb = COLOR_BODY
        p.space_after = Pt(6)

    # Right figures box
    box_r11 = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.75), Inches(5.65), Inches(4.8))
    box_r11.fill.solid()
    box_r11.fill.fore_color.rgb = COLOR_WHITE
    box_r11.line.color.rgb = COLOR_CARD_BORDER

    if roc_img_path.exists():
        s11.shapes.add_picture(str(roc_img_path), Inches(6.9), Inches(1.85), width=Inches(2.7))
    if calib_img_path.exists():
        s11.shapes.add_picture(str(calib_img_path), Inches(9.65), Inches(1.85), width=Inches(2.7))

    tb_caption11 = s11.shapes.add_textbox(Inches(6.9), Inches(5.9), Inches(5.45), Inches(0.5))
    p_cap = tb_caption11.text_frame.paragraphs[0]
    p_cap.text = "Left: Random Forest ROC Curve (AUC 0.6769)  |  Right: Probability Calibration Reliability"
    p_cap.font.size = Pt(9.5); p_cap.font.color.rgb = COLOR_MUTED; p_cap.alignment = PP_ALIGN.CENTER

    # ----------------------------------------------------
    # SLIDE 12: MODEL EXPLAINABILITY VIA SHAP (PART 2)
    # ----------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    add_template_background(s12, 12, "11. Model Explainability via SHAP (Part 2)")

    # Left text box
    box_l12 = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.85), Inches(1.75), Inches(5.65), Inches(4.8))
    box_l12.fill.solid()
    box_l12.fill.fore_color.rgb = COLOR_WHITE
    box_l12.line.color.rgb = COLOR_CARD_BORDER

    tb_lt12 = s12.shapes.add_textbox(Inches(1.05), Inches(1.9), Inches(5.25), Inches(0.4))
    p_lt12 = tb_lt12.text_frame.paragraphs[0]
    p_lt12.text = "TreeExplainer Clinical Risk Attribution"
    p_lt12.font.size = Pt(14); p_lt12.font.bold = True; p_lt12.font.color.rgb = RGBColor(194, 65, 12)

    tb_l12 = s12.shapes.add_textbox(Inches(1.05), Inches(2.35), Inches(5.25), Inches(4.0))
    tf_l12 = tb_l12.text_frame
    tf_l12.word_wrap = True
    b12_items = [
        ("Game-Theoretic Foundation", "Calculates exact Shapley values across 500 test patient encounters to quantify feature impact."),
        ("Top Predictor: Prior Admissions", "prior_inpatient_admissions is by far the strongest single risk factor; repeated acute stays signify chronic disease instability."),
        ("Discharge Pathways", "Patients discharged to home show significantly lower risk than those transferred to skilled nursing or rehab facilities."),
        ("Hospital Utilization", "Cumulative prior visits (total_prior_visits) and stay duration (length_of_stay) represent key frailty drivers."),
        ("Polypharmacy & Diagnoses", "High medication count (num_medications >= 16) and multiple secondary diagnoses elevate readmission probability.")
    ]
    for i, (h, t) in enumerate(b12_items):
        p = tf_l12.paragraphs[0] if i == 0 else tf_l12.add_paragraph()
        r1 = p.add_run(); r1.text = f"- {h}: "; r1.font.bold = True; r1.font.size = Pt(10.5); r1.font.color.rgb = COLOR_TITLE
        r2 = p.add_run(); r2.text = t; r2.font.size = Pt(10.5); r2.font.color.rgb = COLOR_BODY
        p.space_after = Pt(6)

    # Right figure box
    box_r12 = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.75), Inches(5.65), Inches(4.8))
    box_r12.fill.solid()
    box_r12.fill.fore_color.rgb = COLOR_WHITE
    box_r12.line.color.rgb = COLOR_CARD_BORDER

    if shap_img_path.exists():
        s12.shapes.add_picture(str(shap_img_path), Inches(6.9), Inches(1.9), width=Inches(5.45))

    # ----------------------------------------------------
    # SLIDE 13: FASTAPI SERVING & CONTAINERIZATION
    # ----------------------------------------------------
    s13 = prs.slides.add_slide(blank_layout)
    add_template_background(s13, 13, "12. Real-Time Serving Microservice & Containers (Part 2)")
    add_two_column_content(
        s13,
        "FastAPI Inference Microservice",
        [
            ("Asynchronous Architecture", "Built with FastAPI and Uvicorn for high-throughput, low-latency prediction serving."),
            ("GET /health", "Liveness check returning service status, model loaded state, and active champion model."),
            ("GET /model-info", "Exposes champion architecture, test metrics, and clinical decision-support disclaimer."),
            ("POST /predict", "Accepts patient encounter JSON; validates via Pydantic; outputs risk probability and clinical tier."),
            ("POST /explain", "Extracts top 6 clinical feature contributors explaining the patient's individual risk score."),
            ("Pydantic Validation", "Enforces clinical bounds on stay duration (1-14 days), lab counts, and medications.")
        ],
        "Docker Containerization & Compose",
        [
            ("Production Dockerfile", "Lightweight Python 3.12-slim base image, non-root user execution, and pinned dependencies."),
            ("Multi-Container Compose", "docker-compose.yml orchestrates FastAPI microservice (port 8000) and Streamlit UI (port 8501)."),
            ("Isolated Bridge Network", "Secure internal communication between microservices on shared Docker network."),
            ("Optimized Build", "Configured .dockerignore excluding temporary files, virtual environments, and caches."),
            ("Reproducibility", "Guarantees cross-platform deployment across on-premise hospital servers and cloud platforms.")
        ]
    )

    # ----------------------------------------------------
    # SLIDE 14: CONTINUOUS MONITORING, DRIFT & FAIRNESS
    # ----------------------------------------------------
    s14 = prs.slides.add_slide(blank_layout)
    add_template_background(s14, 14, "13. Continuous Monitoring, Drift & Fairness (Part 2)")
    add_two_column_content(
        s14,
        "Statistical Data Drift Engine",
        [
            ("Two-Sample KS Test", "Two-sample Kolmogorov-Smirnov test evaluates continuous numerical distribution shift (p < 0.01 threshold)."),
            ("Population Stability Index (PSI)", "Quantifies magnitude of population drift (PSI < 0.1 stable, PSI > 0.25 severe shift)."),
            ("Continuous Audit Execution", "Audited 10 numerical features between baseline (69,538 encounters) and monitoring window (29,802 encounters)."),
            ("Audit Findings", "All 10 numerical features exhibited stable distributions (zero significant drift detected)."),
            ("Automated Logging", "Audit diagnostics written to logs/drift_monitoring_audit.json with feature-level metrics.")
        ],
        "Subgroup Fairness & Retraining Triggers",
        [
            ("Gender Fairness Audit", "Model discrimination evaluated across Female (ROC-AUC: 0.675) and Male (ROC-AUC: 0.679) cohorts; disparity < 0.005."),
            ("Age Group Disparity Audit", "Consistent performance maintained across high-volume senior brackets ([60-70) and [70-80))."),
            ("Automated Retraining Rules", "Retraining automatically triggered if: (1) ROC-AUC drops by >0.05, or (2) >=3 features show PSI > 0.25."),
            ("Formal Policy", "Documented operational maintenance protocol in docs/retraining_policy.md."),
            ("Ethical Safeguards", "Ensures algorithm does not introduce demographic disparities in transitional care delivery.")
        ]
    )

    # ----------------------------------------------------
    # SLIDE 15: REAL-TIME DECISION SUPPORT (DASHBOARD TAB 7)
    # ----------------------------------------------------
    s15 = prs.slides.add_slide(blank_layout)
    add_template_background(s15, 15, "14. Real-Time Decision Support in Dashboard (Part 2)")
    add_two_column_content(
        s15,
        "Streamlit Tab 7 Interactive Predictor",
        [
            ("Clinical Decision Support Form", "Clinicians input patient age, gender, admission type, stay duration, lab counts, medications, and prior stays."),
            ("On-Demand Scoring", "Invokes fitted ColumnTransformer and Random Forest champion model in real time."),
            ("Visual Gauge Meter", "Interactive Plotly gauge chart displaying predicted readmission risk probability (0% to 100%)."),
            ("Color-Coded Risk Bands", "Green (0-18% Low Risk), Amber (18-35% Moderate Risk), Red (35-100% High Risk)."),
            ("Relative Risk Ratio", "Computes patient risk multiplier compared to average hospital baseline (11.37%)."),
            ("Top Feature Drivers Table", "Ranks top clinical factors driving risk for this specific patient.")
        ],
        "Clinical Risk Tiers & Action Plans",
        [
            ("HIGH RISK (>= 35% Probability)", "Urgent Clinical Coordination: Deploy transitional care nurse, mandatory 48-hour phone check, home medication reconciliation, and rapid 7-day PCP visit."),
            ("MODERATE RISK (18% - 35%)", "Enhanced Monitoring: Schedule primary care follow-up within 7-10 days, review diabetic regimen with nurse educator."),
            ("LOW RISK (< 18%)", "Standard Discharge: Routine primary care follow-up and standard printed discharge guidelines."),
            ("Academic Disclaimer", "Prominently displays prototype advisory: predictions assist, but do not replace, professional clinical judgement.")
        ]
    )

    # ----------------------------------------------------
    # SLIDE 16: AUTOMATED TESTING & EXECUTION EVIDENCE
    # ----------------------------------------------------
    s16 = prs.slides.add_slide(blank_layout)
    add_template_background(s16, 16, "15. Automated Testing & Verification Evidence")
    add_two_column_content(
        s16,
        "End-to-End Pipeline Verification",
        [
            ("Part 1 Pipeline Execution", "python run_pipeline.py completed successfully in 22.78 seconds."),
            ("Data Mart Population", "Loaded 69,987 patient summaries, 99,340 diagnosis rows, and 99,340 fact records."),
            ("Quarantine Isolation", "2,426 invalid/expired encounters quarantined to data/rejected/rejected_encounters.csv."),
            ("Part 2 Pipeline Execution", "python run_mlops_pipeline.py completed successfully in 80.31 seconds."),
            ("Model Artifact Generation", "Saved champion_model.joblib, preprocessor.joblib, and MLflow experiment runs."),
            ("Clean Console Logs", "Structured JSON audit reports saved for both pipelines in logs/ directory.")
        ],
        "100% Pytest Suite Pass Rate (11/11 Tests)",
        [
            ("Test 1: ICD-9 Taxonomy", "Verified clinical code classification into HCUP categories (PASSED)."),
            ("Test 2: Surrogate Keys", "Verified deterministic, unique SHA-256 key generation (PASSED)."),
            ("Test 3: Data Quarantine", "Verified hospice/expired records correctly quarantined (PASSED)."),
            ("Test 4: Data Mart Queries", "Verified relational tables populated and queryable (PASSED)."),
            ("Test 5: Split Integrity", "Verified zero patient overlap across train/val/test splits (PASSED)."),
            ("Test 6: Model Probability", "Verified calibrated output probabilities within [0, 1] (PASSED)."),
            ("Tests 7-10: FastAPI Endpoints", "Verified /health, /model-info, /predict, /explain via TestClient (PASSED)."),
            ("Test 11: Drift Monitoring", "Verified KS-test and PSI metrics calculation (PASSED).")
        ]
    )

    # ----------------------------------------------------
    # SLIDE 17: CLINICAL FINDINGS & KEY TAKEAWAYS
    # ----------------------------------------------------
    s17 = prs.slides.add_slide(blank_layout)
    add_template_background(s17, 17, "16. Clinical Findings & Key Takeaways")
    add_two_column_content(
        s17,
        "Core Clinical Findings",
        [
            ("Prior Admissions Dominate", "Patients with >=2 prior inpatient admissions exhibit over 3.2x higher 30-day readmission risk compared to first-time admissions."),
            ("Stay Duration Threshold", "Hospitalizations exceeding 6 days show sharply elevated risk, especially when combined with polypharmacy (>=15 medications)."),
            ("High-Risk Diagnoses", "Circulatory disorders (CHF, ischemic heart disease) and complex diabetes carry the highest absolute readmission volumes."),
            ("Discharge Vulnerability", "Discharges to skilled nursing facilities (SNF) correlate with elevated readmissions compared to routine home discharges.")
        ],
        "Data Engineering & MLOps Insights",
        [
            ("Zero Patient Leakage is Critical", "Random train/test splits artificially inflate healthcare metrics; patient-level grouping is essential for true generalization."),
            ("Calibration Over Raw Accuracy", "In highly imbalanced healthcare datasets (11.4%), well-calibrated probabilities are vital for clinical risk stratification."),
            ("Explainability Drives Adoption", "Clinicians require transparent factor attribution (SHAP) rather than black-box probability scores."),
            ("Automated CI/CD Verification", "Comprehensive automated tests guard against silent pipeline failures and schema drift.")
        ]
    )

    # ----------------------------------------------------
    # SLIDE 18: CONCLUSION & FUTURE ROADMAP
    # ----------------------------------------------------
    s18 = prs.slides.add_slide(blank_layout)
    add_template_background(s18, 18, "17. Conclusion & Future Roadmap")
    add_two_column_content(
        s18,
        "Summary of Project Achievements",
        [
            ("Unified End-to-End System", "Successfully connected raw healthcare ingestion, relational data marts, multi-model MLOps, and real-time clinical serving."),
            ("Academic & Industry Standards", "Adheres to HIPAA de-identification standards, HCUP clinical taxonomies, and Mitchell et al. Model Card specifications."),
            ("Validated Model Performance", "Delivered Random Forest champion model achieving 0.6769 ROC-AUC and 53.55% sensitivity on held-out test cohort."),
            ("Production Deliverables", "Airflow DAG, star-schema data mart, FastAPI microservice, Docker configs, and 7-tab Streamlit dashboard.")
        ],
        "Future Roadmap & Enhancements",
        [
            ("EHR Standards Integration", "Incorporate HL7 / FHIR APIs for direct interoperability with hospital electronic health record systems."),
            ("Real-Time Streaming Alerts", "Integrate Apache Kafka for real-time patient vital sign streaming and ICU deterioration alerts."),
            ("Contemporary Pharmacotherapy", "Incorporate modern diabetic medications (SGLT2 inhibitors, GLP-1 receptor agonists) into feature space."),
            ("Prospective Pilot Trial", "Deploy decision-support prototype in hospital discharge planning units for prospective clinical validation.")
        ]
    )

    # ----------------------------------------------------
    # SLIDE 19: REFERENCES & DOCUMENTATION INDEX
    # ----------------------------------------------------
    s19 = prs.slides.add_slide(blank_layout)
    add_template_background(s19, 19, "18. References & Documentation Index")
    add_two_column_content(
        s19,
        "Academic & Clinical References",
        [
            ("Strack et al. (2014)", "Impact of HbA1c Measurement on Hospital Readmission Rates: Analysis of 70,000 Clinical Encounters. BioMed Research International."),
            ("Mitchell et al. (2019)", "Model Cards for Model Reporting. Proceedings of the Conference on Fairness, Accountability, and Transparency (ACM FAT*)."),
            ("Lundberg & Lee (2017)", "A Unified Approach to Interpreting Model Predictions. Advances in Neural Information Processing Systems (NeurIPS)."),
            ("CMS HRRP Guidelines", "Centers for Medicare & Medicaid Services: Hospital Readmissions Reduction Program Quality and Payment Directives.")
        ],
        "Project Documentation Index",
        [
            ("README.md", "Master project documentation, architecture guide, and setup instructions."),
            ("docs/project_report_part1.md", "Detailed Part 1 Data Engineering Submission Report (8-10 pages)."),
            ("docs/project_report_part2.md", "Detailed Part 2 MLOps Pipeline Extension Submission Report."),
            ("docs/model_card.md", "Clinical Model Card for Champion Model following Mitchell et al."),
            ("docs/retraining_policy.md", "Continuous data drift and automated retraining policy document."),
            ("docs/data_dictionary.md", "Comprehensive technical and clinical data dictionary.")
        ]
    )

    # ----------------------------------------------------
    # SLIDE 20: THANK YOU & Q&A
    # ----------------------------------------------------
    s20 = prs.slides.add_slide(blank_layout)
    add_template_background(s20, 20, "")

    if cmrit_logo_path.exists():
        s20.shapes.add_picture(str(cmrit_logo_path), Inches(0.8), Inches(0.6), height=Inches(1.2))

    tb_s20_sub = s20.shapes.add_textbox(Inches(0.8), Inches(2.1), Inches(8.0), Inches(0.4))
    p20_sub = tb_s20_sub.text_frame.paragraphs[0]
    p20_sub.text = "THANK YOU"
    p20_sub.font.size = Pt(28); p20_sub.font.bold = True; p20_sub.font.color.rgb = COLOR_ACCENT

    tb_s20_title = s20.shapes.add_textbox(Inches(0.8), Inches(2.75), Inches(11.5), Inches(1.3))
    p20_t = tb_s20_title.text_frame.paragraphs[0]
    p20_t.text = "Hospital Readmission Analytics and Prediction Using Public Data"
    p20_t.font.size = Pt(26); p20_t.font.bold = True; p20_t.font.color.rgb = COLOR_TITLE

    tb_s20_desc = s20.shapes.add_textbox(Inches(0.8), Inches(4.1), Inches(11.5), Inches(0.5))
    p20_d = tb_s20_desc.text_frame.paragraphs[0]
    p20_d.text = "Questions & Answers | Final Project Evaluation (Parts 1 & 2)"
    p20_d.font.size = Pt(16); p20_d.font.color.rgb = COLOR_SUBTITLE

    card_s20 = s20.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.7), Inches(7.5), Inches(1.9))
    card_s20.fill.solid()
    card_s20.fill.fore_color.rgb = COLOR_CARD_BG
    card_s20.line.color.rgb = COLOR_CARD_BORDER

    tb_s20_info = s20.shapes.add_textbox(Inches(1.1), Inches(4.85), Inches(7.0), Inches(1.6))
    tf_s20_info = tb_s20_info.text_frame

    p = tf_s20_info.paragraphs[0]
    p.text = "Student: Vinay Kumar H R    |    USN: 1CR23AI139"
    p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = COLOR_TITLE

    p = tf_s20_info.add_paragraph()
    p.text = "Department of Artificial Intelligence and Machine Learning"
    p.font.size = Pt(12); p.font.color.rgb = COLOR_BODY

    p = tf_s20_info.add_paragraph()
    p.text = "CMR Institute of Technology (CMRIT), Bengaluru"
    p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = RGBColor(194, 65, 12)

    p = tf_s20_info.add_paragraph()
    p.text = "Course: Data Engineering and MLOps  |  Academic Year 2026"
    p.font.size = Pt(11); p.font.color.rgb = COLOR_MUTED

    out_file1 = Path("Hospital_Readmission_Analytics_Final_Presentation.pptx")
    out_file2 = Path("Hospital_Readmission_Analytics_Presentation.pptx")
    prs.save(str(out_file1))
    prs.save(str(out_file2))
    print(f"Presentation saved successfully to {out_file1} and {out_file2} ({len(prs.slides)} slides)!")

if __name__ == "__main__":
    create_presentation()

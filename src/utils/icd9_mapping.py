"""
ICD-9 Clinical Category Classification Utility
Maps ICD-9 diagnostic codes into primary clinical disease categories according to
the Healthcare Cost and Utilization Project (HCUP) clinical taxonomy standards.
"""

def map_icd9_code(code: str) -> str:
    if code is None or code == "?" or str(code).strip() == "":
        return "Unknown / Missing"
    
    code = str(code).strip()
    
    if code.startswith("V"):
        return "Supplementary (V-codes)"
    if code.startswith("E"):
        return "External Causes of Injury (E-codes)"
    
    try:
        prefix = float(code.split(".")[0])
    except ValueError:
        return "Other / Unclassified"
    
    if 390 <= prefix <= 459 or prefix == 785:
        return "Circulatory System"
    elif 460 <= prefix <= 519 or prefix == 786:
        return "Respiratory System"
    elif 520 <= prefix <= 579 or prefix == 787:
        return "Digestive System"
    elif 250 <= prefix < 251:
        return "Diabetes Mellitus"
    elif 800 <= prefix <= 999:
        return "Injury and Poisoning"
    elif 710 <= prefix <= 739:
        return "Musculoskeletal System"
    elif 580 <= prefix <= 629 or prefix == 788:
        return "Genitourinary System"
    elif 140 <= prefix <= 239:
        return "Neoplasms"
    elif 240 <= prefix <= 279 and not (250 <= prefix < 251):
        return "Endocrine and Metabolic"
    elif 290 <= prefix <= 319:
        return "Mental Disorders"
    elif 320 <= prefix <= 389:
        return "Nervous System"
    elif 680 <= prefix <= 709:
        return "Skin and Subcutaneous"
    elif 780 <= prefix <= 799 and prefix not in [785, 786, 787, 788]:
        return "Symptoms and Ill-Defined"
    elif 1 <= prefix <= 139:
        return "Infectious and Parasitic"
    else:
        return "Other / Unclassified"

def get_category_severity_weight(category: str) -> int:
    weights = {
        "Circulatory System": 4,
        "Respiratory System": 4,
        "Neoplasms": 4,
        "Diabetes Mellitus": 3,
        "Digestive System": 3,
        "Genitourinary System": 3,
        "Nervous System": 3,
        "Injury and Poisoning": 2,
        "Musculoskeletal System": 2,
        "Endocrine and Metabolic": 2,
        "Mental Disorders": 2,
        "Skin and Subcutaneous": 1,
        "Infectious and Parasitic": 3,
        "Supplementary (V-codes)": 1,
        "External Causes of Injury (E-codes)": 1,
        "Symptoms and Ill-Defined": 2,
        "Unknown / Missing": 0,
        "Other / Unclassified": 1
    }
    return weights.get(category, 1)

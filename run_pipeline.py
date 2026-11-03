"""
Command-Line Interface to Run the Entire Healthcare Readmission Data Pipeline (Part 1).
"""
import sys
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.etl.pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="Hospital Readmission Analytics ETL Pipeline (Part 1)")
    parser.add_argument("--run", action="store_true", help="Execute complete end-to-end pipeline")
    args = parser.parse_args()

    print("==========================================================================")
    print("Project 5: Hospital Readmission Analytics & Pipeline (Part 1)")
    print("Data Engineering & MLOps")
    print("==========================================================================")
    
    summary = run_pipeline()
    print("\n[+] Pipeline Run Successfully!")
    print(f"    - Raw Records Extracted: {summary['raw_records_extracted']}")
    print(f"    - Valid Records Cleaned: {summary['valid_records_processed']}")
    print(f"    - Quarantined Records:   {summary['quarantined_rejected_records']}")
    print(f"    - Analytical Tables:     {list(summary['data_mart_tables_loaded'].keys())}")
    print(f"    - Total Time Elapsed:    {summary['elapsed_seconds']} s")
    print("\nTo launch the interactive dashboard, run:")
    print("    streamlit run dashboard/app.py")

if __name__ == "__main__":
    main()

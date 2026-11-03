"""
Automated Dataset Downloader & Checksum Verifier for UCI Diabetes 130-US Hospitals Dataset.
"""
import os
import sys
import zipfile
import urllib.request
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.logging_config import setup_logger

logger = setup_logger("downloader")

DATA_URL = "https://archive.ics.uci.edu/static/public/296/diabetes+130-us+hospitals+for+years+1999-2008.zip"
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

def calculate_sha256(filepath: Path) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def download_and_extract() -> dict:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = RAW_DATA_DIR / "dataset_diabetes.zip"
    diabetic_csv = RAW_DATA_DIR / "diabetic_data.csv"
    ids_csv = RAW_DATA_DIR / "IDS_mapping.csv"

    if not diabetic_csv.exists() or not ids_csv.exists():
        logger.info(f"Downloading dataset from {DATA_URL}...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(DATA_URL, headers=headers)
        
        with urllib.request.urlopen(req, timeout=60) as response, open(zip_path, 'wb') as out_file:
            out_file.write(response.read())
        logger.info(f"Downloaded zip: {zip_path.stat().st_size / (1024*1024):.2f} MB")

        logger.info("Extracting ZIP archive...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(RAW_DATA_DIR)

        # Check for nested dataset_diabetes.zip
        for nested in RAW_DATA_DIR.rglob("*.zip"):
            if nested != zip_path:
                with zipfile.ZipFile(nested, 'r') as inner_zip:
                    inner_zip.extractall(RAW_DATA_DIR)

        # Move files to root of raw if nested
        for f in RAW_DATA_DIR.rglob("*.csv"):
            if f.parent != RAW_DATA_DIR:
                target = RAW_DATA_DIR / f.name
                if not target.exists():
                    f.replace(target)
    else:
        logger.info("Dataset files already exist in raw data directory.")

    sha256_val = calculate_sha256(diabetic_csv) if diabetic_csv.exists() else "N/A"
    row_count = 0
    if diabetic_csv.exists():
        with open(diabetic_csv, 'r', encoding='utf-8', errors='ignore') as f:
            row_count = sum(1 for _ in f) - 1

    metadata = {
        "status": "SUCCESS" if (diabetic_csv.exists() and ids_csv.exists()) else "FAILED",
        "diabetic_csv_path": str(diabetic_csv),
        "ids_csv_path": str(ids_csv),
        "sha256_hash": sha256_val,
        "row_count": row_count,
        "source": DATA_URL
    }
    logger.info(f"Download/Extraction verification complete. Encounters raw rows: {row_count}")
    return metadata

if __name__ == "__main__":
    download_and_extract()

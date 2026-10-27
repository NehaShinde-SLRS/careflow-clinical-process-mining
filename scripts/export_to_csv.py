"""
CareFlow Clinical Process Mining — Day 3
Script: export_to_csv.py

Purpose:
    Export the cleaned HospitalOPD dataset to a CSV working copy
    inside the project's data/ directory.

    NOTE ON FILE FORMAT:
    The source file "HospitalOPD_cleaned (1).xls" is NOT a binary Excel file.
    Inspection confirmed it is a comma-separated CSV file saved with a .xls
    extension.  It is read with pandas read_csv using UTF-8 encoding.
    The xlrd engine cannot read it (raises BOF error).

Confirmed schema (24 columns):
    record_no, patient_id, appointment_id, appointment_start_datetime,
    prescription_doctor_id, prescription_doctor_name, prescription_order_id,
    prescription_start_datetime, prescription_end_datetime,
    lab_id, lab_name, lab_start_datetime, lab_end_datetime,
    imaging_request_id, imaging_result_id, imaging_name,
    imaging_start_datetime, imaging_end_datetime,
    pharmacy_sale_line_id, medicine_name, pharmacy_start_datetime,
    pharmacy_end_datetime, flow_code, flow_name

Requirements:
    pip install pandas

Usage:
    python scripts/export_to_csv.py

Safety rules:
    - The source file is never written to, renamed, moved, or deleted.
    - Column names are preserved exactly as they appear in the source.
    - No rows are silently dropped, de-duplicated, or filtered.
    - No clinical values are renamed or recoded.
    - If the target CSV already exists, the script checks it before replacing.
    - Null values are written as empty strings (standard CSV convention).
    - All columns read as strings to prevent silent type conversion.
"""

import sys
import hashlib
from pathlib import Path
import warnings
import pandas as pd

# Reconfigure stdout/stderr for UTF-8 in Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

warnings.filterwarnings("ignore", category=UserWarning)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SOURCE_FILE  = Path(r"C:\Users\user\Videos\HospitalOPD_cleaned (1).xls")
TARGET_DIR   = Path(__file__).resolve().parent.parent / "data"
TARGET_CSV   = TARGET_DIR / "HospitalOPD_cleaned.csv"

# Expected values from project documentation
EXPECTED_ROWS = 62_422
EXPECTED_COLS = 25

SEPARATOR = "=" * 72

ID_FLOAT_COLUMNS = [
    "lab_id",
    "imaging_request_id",
    "imaging_result_id",
    "pharmacy_sale_line_id",
]


def clean_whole_number_id(val) -> str:
    """
    Converts values ending in '.0' to integer-form strings only when confirmed
    to be whole-number IDs. Preserves null values, empty strings, and leading zeros.
    """
    if pd.isna(val) or val is None or val == "":
        return ""
    s = str(val).strip()
    if s.endswith(".0"):
        base = s[:-2]
        if base.isdigit():
            return base
    return s


def section(title: str) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def compute_md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65_536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    # ------------------------------------------------------------------
    # 0. Verify source file
    # ------------------------------------------------------------------
    section("0. Source File Verification")
    if not SOURCE_FILE.exists():
        print(f"[ERROR] Source file not found: {SOURCE_FILE}")
        print("  Confirm the correct local path and update SOURCE_FILE.")
        sys.exit(1)

    src_size = SOURCE_FILE.stat().st_size
    src_md5  = compute_md5(SOURCE_FILE)
    print(f"  Path : {SOURCE_FILE}")
    print(f"  Size : {src_size:,} bytes ({src_size / 1_048_576:.2f} MB)")
    print(f"  MD5  : {src_md5}")

    # ------------------------------------------------------------------
    # 1. Load source
    # ------------------------------------------------------------------
    section("1. Loading Source Excel File (read-only)")
    try:
        import pandas as pd
    except ImportError:
        print("[ERROR] pandas not installed. Run: pip install pandas xlrd")
        sys.exit(1)

    try:
        df = pd.read_csv(
            SOURCE_FILE,
            encoding="utf-8",
            encoding_errors="replace",   # Python 3.10+: replace undecodable bytes
            dtype=str,
            low_memory=False,
        )
    except Exception as exc:
        print(f"[ERROR] Failed to read source file: {exc}")
        sys.exit(1)

    actual_rows, actual_cols = df.shape
    print(f"  File format : CSV (UTF-8, comma-separated) saved with .xls extension")
    print(f"  Loaded: {actual_rows:,} rows × {actual_cols} columns")

    if actual_rows != EXPECTED_ROWS:
        print(f"  [WARN] Row count {actual_rows:,} differs from expected {EXPECTED_ROWS:,}.")
        print("         Proceeding with actual data — investigate the discrepancy.")
    if actual_cols != EXPECTED_COLS:
        print(f"  [WARN] Column count {actual_cols} differs from expected {EXPECTED_COLS}.")

    # ------------------------------------------------------------------
    # 2. Check for existing target CSV
    # ------------------------------------------------------------------
    section("2. Target CSV Check")
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    if TARGET_CSV.exists():
        existing_size = TARGET_CSV.stat().st_size
        print(f"  [WARN] Target CSV already exists: {TARGET_CSV}")
        print(f"         Existing file size: {existing_size:,} bytes")

        # Read the existing CSV to compare
        try:
            existing_df = pd.read_csv(TARGET_CSV, dtype=str, nrows=5)
            existing_full = pd.read_csv(TARGET_CSV, dtype=str)
            ex_rows, ex_cols = existing_full.shape
            print(f"         Existing CSV rows: {ex_rows:,}  cols: {ex_cols}")
            print(f"         Existing CSV columns match source: {list(existing_df.columns) == list(df.columns[:len(existing_df.columns)])}")
        except Exception as exc:
            print(f"         Could not read existing CSV: {exc}")
            ex_rows = -1

        if ex_rows == actual_rows:
            print("  Existing CSV has the same row count as source.")
            print("  Overwriting with a fresh export to ensure byte-for-byte consistency.")
        else:
            print("  Row count mismatch — replacing with fresh export.")

        backup_csv = TARGET_CSV.with_suffix(".csv.bak")
        import shutil
        shutil.copy2(TARGET_CSV, backup_csv)
        print(f"  [BACKUP] Created backup of existing CSV: {backup_csv}")
    else:
        print(f"  Target CSV does not exist. Will create: {TARGET_CSV}")

    # ------------------------------------------------------------------
    # 2b. Format whole-number ID columns
    # ------------------------------------------------------------------
    section("2b. Formatting Whole-Number ID Columns")
    for col in ID_FLOAT_COLUMNS:
        if col in df.columns:
            before_dot_zero = (df[col].astype(str).str.endswith(".0")).sum()
            df[col] = df[col].apply(clean_whole_number_id)
            print(f"  {col:<25}: normalized {before_dot_zero:,} values ending in '.0'")

    # ------------------------------------------------------------------
    # 3. Export to CSV
    # ------------------------------------------------------------------
    section("3. Exporting to CSV")
    print(f"  Encoding: UTF-8 (no BOM) — consistent with source file encoding")
    print(f"  Null values: written as empty strings (standard CSV convention)")
    print(f"  Index: not included in CSV output")
    print(f"  Column names: preserved exactly from source without renaming")

    try:
        df.to_csv(
            TARGET_CSV,
            index=False,
            encoding="utf-8",   # UTF-8 without BOM — matches source encoding
            na_rep="",          # Nulls as empty string
        )
    except Exception as exc:
        print(f"[ERROR] CSV export failed: {exc}")
        sys.exit(1)

    # ------------------------------------------------------------------
    # 4. Verify exported CSV
    # ------------------------------------------------------------------
    section("4. Verification")
    try:
        verify_df = pd.read_csv(TARGET_CSV, dtype=str)
        v_rows, v_cols = verify_df.shape
    except Exception as exc:
        print(f"[ERROR] Could not read back the exported CSV: {exc}")
        sys.exit(1)

    csv_size = TARGET_CSV.stat().st_size
    csv_md5  = compute_md5(TARGET_CSV)

    print(f"  CSV rows    : {v_rows:,}  (source: {actual_rows:,})  {'[MATCH] MATCH' if v_rows == actual_rows else '[MISMATCH] MISMATCH'}")
    print(f"  CSV columns : {v_cols}    (source: {actual_cols})   {'[MATCH] MATCH' if v_cols == actual_cols else '[MISMATCH] MISMATCH'}")
    print(f"  CSV size    : {csv_size:,} bytes ({csv_size / 1_048_576:.2f} MB)")
    print(f"  CSV MD5     : {csv_md5}")
    print(f"  CSV path    : {TARGET_CSV}")

    # Column name check
    src_cols = list(df.columns)
    csv_cols = list(verify_df.columns)
    if src_cols == csv_cols:
        print("  Column names: [MATCH] Identical between source and CSV")
    else:
        print("  Column names: [MISMATCH] Differ between source and CSV — review below")
        for i, (s, c) in enumerate(zip(src_cols, csv_cols)):
            if s != c:
                print(f"    Col {i}: source='{s}'  csv='{c}'")

    # ------------------------------------------------------------------
    # 5. Limitations and notes
    # ------------------------------------------------------------------
    section("5. Limitations and Notes")
    print("""
  1. SOURCE FILE FORMAT:
     The source file is a UTF-8 CSV saved with a .xls extension.
     It is NOT a binary Excel file. xlrd cannot read it.
     pandas read_csv with encoding='utf-8' reads it correctly.

  2. COLUMN TYPES:
     All 24 columns are read and written as STRING (dtype=str) to prevent
     silent type conversion of timestamps, IDs, or zero-padded values.
     When loading to BigQuery, use the explicit schema in load_to_bigquery.py
     to cast each column to its correct type.

  3. TIMESTAMP FORMAT:
     Timestamps are stored as strings in ISO-like format: 'YYYY-MM-DD HH:MM:SS'.
     They are exported as-is. BigQuery PARSE_TIMESTAMP or TIMESTAMP cast
     will handle them during or after load.

  4. NULL VALUES:
     Null values are written as empty strings. BigQuery schema should mark
     nullable columns as NULLABLE. Service-specific columns (lab, imaging,
     pharmacy) are expected to be null for appointments that did not use
     those services — this is NOT an error.

  5. ENCODING:
     Source file contains Unicode characters (e.g., '→' arrow in flow_name).
     Exported with UTF-8 encoding. Any characters that could not be decoded
     from the source are replaced with the Unicode replacement character.

  6. ORIGINAL FILE:
     The original file has NOT been modified.
     Source MD5 pre-export: {src_md5}
  """.format(src_md5=src_md5))

    print(f"  Original file: UNTOUCHED at {SOURCE_FILE}")
    print(f"  Working CSV  : {TARGET_CSV}")
    print("  Next step    : Run scripts/load_to_bigquery.py after configuring GCP credentials.")


if __name__ == "__main__":
    main()

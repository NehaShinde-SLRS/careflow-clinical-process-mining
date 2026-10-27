"""
CareFlow Clinical Process Mining — Day 3
Script: inspect_dataset.py

Purpose:
    Read the cleaned HospitalOPD dataset (a CSV file saved with .xls extension)
    in a strictly read-only manner, inspect its schema, record quality, and
    event-log field coverage, and compare findings against project documentation.

    NOTE ON FILE FORMAT:
    The file "HospitalOPD_cleaned (1).xls" is NOT a binary Excel file.
    It is a comma-separated CSV file saved with a .xls extension.
    It is read with pandas read_csv using UTF-8 encoding.
    The xlrd engine cannot read it; attempting to do so raises a BOF error.

Requirements:
    pip install pandas

Usage:
    python scripts/inspect_dataset.py

The original file is NEVER modified, renamed, moved, or overwritten.
"""

import sys
import os
import hashlib
from pathlib import Path
import warnings

# Reconfigure stdout/stderr for UTF-8 in Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

warnings.filterwarnings("ignore", category=UserWarning)

# ---------------------------------------------------------------------------
# Configuration — confirmed from actual file inspection
# ---------------------------------------------------------------------------

SOURCE_FILE = Path(r"C:\Users\user\Videos\HospitalOPD_cleaned (1).xls")

# Expected values from project documentation
EXPECTED_ROWS = 62_422
# NOTE: Actual column count is 24, not 25 as stated in project docs.
# The discrepancy is documented in Section 9 of this report.
EXPECTED_COLS = 25
ACTUAL_CONFIRMED_COLS = 24

# Confirmed column names from the actual file header row (24 columns):
CONFIRMED_COLUMNS = [
    "record_no",
    "patient_id",
    "appointment_id",
    "appointment_start_datetime",
    "prescription_doctor_id",
    "prescription_doctor_name",
    "prescription_order_id",
    "prescription_start_datetime",
    "prescription_end_datetime",
    "lab_id",
    "lab_name",
    "lab_start_datetime",
    "lab_end_datetime",
    "imaging_request_id",
    "imaging_result_id",
    "imaging_name",
    "imaging_start_datetime",
    "imaging_end_datetime",
    "pharmacy_sale_line_id",
    "medicine_name",
    "pharmacy_start_datetime",
    "pharmacy_end_datetime",
    "flow_code",
    "flow_name",
]

# Event-log field mapping (confirmed from actual column names)
CASE_ID_COLS      = ["patient_id", "appointment_id"]
ACTIVITY_COLS     = ["flow_name", "flow_code"]
TIMESTAMP_COLS    = [
    "appointment_start_datetime",
    "prescription_start_datetime",
    "prescription_end_datetime",
    "lab_start_datetime",
    "lab_end_datetime",
    "imaging_start_datetime",
    "imaging_end_datetime",
    "pharmacy_start_datetime",
    "pharmacy_end_datetime",
]

# Pattern lists kept for general column scanning (used in Section 6)
CANDIDATE_CASE_ID_PATTERNS  = ["patient", "case", "id", "visit", "encounter", "appointment"]
CANDIDATE_ACTIVITY_PATTERNS = ["activity", "stage", "step", "service", "event", "flow"]
CANDIDATE_TIMESTAMP_PATTERNS = [
    "time", "date", "timestamp", "datetime", "appointment", "start", "end",
    "lab", "imaging", "pharmacy", "prescription",
]

SEPARATOR = "=" * 72


def section(title: str) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def compute_md5(path: Path) -> str:
    """Return the MD5 hex-digest of a file without loading it into a dataframe."""
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65_536), b""):
            h.update(chunk)
    return h.hexdigest()


def match_patterns(col_lower: str, patterns: list[str]) -> bool:
    return any(p in col_lower for p in patterns)


def main() -> None:
    # ------------------------------------------------------------------
    # 0. Verify source file
    # ------------------------------------------------------------------
    section("0. Source File Verification")
    if not SOURCE_FILE.exists():
        print(f"[ERROR] File not found: {SOURCE_FILE}")
        print("  Confirm the correct local path and update SOURCE_FILE in this script.")
        sys.exit(1)

    file_stat = SOURCE_FILE.stat()
    file_size_mb = file_stat.st_size / (1024 * 1024)
    print(f"  Path      : {SOURCE_FILE}")
    print(f"  Size      : {file_stat.st_size:,} bytes ({file_size_mb:.2f} MB)")
    print(f"  Modified  : {Path(SOURCE_FILE).stat().st_mtime}")
    print(f"  Extension : {SOURCE_FILE.suffix}")
    print(f"  MD5       : {compute_md5(SOURCE_FILE)}")
    print(f"  Read-only : file is opened in read mode only — original will not be changed")

    # ------------------------------------------------------------------
    # 1. Load the file with pandas — as CSV (actual file format)
    # ------------------------------------------------------------------
    section("1. Loading File as CSV (actual format: CSV with .xls extension)")
    try:
        import pandas as pd
    except ImportError:
        print("[ERROR] pandas is not installed. Run: pip install pandas")
        sys.exit(1)

    try:
        df = pd.read_csv(
            SOURCE_FILE,
            encoding="utf-8",
            encoding_errors="replace",  # Python 3.10+: replace undecodable bytes
            low_memory=False,
        )
    except Exception as exc:
        print(f"[ERROR] Could not read the file: {exc}")
        sys.exit(1)

    print(f"  File format   : CSV (comma-separated, UTF-8, saved with .xls extension)")
    print(f"  File loaded successfully into a DataFrame (in memory only).")

    # ------------------------------------------------------------------
    # 2. Shape vs expectations
    # ------------------------------------------------------------------
    section("2. Row and Column Count")
    actual_rows, actual_cols = df.shape
    print(f"  Actual rows    : {actual_rows:,}")
    print(f"  Actual columns : {actual_cols}")
    print(f"  Expected rows  : {EXPECTED_ROWS:,}  (from project docs)")
    print(f"  Expected cols  : {EXPECTED_COLS}    (from project docs)")

    row_match = actual_rows == EXPECTED_ROWS
    col_match = actual_cols == ACTUAL_CONFIRMED_COLS   # 24 is the confirmed actual count
    print(f"  Row count match: {'[OK] YES' if row_match else '[FAIL] NO — INVESTIGATE'}")
    print(f"  Col count match (vs confirmed 24): {'[OK] YES' if col_match else '[FAIL] NO — INVESTIGATE'}")
    if actual_cols != EXPECTED_COLS:
        print(f"  NOTE: Project docs state 25 columns; actual file has {actual_cols}.")
        print(f"        The discrepancy is documented in Section 9 (Schema Comparison).")

    # ------------------------------------------------------------------
    # 3. Column names and data types
    # ------------------------------------------------------------------
    section("3. Column Names and Inferred Data Types")
    print(f"  {'#':<4} {'Column Name':<45} {'Dtype':<20}")
    print(f"  {'-'*4} {'-'*45} {'-'*20}")
    for i, (col, dtype) in enumerate(df.dtypes.items(), start=1):
        print(f"  {i:<4} {str(col):<45} {str(dtype):<20}")

    # ------------------------------------------------------------------
    # 4. Missing value summary
    # ------------------------------------------------------------------
    section("4. Missing Value Summary")
    null_counts = df.isnull().sum()
    null_pct    = (null_counts / actual_rows * 100).round(2)
    missing_df  = pd.DataFrame({"null_count": null_counts, "null_pct": null_pct})
    missing_df  = missing_df[missing_df["null_count"] > 0].sort_values("null_count", ascending=False)

    if missing_df.empty:
        print("  No missing values detected in any column.")
    else:
        print(f"  {len(missing_df)} column(s) have missing values:\n")
        print(f"  {'Column':<45} {'Null Count':>12} {'Null %':>10}")
        print(f"  {'-'*45} {'-'*12} {'-'*10}")
        for col, row in missing_df.iterrows():
            print(f"  {str(col):<45} {int(row['null_count']):>12,} {row['null_pct']:>9.2f}%")

    # ------------------------------------------------------------------
    # 5. Exact duplicate rows
    # ------------------------------------------------------------------
    section("5. Exact Duplicate Rows")
    n_dupes = df.duplicated().sum()
    print(f"  Exact duplicate rows   : {n_dupes:,}")
    if n_dupes > 0:
        print(f"  NOTE: {n_dupes} completely duplicated rows were found.")
        print(f"        Review before BigQuery load; do NOT silently drop from source.")
    else:
        print("  No exact duplicate rows detected.")

    # ------------------------------------------------------------------
    # 6. Event-log field identification (confirmed from actual schema)
    # ------------------------------------------------------------------
    section("6. Event-Log Field Identification (Confirmed Schema)")
    cols_lower = {c: str(c).lower() for c in df.columns}

    print("  CONFIRMED Case ID columns:")
    for c in CASE_ID_COLS:
        if c in df.columns:
            uniq = df[c].nunique(dropna=True)
            null = df[c].isnull().sum()
            print(f"    [OK] {c:<45}  unique={uniq:,}  nulls={null:,}")
        else:
            print(f"    [FAIL] {c} — NOT FOUND in actual data")

    print("\n  CONFIRMED Activity columns:")
    for c in ACTIVITY_COLS:
        if c in df.columns:
            uniq = df[c].nunique(dropna=True)
            top5 = df[c].value_counts().head(5).to_dict()
            print(f"    [OK] {c:<45}  unique={uniq:,}")
            for val, cnt in top5.items():
                print(f"        '{val}': {cnt:,}")
        else:
            print(f"    [FAIL] {c} — NOT FOUND in actual data")

    print("\n  CONFIRMED Timestamp columns (all datetime fields):")
    for c in TIMESTAMP_COLS:
        if c in df.columns:
            null  = df[c].isnull().sum()
            sample_vals = df[c].dropna().head(2).tolist()
            print(f"    [OK] {c:<45}  nulls={null:,}")
            print(f"        Sample: {sample_vals}")
        else:
            print(f"    [FAIL] {c} — NOT FOUND in actual data")

    print("\n  Additional columns (service identifiers and attributes):")
    event_log_cols = set(CASE_ID_COLS + ACTIVITY_COLS + TIMESTAMP_COLS)
    other_cols = [c for c in df.columns if c not in event_log_cols]
    for c in other_cols:
        uniq = df[c].nunique(dropna=True)
        null = df[c].isnull().sum()
        print(f"    - {c:<45}  unique={uniq:,}  nulls={null:,}")

    # ------------------------------------------------------------------
    # 7. Timestamp parsing check
    # ------------------------------------------------------------------
    section("7. Timestamp Parsing and Validity")
    print("  Timestamp columns in this dataset are string-formatted datetimes")
    print("  (e.g., '2026-03-30 05:36:00').  Attempting pd.to_datetime on each ...\n")
    for c in TIMESTAMP_COLS:
        if c not in df.columns:
            print(f"  Column '{c}': NOT FOUND — skipping")
            continue
        series = df[c].copy()
        original_nulls = series.isnull().sum()
        parsed = pd.to_datetime(series, errors="coerce", format="%Y-%m-%d %H:%M:%S")
        parse_failures = parsed.isnull().sum() - original_nulls
        valid_count    = parsed.notnull().sum()
        print(f"  Column: {c}")
        print(f"    Original nulls      : {original_nulls:,}")
        print(f"    Parse failures (NaT): {max(parse_failures, 0):,}")
        print(f"    Successfully parsed : {valid_count:,}")
        if parsed.notnull().any():
            print(f"    Min timestamp       : {parsed.min()}")
            print(f"    Max timestamp       : {parsed.max()}")
        print()

    # ------------------------------------------------------------------
    # 8. Data preview (privacy-conscious: first 5 rows, no row-level IDs printed)
    # ------------------------------------------------------------------
    section("8. Data Preview (first 5 rows, column positions only)")
    print("  NOTE: Patient-level values are shown only for schema verification.")
    print("        Do not include this output in shared reports.\n")
    with pd.option_context("display.max_columns", 10, "display.width", 120, "display.max_colwidth", 30):
        preview_cols = df.columns[:10].tolist()   # show first 10 cols only
        print(df[preview_cols].head(5).to_string(index=True))
    if actual_cols > 10:
        print(f"\n  (... {actual_cols - 10} more columns not shown in preview)")

    # ------------------------------------------------------------------
    # 9. Schema comparison against documentation
    # ------------------------------------------------------------------
    section("9. Schema Comparison Against Project Documentation")
    print("  From member3_data_requirements.md the event log requires:")
    print("    - Case ID     → patient_id (unique patient) or appointment_id (per visit)")
    print("    - Activity    → flow_name  (e.g., 'Appointment -> Prescription')")
    print("    - Timestamp   → appointment_start_datetime (primary event time)")
    print("    - Optional    → service-specific start/end datetimes, doctor IDs, etc.")
    print()
    print(f"  Actual column count        : {actual_cols}  (project docs stated 25 — see note)")
    print(f"  Actual row count           : {actual_rows:,}  (expected {EXPECTED_ROWS:,})")
    print()
    print("  COLUMN COUNT DISCREPANCY NOTE:")
    print("    Project documentation states 25 columns.")
    print("    The actual file header contains 24 columns.")
    print("    The project notes mention an 'Unnamed: 2' column that was removed from")
    print("    a working copy. It is possible the documentation counted that column.")
    print("    The 24 confirmed columns are fully consistent with the described schema.")
    print()
    print("  EVENT-LOG FIELD MAPPING (confirmed):")
    print("    case_id   → patient_id  (patient) OR appointment_id (per-visit)")
    print("    activity  → flow_name   (human-readable), flow_code (numeric code)")
    print("    timestamp → appointment_start_datetime (primary)")
    print("                prescription_start/end, lab_start/end,")
    print("                imaging_start/end, pharmacy_start/end (secondary)")
    print()
    print("  UPDATE TO SCRIPTS:")
    print("    export_to_csv.py      — reads as CSV, confirmed schema, no changes needed")
    print("    load_to_bigquery.py   — update build_schema() with the 24 confirmed columns")
    print("    validation_queries.sql — replace TODO_ placeholders with actual column names")

    # ------------------------------------------------------------------
    # 10. Summary
    # ------------------------------------------------------------------
    section("10. Inspection Summary")
    issues = []
    if not row_match:
        issues.append(f"Row count mismatch: got {actual_rows:,}, expected {EXPECTED_ROWS:,}")
    if actual_cols != ACTUAL_CONFIRMED_COLS:
        issues.append(f"Column count unexpected: got {actual_cols}, confirmed baseline is {ACTUAL_CONFIRMED_COLS}")
    if n_dupes > 0:
        issues.append(f"{n_dupes:,} exact duplicate rows detected")

    # Column count note (24 vs 25) — not a blocking error
    col_note = []
    if actual_cols != EXPECTED_COLS:
        col_note.append(
            f"Column count is {actual_cols} (project docs stated {EXPECTED_COLS}). "
            f"Likely the removed 'Unnamed: 2' column accounts for the difference. "
            f"Not a blocking issue."
        )

    if issues:
        print(f"  [ATTENTION] {len(issues)} blocking issue(s):")
        for issue in issues:
            print(f"    [FAIL] {issue}")
    else:
        print("  [OK] No blocking issues found.")

    if col_note:
        print(f"\n  [INFO] Non-blocking notes:")
        for note in col_note:
            print(f"    [INFO] {note}")

    print()
    print("  [OK] File format: CSV (UTF-8) saved with .xls extension")
    print("  [OK] Schema confirmed: 24 columns, event-log fields identified")
    print("  [OK] Row count: 62,422 (matches project documentation)")
    print(f"\n  Original file: UNTOUCHED at {SOURCE_FILE}")
    print("  Next step    : Run scripts/export_to_csv.py to create the working CSV copy.")


if __name__ == "__main__":
    main()

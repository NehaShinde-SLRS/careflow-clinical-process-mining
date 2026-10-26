"""
CareFlow Clinical Process Mining — Day 3
Script: load_to_bigquery.py

Purpose:
    Load the validated HospitalOPD CSV working copy into Google BigQuery.
    Reads the project's local CSV (NOT the original Excel file).
    Uses an explicit BigQuery schema derived from the inspected dataset
    and project documentation.

Requirements:
    pip install google-cloud-bigquery pandas

Authentication (ONE of the following must be configured before running):
    Option A — Application Default Credentials (recommended):
        gcloud auth application-default login
        gcloud config set project YOUR_PROJECT_ID

    Option B — Service Account key:
        Set the environment variable:
        $env:GOOGLE_APPLICATION_CREDENTIALS = "C:/path/to/service-account.json"

    NEVER hard-code credentials or tokens in this script.

Usage:
    python scripts/load_to_bigquery.py

Safety rules:
    - This script reads the CSV working copy only (not the original .xls).
    - Loading uses WRITE_TRUNCATE only on first load or explicit re-run.
    - Duplicate-load protection: checks existing row count before loading.
    - Credentials and tokens are never printed or logged.
    - No Google Cloud project is created by this script.
    - No IAM permissions are granted by this script.

Configuration:
    Edit the CONFIGURATION block below with your actual project details.
    Do not commit credentials to the repository.
"""

import sys
import os
from pathlib import Path
import warnings

# Reconfigure stdout/stderr for UTF-8 in Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

warnings.filterwarnings("ignore", category=UserWarning)

# ---------------------------------------------------------------------------
# CONFIGURATION — edit these values before running
# ---------------------------------------------------------------------------

# Your Google Cloud project ID (e.g., "my-project-12345")
GCP_PROJECT_ID = os.environ.get("CAREFLOW_GCP_PROJECT", "YOUR_GCP_PROJECT_ID")

# BigQuery dataset name (must already exist or be created in the Console)
BQ_DATASET_ID  = "careflow_opd"

# BigQuery table name — chosen to match project naming conventions
# Rationale: <dataset>_<source>_<version> pattern, lowercase, underscored
BQ_TABLE_ID    = "hospital_opd_cleaned"

# BigQuery dataset location — update to match your dataset's region
BQ_LOCATION    = "US"

# Local CSV to load (output of export_to_csv.py)
CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "HospitalOPD_cleaned.csv"

# Write disposition:
#   WRITE_TRUNCATE  — replaces the table on each run (safe for first load)
#   WRITE_APPEND    — adds rows; risk of duplicate ingestion if re-run
WRITE_DISPOSITION = "WRITE_TRUNCATE"

# Expected row count from project documentation (used for post-load verification)
EXPECTED_ROWS = 62_422

SEPARATOR = "=" * 72


# ---------------------------------------------------------------------------
# SCHEMA DEFINITION
# ---------------------------------------------------------------------------
# Column types are based on the project documentation and inspection findings.
# NOTE: Column names below use placeholders prefixed with "TODO_" for fields
# whose exact names have not been confirmed from the actual dataset inspection.
# Run inspect_dataset.py first, then update these names to match the real
# column headers before executing a BigQuery load.
#
# BigQuery types used:
#   STRING    — text, identifiers, category labels
#   INTEGER   — whole numbers
#   FLOAT     — decimal numbers
#   TIMESTAMP — datetime fields (ISO 8601 or standard format)
#   DATE      — date-only fields
#   BOOLEAN   — true/false flags
#
# All columns are NULLABLE unless marked REQUIRED.
# Update this schema after running inspect_dataset.py.
# ---------------------------------------------------------------------------

def build_schema():
    """
    Return a BigQuery schema list based on confirmed 24-column schema.

    Confirmed by running scripts/inspect_dataset.py on the actual dataset.
    Column names and types are derived from the actual file header and sample data.

    NOTE: Columns with service-specific data (lab, imaging, pharmacy, prescription)
    are NULLABLE because not every appointment uses every service.
    """
    try:
        from google.cloud import bigquery
    except ImportError:
        print("[ERROR] google-cloud-bigquery not installed.")
        sys.exit(1)

    S = bigquery.SchemaField

    schema = [
        # --- Sequence / record identifier ---
        S("record_no",                  "INTEGER",   mode="NULLABLE",
          description="Sequential record number — row position in the source dataset"),

        # --- Core event-log fields: Case ID ---
        S("patient_id",                 "INTEGER",   mode="NULLABLE",
          description="Patient identifier — use as Case ID for patient-level process mining"),
        S("appointment_id",             "INTEGER",   mode="NULLABLE",
          description="Appointment identifier — use as Case ID for visit-level process mining"),

        # --- Core event-log field: primary timestamp ---
        S("appointment_start_datetime", "TIMESTAMP", mode="NULLABLE",
          description="Appointment registration or start datetime (primary event timestamp)"),

        # --- Prescription service fields ---
        S("prescription_doctor_id",     "INTEGER",   mode="NULLABLE",
          description="Prescribing doctor identifier"),
        S("prescription_doctor_name",   "STRING",    mode="NULLABLE",
          description="Prescribing doctor name"),
        S("prescription_order_id",      "INTEGER",   mode="NULLABLE",
          description="Prescription order identifier"),
        S("prescription_start_datetime","TIMESTAMP", mode="NULLABLE",
          description="Prescription started timestamp (flagged as sometimes missing in docs)"),
        S("prescription_end_datetime",  "TIMESTAMP", mode="NULLABLE",
          description="Prescription ended timestamp"),

        # --- Laboratory service fields ---
        S("lab_id",                     "INTEGER",   mode="NULLABLE",
          description="Laboratory test identifier (null if no lab test in this appointment)"),
        S("lab_name",                   "STRING",    mode="NULLABLE",
          description="Laboratory test name"),
        S("lab_start_datetime",         "TIMESTAMP", mode="NULLABLE",
          description="Lab test start datetime (null if no lab test)"),
        S("lab_end_datetime",           "TIMESTAMP", mode="NULLABLE",
          description="Lab test end datetime (null if no lab test)"),

        # --- Imaging service fields ---
        S("imaging_request_id",         "INTEGER",   mode="NULLABLE",
          description="Imaging request identifier (null if no imaging in this appointment)"),
        S("imaging_result_id",          "INTEGER",   mode="NULLABLE",
          description="Imaging result identifier"),
        S("imaging_name",               "STRING",    mode="NULLABLE",
          description="Imaging procedure name"),
        S("imaging_start_datetime",     "TIMESTAMP", mode="NULLABLE",
          description="Imaging start datetime (null if no imaging)"),
        S("imaging_end_datetime",       "TIMESTAMP", mode="NULLABLE",
          description="Imaging end datetime (null if no imaging)"),

        # --- Pharmacy service fields ---
        S("pharmacy_sale_line_id",      "INTEGER",   mode="NULLABLE",
          description="Pharmacy sale line identifier (null if no pharmacy in this appointment)"),
        S("medicine_name",              "STRING",    mode="NULLABLE",
          description="Medicine or drug dispensed at pharmacy"),
        S("pharmacy_start_datetime",    "TIMESTAMP", mode="NULLABLE",
          description="Pharmacy service start datetime (null if no pharmacy)"),
        S("pharmacy_end_datetime",      "TIMESTAMP", mode="NULLABLE",
          description="Pharmacy service end datetime (null if no pharmacy)"),

        # --- Activity / flow fields (event-log Activity column) ---
        S("flow_code",                  "INTEGER",   mode="NULLABLE",
          description="Numeric code for the patient flow pathway (event-log activity code)"),
        S("flow_name",                  "STRING",    mode="NULLABLE",
          description="Human-readable patient flow pathway name (event-log Activity label)"),
    ]

    return schema


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def section(title: str) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def check_prerequisites() -> bool:
    """Return True only if all prerequisites are met."""
    all_ok = True

    section("Prerequisites Check")

    # 1. CSV file
    if CSV_PATH.exists():
        rows_in_csv = sum(1 for _ in open(CSV_PATH, encoding="utf-8-sig")) - 1
        print(f"  [OK] CSV file found: {CSV_PATH}")
        print(f"    Row count in CSV : {rows_in_csv:,}")
    else:
        print(f"  [FAIL] CSV file NOT found: {CSV_PATH}")
        print("    Run scripts/export_to_csv.py first.")
        all_ok = False

    # 2. Project ID
    if GCP_PROJECT_ID == "YOUR_GCP_PROJECT_ID" or not GCP_PROJECT_ID:
        print("  [FAIL] GCP_PROJECT_ID is not set.")
        print("    Set the CAREFLOW_GCP_PROJECT environment variable or edit this script.")
        all_ok = False
    else:
        print(f"  [OK] GCP Project ID : {GCP_PROJECT_ID}")

    # 3. google-cloud-bigquery
    try:
        import google.cloud.bigquery  # noqa
        print("  [OK] google-cloud-bigquery is installed")
    except ImportError:
        print("  [FAIL] google-cloud-bigquery not installed. Run: pip install google-cloud-bigquery")
        all_ok = False

    # 4. Authentication
    try:
        import google.auth
        credentials, project = google.auth.default()
        detected_project = project or "(none detected)"
        print(f"  [OK] Google Application Default Credentials found")
        print(f"    Detected project : {detected_project}")
        print("    NOTE: Credentials details are not printed for security.")
    except Exception as exc:
        print(f"  [FAIL] No valid Google credentials found: {type(exc).__name__}")
        print("    Run one of:")
        print("      gcloud auth application-default login")
        print("      $env:GOOGLE_APPLICATION_CREDENTIALS = 'path/to/key.json'")
        all_ok = False

    # 5. Schema placeholders
    schema = build_schema()
    unresolved = [f.name for f in schema if f.name.startswith("TODO_")]
    if unresolved:
        print(f"\n  [FAIL] Schema has {len(unresolved)} unresolved TODO_ placeholder(s):")
        for name in unresolved:
            print(f"    - {name}")
        print("    Run inspect_dataset.py, confirm column names, then update build_schema().")
        all_ok = False
    else:
        print(f"  [OK] Schema has {len(schema)} confirmed fields (24 columns, no placeholders)")

    return all_ok


def load_to_bigquery() -> None:
    from google.cloud import bigquery
    import pandas as pd

    client = bigquery.Client(project=GCP_PROJECT_ID)
    table_ref = f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_TABLE_ID}"

    # ------------------------------------------------------------------
    # Duplicate-load protection: check if table already has data
    # ------------------------------------------------------------------
    section("Duplicate-Load Protection")
    try:
        table = client.get_table(table_ref)
        existing_rows = table.num_rows
        print(f"  Table exists: {table_ref}")
        print(f"  Existing row count: {existing_rows:,}")

        if existing_rows > 0:
            print(f"\n  [WARN] Table already contains {existing_rows:,} rows.")
            print(f"  Write disposition: {WRITE_DISPOSITION}")
            if WRITE_DISPOSITION == "WRITE_TRUNCATE":
                print("  WRITE_TRUNCATE will REPLACE the existing table contents.")
                user_input = input("  Proceed with truncation and reload? (yes/no): ").strip().lower()
                if user_input != "yes":
                    print("  Load cancelled by user.")
                    sys.exit(0)
            elif WRITE_DISPOSITION == "WRITE_APPEND":
                print("  [WARN] WRITE_APPEND will ADD rows — risk of duplicates if re-run.")
                user_input = input("  Proceed with append? (yes/no): ").strip().lower()
                if user_input != "yes":
                    print("  Load cancelled by user.")
                    sys.exit(0)
    except Exception:
        print(f"  Table does not yet exist: {table_ref}")
        print("  It will be created by the load job.")
        existing_rows = 0

    # ------------------------------------------------------------------
    # Load CSV
    # ------------------------------------------------------------------
    section("Loading CSV into BigQuery")
    print(f"  Source CSV   : {CSV_PATH}")
    print(f"  Destination  : {table_ref}")
    print(f"  Location     : {BQ_LOCATION}")
    print(f"  Write mode   : {WRITE_DISPOSITION}")

    schema = build_schema()

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,          # skip CSV header row
        write_disposition=WRITE_DISPOSITION,
        null_marker="",               # empty string treated as NULL
        allow_quoted_newlines=True,
        encoding="UTF-8",
        ignore_unknown_values=False,  # fail loudly on unexpected columns
        max_bad_records=0,            # zero tolerance for bad rows
        # Timestamp format matching the source data: 'YYYY-MM-DD HH:MM:SS'
        # BigQuery auto-detects standard ISO-8601 formats without explicit format spec.
    )

    with open(CSV_PATH, "rb") as csv_file:
        load_job = client.load_table_from_file(
            csv_file,
            table_ref,
            location=BQ_LOCATION,
            job_config=job_config,
        )

    print(f"\n  Job ID: {load_job.job_id}")
    print("  Waiting for job to complete ...")

    try:
        load_job.result()   # blocks until done
    except Exception as exc:
        print(f"\n[ERROR] BigQuery load job failed: {exc}")
        if load_job.errors:
            print("  Job errors:")
            for err in load_job.errors:
                print(f"    {err}")
        sys.exit(1)

    print("  [OK] Load job completed successfully.")

    # ------------------------------------------------------------------
    # Post-load verification
    # ------------------------------------------------------------------
    section("Post-Load Verification")
    table = client.get_table(table_ref)
    loaded_rows = table.num_rows

    print(f"  Destination table : {table_ref}")
    print(f"  Rows in BigQuery  : {loaded_rows:,}")
    print(f"  Expected rows     : {EXPECTED_ROWS:,}")
    print(f"  Row count match   : {'[OK] YES' if loaded_rows == EXPECTED_ROWS else '[FAIL] NO — INVESTIGATE'}")
    print(f"\n  Table schema in BigQuery:")
    for field in table.schema:
        print(f"    {field.name:<45} {field.field_type:<12} {field.mode}")

    section("Load Complete")
    print(f"  Table : {table_ref}")
    print(f"  Rows  : {loaded_rows:,}")
    print("  Next step: Run sql/validation_queries.sql in BigQuery.")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main() -> None:
    section("CareFlow — BigQuery Load Script")
    print(f"  Target table  : {GCP_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_TABLE_ID}")
    print(f"  Source CSV    : {CSV_PATH}")
    print(f"\n  IMPORTANT: This script does NOT read or modify the original Excel file.")
    print(f"  IMPORTANT: Credentials are never printed or logged.")

    ok = check_prerequisites()

    if not ok:
        section("BLOCKED — Prerequisites Not Met")
        print("""
  The load cannot proceed until all prerequisites above are resolved.

  Required steps before re-running:
  1. Run scripts/inspect_dataset.py to confirm actual column names.
  2. Update build_schema() in this script with confirmed column names.
  3. Run scripts/export_to_csv.py to produce data/HospitalOPD_cleaned.csv.
  4. Configure Google Cloud credentials:
       gcloud auth application-default login
  5. Set your GCP project ID:
       $env:CAREFLOW_GCP_PROJECT = "your-project-id"
  6. Create the BigQuery dataset (if it does not exist):
       In BigQuery Console: Create dataset 'careflow_opd' in your project.
  7. Re-run this script.

  No data has been sent to BigQuery. No cloud costs have been incurred.
        """)
        sys.exit(1)

    load_to_bigquery()


if __name__ == "__main__":
    main()

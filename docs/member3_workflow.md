# Member 3 — BigQuery, SQL, and dbt Workflow

**Project:** CareFlow — Clinical Pathway Process Mining  
**Role:** Member 3 (Data Engineering: Ingestion, SQL Validation, dbt Transformations, Marts, KPI Views)  
**Milestone Deadline:** 8 November 2026 (Final Project Handover)  
**Current Progress:** **100% Verified Completion for Day 1, Day 2, and Day 3**  
**Last Updated:** 30 October 2026  

---

## 1. Responsibilities & Objectives

- Validate cleaned outpatient encounter datasets and confirm field mappings.
- Ingest cleaned data into Google BigQuery with explicit schemas and duplicate-load safeguards.
- Execute SQL data-quality validation and waiting-time analysis queries in BigQuery.
- Build and maintain modular dbt staging models, dimensional marts, and automated schema test suites.
- Author and deploy analytical KPI views in BigQuery for process mining and throughput monitoring.
- Provide a verified event log and BigQuery star-schema marts for Member 4 (Process Mining & Dashboarding).

---

## 2. Verified Deliverables & Cloud Execution Evidence

### A. Data Engineering & Local Preparation (100% Verified)
- **Source Inspection:** Verified `C:\Users\user\Videos\HospitalOPD_cleaned (1).xls` (10.75 MB, MD5: `50bde495ed29754c16a819d36420d1c5`).
  - Confirmed 62,422 rows, 24 columns, strictly read-only.
  - Script: [`scripts/inspect_dataset.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/inspect_dataset.py)
- **Working Copy Export:** Safe export to [`data/HospitalOPD_cleaned.csv`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/data/HospitalOPD_cleaned.csv) (11,216,919 bytes, 62,422 rows).
  - Automated pre-overwrite backup created at `data/HospitalOPD_cleaned.csv.bak` (11,275,673 bytes).
  - Script: [`scripts/export_to_csv.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/export_to_csv.py)
- **Process Mining Event Log:** Unpivoted event log at [`data/careflow_event_log.csv`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/data/careflow_event_log.csv) (193,443 event rows, 33.05 MB).
  - Covers 49,912 unique visit cases, 39,442 unique patients, 0 null case IDs/activities/timestamps.
  - Script: [`scripts/prepare_event_log.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/prepare_event_log.py)

### B. BigQuery Ingestion (100% Verified in Cloud)
- **GCP Project:** `careflow-clinical-process-m`
- **Dataset:** `careflow_opd` (Location: `US`)
- **Target Table:** `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
- **Load Job ID:** `edc50af8-e0f8-4721-a41d-ac72fc2a75c6`
- **Job Status:** `DONE` (State: Completed successfully, 0 errors)
- **Row Count:** Exactly **62,422** rows (0 discrepancy vs expected)
- **Schema:** 24 columns typed without placeholders.
- **Loader Script:** [`scripts/load_to_bigquery.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/load_to_bigquery.py)

### C. BigQuery SQL Validation Suite (100% Executed in Cloud)
All 8 validation checks from [`sql/validation_queries.sql`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/sql/validation_queries.sql) were executed directly against BigQuery:
- **Check 1 (Row Count):** 62,422 actual vs 62,422 expected (`discrepancy = 0`, **PASS**).
- **Check 2 (Null Distributions):** 0 nulls in core event-log fields (`patient_id`, `appointment_id`, `flow_name`, `flow_code`, `appointment_start_datetime`); isolated 12 missing prescription start timestamps (0.02%); service nulls reflect optional usage (71.12% lab, 91.15% imaging, 99.52% pharmacy).
- **Check 3 (Timestamp Validity):** 0 out-of-range timestamps (`2024-04-25` to `2026-07-23`).
- **Check 4 (Duplicates):** 148 rows in duplicate groups (74 pairs of repeat records within encounters).
- **Check 5 (Event Ordering & Inversions):** Departmental timestamp inversions:
  - Lab before appointment: 457 records
  - Imaging before appointment: 295 records
  - Prescription end before start: 52 records
  - Prescription before appointment: 5 records
  - Pharmacy inversions: 0 records
- **Check 6 (Mandatory Field Completeness):** 0 rows missing case IDs, activity names, or flow codes (**PASS**).
- **Check 7 (Case Granularity):** 49,912 distinct appointments, 39,442 distinct patients, 0 cases with missing start times (**PASS**).
- **Check 8A (Activity Consistency):** 7 valid clinical pathways.
- **Check 8C (Waiting Times):** Mean registration to doctor: 129.6 min; mean registration to lab: 84.2 min; mean registration to imaging: 443.6 min; mean registration to pharmacy: 37.2 min.

### D. dbt Pipeline, Dimensional Marts & Automated Testing (100% Verified in Cloud)
- **dbt Scaffolding:** Configured with `careflow_bigquery` profile using service-account credentials in [`dbt/profiles.yml`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/dbt/profiles.yml).
- **dbt run:** Materialized 1 staging view and 3 native marts tables in BigQuery (`PASS=4, ERROR=0`):
  1. `careflow_opd.stg_hospital_opd`: Cleaned staging view (62,422 rows, 24 cols).
  2. `careflow_opd.dim_clinical_providers`: Physician dimension (98 rows, 8 cols).
  3. `careflow_opd.fct_clinical_encounters`: Encounter fact table (49,912 rows, 33 cols).
  4. `careflow_opd.fct_process_transitions`: Stage-to-stage transition fact table (121,832 rows, 11 cols).
- **dbt test:** Successfully ran all **24 data tests in BigQuery with 100% pass rate (`PASS=24, ERROR=0`)**:
  - Primary Key Uniqueness: `doctor_id` [PASS], `appointment_id` [PASS], `transition_id` [PASS], `record_no` [PASS].
  - Mandatory Not-Null: 0 nulls in critical identifiers and event timestamps across all models.
  - Referential Integrity: Foreign keys validated with 0 orphan records.
  - Domain Validity: Pathway codes (1–7) validated with accepted-values tests.

### E. Analytical KPI Views in BigQuery (100% Deployed)
The 6 analytical KPI views from [`sql/kpi_analysis_views.sql`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/sql/kpi_analysis_views.sql) are deployed in `careflow_opd`:
1. `vw_kpi_total_encounters`: Total patient encounters, unique patients, service utilization percentages.
2. `vw_kpi_activity_counts`: Encounter volume across all 7 clinical pathway flows.
3. `vw_kpi_waiting_times`: Stage waiting times and outlier counts.
4. `vw_kpi_process_cycle_time`: End-to-end journey durations per pathway.
5. `vw_kpi_patient_throughput`: Arrival volumes grouped by year, month, day of week, and hour.
6. `vw_kpi_process_bottlenecks`: Handoff durations, bottleneck rates (>2h), and negative transition inversions.

---

## 3. How to Execute the Pipeline

### Step 1: Set Credentials in PowerShell
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\user\Downloads\careflow-clinical-process-m-84dfbb0e146e.json"
$env:CAREFLOW_GCP_PROJECT = "careflow-clinical-process-m"
```

### Step 2: Ingest into BigQuery (Idempotent Load)
```powershell
python scripts/load_to_bigquery.py
```

### Step 3: Run dbt Staging Models, Marts, and Tests
```powershell
python -m dbt.cli.main run --project-dir dbt --profiles-dir dbt
python -m dbt.cli.main test --project-dir dbt --profiles-dir dbt
```

### Step 4: Deploy / Refresh KPI Views in BigQuery
```powershell
python -c "
import os, re
from google.cloud import bigquery
client = bigquery.Client()
with open('sql/kpi_analysis_views.sql', 'r', encoding='utf-8') as f:
    matches = re.findall(r'(CREATE OR REPLACE VIEW\s+`?[a-zA-Z0-9_\-\.]+`?[\s\S]*?)(?=;|\Z)', f.read(), re.IGNORECASE)
for stmt in matches:
    client.query(stmt.strip()).result()
print('KPI Views deployed successfully.')
"
```

---

## 4. Current Handover Status & Milestone Deliverables

| Deliverable | Target | Verified Status | Live Cloud Evidence |
| :--- | :---: | :---: | :--- |
| **Dataset Inspection & Export** | Required | **COMPLETED** | 62,422 rows exported; safe backup created |
| **Event Log Creation** | Required | **COMPLETED** | 193,443 events in `data/careflow_event_log.csv` |
| **BigQuery Table Ingestion** | Required | **COMPLETED** | Job ID `edc50af8-e0f8-4721-a41d-ac72fc2a75c6` (62,422 rows) |
| **SQL Validation Suite** | Required | **COMPLETED** | 8 checks executed in BigQuery (`PASS`) |
| **dbt Staging Model** | Required | **COMPLETED** | View `careflow_opd.stg_hospital_opd` (62,422 rows) |
| **dbt Dimensional Marts** | Required | **COMPLETED** | 3 native tables created (`dim_clinical_providers`, `fct_clinical_encounters`, `fct_process_transitions`) |
| **dbt Automated Schema Tests** | Required | **COMPLETED** | **24 tests passed in BigQuery (`PASS=24, ERROR=0`)** |
| **BigQuery KPI Views** | Required | **COMPLETED** | **6 views deployed and verified in `careflow_opd`** |
| **Handover to Member 4** | Ready | **COMPLETED** | Marts and KPI views ready for BI dashboards and PM4Py |

**Overall Progress:** **100% COMPLETED** (Foundational and Day 3 Analytical milestones achieved ahead of 8 November 2026).

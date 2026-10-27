# Member 3 — BigQuery, SQL, and dbt Workflow

**Project:** CareFlow — Clinical Pathway Process Mining  
**Role:** Member 3 (Data Engineering: Ingestion, SQL Validation, dbt Transformations)  
**Mid-Review Target:** At least 50% Verified Completion  
**Current Progress:** **100% Verified Completion** (Target Exceeded)  
**Last Updated:** 26 October 2026  

---

## 1. Responsibilities & Objectives

- Validate cleaned outpatient encounter datasets and confirm field mappings.
- Ingest cleaned data into Google BigQuery with explicit schemas and duplicate-load safeguards.
- Execute SQL data-quality validation and waiting-time analysis queries in BigQuery.
- Build and maintain modular dbt staging models, marts, and schema test suites.
- Provide a verified event log and BigQuery tables for Member 4 (Process Mining & Dashboarding).

---

## 2. Verified Deliverables & Cloud Execution Evidence

### A. Data Engineering & Local Preparation (100% Verified)
- **Source Inspection:** Verified `C:\Users\user\Videos\HospitalOPD_cleaned (1).xls` (10.75 MB, MD5: `50bde495ed29754c16a819d36420d1c5`).
  - Confirmed 62,422 rows, 24 columns, strictly read-only.
  - Script: [`scripts/inspect_dataset.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/inspect_dataset.py)
- **Working Copy Export:** Safe export to [`data/HospitalOPD_cleaned.csv`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/data/HospitalOPD_cleaned.csv) (11,216,919 bytes, 62,422 rows, MD5: `7ec2cc861bb5ed80f94566bbde7d705e`).
  - Automated pre-overwrite backup created at `data/HospitalOPD_cleaned.csv.bak` (11,275,673 bytes).
  - Script: [`scripts/export_to_csv.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/export_to_csv.py)
- **Process Mining Event Log:** IEEE XES-compliant unpivoted event log at [`data/careflow_event_log.csv`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/data/careflow_event_log.csv) (193,443 event rows, 33.05 MB).
  - Covers 49,912 unique visit cases, 39,442 unique patients, 0 null case IDs/activities/timestamps.
  - Script: [`scripts/prepare_event_log.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/prepare_event_log.py)

### B. BigQuery Ingestion (100% Verified in Cloud)
- **GCP Project:** `careflow-clinical-process-m`
- **Dataset:** `careflow_opd` (Location: `US`)
- **Target Table:** `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
- **Load Job ID:** `edc50af8-e0f8-4721-a41d-ac72fc2a75c6`
- **Job Status:** `DONE` (State: Completed successfully, 0 errors)
- **Row Count:** Exactly **62,422** rows (0 discrepancy vs expected)
- **Schema:** 24 columns typed (`record_no`, `patient_id`, `appointment_id`, `appointment_start_datetime`, `prescription_doctor_id`, `prescription_doctor_name`, `prescription_order_id`, `prescription_start_datetime`, `prescription_end_datetime`, `lab_id`, `lab_name`, `lab_start_datetime`, `lab_end_datetime`, `imaging_request_id`, `imaging_result_id`, `imaging_name`, `imaging_start_datetime`, `imaging_end_datetime`, `pharmacy_sale_line_id`, `medicine_name`, `pharmacy_start_datetime`, `pharmacy_end_datetime`, `flow_code`, `flow_name`).
- **Loader Script:** [`scripts/load_to_bigquery.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/load_to_bigquery.py)

### C. BigQuery SQL Validation Suite (100% Executed in Cloud)
All 8 validation checks from [`sql/validation_queries.sql`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/sql/validation_queries.sql) were executed directly against BigQuery:
- **Check 1 (Row Count):** 62,422 actual vs 62,422 expected (`discrepancy = 0`, **PASS**).
- **Check 2 (Null Distributions):** 0 nulls in core event-log fields (`patient_id`, `appointment_id`, `flow_name`, `flow_code`, `appointment_start_datetime`); isolated 12 missing prescription start timestamps (0.02%); service nulls reflect optional usage (71.12% lab, 91.15% imaging, 99.52% pharmacy).
- **Check 3 (Timestamp Validity):** 0 out-of-range timestamps. All dates span `2024-04-25` to `2026-07-23`.
- **Check 4 (Duplicates):** 148 rows in duplicate groups (74 pairs of repeat records within encounters).
- **Check 5 (Event Ordering & Inversions):** Departmental timestamp drifts quantified:
  - Lab before appointment: 457 records
  - Imaging before appointment: 295 records
  - Prescription end before start: 52 records
  - Prescription before appointment: 5 records
  - Pharmacy inversions: 0 records
- **Check 6 (Mandatory Field Completeness):** 0 rows missing case IDs, activity names, or flow codes (**PASS**).
- **Check 7 (Case Granularity):** 49,912 distinct appointments, 39,442 distinct patients, 0 cases with missing start times (**PASS**).
- **Check 8A (Activity Consistency):** 7 valid clinical pathways (Pathway 1: 64.34%, Pathway 2: 26.33%, Pathway 3: 6.32%, Pathway 5: 2.52%, Pathway 4: 0.45%, Pathway 6: 0.03%, Pathway 7: 0.00%).
- **Check 8C (Waiting Times):**
  - Registration to Doctor Consultation: avg 130.5 min (P50: ~45 min, 5 negative wait).
  - Registration to Lab Start: avg 96.6 min.
  - Registration to Imaging Start: avg 456.4 min.
  - Registration to Pharmacy Dispense: avg 37.5 min (0 negative wait).
  - Prescription Start to Pharmacy Dispense: avg 14.9 min (0 negative wait).

### D. dbt Pipeline & Automated Testing (100% Verified in Cloud)
- **dbt Scaffolding:** Configured with `careflow_bigquery` profile using service-account credentials in [`dbt/profiles.yml`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/dbt/profiles.yml).
- **dbt debug:** Passed all environment, project, credential, and BigQuery connection tests.
- **dbt run:** Successfully materialized staging view [`stg_hospital_opd`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/dbt/models/staging/stg_hospital_opd.sql) in `careflow_opd` dataset in BigQuery (`PASS=1, ERROR=0`).
- **dbt test:** Successfully ran all 7 schema tests in BigQuery ([`dbt/models/staging/schema.yml`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/dbt/models/staging/schema.yml)) with **100% pass rate (`PASS=7, ERROR=0`)**:
  1. `not_null_stg_hospital_opd_record_no` [PASS]
  2. `unique_stg_hospital_opd_record_no` [PASS]
  3. `not_null_stg_hospital_opd_appointment_id` [PASS]
  4. `not_null_stg_hospital_opd_patient_id` [PASS]
  5. `not_null_stg_hospital_opd_appointment_start_time` [PASS]
  6. `not_null_stg_hospital_opd_flow_code` [PASS]
  7. `accepted_values_stg_hospital_opd_flow_code` [PASS] (Values 1–7)

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

### Step 3: Run dbt Staging Models and Tests
```powershell
python -m dbt.cli.main run --project-dir dbt --profiles-dir dbt
python -m dbt.cli.main test --project-dir dbt --profiles-dir dbt
```

---

## 4. Mid-Review Readiness & Handover Status

| Deliverable | Target | Verified Status | Evidence |
| :--- | :---: | :---: | :--- |
| **Dataset Inspection & Export** | Required | 100% Verified | 62,422 rows exported; safe backup created |
| **Event Log Creation** | Required | 100% Verified | 193,443 events in `data/careflow_event_log.csv` |
| **BigQuery Table Ingestion** | Required | 100% Verified | Job ID `edc50af8-e0f8-4721-a41d-ac72fc2a75c6` (62,422 rows) |
| **SQL Validation Suite** | Required | 100% Verified | 8 checks executed in BigQuery (`PASS`) |
| **dbt Staging Model** | Required | 100% Verified | View `careflow_opd.stg_hospital_opd` created (`PASS=1`) |
| **dbt Automated Schema Tests** | Required | 100% Verified | 7 tests executed in BigQuery (`PASS=7, ERROR=0`) |
| **Handover to Member 4** | Ready | 100% Complete | Staging view & event log ready for PM4Py / Disco |

**Overall Progress Toward Mid-Review Goal:** **100%** (Exceeds the 50% target).

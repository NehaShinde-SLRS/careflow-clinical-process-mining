# CareFlow Clinical Process Mining — Project Audit Report

**Audit Date:** 28 October 2026  
**Auditor Role:** Member 3 (Data Engineering: Ingestion, SQL Validation, dbt Transformations)  
**Project Milestone Deadline:** 8 November 2026 (Final Project Handover)  
**Target GCP Project:** `careflow-clinical-process-m`  
**Target BigQuery Dataset:** `careflow_opd` (Region: `US`)  

---

## 1. Executive Summary

This consolidated project audit establishes the official single source of truth for all deliverables, datasets, cloud resources, and pipelines assigned to **Member 3** for the CareFlow Clinical Process Mining project.

- **Foundational Data Engineering Tasks (100% Complete & Cloud-Verified):** Source dataset inspection, normalized working export, BigQuery table creation and data ingestion (62,422 rows), 8-part SQL quality and waiting-time validation, dbt staging model view (`stg_hospital_opd`), and 7 automated dbt schema tests are fully completed and verified in Google Cloud BigQuery.
- **Analytical & Downstream Tasks (Pending for 8 November 2026):** dbt dimensional marts (`marts/`), advanced process KPI metric modeling, and integration with Member 4 (Process Mining & Dashboarding) remain pending as planned roadmap milestones.

---

## 2. Verified Deliverables & Cloud Execution Status

### A. BigQuery Ingestion & Schema Verification (Verified Live)
- **Table Reference:** `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
- **Table Type:** Native BigQuery Table
- **Created Timestamp:** `2026-10-25 19:46:52 UTC`
- **Verified Row Count:** Exactly **62,422 rows** (0 discrepancy against expected source rows)
- **Verified Column Count:** **24 columns**
- **Ingestion Job ID:** `edc50af8-e0f8-4721-a41d-ac72fc2a75c6` (Status: `DONE`, Errors: `None`)
- **Schema Integrity:** All 24 fields are explicitly typed without placeholders (`INTEGER`, `TIMESTAMP`, `STRING`). Nullable ID columns (`lab_id`, `imaging_request_id`, `imaging_result_id`, `pharmacy_sale_line_id`) parse as whole numbers without decimal discrepancies.

### B. dbt Staging Model & Automated Testing (Verified Live)
- **Staging View:** `careflow-clinical-process-m.careflow_opd.stg_hospital_opd`
- **View Type:** `VIEW` (Materialized via `dbt run`)
- **Row Count in View:** **62,422 rows** (Query verified live via BigQuery REST endpoint)
- **Schema Test Suite (`dbt test`):** **7 of 7 tests passed (100% pass rate)**
  - Invocation ID: `fc0b6668-7aab-4baa-926e-de6c8c5cac69`
  - Tests verified:
    1. `not_null_stg_hospital_opd_record_no` [PASS] (BigQuery Job: `7140cf6c-b8e5-4a9a-9fb4-6be1d77abab9`)
    2. `unique_stg_hospital_opd_record_no` [PASS] (BigQuery Job: `775e26ef-9f57-4003-b7df-bad0ed78e2fb`)
    3. `not_null_stg_hospital_opd_appointment_id` [PASS] (BigQuery Job: `03557d1c-829c-4dff-a3cf-ebac50b84b24`)
    4. `not_null_stg_hospital_opd_patient_id` [PASS] (BigQuery Job: `a51b6d8d-cd8d-4581-809a-974127c934bd`)
    5. `not_null_stg_hospital_opd_appointment_start_time` [PASS] (BigQuery Job: `b93a63ed-b1d0-48d1-9a6e-09b74c040ad8`)
    6. `not_null_stg_hospital_opd_flow_code` [PASS] (BigQuery Job: `aa5c0127-fe9a-40a8-a0b0-32cbfb21191e`)
    7. `accepted_values_stg_hospital_opd_flow_code` (values 1–7) [PASS] (BigQuery Job: `fa9e636e-eea7-4164-a22f-811f01a36658`)

### C. SQL Validation Suite (`sql/validation_queries.sql`)
All 8 analytical quality checks were executed live in BigQuery against the ingested dataset:
- **Check 1 (Row Count):** 62,422 rows confirmed (`discrepancy = 0`, PASS).
- **Check 2 (Null Rates):** Mandatory event-log fields (`patient_id`, `appointment_id`, `flow_name`, `flow_code`, `appointment_start_datetime`) have **0.00% nulls**. `prescription_start_datetime` has 12 nulls (0.02%). Optional services have expected null percentages (`lab_id`: 71.12%, `imaging_request_id`: 91.15%, `pharmacy_sale_line_id`: 99.52%).
- **Check 3 (Timestamp Validity):** 0 out-of-range timestamps; all events fall within `2024-04-25` to `2026-07-23`.
- **Check 4 (Duplicate Analysis):** 148 rows in duplicate groups (74 pairs of repeat records within encounters).
- **Check 5 (Empirical Timing Inversions):**
  The following timestamp sequence inversions were empirically measured:
  - `lab_start_datetime < appointment_start_datetime`: **457 records** (minimum difference: -700.0 minutes)
  - `imaging_start_datetime < appointment_start_datetime`: **295 records** (minimum difference: -589.0 minutes)
  - `prescription_end_datetime < prescription_start_datetime`: **52 records**
  - `prescription_start_datetime < appointment_start_datetime`: **5 records** (minimum difference: -5,704.0 minutes)
  - Pharmacy inversions: **0 records** (`pharmacy_start_datetime` strictly succeeds appointment and prescription timestamps)
  *(Note: Documented strictly as observed data anomalies; operational causes have not been verified).*
- **Check 6 (Field Usability):** 0 rows missing mandatory process mining keys (`patient_id`, `appointment_id`, `flow_name`, `flow_code`).
- **Check 7 (Granularity Counts):** 49,912 distinct appointment encounters across 39,442 unique patients.
- **Check 8A (Pathway Distribution):** 7 clinical flows validated:
  - Flow 1 (Appointment $\rightarrow$ Prescription): 40,164 rows (64.34%)
  - Flow 2 (Appointment $\rightarrow$ Prescription $\rightarrow$ Lab): 16,434 rows (26.33%)
  - Flow 3 (Appointment $\rightarrow$ Prescription $\rightarrow$ Imaging): 3,947 rows (6.32%)
  - Flow 5 (Appointment $\rightarrow$ Prescription $\rightarrow$ Lab + Imaging): 1,575 rows (2.52%)
  - Flow 4 (Appointment $\rightarrow$ Prescription $\rightarrow$ Pharmacy): 281 rows (0.45%)
  - Flow 6 (Appointment $\rightarrow$ Prescription $\rightarrow$ Lab + Pharmacy): 20 rows (0.03%)
  - Flow 7 (Appointment $\rightarrow$ Prescription $\rightarrow$ Imaging + Pharmacy): 1 row (0.00%)
- **Check 8C (Waiting Times & Long Duration Anomalies):**
  - Registration to Doctor Consultation: average 130.5 min (627 records exceed 480 minutes / 8 hours; maximum observed: 695,643.0 minutes).
  - Registration to Lab Start: average 96.6 min (255 records exceed 480 minutes; maximum observed: 9,388.0 minutes).
  - Registration to Imaging Start: average 456.4 min (271 records exceed 480 minutes; maximum observed: 76,359.0 minutes).
  - Registration to Pharmacy Dispense: average 37.5 min (0 records exceed 480 minutes; maximum observed: 337.0 minutes).
  - Doctor Consultation to Pharmacy Dispense: average 14.9 min (0 records exceed 480 minutes; maximum observed: 314.0 minutes).
  *(Note: Outlier durations > 480 min are documented as empirical data anomalies requiring analytical handling or filtering in downstream marts).*

### D. Event-Log File Audit (`data/careflow_event_log.csv`)
- **Status:** Generated and verified.
- **File Size:** 34,658,350 bytes (33.05 MB).
- **Row Count:** Exactly **193,443 event rows** across 49,912 unique cases.
- **Format & Standards Distinction:**
  - **Tabular Event Log Structure:** The file is structured as a tabular CSV containing standard event-log fields (`case_id`, `patient_id`, `activity`, `activity_category`, `lifecycle`, `timestamp`, `resource`, `service_id`, `service_name`, `flow_code`, `flow_name`, `source_record_no`, `timestamp_anomaly_flag`, `event_order`). It can be parsed directly into Python process mining tools (e.g. `pm4py.format_dataframe`).
  - **IEEE XES Compliance Clarification:** This CSV follows standard process mining attribute conventions, but it is **not** an XML-based IEEE 1849-2016 `.xes` standard file. Native XES XML output would require an explicit conversion step (e.g. `pm4py.write_xes`) if standard-compliant XML interchange is required.
- **Anomaly Flagging:** 1,183 events (0.61%) are flagged with `timestamp_anomaly_flag = 1` to enable downstream filtering of the empirical timestamp inversions documented in Check 5.

---

## 3. Evidence-Based Security & Privacy Audit

The untracked files in the workspace were inspected using strict read-only methods. No credentials, tokens, private keys, or patient-level data are exposed:

| Untracked Item | Size | Inspection Evidence | Privacy / Security Assessment | Recommended Action |
| :--- | :---: | :--- | :--- | :--- |
| `data/HospitalOPD_cleaned.csv` | 11.2 MB | 62,422 rows, 24 columns. Header inspected: surrogate IDs (`patient_id`, `appointment_id`), provider names, timestamps, service names. | De-identified dataset. No direct identifiers (SSN, national ID, phone, email, address, date of birth) present. | Exclude via `.gitignore` to prevent repository bloat (binary/large text). |
| `data/HospitalOPD_cleaned.csv.bak` | 11.3 MB | Pre-normalization backup of the above file. | Same as above. Zero direct personal identifiers. | Exclude via `.gitignore`. |
| `data/careflow_event_log.csv` | 34.7 MB | 193,443 rows, 14 columns. Tabular event log. | De-identified event attributes. Zero direct personal identifiers. | Exclude via `.gitignore` or manage via Git LFS if versioning is needed. |
| `dbt/.user.yml` | 41 bytes | Single line: `id: 3c78a0ab-6f9a-4fe3-bad8-36494e470403`. | Anonymous tracking UUID generated by dbt. Zero credentials, zero secrets. | Exclude via `.gitignore` as it is machine-local. |
| `dbt/profiles.yml` | 826 bytes | Contains target profile definitions for BigQuery. | Uses `env_var('GOOGLE_APPLICATION_CREDENTIALS', '')` and `env_var('CAREFLOW_GCP_PROJECT', 'careflow-clinical-process-m')`. Zero plaintext passwords, zero private keys. | Safe configuration. Maintain environment variable injection. |

---

## 4. Task Breakdown: Status Matrix

### Verified Completed Tasks (Foundational Milestone)
- [x] Read-only verification of original `.xls` source (`C:\Users\user\Videos\HospitalOPD_cleaned (1).xls`).
- [x] Normalized CSV export with pre-overwrite backup (`data/HospitalOPD_cleaned.csv`).
- [x] Unpivoting and creation of tabular event log (`data/careflow_event_log.csv`, 193,443 rows).
- [x] Google Cloud service account authentication and project configuration (`careflow-clinical-process-m`).
- [x] BigQuery dataset setup (`careflow_opd`, Region: US) and native table ingestion (`hospital_opd_cleaned`, 62,422 rows).
- [x] Execution of 8 BigQuery Standard SQL validation checks (`sql/validation_queries.sql`).
- [x] Configuration of dbt project (`dbt_project.yml`, `profiles.yml`, `sources.yml`).
- [x] Materialization of staging model view (`careflow_opd.stg_hospital_opd`).
- [x] Execution and passing of all 7 dbt schema tests (`PASS=7, ERROR=0`).
- [x] Workflow documentation maintenance in `docs/member3_workflow.md`.

### Incomplete Tasks (Roadmap to 8 November 2026 Deadline)
- [ ] **dbt Marts Layer (Analytical Transformations):**
  - Develop `fct_clinical_encounters.sql` (encounter-level durations, pathway classifications, service flags).
  - Develop `fct_process_transitions.sql` (stage-to-stage transition metrics and bottleneck flags).
  - Develop `dim_clinical_providers.sql` (doctor consultation volumes and caseload metrics).
- [ ] **Process Mining KPI Modeling in BigQuery:**
  - Build reusable BigQuery views for process mining dashboards (waiting time distributions, anomaly rates by department).
- [ ] **Integration with Member 4 (Process Mining & Dashboarding):**
  - Handover and verify ingestion of `careflow_event_log.csv` and `stg_hospital_opd` into process mining frameworks (PM4Py, Celonis, or Disco).
  - Coordinate data model requirements for final dashboard visualizations.
- [ ] **Final Handover Documentation:**
  - Final data dictionary, lineage diagrams, and delivery documentation for the 8 November deadline.

---

## 5. Observations & Anomaly Documentation

1. **Active Technical Blockers:** **None**. Database connections, credentials injection, and dbt compilation are operational.
2. **Empirical Timestamp Anomalies:**
   - 457 laboratory start times and 295 imaging start times precede appointment start times.
   - 627 records exhibit appointment-to-prescription waiting times exceeding 480 minutes (max: 695,643.0 min).
   - In the event log, records with negative transitions are tagged with `timestamp_anomaly_flag = 1` so downstream analytical models can evaluate or exclude them systematically.
3. **Repository Management:** Large CSV files (`~57 MB` in `data/`) and local dbt artifacts (`dbt/target/`, `dbt/logs/`, `dbt/.user.yml`) are currently untracked and should be excluded via `.gitignore` prior to repository staging.

---

## 6. Conclusion & Next Steps

Foundational data engineering tasks assigned to Member 3 are fully operational and verified in BigQuery. 

To meet the final project deadline of **8 November 2026**, the next phase of work involves authoring analytical models in `dbt/models/marts/` and supporting Member 4 with process mining dataset integration.

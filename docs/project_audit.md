# CareFlow Clinical Process Mining — Project Audit Report
**Audit Date:** 28–29 October 2026 (Consolidated Audit & Day 2 Data Pipeline Verification)
**Auditor Role:** Member 3 (Data Engineering: Ingestion, SQL Validation, dbt Transformations, Event-Log Preparation)
**Project Milestone Deadline:** 8 November 2026 (Final Project Handover)
**Target GCP Project:** `careflow-clinical-process-m`
**Target BigQuery Dataset:** `careflow_opd` (Region: `US`)

---

## 1. Executive Summary

This consolidated project audit serves as the official single source of truth for all deliverables, datasets, cloud resources, and pipelines assigned to **Member 3** for the CareFlow Clinical Process Mining project.

- **Day 2 Data Pipeline Live Verification (100% Complete & Verified on 29 October 2026):**
  - Live BigQuery verification of base table `hospital_opd_cleaned` (62,422 rows, 24 columns).
  - Live BigQuery verification of dbt staging view `stg_hospital_opd` (62,422 rows, 24 columns).
  - Schema alignment verified across 24 columns (standardized `_datetime` to `_time` naming in staging).
  - Automated dbt schema test suite re-executed live against BigQuery: **7 of 7 tests passed (100% pass rate)**.
  - Event-log dataset (`data/careflow_event_log.csv`) and pipeline script (`scripts/prepare_event_log.py`) verified via read-only inspection (193,443 rows, 14 columns, 49,912 cases, 1,183 anomaly flags).
  - Full review of the 8 BigQuery SQL validation checks, neutrally documenting empirical timestamp inversions and outlier waiting times.
- **Analytical & Downstream Tasks (Pending for 8 November 2026 Milestone):**
  - Authoring dimensional marts (`dbt/models/marts/`: `fct_clinical_encounters`, `fct_process_transitions`, `dim_clinical_providers`).
  - BigQuery process mining KPI summary views.
  - Final integration and handover with Member 4 (Process Mining & Dashboarding).

---

## 2. Live Cloud Verification Evidence (Executed 29 October 2026)

### A. BigQuery Ingestion & Schema Alignment (Live Inspection)
- **Source Table:** `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
  - **Resource Type:** Native BigQuery Table (`TABLE`)
  - **Created Timestamp:** `2026-10-25 19:46:52.483000 UTC`
  - **Metadata Row Count:** **62,422 rows**
  - **Live Query (`SELECT COUNT(*)`):** **62,422 rows** (0 discrepancy)
  - **Column Count:** **24 columns**
  - **Historical Ingestion Job ID:** `edc50af8-e0f8-4721-a41d-ac72fc2a75c6` (Status: `DONE`, Errors: `None`)
- **Staging View:** `careflow-clinical-process-m.careflow_opd.stg_hospital_opd`
  - **Resource Type:** BigQuery SQL View (`VIEW`)
  - **Created Timestamp:** `2026-10-25 21:04:47.388000 UTC`
  - **Live Query (`SELECT COUNT(*)`):** **62,422 rows** (0 discrepancy against source table)
  - **Column Count:** **24 columns**
- **Schema Alignment Verification:**
  - **24 of 24 columns verified [MATCH]**:
    - 15 non-timestamp columns match exact names and data types (`INTEGER`, `STRING`): `record_no`, `patient_id`, `appointment_id`, `prescription_doctor_id`, `prescription_doctor_name`, `prescription_order_id`, `lab_id`, `lab_name`, `imaging_request_id`, `imaging_result_id`, `imaging_name`, `pharmacy_sale_line_id`, `medicine_name`, `flow_code`, `flow_name`.
    - 9 timestamp columns standardized in dbt staging view from `_datetime` to `_time` (all `TIMESTAMP` type): `appointment_start_time`, `prescription_start_time`, `prescription_end_time`, `lab_start_time`, `lab_end_time`, `imaging_start_time`, `imaging_end_time`, `pharmacy_start_time`, `pharmacy_end_time`.
    - All nullable identifier columns (`lab_id`, `imaging_request_id`, `imaging_result_id`, `pharmacy_sale_line_id`) parse as whole numbers without decimal discrepancies.

### B. dbt Test Execution Suite (Live Execution on 29 October 2026)
- **Invocation Command:** `dbt test --project-dir dbt --profiles-dir dbt`
- **Invocation ID:** `af9f9484-b31b-4147-8ae3-b52537edce65`
- **Execution Timestamp:** `2026-10-29 17:18:03 UTC`
- **Summary:** **7 of 7 data tests passed (PASS=7, WARN=0, ERROR=0, SKIP=0, TOTAL=7)**
- **Elapsed Time:** 10.56 seconds
- **Individual Test Execution Results:**
  1. `not_null_stg_hospital_opd_appointment_start_time`: **[PASS in 4.20s]** (BigQuery Job ID: `098ec86e-bec2-4d9b-b108-0cc19f41014c`)
  2. `accepted_values_stg_hospital_opd_flow_code__False__1__2__3__4__5__6__7`: **[PASS in 4.26s]** (BigQuery Job ID: `ce904f2c-0f6a-41ff-8e6f-b28cfd1fd55c`)
  3. `not_null_stg_hospital_opd_flow_code`: **[PASS in 4.29s]** (BigQuery Job ID: `61bee711-357e-41bf-8d47-2f6cf745e90c`)
  4. `not_null_stg_hospital_opd_appointment_id`: **[PASS in 4.78s]** (BigQuery Job ID: `b36d5bb1-c4bc-45b0-b880-7b7384cf5f9c`)
  5. `not_null_stg_hospital_opd_patient_id`: **[PASS in 3.27s]** (BigQuery Job ID: `73d7aab2-e9b8-4a48-8e80-f6c10a717731`)
  6. `unique_stg_hospital_opd_record_no`: **[PASS in 3.33s]** (BigQuery Job ID: `d75f3c90-cb68-44b9-aaba-c63e6ab80d5a`)
  7. `not_null_stg_hospital_opd_record_no`: **[PASS in 3.49s]** (BigQuery Job ID: `62aaf047-cefb-454e-a4f9-b635d2ef4561`)

### C. Event-Log Pipeline & Dataset Audit (Read-Only Inspection)
- **Pipeline Script:** `scripts/prepare_event_log.py`
  - Input file confirmed: `data/HospitalOPD_cleaned.csv` (line 51)
  - Output file confirmed: `data/careflow_event_log.csv` (line 52)
- **Event-Log File:** `data/careflow_event_log.csv`
  - **File Size:** 34,658,350 bytes (~33.05 MB)
  - **Total Event Rows:** Exactly **193,443 rows**
  - **Column Structure (14 fields):** `case_id`, `patient_id`, `activity`, `activity_category`, `lifecycle`, `timestamp`, `resource`, `service_id`, `service_name`, `flow_code`, `flow_name`, `source_record_no`, `timestamp_anomaly_flag`, `event_order`
  - **Granularity & Entities:**
    - Unique cases (`case_id` = `appointment_id`): **49,912**
    - Unique patients (`patient_id`): **39,442**
    - Null mandatory keys (`case_id`, `activity`, `timestamp`): **0 (0.00%)**
    - Timestamp boundary: `2024-04-25 11:12:00` to `2026-07-23 16:43:00`
    - Flagged timestamp anomalies (`timestamp_anomaly_flag = 1`): **1,183 (0.61%)**
  - **Standards & Format Clarification:**
    - *Tabular Event Log Structure:* Structured as a CSV conforming to standard process mining event-log conventions, directly ingestible into PM4Py via DataFrame loader (`pm4py.format_dataframe`).
    - *IEEE XES Format Distinction:* The file is a flat CSV and **not** an XML-based IEEE 1849-2016 `.xes` document. Generating a formal XML-based XES export would require serialization via `pm4py.write_xes` if standard XML interchange is required by Member 4.

### D. SQL Validation Suite Review (`sql/validation_queries.sql`)
The 8 analytical quality checks were reviewed and confirmed against BigQuery execution benchmarks:
- **Check 1 (Row Count):** 62,422 rows confirmed (`discrepancy = 0`, PASS).
- **Check 2 (Null Rates):** Mandatory process keys (`patient_id`, `appointment_id`, `flow_name`, `flow_code`, `appointment_start_datetime`) have **0.00% nulls**. `prescription_start_datetime` has 12 nulls (0.02%). Optional service fields exhibit expected null rates reflecting non-utilized services (`lab_id`: 71.12%, `imaging_request_id`: 91.15%, `pharmacy_sale_line_id`: 99.52%).
- **Check 3 (Timestamp Validity):** 0 out-of-range timestamps; all events fall within `2024-04-25` to `2026-07-23`.
- **Check 4 (Duplicate Analysis):** 148 rows in duplicate groups (74 pairs of repeat records within encounters).
- **Check 5 (Empirical Timing Inversions):**
  - `lab_start_datetime < appointment_start_datetime`: **457 records** (minimum difference: -700.0 minutes)
  - `imaging_start_datetime < appointment_start_datetime`: **295 records** (minimum difference: -589.0 minutes)
  - `prescription_end_datetime < prescription_start_datetime`: **52 records**
  - `prescription_start_datetime < appointment_start_datetime`: **5 records** (minimum difference: -5,704.0 minutes)
  - Pharmacy inversions: **0 records** (`pharmacy_start_datetime` strictly succeeds appointment and prescription timestamps)
  *(Note: Documented strictly as observed empirical data anomalies; operational causes have not been verified).*
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
- **Check 8C (Waiting Times & Duration Outliers):**
  - Registration to Doctor Consultation: average 130.5 min (627 records exceed 480 minutes / 8 hours; maximum observed: 695,643.0 minutes).
  - Registration to Lab Start: average 96.6 min (255 records exceed 480 minutes; maximum observed: 9,388.0 minutes).
  - Registration to Imaging Start: average 456.4 min (271 records exceed 480 minutes; maximum observed: 76,359.0 minutes).
  - Registration to Pharmacy Dispense: average 37.5 min (0 records exceed 480 minutes; maximum observed: 337.0 minutes).
  - Doctor Consultation to Pharmacy Dispense: average 14.9 min (0 records exceed 480 minutes; maximum observed: 314.0 minutes).
  *(Note: Outlier durations > 480 min are documented as empirical data anomalies requiring analytical handling or filtering in downstream marts).*

---

## 3. Evidence-Based Security & Privacy Assessment

Untracked files in the workspace were inspected using strict read-only methods. No credentials, tokens, private keys, or patient-level data are exposed:

| Untracked Item | Size | Inspection Evidence | Privacy / Security Assessment | Recommended Action |
| :--- | :---: | :--- | :--- | :--- |
| `data/HospitalOPD_cleaned.csv` | 11.2 MB | 62,422 rows, 24 columns. Header inspected: surrogate IDs (`patient_id`, `appointment_id`), provider names, timestamps, service names. | De-identified clinical dataset. Zero direct identifiers (SSN, national ID, phone, email, address, date of birth) present. | Exclude via `.gitignore` to prevent repository bloat. |
| `data/HospitalOPD_cleaned.csv.bak` | 11.3 MB | Pre-normalization backup of the above file. | Same as above. Zero direct personal identifiers. | Exclude via `.gitignore`. |
| `data/careflow_event_log.csv` | 34.7 MB | 193,443 rows, 14 columns. Tabular event log. | De-identified event attributes. Zero direct personal identifiers. | Exclude via `.gitignore` or manage via Git LFS if versioning is needed. |
| `dbt/.user.yml` | 41 bytes | Single line: `id: 3c78a0ab-6f9a-4fe3-bad8-36494e470403`. | Anonymous tracking UUID generated by dbt. Zero credentials, zero secrets. | Exclude via `.gitignore` as it is machine-local. |
| `dbt/profiles.yml` | 826 bytes | Target profile definitions for BigQuery. | Uses `env_var('GOOGLE_APPLICATION_CREDENTIALS', '')` and `env_var('CAREFLOW_GCP_PROJECT', 'careflow-clinical-process-m')`. Zero plaintext passwords or private keys. | Safe configuration. Maintain environment variable injection. |

---

## 4. Task Breakdown: Status Matrix

### Verified Completed Tasks (Foundational & Day 2 Verification Milestone)
- [x] Read-only verification of original `.xls` source dataset.
- [x] Normalized CSV export with pre-overwrite backup (`data/HospitalOPD_cleaned.csv`).
- [x] Tabular event log generation and validation (`data/careflow_event_log.csv`, 193,443 rows).
- [x] Google Cloud service account authentication and environment configuration (`careflow-clinical-process-m`).
- [x] BigQuery dataset setup (`careflow_opd`, Region: US) and native table ingestion (`hospital_opd_cleaned`, 62,422 rows).
- [x] BigQuery staging view deployment (`careflow_opd.stg_hospital_opd`, 62,422 rows).
- [x] Day 2 Live BigQuery verification of base table, staging view, row counts, and 24-column schema match (29 Oct 2026).
- [x] Day 2 Live re-execution and passing of all 7 automated dbt tests (`PASS=7, ERROR=0`, Invocation: `af9f9484-b31b-4147-8ae3-b52537edce65`).
- [x] Read-only inspection of event-log dataset and generation script (`scripts/prepare_event_log.py`).
- [x] Review of all 8 BigQuery Standard SQL validation checks (`sql/validation_queries.sql`).
- [x] Workflow documentation maintenance in `docs/member3_workflow.md`.

### Incomplete Tasks (Roadmap to 8 November 2026 Milestone)
- [ ] **dbt Marts Layer (Analytical Transformations):**
  - Develop `fct_clinical_encounters.sql` (encounter-level durations, pathway classifications, service flags).
  - Develop `fct_process_transitions.sql` (stage-to-stage transition metrics and bottleneck flags).
  - Develop `dim_clinical_providers.sql` (doctor consultation volumes and caseload metrics).
- [ ] **Process Mining KPI Modeling in BigQuery:**
  - Build reusable BigQuery views for process mining dashboards (waiting time distributions, anomaly rates by department).
- [ ] **Integration with Member 4 (Process Mining & Dashboarding):**
  - Coordinate data model requirements and verify ingestion of `careflow_event_log.csv` and `stg_hospital_opd` into process mining frameworks (PM4Py, Celonis, or Disco).
  - Provide XML XES conversion (`pm4py.write_xes`) if standard-compliant XML interchange is required.
- [ ] **Final Handover Documentation:**
  - Final data dictionary, lineage diagrams, and delivery documentation for the 8 November deadline.

---

## 5. Observations & Anomaly Documentation

1. **Active Technical Blockers:** **None**. Database connections, credentials injection, and dbt test compilation are fully operational.
2. **Empirical Timestamp Anomalies:**
   - 457 laboratory start times and 295 imaging start times precede appointment start times.
   - 627 records exhibit appointment-to-prescription waiting times exceeding 480 minutes (max: 695,643.0 min).
   - In the event log, records with negative transitions are tagged with `timestamp_anomaly_flag = 1` so downstream analytical models can evaluate or exclude them systematically.
3. **Repository Management:** Large CSV files (`~57 MB` in `data/`) and local dbt artifacts (`dbt/target/`, `dbt/logs/`, `dbt/.user.yml`) are currently untracked and should be excluded via `.gitignore` prior to repository staging.

---

## 6. Conclusion & Day 2 Sign-off

All Day 2 data pipeline verification steps assigned to Member 3 are **100% complete, cloud-verified, and documented**.
The base table, staging view, schema mapping, automated dbt tests, and event log are fully validated. The project is positioned to begin authoring analytical dimensional models in `dbt/models/marts/` and initiating integration with Member 4 ahead of the **8 November 2026** milestone deadline.

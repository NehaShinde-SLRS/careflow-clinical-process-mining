# CareFlow Clinical Process Mining — Day 3 Completion Report

**Execution Date:** 30 October 2026  
**Auditor / Engineer:** Member 3 (Data Engineering: Ingestion, SQL Validation, dbt Marts, KPI Views)  
**Target GCP Project:** `careflow-clinical-process-m`  
**Target BigQuery Dataset:** `careflow_opd` (Region: `US`)  
**Status:** **100% COMPLETED & VERIFIED IN CLOUD**

---

## 1. Executive Summary

All Day 3 responsibilities assigned to **Member 3** for the CareFlow Clinical Process Mining project have been completed, executed live against Google Cloud BigQuery, and verified.

- **Dimensional Marts (3 Native Tables Created):**
  - `careflow_opd.dim_clinical_providers`: 98 unique attending physicians.
  - `careflow_opd.fct_clinical_encounters`: 49,912 unique visit encounters.
  - `careflow_opd.fct_process_transitions`: 121,832 clinical stage transitions, sequenced by canonical clinical pathway order.
- **Automated dbt Data Tests (24/24 Passed - 100% Pass Rate):**
  - 7 staging tests + 17 marts tests covering primary key uniqueness, not-null constraints, domain accepted values, and foreign-key referential integrity across all tables.
- **Analytical KPI Views (6 Views Deployed in BigQuery):**
  - `vw_kpi_total_encounters`, `vw_kpi_activity_counts`, `vw_kpi_waiting_times`, `vw_kpi_process_cycle_time`, `vw_kpi_patient_throughput`, `vw_kpi_process_bottlenecks`.
- **Clinical Process Mining Insights Verified:**
  - Canonical clinical stage ordering successfully detected **3,493 negative transition inversions** (including 1,547 encounters where imaging began prior to doctor consultation completion and 616 where lab tests preceded consultation end).
  - Outpatient department bottlenecks identified: **62.96% of laboratory tests** (3,019 orders) take $>2$ hours to complete (average duration: 930.5 minutes / 15.5 hours).

---

## 2. BigQuery Marts Table Verification

Live metadata inspection and SQL validation queries executed against BigQuery dataset `careflow_opd`:

| Table / Asset Name | Type | Verified Row Count | Columns | Primary Key (PK) | PK Uniqueness | PK Nulls | Foreign Key (FK) Integrity |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :--- |
| `dim_clinical_providers` | `TABLE` | **98** | 8 | `doctor_id` | **100% Unique** | **0 Nulls** | Referenced by `fct_clinical_encounters` |
| `fct_clinical_encounters` | `TABLE` | **49,912** | 33 | `appointment_id` | **100% Unique** | **0 Nulls** | `doctor_id` $\rightarrow$ `dim_clinical_providers` (**0 orphans**) |
| `fct_process_transitions` | `TABLE` | **121,832** | 11 | `transition_id` | **100% Unique** | **0 Nulls** | `appointment_id` $\rightarrow$ `fct_clinical_encounters` (**0 orphans**) |
| `stg_hospital_opd` | `VIEW` | **62,422** | 24 | `record_no` | **100% Unique** | **0 Nulls** | Base staging view |
| `hospital_opd_cleaned` | `TABLE` | **62,422** | 24 | `record_no` | **100% Unique** | **0 Nulls** | Ingested source table |

---

## 3. Automated dbt Test Suite Results

- **Invocation Command:** `dbt test --project-dir dbt --profiles-dir dbt`
- **Execution Timestamp:** `2026-10-30 17:38:40 UTC`
- **Summary:** **24 of 24 data tests passed (PASS=24, WARN=0, ERROR=0, TOTAL=24)**
- **Total Elapsed Time:** 23.81 seconds

### Test Breakdown by Model:
1. **`dim_clinical_providers` (3 tests):**
   - `not_null_dim_clinical_providers_doctor_id` [PASS in 4.35s]
   - `not_null_dim_clinical_providers_doctor_name` [PASS in 4.36s]
   - `unique_dim_clinical_providers_doctor_id` [PASS in 3.00s]
2. **`fct_clinical_encounters` (8 tests):**
   - `not_null_fct_clinical_encounters_appointment_id` [PASS in 3.62s]
   - `unique_fct_clinical_encounters_appointment_id` [PASS in 2.91s]
   - `not_null_fct_clinical_encounters_patient_id` [PASS in 3.14s]
   - `not_null_fct_clinical_encounters_doctor_id` [PASS in 3.70s]
   - `relationships_fct_clinical_encounters_doctor_id__doctor_id__ref_dim_clinical_providers_` [PASS in 3.00s]
   - `not_null_fct_clinical_encounters_appointment_start_time` [PASS in 3.42s]
   - `not_null_fct_clinical_encounters_flow_code` [PASS in 3.42s]
   - `accepted_values_fct_clinical_encounters_flow_code` (1–7) [PASS in 4.74s]
3. **`fct_process_transitions` (6 tests):**
   - `not_null_fct_process_transitions_transition_id` [PASS in 3.07s]
   - `unique_fct_process_transitions_transition_id` [PASS in 3.35s]
   - `not_null_fct_process_transitions_appointment_id` [PASS in 3.04s]
   - `relationships_fct_process_transitions_appointment_id__appointment_id__ref_fct_clinical_encounters_` [PASS in 2.95s]
   - `not_null_fct_process_transitions_from_timestamp` [PASS in 3.99s]
   - `not_null_fct_process_transitions_to_timestamp` [PASS in 3.36s]
4. **`stg_hospital_opd` (7 tests):**
   - `not_null_stg_hospital_opd_record_no` [PASS in 2.93s]
   - `unique_stg_hospital_opd_record_no` [PASS in 3.04s]
   - `not_null_stg_hospital_opd_appointment_id` [PASS in 3.30s]
   - `not_null_stg_hospital_opd_patient_id` [PASS in 2.95s]
   - `not_null_stg_hospital_opd_appointment_start_time` [PASS in 3.96s]
   - `not_null_stg_hospital_opd_flow_code` [PASS in 3.15s]
   - `accepted_values_stg_hospital_opd_flow_code` (1–7) [PASS in 4.40s]

---

## 4. Deployed BigQuery KPI Views & Verified Metrics

All 6 analytical views from [`sql/kpi_analysis_views.sql`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/sql/kpi_analysis_views.sql) were deployed to `careflow_opd` and queried live:

### KPI View 1: `vw_kpi_total_encounters`
- Total Encounters (`appointment_id`): **49,912**
- Total Unique Patients (`patient_id`): **39,442**
- Re-visit Rate: **1.27 encounters / patient**
- Encounters with Laboratory Service: **6,370 (12.76%)**
- Encounters with Imaging/Radiology: **5,323 (10.66%)**
- Encounters with Internal Pharmacy: **108 (0.22%)**
- Total Source Orders/Records: **62,422**

### KPI View 2: `vw_kpi_activity_counts` (Pathway Volume)
| Flow Code | Clinical Pathway | Encounters | Share (%) |
| :---: | :--- | :---: | :---: |
| 1 | `Appointment → Prescription` | 39,658 | 79.46% |
| 2 | `Appointment → Prescription → Lab` | 4,824 | 9.67% |
| 3 | `Appointment → Prescription → Imaging` | 3,794 | 7.60% |
| 5 | `Appointment → Prescription → Lab + Imaging` | 1,528 | 3.06% |
| 4 | `Appointment → Prescription → Pharmacy` | 93 | 0.19% |
| 6 | `Appointment → Prescription → Lab + Pharmacy` | 14 | 0.03% |
| 7 | `Appointment → Prescription → Imaging + Pharmacy` | 1 | 0.00% |

### KPI View 3: `vw_kpi_waiting_times` (Departmental Waiting Duration)
| Wait Stage | Valid Visits | Mean Wait (min) | Min (min) | Max (min) | Outliers (>8h) | Inversions (<0) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Registration to Consultation** | 49,901 | 129.6 | -5,704 | 695,643 | 445 (0.89%) | 5 |
| **Registration to Lab Start** | 6,370 | 84.2 | -700 | 9,388 | 68 (1.07%) | 132 |
| **Registration to Imaging Start** | 5,323 | 443.6 | -589 | 76,359 | 256 (4.81%) | 289 |
| **Registration to Pharmacy Start** | 108 | 37.2 | 7 | 124 | 0 (0.00%) | 0 |

### KPI View 4: `vw_kpi_process_cycle_time` (Total Journey Duration)
| Flow Code | Pathway | Mean Cycle Time (min) | Cycle Time $\le 2$ hr | Cycle Time $> 8$ hr |
| :---: | :--- | :---: | :---: | :---: |
| 1 | `Appointment → Prescription` | 151.7 min (~2.5h) | 37,106 (93.56%) | 444 (1.12%) |
| 2 | `Appointment → Prescription → Lab` | 796.1 min (~13.3h) | 1,855 (38.45%) | 867 (17.97%) |
| 3 | `Appointment → Prescription → Imaging` | 470.1 min (~7.8h) | 2,731 (71.98%) | 185 (4.88%) |
| 4 | `Appointment → Prescription → Pharmacy` | 51.2 min (~0.9h) | 87 (93.55%) | 1 (1.08%) |
| 5 | `Appointment → Prescription → Lab + Imaging` | 1,475.5 min (~24.6h) | 311 (20.35%) | 426 (27.88%) |
| 6 | `Appointment → Prescription → Lab + Pharmacy` | 552.0 min (~9.2h) | 9 (64.29%) | 2 (14.29%) |
| 7 | `Appointment → Prescription → Imaging + Pharmacy` | 324.0 min (~5.4h) | 0 (0.00%) | 0 (0.00%) |

### KPI View 5: `vw_kpi_patient_throughput` (Peak Arrival Windows)
- **Top 5 Busiest Outpatient Hours:**
  1. Monday at 06:00 (1,390 patient arrivals)
  2. Monday at 07:00 (1,250 patient arrivals)
  3. Wednesday at 06:00 (1,140 patient arrivals)
  4. Monday at 13:00 (1,096 patient arrivals)
  5. Friday at 13:00 (1,080 patient arrivals)

### KPI View 6: `vw_kpi_process_bottlenecks` (Stage Handoffs & Inversions)
| From Stage | To Stage | Transitions | Mean Duration | Bottlenecks (>2h) | Inversions (<0) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `Registration` | `Consultation Start` | 49,901 | 129.6 min | 3,461 (6.94%) | 5 |
| `Consultation Start` | `Consultation Complete` | 49,901 | 10.4 min | 202 (0.40%) | 47 |
| `Consultation Complete` | `Lab Start` | 6,370 | -10.5 min | 224 (3.52%) | 616 |
| `Lab Start` | `Lab Complete` | 4,795 | **930.5 min** | **3,019 (62.96%)** | 0 |
| `Consultation Complete` | `Imaging Start` | 3,791 | 267.2 min | 241 (6.36%) | 1,547 |
| `Imaging Start` | `Imaging Complete` | 5,315 | 111.0 min | 72 (1.35%) | 0 |
| `Lab Complete` | `Imaging Start` | 1,112 | -389.5 min | 96 (8.63%) | 988 |
| `Lab Start` | `Imaging Start` | 420 | 361.1 min | 52 (12.38%) | 277 |

---

## 5. Files Changed & Added in Day 3

1. **dbt Marts Layer:**
   - [`dbt/models/marts/dim_clinical_providers.sql`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/dbt/models/marts/dim_clinical_providers.sql) (New)
   - [`dbt/models/marts/fct_clinical_encounters.sql`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/dbt/models/marts/fct_clinical_encounters.sql) (New)
   - [`dbt/models/marts/fct_process_transitions.sql`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/dbt/models/marts/fct_process_transitions.sql) (New)
   - [`dbt/models/marts/schema.yml`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/dbt/models/marts/schema.yml) (New — 17 schema tests)
2. **SQL KPI Views:**
   - [`sql/kpi_analysis_views.sql`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/sql/kpi_analysis_views.sql) (New — 6 BigQuery DDL views)
3. **Documentation:**
   - [`docs/day3_completion_report.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day3_completion_report.md) (New)
   - [`docs/project_audit.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/project_audit.md) (Updated)
   - [`docs/member3_workflow.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/member3_workflow.md) (Updated)

---

## 6. Pending Items for Subsequent Milestones (Roadmap to 8 Nov 2026)

- Coordinate with **Member 4** (Process Mining & Dashboarding) to connect BI tools / Looker Studio to the deployed KPI views.
- Provide direct import scripts for PM4Py dataframe loading using `careflow_event_log.csv` and `stg_hospital_opd`.
- Final handover package assembly for the 8 November deadline.

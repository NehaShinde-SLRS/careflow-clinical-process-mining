# CareFlow Clinical Process Mining — Project Audit Report

**Audit Date:** 28–31 October 2026 (Consolidated Audit: Ingestion, Staging, Marts, KPIs, Model Review & Event Log Validation)  
**Auditor Role:** Member 3 (Data Engineering: Ingestion, SQL Validation, dbt Marts, KPI Views, Event-Log Preparation)  
**Project Milestone Deadline:** 8 November 2026 (Final Project Handover)  
**Target GCP Project:** `careflow-clinical-process-m`  
**Target BigQuery Dataset:** `careflow_opd` (Region: `US`)  

---

## 1. Executive Summary

This consolidated project audit serves as the official single source of truth for all deliverables, datasets, cloud resources, and pipelines assigned to **Member 3** for the CareFlow Clinical Process Mining project.

- **Foundational & Staging Pipeline (100% Complete & Verified):**
  - Base table `hospital_opd_cleaned`: Native BigQuery table (62,422 rows, 24 columns).
  - Staging view `stg_hospital_opd`: BigQuery SQL view (62,422 rows, 24 columns).
  - Event log `data/careflow_event_log.csv`: 193,443 rows, 14 columns, 49,912 cases, 1,183 anomaly flags.
- **Day 3 Dimensional Marts Layer (100% Complete & Verified in BigQuery):**
  - `dim_clinical_providers`: 98 unique attending clinicians (Table, 98 rows, 7.5 KB).
  - `fct_clinical_encounters`: 49,912 visit encounters with service utilization flags, waiting durations, cycle times, and anomaly tags (Table, 49,912 rows, 10.12 MB).
  - `fct_process_transitions`: 121,832 stage-to-stage process transitions ordered by canonical clinical pathway sequence (Table, 121,832 rows, 13.52 MB).
- **Automated dbt Data Tests (24/24 Passed - 100% Pass Rate):**
  - 7 staging tests + 17 marts schema tests covering primary key uniqueness, not-null constraints, domain accepted values, and foreign-key referential integrity across all models.
- **Analytical KPI Views (6 Views Deployed in BigQuery):**
  - `vw_kpi_total_encounters`, `vw_kpi_activity_counts`, `vw_kpi_waiting_times`, `vw_kpi_process_cycle_time`, `vw_kpi_patient_throughput`, `vw_kpi_process_bottlenecks`.
- **Day 4 dbt Model & Performance Review (100% Verified):**
  - Decoupled modular DAG, 0 orphan foreign key records, sub-second query performance ($<15$ ms slot time), fully documented in `docs/day4_completion_report.md`.
- **Day 5 Event Log Validation (100% Verified):**
  - Exhaustive 8-dimension audit of `data/careflow_event_log.csv`: 0 nulls across all 14 columns, 0 exact duplicates, 100% valid timestamps (819 days), 100% source record traceability, fully documented in `docs/day5_event_log_validation_report.md`.
- **Downstream Handover (Next Steps for 8 November 2026 Deadline):**
  - Integration with Member 4 (Process Mining & Dashboarding): BI dashboard connection and process discovery import.

---

## 2. Live Cloud Verification Evidence (Executed 30–31 October 2026)

### A. BigQuery Marts Table Verification (Live Query Evidence)
- **Dataset Reference:** `careflow-clinical-process-m.careflow_opd`
- **Objects Summary:**
  - `dim_clinical_providers`: Native Table, **98 rows**, 8 columns, 7.5 KB. Primary key `doctor_id` is 100% unique (0 nulls). Query benchmark slot latency: 8 ms.
  - `fct_clinical_encounters`: Native Table, **49,912 rows**, 33 columns, 10.12 MB. Primary key `appointment_id` is 100% unique (0 nulls). Referential integrity to `dim_clinical_providers` confirmed (**0 orphan records**). Query benchmark slot latency: 15 ms.
  - `fct_process_transitions`: Native Table, **121,832 rows**, 11 columns, 13.52 MB. Primary key `transition_id` is 100% unique (0 nulls). Referential integrity to `fct_clinical_encounters` confirmed (**0 orphan records**). Query benchmark slot latency: 8 ms.
  - `hospital_opd_cleaned`: Native Table, **62,422 rows**, 24 columns.
  - `stg_hospital_opd`: SQL View, **62,422 rows**, 24 columns.

### B. dbt Test Execution Suite (Live Execution on 30 October 2026)
- **Invocation Command:** `dbt test --project-dir dbt --profiles-dir dbt`
- **Execution Timestamp:** `2026-10-30 17:38:40 UTC`
- **Summary:** **24 of 24 data tests passed (PASS=24, WARN=0, ERROR=0, TOTAL=24)**
- **Elapsed Time:** 23.81 seconds
- **Test Integrity Breakdown:**
  - Primary Key Uniqueness: `doctor_id` [PASS], `appointment_id` [PASS], `transition_id` [PASS], `record_no` [PASS].
  - Mandatory Not-Null: Core identifiers, arrival timestamps, and transition timestamps have 0 nulls across all models.
  - Referential Integrity: Foreign key `fct_clinical_encounters.doctor_id` $\rightarrow$ `dim_clinical_providers.doctor_id` [PASS]; `fct_process_transitions.appointment_id` $\rightarrow$ `fct_clinical_encounters.appointment_id` [PASS].
  - Domain Accepted Values: Pathway flow codes (1–7) validated across all encounters [PASS].

### C. BigQuery KPI Analysis Views Deployment
The 6 analytical KPI views from `sql/kpi_analysis_views.sql` were deployed and queried live in BigQuery:
1. `vw_kpi_total_encounters`: 49,912 unique outpatient encounters across 39,442 unique patients (1.27 visits/patient). Lab utilization: 12.76%, Imaging utilization: 10.66%, Pharmacy fulfillment: 0.22%.
2. `vw_kpi_activity_counts`: Pathway 1 (`Appointment → Prescription`) comprises 79.46% of visits (39,658 encounters); Pathway 2 (with Lab) comprises 9.67% (4,824 encounters); Pathway 3 (with Imaging) comprises 7.60% (3,794 encounters); Pathway 5 (Lab + Imaging) comprises 3.06% (1,528 encounters).
3. `vw_kpi_waiting_times`: Average waiting time to consultation is 129.6 minutes (445 encounters $>480$ min); average waiting time to lab is 84.2 minutes; average waiting time to imaging is 443.6 minutes.
4. `vw_kpi_process_cycle_time`: Pathway 1 average cycle time is 151.7 minutes (93.56% $\le 2$ hours); Pathway 2 (Lab) average cycle time is 796.1 minutes (13.3 hours); Pathway 5 (Lab + Imaging) average cycle time is 1,475.5 minutes (24.6 hours).
5. `vw_kpi_patient_throughput`: Peak patient arrival surges occur on Monday mornings (06:00–07:00: 2,640 arrivals), Wednesday mornings (06:00: 1,140 arrivals), and Friday afternoons (13:00: 1,080 arrivals).
6. `vw_kpi_process_bottlenecks`: By ordering transitions using the canonical clinical sequence, 3,493 negative transitions were quantified (including 1,547 encounters where imaging was taken before consultation end). Departmental bottleneck detected: **62.96% of laboratory tests** (3,019 orders) take $>2$ hours to complete (mean duration: 930.5 minutes).

### D. Event Log In-Depth Validation Scorecard (`data/careflow_event_log.csv`)
- **File Metrics:** 34,658,350 bytes (33.05 MB), 193,443 event rows, 14 columns.
- **Completeness:** 0 nulls across all 14 columns (100% complete).
- **Exact Deduplication:** 0 exact duplicate records across all columns.
- **Cases & Patients:** 49,912 unique cases, 39,442 unique patients (mean: 3.88 events/case, median: 3.0, range: 2–57).
- **Clinical Concurrency:** 14,481 instances share `(case_id, activity, timestamp)` representing multi-order simultaneous diagnostics with distinct `service_id` and `source_record_no` entries.
- **Timespan:** 100% valid timestamps spanning 819 operating days (`2024-04-25 11:12:00` to `2026-07-23 16:43:00`).
- **Anomalies Tagged:** 1,183 events (0.61%) with `timestamp_anomaly_flag = 1` (457 lab start, 293 imaging start, 273 imaging complete, 155 lab complete, 5 consultation start).
- **Traceability:** 100% of event source records map to verified source row IDs (`record_no`) with 0 orphans.

---

## 3. Evidence-Based Security & Privacy Assessment

All untracked local files were inspected using strict read-only methods. No credentials, tokens, private keys, or patient-level data are exposed:

| Untracked Item | Size | Inspection Evidence | Privacy / Security Assessment | Recommended Action |
| :--- | :---: | :--- | :--- | :--- |
| `data/HospitalOPD_cleaned.csv` | 11.2 MB | 62,422 rows, 24 columns. Surrogate IDs, provider names, timestamps. | De-identified clinical dataset. Zero direct personal identifiers. | Exclude via `.gitignore`. |
| `data/HospitalOPD_cleaned.csv.bak` | 11.3 MB | Pre-normalization backup of source data. | Same as above. Zero direct personal identifiers. | Exclude via `.gitignore`. |
| `data/careflow_event_log.csv` | 34.7 MB | 193,443 rows, 14 columns. Tabular event log. | De-identified event attributes. Zero direct personal identifiers. | Exclude via `.gitignore` or track via Git LFS. |
| `dbt/.user.yml` | 41 bytes | Anonymous UUID generated by dbt. | Zero credentials, zero secrets. | Exclude via `.gitignore`. |
| `dbt/profiles.yml` | 826 bytes | Target profile definitions for BigQuery. | Uses `env_var('GOOGLE_APPLICATION_CREDENTIALS', '')` and `env_var('CAREFLOW_GCP_PROJECT', '')`. Zero plaintext secrets. | Safe configuration. Maintain env var injection. |

---

## 4. Task Breakdown: Status Matrix

### Verified Completed Tasks (Foundational, Day 3, Day 4 & Day 5 Milestones)
- [x] Read-only verification of original `.xls` source dataset.
- [x] Normalized CSV export with pre-overwrite backup (`data/HospitalOPD_cleaned.csv`).
- [x] Tabular event log generation and validation (`data/careflow_event_log.csv`, 193,443 rows).
- [x] BigQuery dataset setup (`careflow_opd`, Region: US) and native table ingestion (`hospital_opd_cleaned`, 62,422 rows).
- [x] BigQuery staging view deployment (`careflow_opd.stg_hospital_opd`, 62,422 rows).
- [x] 8 BigQuery Standard SQL validation checks executed and documented (`sql/validation_queries.sql`).
- [x] Materialization of Provider Dimension (`dim_clinical_providers`, 98 rows, native table).
- [x] Materialization of Encounter Fact Table (`fct_clinical_encounters`, 49,912 rows, native table).
- [x] Materialization of Process Transitions Fact Table (`fct_process_transitions`, 121,832 rows, native table).
- [x] Authoring and passing of all 24 dbt data tests (`PASS=24, ERROR=0`, 100% pass rate).
- [x] Deployment and live querying of 6 analytical KPI views in BigQuery (`sql/kpi_analysis_views.sql`).
- [x] Detailed completion reporting in `docs/day3_completion_report.md`.
- [x] Day 4 dbt model review, DAG dependency analysis, and performance benchmarking (`docs/day4_completion_report.md`).
- [x] Day 5 comprehensive event log data quality and sequence validation (`docs/day5_event_log_validation_report.md`).

### Incomplete Tasks (Roadmap to 8 November 2026 Milestone)
- [ ] **Integration with Member 4 (Process Mining & Dashboarding):**
  - Verify BI tool connection (Looker Studio / Tableau) to the 6 deployed KPI views.
  - Coordinate process mining script imports using `careflow_event_log.csv` and `stg_hospital_opd`.
  - Provide XML-based XES export via `pm4py.write_xes` if standard XML interchange is required.
- [ ] **Final Handover Documentation:**
  - Final data dictionary, lineage diagrams, and delivery documentation for the 8 November deadline.

---

## 5. Conclusion & Days 4–5 Sign-off

All Day 4 (dbt Model Review) and Day 5 (Event Log Validation) tasks assigned to Member 3 are **100% completed, cloud-verified, and fully documented**.

The warehouse now contains:
1. Verified staging model (`stg_hospital_opd`).
2. High-performance dimensional star-schema marts (`dim_clinical_providers`, `fct_clinical_encounters`, `fct_process_transitions`) with sub-second execution latencies.
3. 24 passing automated data quality and referential integrity tests.
4. 6 live analytical views serving all core process mining and throughput KPIs.
5. Fully profiled, de-identified clinical event log (`data/careflow_event_log.csv`, 193,443 rows) ready for process discovery algorithms.

The project is fully prepared for final dashboard integration and process mining analytics with Member 4 ahead of the **8 November 2026** milestone deadline.

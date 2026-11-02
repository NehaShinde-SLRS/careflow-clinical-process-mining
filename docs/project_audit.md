# CareFlow Clinical Process Mining — Project Audit Report

**Audit Date:** 28 October – 2 November 2026 (Consolidated Audit: Ingestion, Staging, Marts, KPIs, Model Review, Event Log Validation, Day 6 Process Mining Analysis & Day 7 Data Dictionary)
**Auditor Role:** Member 3 (Data Engineering: Ingestion, SQL Validation, dbt Marts, KPI Views, Event-Log Preparation, Process Mining Analytics)
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
- **Day 6 Process Mining Analysis (100% Complete & Verified):**
  - Process Discovery & DFG: 143,531 transitions across 56 unique edges; 99.16% start at Registration; 82.95% end at Consultation Completion.
  - Process Variants: 602 unique variants across 49,912 cases; top 2 cover **82.76%** of cases; top 6 cover **90.00%**; top 18 cover **95.00%**.
  - Bottleneck Analysis: Laboratory Turnaround Time (TAT) is the primary bottleneck at **279.3 minutes (4.65 hours)** mean duration (62.96% $>2$ hours; batched panels reach 930.5 min / 15.5 hours); clinic registration wait averages **114.9 minutes**.
  - Rework & Loop Detection: 20,070 direct self-loops across 4,231 cases (8.48%) driven by concurrent multi-order lab tests (11,387 loops) and staggered results (8,238 loops); 3,746 multi-lab cases (7.51%).
  - Process Conformance: **85.45% canonical happy path conformance**; 418 cases (0.84%) out-of-order diagnostic start; 1,184 cases (2.37%) pre-consultation radiology.
  - Deliverables: Python pipeline ([`scripts/process_mining_analysis.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/process_mining_analysis.py)), BigQuery SQL analytics suite ([`sql/day6_process_mining_queries.sql`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/sql/day6_process_mining_queries.sql)), and detailed report ([`docs/day6_process_mining_analysis.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day6_process_mining_analysis.md)).
- **Day 7 Data Dictionary & Lineage Documentation (100% Complete & Verified):**
  - Production Data Dictionary ([`docs/data_dictionary.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/data_dictionary.md)): Detailed documentation of 11 BigQuery database objects (146 columns) and 12 total project entities (160 columns) including the local event log (`data/careflow_event_log.csv`, 14 columns), detailing keys, types, nullability, clinical ontology, and pathway definitions.
  - Source-to-Target Mapping ([`docs/source_to_target_mapping.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/source_to_target_mapping.md)): Comprehensive lineage flowcharts, star-schema ER diagram, transformation expressions, business rules, and provenance matrix (0 orphan references, 62,262 distinct source rows referenced, 160 duplicate intra-encounter order lines consolidated).
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

### E. Day 6 Process Mining Analysis Scorecard (Executed 31 October 2026)
- **Pipeline Implementation:** [`scripts/process_mining_analysis.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/process_mining_analysis.py) (executed end-to-end on 193,443 events).
- **SQL Analytics Suite:** [`sql/day6_process_mining_queries.sql`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/sql/day6_process_mining_queries.sql) (6 BigQuery Standard SQL queries, 100% syntax and dry-run verified).
- **Comprehensive Report:** [`docs/day6_process_mining_analysis.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day6_process_mining_analysis.md).
- **Process Discovery (DFG):**
  - Discovered 143,531 total transitions across 56 unique transition edges.
  - Case entry activities: `Appointment Registration` (49,494 cases, 99.16%), `Imaging Started` (282 cases, 0.56%), `Lab Test Started` (131 cases, 0.26%), `Prescription Consultation Started` (5 cases, 0.01%).
  - Case exit activities: `Prescription Consultation Completed` (41,400 cases, 82.95%), `Lab Test Completed` (4,522 cases, 9.06%), `Imaging Completed` (2,521 cases, 5.05%), `Lab Test Started` (1,321 cases, 2.65% discharged with pending lab).
- **Process Variants & Pareto Distribution:**
  - Discovered 602 unique execution variants across 49,912 cases.
  - Variant 1 (`Reg -> Consult Start -> Consult Complete`): 39,141 cases (78.42%), mean cycle time 134.7 min, median 29.0 min.
  - Variant 2 (`Reg -> Consult -> Imaging`): 2,168 cases (4.34%), mean cycle time 450.4 min, median 57.0 min.
  - Top 2 variants account for **82.76%**; top 6 account for **90.00%**; top 18 account for **95.00%** (classic Pareto concentration).
- **Bottlenecks & Delays:**
  - Laboratory Turnaround Time (Primary Bottleneck): Mean `Lab Start -> Lab Complete` duration is **279.3 minutes (4.65 hours)** (median: 81.0 min, P90: 229.5 min). Across batched panels, average lab elapsed duration reaches **930.5 minutes (15.5 hours)**. 62.96% of lab tests require $>2$ hours.
  - Clinic Waiting Time: Mean registration-to-consultation wait is **114.9 minutes (1.9 hours)** (median: 25.0 min, P90: 91.0 min). High positive skew driven by morning peak arrivals (2,640 arrivals at 06:00–07:00 Mondays).
  - Post-Consultation Imaging Delay: Mean delay of **419.3 minutes (7.0 hours)** from consultation completion to radiology start.
- **Rework & Loops:**
  - 20,070 direct self-loops observed across 4,231 cases (8.48% of all cases).
  - Predominantly driven by concurrent laboratory test orders (11,387 loops) and sequential laboratory completions (8,238 loops).
  - 3,746 cases (7.51%) have $>1$ laboratory test; 640 cases (1.28%) have repeated consultations; 98 cases (0.20%) have multiple imaging studies.
- **Process Conformance:**
  - **85.45% of cases (42,650)** strictly adhere to canonical happy path trajectories.
  - 418 cases (0.84%) exhibit out-of-order diagnostic start prior to desk registration.
  - 1,184 cases (2.37%) exhibit pre-consultation radiology scans.

### F. Day 7 Data Dictionary & Lineage Specifications (Completed 2 November 2026)
- **Production Data Dictionary:** [`docs/data_dictionary.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/data_dictionary.md).
  - Documents 11 Google Cloud BigQuery database objects (146 columns) and 12 total project entities (160 columns) including the local event log (`data/careflow_event_log.csv`, 14 columns).
  - Covers all 160 columns with explicit BigQuery/CSV data types, nullable states, primary/foreign key relationships, clinical definitions, and sample values.
  - Detailed ontology covering clinical identifiers, departmental services, timestamp semantics, pathway codes (1-7), and operational measures.
- **Source-to-Target Mapping (STTM):** [`docs/source_to_target_mapping.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/source_to_target_mapping.md).
  - Complete architectural data lineage Mermaid flowchart (Layers 0 through 6).
  - Warehouse dimensional star-schema Entity-Relationship (ER) diagram.
  - Column-by-column transformation rules, aggregation expressions, and business logic across raw ingestion, staging view, dimensional marts, event log generation, and analytical KPI views.
  - Exception handling rules for missing timestamps (12 consultation starts), incomplete diagnostics (4,702 ongoing labs, 10 incomplete scans), and timestamp inversions.
  - Provenance traceability matrix verifying 0 orphan references, 62,262 distinct source rows referenced in the event log, and 160 intra-encounter duplicate order lines consolidated during extraction.

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

### Verified Completed Tasks (Foundational, Day 3, Day 4, Day 5, Day 6 & Day 7 Milestones)
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
- [x] Day 6 Process Discovery & DFG extraction (143,531 transitions across 56 unique edges).
- [x] Day 6 Process Variants Analysis (602 unique variants, Pareto 82.76% top 2, 90.00% top 6).
- [x] Day 6 Bottleneck and Waiting Time Analysis (Lab TAT 279.3 min / 4.65h; Registration wait 114.9 min).
- [x] Day 6 Rework and Loop Detection (20,070 direct self-loops across 4,231 cases; 3,746 multi-lab cases).
- [x] Day 6 Process Conformance Analysis (85.45% canonical happy path, 0.84% out-of-order start).
- [x] Day 6 Reusable Python analysis pipeline ([`scripts/process_mining_analysis.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/process_mining_analysis.py)).
- [x] Day 6 Reusable BigQuery SQL analytics suite ([`sql/day6_process_mining_queries.sql`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/sql/day6_process_mining_queries.sql)).
- [x] Day 6 Comprehensive Process Mining Analysis Report ([`docs/day6_process_mining_analysis.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day6_process_mining_analysis.md)).
- [x] Day 7 Production Data Dictionary authored ([`docs/data_dictionary.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/data_dictionary.md)).
- [x] Day 7 End-to-End Source-to-Target Mapping authored ([`docs/source_to_target_mapping.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/source_to_target_mapping.md)).

### Incomplete Tasks (Roadmap to 8 November 2026 Milestone — Day 8 Integration)
- [ ] **Integration with Member 4 (Process Mining & Dashboarding):**
  - Verify BI tool connection (Looker Studio / Tableau) to the 6 deployed BigQuery KPI views.
  - Coordinate process mining script imports using `careflow_event_log.csv` and `stg_hospital_opd`.
  - Provide XML-based XES export via `pm4py.write_xes` if standard XML interchange is required by Member 4.

---

## 5. Conclusion & Days 4–7 Sign-off

All Day 4 (dbt Model Review), Day 5 (Event Log Validation), Day 6 (Process Mining Analysis), and Day 7 (Data Dictionary & Documentation) tasks assigned to Member 3 are **100% completed, cloud-verified, and fully documented**.

The warehouse, analytical suite, and engineering documentation now contain:
1. Verified staging model (`stg_hospital_opd`).
2. High-performance dimensional star-schema marts (`dim_clinical_providers`, `fct_clinical_encounters`, `fct_process_transitions`) with sub-second execution latencies.
3. 24 passing automated data quality and referential integrity tests.
4. 6 live analytical views serving all core process mining and throughput KPIs.
5. Fully profiled, de-identified clinical event log (`data/careflow_event_log.csv`, 193,443 rows).
6. End-to-end Process Mining Analysis covering DFG discovery, 602 execution variants, Pareto distributions, bottleneck quantification, self-loops, and conformance scoring with targeted clinical recommendations.
7. Production-grade Data Dictionary documenting 11 BigQuery warehouse objects (146 columns) and 12 total project entities (160 columns) including the local event log, types, nullability, clinical ontology, and pathway definitions.
8. End-to-end Source-to-Target Mapping (STTM) with architectural lineage flowcharts, star-schema ER diagram, transformation expressions, exception handling rules, and deterministic 1:1 provenance traceability.

The project is fully prepared for final dashboard integration and process mining handover with Member 4 ahead of the **8 November 2026** milestone deadline.

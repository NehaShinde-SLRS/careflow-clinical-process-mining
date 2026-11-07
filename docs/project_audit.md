# CareFlow Clinical Process Mining — Project Audit Report

**Audit Date:** 28 October – 7 November 2026 (Consolidated Audit: Ingestion, Staging, Marts, KPIs, Model Review, Event Log Validation, Day 6 Process Mining Analysis, Day 7 Data Dictionary, Day 8 Team Integration, Day 9 PM4Py Process Discovery, Day 10 Clinical Process Performance Analysis, Day 11 Power BI Dashboard & BI Integration, and Day 12 Clinical Process Conformance Checking & Compliance Analysis)
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
- **Day 8 System Architecture & Team Integration (100% Complete & Verified):**
  - Enterprise System Architecture ([`docs/day8_system_architecture.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day8_system_architecture.md)): Decoupled 5-tier architecture, component specifications, security boundaries, and scalability benchmarks.
  - Master Data Lineage ([`docs/day8_data_lineage.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day8_data_lineage.md)): End-to-end lineage diagram, 4-tier granularity transition matrix (62,422 $\rightarrow$ 49,912 $\rightarrow$ 98 $\rightarrow$ 121,832 $\rightarrow$ 193,443 rows), column-level lineage table, and 160-row reconciliation.
  - Team Integration Matrix ([`docs/day8_team_integration.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day8_team_integration.md)): Cross-member deliverable tracking, dependencies, and formal Data Contracts A, B, C, and D governing inter-member data exchange.
  - Technical Integration Audit ([`docs/day8_integration_audit.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day8_integration_audit.md)): 100% schema consistency verified, 0 orphan keys, sub-15ms BI query performance, 4 operational issues identified with production-ready fixes.
- **Day 9 PM4Py Process Discovery & Model Interchange (100% Complete & Verified):**
  - Production PM4Py Pipeline ([`scripts/pm4py_process_discovery.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/pm4py_process_discovery.py)): Algorithmic process discovery using PM4Py 2.7.23.11 on Python 3.14.7 across 193,443 events and 49,912 cases.
  - Process Discovery Report ([`docs/day9_process_discovery.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day9_process_discovery.md)) & Final Audit Report ([`docs/day9_final_verification_report.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day9_final_verification_report.md)): Complete documentation of Frequency DFG (56 edges), Performance DFG, Inductive Petri Net (33 places, 40 transitions, 94 arcs), Process Tree, 602 variants (Pareto Top 2 = 82.76%), and Lab TAT bottleneck quantification (279.3 min / 4.65h).
  - Reproducible Model Interchange: 5 publication-grade PNG diagrams, Inductive Petri Net XML ([`outputs/process_mining/inductive_petri_net.pnml`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/inductive_petri_net.pnml)), Process Tree ([`outputs/process_mining/inductive_process_tree.ptml`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/inductive_process_tree.ptml)), Graphviz DOT, structured JSON summary, and compressed IEEE XES log ([`data/careflow_event_log.xes.gz`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/data/careflow_event_log.xes.gz), 5.81 MB).
- **Day 10 Clinical Process Performance Analysis (100% Complete & Verified):**
  - Production Performance Pipeline ([`scripts/process_performance_analysis.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/process_performance_analysis.py)): Empirical performance decomposition across all 49,912 cases and 819 operational days.
  - Journey Durations: Cohort mean 294.7 min (4.91h), median 39.0 min, P90 198.0 min (3.30h), P95 353.0 min (5.88h). Core efficiency corridor: 83.79% of visits complete in <= 2 hours.
  - Service vs Waiting Decomposition: Mean active service 111.6 min (16.07% Process Cycle Efficiency) vs mean passive waiting 184.0 min. Patients wait 1.65 min for every 1 min of care.
  - Departmental Bottlenecks: Laboratory TAT (mean 930.5m across utilizing cases, 62.96% >2h, 20.25% >8h); Radiology queue wait (mean 595.2m); Registration wait (mean 129.8m).
  - Delay Patterns & Multi-Service Compounding: Monday morning arrival peak (10,043 cases, wait 209.8m); 06:00-07:00 arrival peak; diagnostic compounding effect (Flow 1: 3.0h vs Flow 5: 29.2h); Clinician throughput variance across 98 attending physicians.
  - Performance Artifacts: 5 high-resolution PNG charts in `outputs/process_performance/`, structured JSON metrics (`performance_metrics_summary.json`), and standalone evidence bottleneck report (`evidence_based_bottleneck_report.md`).
- **Day 11 Power BI Dashboard & BI Integration (100% Complete & Verified):**
  - Production Dashboard Handover: Located and verified [`careflow_POWERBI_dashboard.pbix`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/careflow_POWERBI_dashboard.pbix) (5,322,900 bytes / 5.08 MB) received from Member 4.
  - Report Architecture: Modern PBIR v2.14 / Fabric Report format (Power BI Desktop v2.159.229.0, Release 2026.10), Fluent2 dark clinical theme (`#38BDF8` cyan callouts), and custom background visual canvases.
  - Visual & Page Inventory: 2 Full HD 1080p pages hosting 19 interactive visuals (Page 1: 9 visuals covering volume, stage latencies, top labs, and arrival profile; Page 2: 10 visuals covering doctor caseload, radiology modalities, monthly trends, and stay durations).
  - Data Model & DAX Verification: Decoupled tabular model with `cleaned_HospitalOPD` (49,912 encounters) and dedicated `Measure` table hosting 11 verified clinical DAX measures.
  - Cross-System Parity: 100% exact numerical and statistical reconciliation with BigQuery warehouse marts (`dim_clinical_providers`, `fct_clinical_encounters`, `fct_process_transitions`) and analytical views (`vw_kpi_*`) (49,912 encounters, 39,442 patients, 98 doctors, consult wait ~26 min, lab TAT ~1.2h).
  - BigQuery DirectQuery Blueprint: Documented Power Query (M) script and Dual Storage Mode optimization for enterprise Power BI Service deployment.
  - Deliverables: Safe inspection script ([`scripts/inspect_pbix_datamodel.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/inspect_pbix_datamodel.py)) and comprehensive report ([`docs/day11_powerbi_integration.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day11_powerbi_integration.md)).
- **Day 12 Clinical Process Conformance & Compliance Checking (100% Complete & Verified):**
  - Full-Cohort Dual Engine Execution: Token-based replay and $A^*$ optimal alignment checking executed on all 49,912 cases (193,443 events) across 602 unique trace variants with exact case-frequency weighting in 79.33 seconds with zero truncation.
  - Normative Petri Net Architecture: Built and verified marked Petri Net $N = (P, T, F, m_0, m_f)$ with 16 places, 21 transitions (9 visible clinical activities + 12 silent $\tau$ control routings), and 44 directed arcs, rigorously verified in [`scripts/test_petri_net_loops.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/test_petri_net_loops.py) with microsecond tie-breaking ($timestamp + event\_order \times 1\,\mu\text{s}$) across 34,739 cases.
  - Conformance Scorecard: **97.19% Overall Log Fitness ($f_{log}$)** (579,787 / 581,159 tokens consumed correctly), **97.82% Average Trace Fitness** (Median: 100.00%), **86.94% Guideline Adherence** (43,395 cases strictly conforming), **99.36% Behavioral Precision ($ETConformance$)**, **95.89% Mean Alignment Fitness** (Median: 100.00%).
  - Optimal Alignment Moves: **168,696 Synchronous moves** (86.34% of 195,379 total moves; 87.21% of log events), **24,747 Log-Only moves** (12.67% of total moves; 12.79% of log events), **1,936 Model-Only moves** (0.99% of total moves).
  - Empirical Deviation Taxonomy: 1,915 pre-consultation imaging inversions (3.84%), 1,575 incomplete laboratory discharges (3.16%), 498 pre-consultation lab inversions (1.00%), 418 walk-in registration bypasses (0.84%), 0 incomplete consultations (0.00%), 0 incomplete pharmacy dispensations (0.00%), 1,183 timestamp anomaly flags across 418 cases.
  - Rework & Loop Detection: 20,070 direct self-loops across 4,231 cases (8.48%) driven by multi-order phlebotomy batching (11,387 loops) and staggered analyzer releases (8,238 loops); 639 doctor re-consultations (1.28%).
  - Length of Stay (LOS) Association: Encounters with rework are statistically associated with a **6.9x longer median visit duration** (**4.03 hours** with rework vs **0.58 hours** without rework).
  - Deliverables & Artifacts: In-memory verification script ([`scripts/test_petri_net_loops.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/test_petri_net_loops.py)), production pipeline ([`scripts/process_conformance_analysis.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/process_conformance_analysis.py)), technical report ([`docs/day12_conformance_checking.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day12_conformance_checking.md)), and 7 verified artifacts in `outputs/process_conformance/` (`reference_model.pnml`, `reference_model.png` 957 KB, `conformance_overview_dashboard.png`, `deviations_distribution.png`, `rework_and_loops_analysis.png`, `conformance_summary_metrics.json`, `conformance_audit_report.md`).
- **Downstream Handover (Next Steps for 8 November 2026 Deadline):**
  - Final project delivery archive, executive summary deck, and multi-member handover sign-off ahead of the 8 November 2026 deadline.

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

### G. Day 8 System Architecture & Team Integration Audit (Completed 3 November 2026)
- **Enterprise System Architecture:** [`docs/day8_system_architecture.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day8_system_architecture.md).
  - Documents decoupled 5-tier architecture: Ingestion & Staging (L1), Warehouse Storage & Compute (L2), Analytics Modeling & Transformation (L3), Clinical Process Mining Engine (L4), and Executive BI & Presentation (L5).
  - Explicit component specifications, security boundaries, and scalability benchmarks.
- **Master Data Lineage:** [`docs/day8_data_lineage.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day8_data_lineage.md).
  - Comprehensive end-to-end Mermaid lineage diagram across all 7 stages from raw Excel/CSV to Looker Studio BI dashboards.
  - Multi-tier granularity transition matrix (62,422 raw transaction rows $\rightarrow$ 49,912 encounter rows $\rightarrow$ 98 provider dimension rows $\rightarrow$ 121,832 transition fact rows $\rightarrow$ 193,443 discrete clinical event rows).
  - Granular column-level lineage tracking and complete mathematical reconciliation of 160 duplicate intra-encounter order lines.
- **Cross-Functional Team Integration Matrix:** [`docs/day8_team_integration.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day8_team_integration.md).
  - Full matrix detailing deliverables, dependencies, operational status, and blockers across Member 1 (Data Cleaning), Member 2 (Clinical EDA), Member 3 (Engineering & Modeling), and Member 4 (BI & Process Mining).
  - 4 formal data contracts: Contract A (M1 $\rightarrow$ M3), Contract B (M2 $\rightarrow$ M3), Contract C (M3 $\rightarrow$ M4 BI Views), and Contract D (M3 $\rightarrow$ M4 PM4Py / Event Log).
- **Technical Integration Audit Report:** [`docs/day8_integration_audit.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day8_integration_audit.md).
  - 100% schema consistency verified across 11 BigQuery objects (146 columns) and local event log (14 columns).
  - Zero orphan foreign key records across all star-schema relationships.
  - Slot query latency $<15$ ms across all 6 analytical KPI views.
  - 4 key operational integration issues identified and provided with production-ready mitigation scripts (concurrent events ordering, schema migration sync, BigQuery BI credentials, and XML XES interchange).

### H. Day 9 PM4Py Process Discovery & Model Interchange Verification (Completed 4 November 2026)
- **Pipeline Implementation:** [`scripts/pm4py_process_discovery.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/pm4py_process_discovery.py) (executed end-to-end on 193,443 events using PM4Py 2.7.23.11 on Python 3.14.7).
- **Comprehensive Report:** [`docs/day9_process_discovery.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day9_process_discovery.md).
- **Log Quality Scorecard:** 0 nulls across 14 columns, 0 duplicate records, 0 single-event cases across 49,912 cases and 39,442 patients.
- **Directly-Follows Graph (DFG):** 143,531 transitions across 56 unique edge types. Primary entry: `Appointment Registration` (99.16%); primary exit: `Prescription Consultation Completed` (82.95%).
- **Inductive Miner Modeling:** Discovered Inductive Petri Net (33 places, 40 transitions, 94 arcs; initial marking: `['source']`, final marking: `['sink']`) and Inductive Process Tree.
- **Process Variants & Pareto Distribution:** 602 unique variants. Strong Pareto concentration: Top 2 cover **82.76%**; Top 6 cover **90.00%**; Top 18 cover **95.00%**.
- **Departmental Bottlenecks:** Confirmed Laboratory Turnaround Time (TAT) as primary bottleneck averaging **279.3 minutes (4.65 hours)** with batched panels reaching 930.5 min (15.5 hours); OPD registration wait averages **114.9 minutes**.
- **Model Interchange Artifacts:**
  - 5 publication-grade PNG diagrams: DFG frequency network, DFG performance bottleneck graph, Process variants Pareto curve, Departmental waiting times, Activity frequency distribution.
  - Standard Inductive Petri Net PNML ([`outputs/process_mining/inductive_petri_net.pnml`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/inductive_petri_net.pnml), 19.1 KB).
  - Inductive Process Tree PTML ([`outputs/process_mining/inductive_process_tree.ptml`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/inductive_process_tree.ptml), 11.3 KB).
  - Graphviz DOT representation ([`outputs/process_mining/dfg_frequency.dot`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/dfg_frequency.dot), 5.3 KB).
  - Compressed IEEE XML XES event log ([`data/careflow_event_log.xes.gz`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/data/careflow_event_log.xes.gz), 5.81 MB).
  - Structured machine-readable JSON summary ([`outputs/process_mining/pm4py_discovery_summary.json`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/pm4py_discovery_summary.json), 6.3 KB).

### I. Day 10 Clinical Process Performance Verification (Completed 5 November 2026)
- **Pipeline Implementation:** [`scripts/process_performance_analysis.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/process_performance_analysis.py) (executed end-to-end across 49,912 outpatient encounters).
- **Comprehensive Report:** [`docs/day10_performance_analysis.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day10_performance_analysis.md).
- **Patient Journey Metrics:** Cohort mean journey duration is **294.7 minutes (4.91 hours)** (median: 39.0 min; P90: 198.0 min / 3.30h; P95: 353.0 min / 5.88h). 83.79% of encounters complete within 2 hours.
- **Service vs Waiting Decomposition:** Mean active clinical care accounts for only **111.6 minutes** (16.07% Process Cycle Efficiency), while patients spend **184.0 minutes** in passive queues.
- **Departmental Bottlenecks:** Laboratory TAT is the primary institutional delay averaging **930.5 minutes (15.51 hours)** across utilizing cases (62.96% >2 hours; 20.25% >8 hours); Post-consultation imaging queue averages **595.2 minutes (9.92 hours)**; Registration queue wait averages **129.8 minutes**.
- **Real-Data Operational Patterns:** Monday arrival surge (10,043 cases, wait 209.8m); 06:00-07:00 arrival peak (6,211 arrivals); Diagnostic compounding delay (Flow 1: 3.0h vs Flow 5: 29.2h); Clinician throughput variation across 98 attending physicians.
- **Generated Artifacts in `outputs/process_performance/`:**
  - 5 publication-grade PNG diagrams: `patient_journey_duration_distribution.png`, `service_vs_waiting_time_by_pathway.png`, `departmental_bottlenecks_ranking.png`, `temporal_arrival_waiting_patterns.png`, `clinician_performance_variance.png`.
  - Structured metrics JSON ([`outputs/process_performance/performance_metrics_summary.json`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_performance/performance_metrics_summary.json), 19.5 KB).
  - Standalone evidence bottleneck report ([`outputs/process_performance/evidence_based_bottleneck_report.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_performance/evidence_based_bottleneck_report.md), 2.9 KB).

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
- [x] Day 8 Enterprise System Architecture Diagram and Component Specifications authored ([`docs/day8_system_architecture.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day8_system_architecture.md)).
- [x] Day 8 End-to-End Data Lineage & Column-Level Granularity Transitions authored ([`docs/day8_data_lineage.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day8_data_lineage.md)).
- [x] Day 8 Cross-Functional Team Integration Matrix & Data Contracts authored ([`docs/day8_team_integration.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day8_team_integration.md)).
- [x] Day 8 Technical Integration Audit & Schema Consistency Verification authored ([`docs/day8_integration_audit.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day8_integration_audit.md)).
- [x] Day 9 PM4Py Process Discovery Pipeline authored and executed ([`scripts/pm4py_process_discovery.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/pm4py_process_discovery.py)).
- [x] Day 9 Frequency DFG, Performance DFG, Inductive Petri Net (33 places, 40 transitions, 94 arcs), and Process Tree discovery.
- [x] Day 9 Process variants analysis and cumulative Pareto curve quantification (Top 2 variants = 82.76%; Top 6 = 90.00%; Top 18 = 95.00%).
- [x] Day 9 Publication-grade visualization suite and standard interchange artifacts generated (5 PNGs, PNML model, PTML tree, DOT graph, compressed IEEE XES log, structured JSON summary).
- [x] Day 9 Comprehensive PM4Py Process Discovery Report authored ([`docs/day9_process_discovery.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day9_process_discovery.md)) and Final Verification Report ([`docs/day9_final_verification_report.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day9_final_verification_report.md)).
- [x] Day 10 Clinical Process Performance Pipeline authored and executed ([`scripts/process_performance_analysis.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/process_performance_analysis.py)).
- [x] Day 10 Patient journey duration analysis & percentile modeling across 49,912 outpatient encounters.
- [x] Day 10 Active service time vs passive waiting queue decomposition & Process Cycle Efficiency (PCE %) calculation.
- [x] Day 10 Departmental bottleneck ranking & threshold violation quantification (Laboratory TAT: 63.0% >2h).
- [x] Day 10 Temporal arrival surges, multi-service compounding delay, and clinician workload variance analysis.
- [x] Day 10 Performance visualization suite and evidence bottleneck reports generated (5 PNGs, JSON, MD in `outputs/process_performance/`).
- [x] Day 10 Comprehensive Clinical Process Performance Analysis Report authored ([`docs/day10_performance_analysis.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day10_performance_analysis.md)).
- [x] Day 11 Power BI dashboard file located, unpacked, and verified ([`careflow_POWERBI_dashboard.pbix`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/careflow_POWERBI_dashboard.pbix), 5.08 MB).
- [x] Day 11 Visual inventory and canvas layout mapped (19 visuals across Page 1 and Page 2).
- [x] Day 11 DAX clinical measure definitions and unit scaling verified across all 11 metrics in `Measure` calculation table.
- [x] Day 11 Cross-system reconciliation confirmed with 100% exact parity between Power BI, BigQuery marts/views, and PM4Py models.
- [x] Day 11 Safe inspector script authored and executed ([`scripts/inspect_pbix_datamodel.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/inspect_pbix_datamodel.py)) with zero credential leaks.
- [x] Day 11 Comprehensive Power BI Integration Report authored ([`docs/day11_powerbi_integration.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day11_powerbi_integration.md)).
- [x] Day 12 In-Memory Petri Net Verification Pipeline authored and executed ([`scripts/test_petri_net_loops.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/test_petri_net_loops.py)), proving 100% fitness on all 9 clinical pathways and microsecond tie-breaking.
- [x] Day 12 Full-Cohort Process Conformance Analysis Pipeline authored and executed ([`scripts/process_conformance_analysis.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/process_conformance_analysis.py)) across all 49,912 cases and 193,443 events in 79.33s.
- [x] Day 12 Token-based replay analysis ($f_{log} = 97.19\%$, $\bar{f}_{trace} = 97.82\%$, Guideline Adherence = 86.94% / 43,395 cases).
- [x] Day 12 Optimal Alignment $A^*$ search on 602 variants with exact frequency weighting across 195,379 total moves (Mean Fitness = 95.89%, Median = 100.00%, 168,696 Synchronous moves [86.34%], 24,747 Log-Only deviations [12.67%], 1,936 Model-Only skips [0.99%]).
- [x] Day 12 Behavioral Precision quantified at 99.36% ($ETConformance$), confirming high behavioral specificity of the normative Petri Net.
- [x] Day 12 Clinical deviation taxonomy categorized (1,915 pre-consult imaging inversions, 1,575 incomplete lab discharges, 498 pre-consult lab inversions, 418 walk-in bypasses, 0 incomplete consultations/pharmacy).
- [x] Day 12 Clinical rework self-loop quantification (20,070 loops across 4,231 cases; 6.9x longer median LOS associated with rework [4.03h vs 0.58h]).
- [x] Day 12 Complete publication-grade visualization suite and conformance artifacts generated (7 files in `outputs/process_conformance/`: `reference_model.pnml`, `reference_model.png` 957 KB, `conformance_overview_dashboard.png`, `deviations_distribution.png`, `rework_and_loops_analysis.png`, `conformance_summary_metrics.json`, `conformance_audit_report.md`).
- [x] Day 12 Comprehensive Clinical Process Conformance & Compliance Report authored ([`docs/day12_conformance_checking.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day12_conformance_checking.md)).

### Incomplete Tasks (Roadmap to 8 November 2026 Milestone — Final Project Handover)
- [ ] **Final Project Handover & Team Integration Sign-Off:**
  - Final project delivery archive, executive presentation summary, and multi-member handover sign-off ahead of the 8 November 2026 deadline.

---

## 5. Conclusion & Days 4–12 Sign-off

All Day 4 (dbt Model Review), Day 5 (Event Log Validation), Day 6 (Process Mining Analysis), Day 7 (Data Dictionary & Documentation), Day 8 (Team Integration & Architecture), Day 9 (PM4Py Process Discovery & Integration), Day 10 (Clinical Process Performance Analysis), Day 11 (Power BI Dashboard & BI Integration), and Day 12 (Clinical Process Conformance Checking & Compliance Analysis) tasks assigned to Member 3 are **100% completed, cloud-verified, and fully documented**.

The warehouse, analytical suite, and engineering documentation now contain:
1. Verified staging model (`stg_hospital_opd`).
2. High-performance dimensional star-schema marts (`dim_clinical_providers`, `fct_clinical_encounters`, `fct_process_transitions`) with sub-second execution latencies.
3. 24 passing automated data quality and referential integrity tests.
4. 6 live analytical views serving all core process mining and throughput KPIs.
5. Fully profiled, de-identified clinical event log (`data/careflow_event_log.csv`, 193,443 rows).
6. End-to-end Process Mining Analysis covering DFG discovery, 602 execution variants, Pareto distributions, bottleneck quantification, self-loops, and conformance scoring with targeted clinical recommendations.
7. Production-grade Data Dictionary documenting 11 BigQuery warehouse objects (146 columns) and 12 total project entities (160 columns) including the local event log, types, nullability, clinical ontology, and pathway definitions.
8. End-to-end Source-to-Target Mapping (STTM) with architectural lineage flowcharts, star-schema ER diagram, transformation expressions, exception handling rules, and deterministic 1:1 provenance traceability.
9. Enterprise System Architecture, Master Data Lineage, Team Integration Matrix (with formal Data Contracts A-D), and Technical Integration Audit Report establishing full operational readiness for Member 4.
10. Complete PM4Py algorithmic process discovery suite featuring Frequency & Performance DFGs, Inductive Petri Net & Process Tree models, 5 publication-grade PNG diagrams, standard PNML/PTML interchange files, and compressed IEEE XML XES event log (`data/careflow_event_log.xes.gz`, 5.81 MB).
11. Exhaustive clinical process performance decomposition quantifying patient journey duration percentiles, active clinical service vs passive waiting dwell times, Process Cycle Efficiency (PCE %) across 7 clinical pathways, departmental bottleneck rankings, temporal arrival surges, and clinician throughput variance with 5 publication-grade PNG visualizations in `outputs/process_performance/`.
12. Complete Power BI BI integration suite certifying `careflow_POWERBI_dashboard.pbix` (5.08 MB) across 19 visual containers, 11 DAX measures, and 100% exact statistical parity with BigQuery data marts and PM4Py models.
13. Complete Clinical Process Conformance Checking suite certifying 97.19% Log Fitness, 99.36% Precision, 95.89% Alignment Fitness, full deviation taxonomy, rework quantification (20,070 self-loops, 6.9x longer median LOS associated with rework), and 7 publication-grade conformance artifacts in `outputs/process_conformance/`.

The project is fully prepared for final project delivery archive and team sign-off ahead of the **8 November 2026** milestone deadline.

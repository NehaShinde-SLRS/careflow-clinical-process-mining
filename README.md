# CareFlow — Clinical Process Mining & Pathway Intelligence

[![Python 3.14](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![Google BigQuery](https://img.shields.io/badge/Google_Cloud-BigQuery-669DF6.svg)](https://cloud.google.com/bigquery)
[![dbt Core](https://img.shields.io/badge/dbt-Core_1.8+-FF694B.svg)](https://www.getdbt.com/)
[![PM4Py](https://img.shields.io/badge/PM4Py-2.7.23-2E7D32.svg)](https://pm4py.fit.fraunhofer.de/)
[![Power BI](https://img.shields.io/badge/Power_BI-Desktop_2026-F2C811.svg)](https://powerbi.microsoft.com/)
[![Project Status](https://img.shields.io/badge/Project_Status-Verified_with_Limitations-success.svg)]()

CareFlow is an enterprise-grade clinical process intelligence and pathway mining initiative conducted between **28 October and 8 November 2026**. 

Analyzing an outpatient cohort of **49,912 visit encounters** (193,443 events) across **819 operational days** (`2024-04-25` to `2026-07-23`), the platform uncovers true patient flow dynamics, quantifies systemic diagnostic bottlenecks, evaluates clinical guideline compliance, and surfaces actionable operational interventions for hospital leadership.

---

## 1. Enterprise System Architecture

CareFlow decouples data processing, analytical modeling, process mining, and visual reporting into four modular tiers:

```
                                  CareFlow Architecture Stack
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 1: Data Acquisition & Preprocessing                                                              │
│  - Raw Outpatient Encounter Dataset: data/HospitalOPD_cleaned.csv (62,422 rows, 24 cols)               │
│  - Process Mining Event Log: data/careflow_event_log.csv (193,443 rows, 14 cols, 49,912 cases)        │
│  - Standard XES Archive: data/careflow_event_log.xes.gz (6.09 MB compressed IEEE XML XES)             │
└───────────────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 2: Cloud Data Warehouse & Dimensional Marts (Google Cloud Platform & dbt Core)                   │
│  - Target BigQuery Dataset: careflow-clinical-process-m.careflow_opd (Region: US)                     │
│  - Cleaned Staging View: stg_hospital_opd (62,422 rows)                                               │
│  - Dimensional Star-Schema: dim_clinical_providers (98 rows), fct_clinical_encounters (49,912 rows),   │
│    fct_process_transitions (121,832 canonical state transitions)                                      │
│  - Automated Test Suite: 24/24 Data Quality & Referential Integrity Tests Passed (PASS=24, ERROR=0)   │
│  - Analytical KPI Views: 6 Live SQL Views deployed in careflow_opd                                     │
└───────────────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 3: Advanced Process Mining Engine (Python 3.14 & PM4Py 2.7.23.11)                                │
│  - Process Discovery: Frequency DFG (56 edges), Performance DFG, Inductive Petri Net, Process Tree     │
│  - Process Variants: 602 unique variants (Pareto Top 2 = 82.76%, Top 6 = 90.00%, Top 18 = 95.00%)     │
│  - Performance Decomposition: Active Service vs Passive Wait (PCE = 16.07%), Departmental Bottlenecks │
│  - Conformance Checking: Normative Petri Net (16 P, 21 T, 44 A), Token Replay (f_log = 97.19%),        │
│    Optimal Alignment A* (f_align = 95.89%), Precision (99.36%), Deviation & Rework Taxonomy           │
└───────────────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 4: Business Intelligence & Decision Support (Microsoft Power BI & Executive Reports)             │
│  - Production Dashboard: careflow_POWERBI_dashboard.pbix (5.08 MB, PBIR v2.14, Import Mode over CSV)   │
│  - Verified Parity: 100% Exact Match on Core Entities (49,912 Encounters, 39,442 Patients, 98 Doctors) │
│  - Visual Artifacts Suite: 23 Publication-Grade Charts & Model Files in outputs/                       │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Key Empirical Findings & Clinical Scorecard

| Analytical Domain | Primary Metric | Empirical Value | Clinical Interpretation & Governance Context |
| :--- | :--- | :---: | :--- |
| **Cohort Scale** | Total Encounters / Cases | **49,912** | Complete outpatient population analyzed over 819 operational days |
| **Beneficiaries** | Distinct Patients Served | **39,442** | Average of 1.27 outpatient visits per unique patient |
| **Physicians** | Attending Outpatient Clinicians | **98** | Tracked across general OPD and specialized clinical clinics |
| **Primary Happy Path** | Pathway 1 (`Appt → Consult`) | **79.47% (39,667)**| Standard consultation journey (median duration: 29.0 minutes) |
| **Diagnostic Referral**| Pathways with Lab / Imaging | **20.31% (10,137)**| Diagnostic testing escalates visit durations (8.0 to 24.9 hours) |
| **Cycle Efficiency** | Process Cycle Efficiency (PCE) | **16.07%** | Patients wait 1.65 minutes passively for every 1 minute of active medical care |
| **Primary Bottleneck** | Laboratory Turnaround Time (TAT)| **930.5 min (15.5h)**| Mean TAT across utilizing visits; 62.96% exceed 2h benchmark |
| **Secondary Bottleneck**| Post-Consultation Radiology Queue| **595.2 min (9.92h)**| Median wait before imaging scan is 39.0 min; mean is 9.9 hours |
| **Arrival Surge** | Diurnal Intake Peak | **2,640 arrivals** | Monday 06:00–07:00 arrival peak inflates waiting time to 209.8 min |
| **Log Fitness** | Overall Log Fitness ($f_{log}$) | **97.19%** | Token replay: 579,787 / 581,159 tokens consumed correctly |
| **Trace Adherence** | Strictly Conforming Cases | **86.94% (43,395)**| Encounters follow normative reference guidelines with zero deviations |
| **Model Precision** | Behavioral Precision ($P_{ET}$) | **99.36%** | High behavioral specificity closely constraining valid clinical pathways |
| **Alignment Fitness** | Mean $A^*$ Alignment Fitness | **95.89%** | Median: 100.00% across 195,379 total moves (86.34% synchronous) |
| **Clinical Rework** | Cases with Direct Self-Loops | **4,231 (8.48%)** | 20,070 loops driven by multi-order lab batching and result verification |
| **LOS Association** | Median Duration with Rework | **4.03h vs 0.58h** | 6.9x longer median duration statistically associated with clinical rework |

---

## 3. Repository Directory Structure

```
careflow-clinical-process-mining/
├── careflow_POWERBI_dashboard.pbix   # Production Power BI Dashboard (5.32 MB, 19 visuals)
├── README.md                          # Master Project Repository Portal
├── .gitignore                         # Git tracking exclusions
│
├── data/                              # Source & Processed Datasets (Protected & Read-Only)
│   ├── HospitalOPD_cleaned.csv        # Working copy encounter dataset (62,422 rows, 24 cols)
│   ├── HospitalOPD_cleaned.csv.bak    # Pre-load verified safe backup (11.28 MB)
│   ├── careflow_event_log.csv         # Process mining event log (193,443 rows, 14 cols)
│   └── careflow_event_log.xes.gz      # IEEE XML XES compressed event log (6.09 MB)
│
├── dbt/                               # dbt Cloud Transformation & Schema Test Suite
│   ├── dbt_project.yml                # dbt project definition (careflow_dbt v1.0.0)
│   ├── profiles.yml                   # Service-account profile (careflow_bigquery)
│   ├── models/
│   │   ├── sources.yml                # BigQuery raw source table declaration
│   │   ├── staging/
│   │   │   ├── stg_hospital_opd.sql   # Cleaned encounter staging view (62,422 rows)
│   │   │   └── schema.yml             # Staging primary key & domain tests (7 tests)
│   │   └── marts/
│   │       ├── dim_clinical_providers.sql # Attending physician dimension (98 rows)
│   │       ├── fct_clinical_encounters.sql# Visit encounter fact table (49,912 rows)
│   │       ├── fct_process_transitions.sql# Process transition fact table (121,832 rows)
│   │       └── schema.yml             # Marts schema & referential integrity tests (17 tests)
│   └── target/                        # Compiled SQL & run_results.json (24/24 tests passed)
│
├── sql/                               # Production BigQuery SQL Suites
│   ├── validation_queries.sql         # 8 data quality & reconciliation audit checks
│   ├── kpi_analysis_views.sql         # 6 analytical KPI views deployed in careflow_opd
│   └── day6_process_mining_queries.sql# SQL process discovery & variant analysis queries
│
├── scripts/                           # Production Python Pipelines (Python 3.14 / PM4Py 2.7)
│   ├── inspect_dataset.py             # Day 1: Source dataset inspection & profiling
│   ├── export_to_csv.py               # Day 2: Safe CSV export & backup generator
│   ├── load_to_bigquery.py            # Day 3: Idempotent BigQuery cloud table loader
│   ├── prepare_event_log.py           # Day 5: Event log transformation & de-identification
│   ├── process_mining_analysis.py     # Day 6: Initial DFG & variant mining pipeline
│   ├── pm4py_process_discovery.py     # Day 9: Inductive Miner & PM4Py discovery pipeline
│   ├── process_performance_analysis.py# Day 10: Performance decomposition & queue pipeline
│   ├── inspect_pbix_datamodel.py      # Day 11: Safe read-only Power BI model inspector
│   ├── inspect_pbix.py                # Day 11: Deep PBIX layout inspector
│   ├── test_petri_net_loops.py        # Day 12: In-memory Petri Net pathway validator
│   └── process_conformance_analysis.py# Day 12: Full-cohort conformance checking pipeline
│
├── outputs/                           # Verified Publication Artifacts & Models
│   ├── process_mining/                # Day 9: Process Discovery Deliverables (9 files)
│   │   ├── dfg_frequency_graph.png    # Frequency Directly-Follows Graph
│   │   ├── dfg_performance_graph.png  # Performance Directly-Follows Graph (Durations)
│   │   ├── process_variants_pareto.png# Cumulative Pareto variant distribution
│   │   ├── bottleneck_waiting_times.png# Queue latency comparison chart
│   │   ├── activity_frequency_distribution.png # Activity occurrence counts
│   │   ├── inductive_petri_net.pnml   # Discovered Inductive Petri Net XML
│   │   ├── inductive_process_tree.ptml# Discovered Process Tree XML
│   │   ├── dfg_frequency.dot          # Graphviz DOT graph representation
│   │   └── pm4py_discovery_summary.json # Structured discovery metrics JSON
│   ├── process_performance/           # Day 10: Performance Decomposition Deliverables (7 files)
│   │   ├── patient_journey_duration_distribution.png # Journey duration histogram
│   │   ├── service_vs_waiting_time_by_pathway.png    # Service vs waiting time breakdown
│   │   ├── departmental_bottlenecks_ranking.png      # Departmental bottleneck rates
│   │   ├── temporal_arrival_waiting_patterns.png     # Hourly/diurnal intake heatmaps
│   │   ├── clinician_performance_variance.png        # Attending physician workloads
│   │   ├── performance_metrics_summary.json          # Structured performance metrics
│   │   └── evidence_based_bottleneck_report.md       # Evidence bottleneck report
│   └── process_conformance/           # Day 12: Conformance Checking Deliverables (7 files)
│       ├── reference_model.pnml       # Normative Reference Petri Net XML (16 P, 21 T)
│       ├── reference_model.png        # 300 DPI layout diagram of normative model
│       ├── conformance_overview_dashboard.png # 4-panel executive conformance dashboard
│       ├── deviations_distribution.png# Pathway deviation & bypass distribution
│       ├── rework_and_loops_analysis.png # Loop delay breakdown & 6.9x LOS boxplot
│       ├── conformance_summary_metrics.json # Full structured conformance metrics
│       └── conformance_audit_report.md# Standalone compliance audit report
│
└── docs/                              # Comprehensive Technical Documentation (23 reports)
    ├── day13_final_handover_report.md # Master Project Handover & Executive Synthesis Report
    ├── project_audit.md               # Master Consolidated Project Audit (Days 1–13)
    ├── member3_workflow.md            # Data Engineering & Process Mining Workflow Log
    ├── day12_conformance_checking.md  # Day 12: Advanced Conformance & Compliance Report
    ├── day11_powerbi_integration.md   # Day 11: Power BI Data Model & Reconciliation Report
    ├── day10_performance_analysis.md  # Day 10: Clinical Process Performance Report
    ├── day9_process_discovery.md      # Day 9: PM4Py Algorithmic Discovery Report
    ├── day9_final_verification_report.md # Day 9: Model Interchange Verification Report
    ├── day8_system_architecture.md    # Day 8: Enterprise Platform Architecture Report
    ├── day8_data_lineage.md           # Day 8: End-to-End Master Data Lineage Report
    ├── day8_team_integration.md       # Day 8: Cross-Member Contracts (Data Contracts A–D)
    ├── day8_integration_audit.md      # Day 8: Technical Schema & Integration Audit Report
    ├── data_dictionary.md             # Production Data Dictionary (12 entities, 160 cols)
    ├── source_to_target_mapping.md    # Master Source-to-Target Mapping (STTM)
    ├── day6_process_mining_analysis.md# Day 6: Exploratory Process Mining Report
    ├── day6_event_log_report.md       # Day 6: Event Log Schema Verification Report
    ├── day5_event_log_validation_report.md # Day 5: 8-Dimension Event Log Quality Report
    ├── day5_data_quality_report.md    # Day 5: Outpatient Data Quality Report
    ├── day4_completion_report.md      # Day 4: dbt Model Architecture & Latency Report
    ├── day3_completion_report.md      # Day 3: BigQuery Ingestion & Schema Test Report
    ├── day3_day4_completion_report.md # Day 3–4: Ingestion & Model Completion Report
    ├── member3_data_requirements.md   # Engineering Prerequisites & Source Ingestion Contract
    └── data_quality_notes.md          # Initial Dataset Quality Observations
```

---

## 4. How to Execute the Pipelines

### 4.1 Prerequisites
- Python 3.10+ (tested on Python 3.14.7).
- Google Cloud SDK & BigQuery service-account key (`GOOGLE_APPLICATION_CREDENTIALS`).
- Core libraries: `pandas`, `pm4py>=2.7.0`, `matplotlib`, `dbt-bigquery>=1.8.0`.

### 4.2 Pipeline Execution Commands (PowerShell)

```powershell
# 1. Set Google Cloud Service Account Credentials
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\service-account-key.json"
$env:CAREFLOW_GCP_PROJECT = "careflow-clinical-process-m"

# 2. Ingest Working Dataset into BigQuery
python scripts/load_to_bigquery.py

# 3. Execute dbt Staging Models, Marts & Automated Test Suite (24 tests)
python -m dbt.cli.main run --project-dir dbt --profiles-dir dbt
python -m dbt.cli.main test --project-dir dbt --profiles-dir dbt

# 4. Transform & Prepare Clinical Process Mining Event Log
python scripts/prepare_event_log.py

# 5. Run Day 9 PM4Py Process Discovery Pipeline (DFGs, Petri Net, XES)
python scripts/pm4py_process_discovery.py

# 6. Run Day 10 Process Performance Analysis Pipeline (PCE %, Bottlenecks)
python scripts/process_performance_analysis.py

# 7. Execute Safe Power BI Tabular Model Inspector
python scripts/inspect_pbix_datamodel.py

# 8. Run In-Memory Petri Net Pathway Verification Script
python scripts/test_petri_net_loops.py

# 9. Execute Day 12 Full-Cohort Process Conformance Analysis Pipeline
python scripts/process_conformance_analysis.py
```

---

## 5. Clinical Governance Recommendations

Based on empirical bottleneck quantification and conformance checking across 49,912 encounters, four actionable operational reforms are delivered to hospital leadership:

1. **Mandatory Administrative Registration Hard-Stops:**
   - *Problem:* 418 encounters (0.84%) contain 1,183 events logged prior to recorded front-desk registration, primarily from departmental diagnostic orders stamped before administrative check-in.
   - *Intervention:* Configure EHR hard-stops requiring barcode wristband registration scans prior to phlebotomy accessioning or radiology acquisition. Urgent walk-in stabilization must log a designated "Acute Care Override" flag.
2. **Standardization of Pre-Consultation Diagnostic Protocols:**
   - *Problem:* 1,915 pre-consultation imaging inversions (3.84%) and 498 pre-consultation lab inversions (1.00%) represent guideline deviations under strict serial models.
   - *Intervention:* Formally sanction chronic disease follow-up care pathways in the hospital EHR as "Protocol-Authorized Pre-Visits" (e.g., routine orthopedic follow-up X-rays, oncology restaging scans), ensuring prior contraindication screening is documented.
3. **Automated Laboratory Send-Out Result Reconciliation:**
   - *Problem:* 1,575 encounters (3.16%) discharged with dangling uncompleted laboratory orders due to delayed 48–72h send-out assays.
   - *Intervention:* Implement an automated LIS-EHR reconciliation daemon that closes outpatient encounter records upon secondary result transmission, routing panic values directly to the primary attending physician's mobile inbox.
4. **Dedicated Express Results-Review Clinics:**
   - *Problem:* Outpatient visits involving clinical rework and physician re-consultations are associated with a **6.9x longer median duration** (4.03 hours vs 0.58 hours).
   - *Intervention:* Establish dedicated "Results-Review Express Clinics" staffed by senior nurse practitioners or triage physicians to review diagnostic findings, eliminating the need for patients to re-enter general consultation waiting queues.

---

## 6. Project Sign-Off & Official Status

- **Execution Status:** **COMPLETED WITH DOCUMENTED LIMITATIONS**  
- **Validation Status:** **VERIFIED WITH DOCUMENTED LIMITATIONS** (SHA-256 hashes strictly verified for 7 core protected files; dbt configs and analytical outputs verified for presence and execution with documented pre-Day 13 baseline limitations)  
- **Final Sign-Off Date:** **8 November 2026**  
- **Role:** Database Management  
- **Target Recipient:** CareFlow Clinical Operations, Hospital Leadership & Cross-Functional Team

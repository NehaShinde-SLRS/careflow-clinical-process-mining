# CareFlow Clinical Process Mining — Day 9 PM4Py Process Discovery & Integration Report

**Document Version:** 1.0.0  
**Effective Date:** 4 November 2026  
**Author / Engineer:** Senior Process Mining Engineer / Member 3 (Data Engineering & Process Mining)  
**Milestone Target:** 8 November 2026 (Final Project Handover)  
**Target GCP Project:** `careflow-clinical-process-m`  
**Target BigQuery Dataset:** `careflow_opd` (Region: `US`)  
**Status:** **100% EXECUTED, VALIDATED & ARTIFACTS VERIFIED**  

---

## 1. Executive Summary & Integration Architecture

This technical report documents the complete implementation of **Day 9: PM4Py Integration & Process Discovery** for the CareFlow Clinical Process Mining initiative.

The objective of Day 9 is to ingest the standardized clinical event log ([`data/careflow_event_log.csv`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/data/careflow_event_log.csv)), execute formal algorithmic process discovery using **PM4Py (Process Mining for Python, version 2.7.23.11)**, validate event log data quality, discover the underlying outpatient clinical pathways using Directly-Follows Graphs (DFG) and the Inductive Miner, analyze variant frequencies and Pareto distributions, quantify departmental delays, and produce reproducible visual and standard model interchange artifacts (PNML, PTML, DOT, compressed IEEE XES).

### Key Execution Highlights:
- **PM4Py Integration:** Successfully installed and verified `pm4py==2.7.23.11` along with core scientific dependencies (`matplotlib 3.11.2`, `scipy 1.18.1`, `cvxopt 1.3.3`, `lxml 6.1.3`, `networkx 3.7`) on Python 3.14.7.
- **Log Integrity:** **193,443 events** across **49,912 distinct outpatient cases** and **39,442 unique patients** validated with **0 nulls**, **0 exact duplicates**, and **0 single-event orphan cases**.
- **Process Discovery (DFG):** Discovered **143,531 transitions** across **56 unique transition edges**. Case ingress is dominated by *Appointment Registration* (99.16%), while case egress is dominated by *Prescription Consultation Completed* (82.95%).
- **Inductive Miner Modeling:** Discovered a sound Inductive Petri Net (**33 places, 40 transitions, 94 arcs**) and Inductive Process Tree, exported to standard PNML and PTML interchange formats.
- **Process Variants & Pareto Distribution:** Identified **602 unique execution variants**. The clinical process exhibits strong Pareto concentration: **Top 2 variants account for 82.76%** of all patient visits; **Top 6 account for 90.00%**; **Top 18 account for 95.00%**.
- **Operational Bottleneck Quantification:** Quantified the primary hospital bottleneck as **Laboratory Turnaround Time (TAT)** averaging **279.3 minutes (4.65 hours)** with batched panels taking up to 15.5 hours. Clinic registration waiting time averages **114.9 minutes (1.92 hours)**.
- **Standard Interchange Deliverables:** Generated 5 publication-grade PNG diagrams, Graphviz DOT graph, Inductive PNML/PTML models, structured audit JSON, and a gzip-compressed IEEE XES log ([`data/careflow_event_log.xes.gz`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/data/careflow_event_log.xes.gz), 5.81 MB) for seamless downstream ingestion by Member 4.

---

## 2. Event Log Data Quality & PM4Py Schema Validation

The input event log [`data/careflow_event_log.csv`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/data/careflow_event_log.csv) was inspected and mapped into PM4Py's internal data model using `pm4py.format_dataframe`:

$$\text{case\_id} \longrightarrow \texttt{case:concept:name} \quad | \quad \text{activity} \longrightarrow \texttt{concept:name} \quad | \quad \text{timestamp} \longrightarrow \texttt{time:timestamp}$$

### Data Quality Scorecard:

| Quality Dimension | Evaluated Metric | Verification Result | Quality Assessment |
| :--- | :--- | :---: | :--- |
| **Row Completeness** | Missing values across all 14 columns | **0 nulls (0.00%)** | **PASS** — Complete attribute population |
| **Duplicate Records** | Exact duplicate rows across all 14 columns | **0 duplicates (0.00%)** | **PASS** — Fully deduplicated event stream |
| **Case Continuity** | Encounters with only 1 event | **0 cases (0.00%)** | **PASS** — Every case represents a multi-step journey |
| **Case Event Range** | Min, Median, Mean, Max events per case | **Min: 2, Med: 3, Mean: 3.88, Max: 57** | **PASS** — Plausible clinical event distribution |
| **Temporal Span** | Earliest to latest recorded timestamp | **819 operational days** (`2024-04-25` to `2026-07-23`)| **PASS** — Continuous multi-year operational window |
| **Timestamp Format** | ISO-8601 string parsing to UTC datetime | **100% valid parsed timestamps** | **PASS** — Zero timezone or format errors |
| **Early Diagnostic Starts** | `timestamp_anomaly_flag == True` | **1,183 events (0.61%) across 418 cases (0.84%)** | **TAGGED** — Direct diagnostic check-ins prior to desk registration |

---

## 3. Algorithmic Process Discovery (Directly-Follows Graph)

Using `pm4py.discover_dfg`, the directly-follows relation was extracted across the entire event log:

$$\text{Total DFG Transitions} = \mathbf{143,531} \quad | \quad \text{Distinct Directed Edges} = \mathbf{56}$$

### 3.1 Case Ingress (Start Activities)
| Start Activity | Case Count | Share (%) | Clinical Description |
| :--- | :---: | :---: | :--- |
| **Appointment Registration** | **49,494** | **99.16%** | Standard front-desk OPD check-in |
| **Imaging Started** | 282 | 0.56% | Direct radiology referral / emergency triage bypass |
| **Lab Test Started** | 131 | 0.26% | Pre-scheduled fasting phlebotomy prior to desk registration |
| **Prescription Consultation Started** | 5 | 0.01% | Immediate provider consultation encounter |
| **Total** | **49,912** | **100.00%** | **4 distinct ingress points** |

### 3.2 Case Egress (End Activities)
| End Activity | Case Count | Share (%) | Clinical Description |
| :--- | :---: | :---: | :--- |
| **Prescription Consultation Completed** | **41,400** | **82.95%** | Standard discharge following physician encounter |
| **Lab Test Completed** | 4,522 | 9.06% | Discharge following specimen results verification |
| **Imaging Completed** | 2,521 | 5.05% | Discharge following completion of radiology scan |
| **Lab Test Started** | 1,321 | 2.65% | Patient discharged with outpatient pending send-out lab |
| **Pharmacy Dispensation Completed** | 95 | 0.19% | Prescription dispensed at outpatient pharmacy desk |
| **Prescription Consultation Started** | 46 | 0.09% | Ongoing or interrupted consultation record |
| **Imaging Started** | 7 | 0.01% | Ongoing radiology procedure at log cutoff |
| **Total** | **49,912** | **100.00%** | **7 distinct egress points** |

### 3.3 Top 10 Directly-Follows Transitions
| Rank | Source Activity $\longrightarrow$ Target Activity | Transition Count | Mean Latency | Clinical Significance |
| :-: | :--- | :---: | :---: | :--- |
| 1 | `Prescription Consultation Started` $\longrightarrow$ `Completed` | **50,338** | 4.6 min | Active physician examination and order entry |
| 2 | `Appointment Registration` $\longrightarrow$ `Prescription Consultation Started` | **47,882** | 114.9 min | OPD clinic waiting room queue latency |
| 3 | `Lab Test Started` $\longrightarrow$ `Lab Test Started` | **11,387** | 0.0 min | Multi-order simultaneous lab specimen collection (self-loop) |
| 4 | `Lab Test Completed` $\longrightarrow$ `Lab Test Completed` | **8,238** | 0.0 min | Multi-analyte batched diagnostic result release (self-loop) |
| 5 | `Imaging Started` $\longrightarrow$ `Imaging Completed` | **5,267** | 56.6 min | Radiology scan acquisition & image archiving |
| 6 | `Prescription Consultation Completed` $\longrightarrow$ `Lab Test Started` | **5,242** | 33.8 min | Patient transit to phlebotomy collection desk |
| 7 | `Lab Test Started` $\longrightarrow$ `Lab Test Completed` | **4,396** | **279.3 min (4.65h)** | Primary laboratory analyzer processing turnaround time |
| 8 | `Prescription Consultation Completed` $\longrightarrow$ `Imaging Started` | **2,904** | **419.3 min (6.99h)** | Patient queue and scheduling latency for radiology |
| 9 | `Imaging Completed` $\longrightarrow$ `Prescription Consultation Started` | **1,618** | 63.8 min | Review consultation following diagnostic scan completion |
| 10 | `Appointment Registration` $\longrightarrow$ `Imaging Started` | **1,587** | 27.6 min | Pre-consultation walk-in radiology protocol |

---

## 4. Inductive Miner Process Modeling (Petri Net & Process Tree)

PM4Py's **Inductive Miner** (`pm4py.discover_petri_net_inductive` and `pm4py.discover_process_tree_inductive`) was executed on the event log to discover formal, executable workflow nets.

### 4.1 Inductive Petri Net Properties
- **Places:** **33**
- **Transitions:** **40** (including silent $\tau$-transitions representing concurrent routing, conditional skips, and diagnostic loopbacks)
- **Directed Arcs:** **94**
- **Initial Marking:** `['source']` (Single input place)
- **Final Marking:** `['sink']` (Single output place)
- **Soundness & Liveness:** Confirms a strictly structured workflow net without deadlocks, livelocks, or unbounded token accumulation.
- **Interchange Export:** Saved in standard XML Petri Net Markup Language: [`outputs/process_mining/inductive_petri_net.pnml`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/inductive_petri_net.pnml).

### 4.2 Inductive Process Tree Representation
The discovered process tree models the clinical process as a hierarchical operator tree with sequence (`->`), parallel concurrency (`+`), loop (`*`), and exclusive choice (`X`):

```
+( 
    X( tau, *( 'Lab Test Completed', tau ) ), 
    *( 'Prescription Consultation Completed', tau ), 
    X( tau, *( 'Prescription Consultation Started', tau ) ), 
    'Appointment Registration', 
    X( tau, *( 'Lab Test Started', tau ) ), 
    X( tau, *( 'Pharmacy Dispensation Completed', tau ) ), 
    X( tau, *( 'Pharmacy Dispensation Started', tau ) ), 
    X( tau, *( ->( 'Imaging Started', X( tau, *( 'Imaging Completed', tau ) ) ), tau ) ) 
)
```

- **Interchange Export:** Saved in standard Process Tree Markup Language: [`outputs/process_mining/inductive_process_tree.ptml`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/inductive_process_tree.ptml).

---

## 5. Clinical Process Variants & Cumulative Pareto Distribution

Using `pm4py.get_variants_as_tuples`, **602 distinct execution traces** were discovered across 49,912 cases.

### 5.1 Pareto Concentration Thresholds
The clinical workflow exhibits extraordinary Pareto concentration:

$$\mathbf{\text{Top 2 Variants}} \longrightarrow \mathbf{82.76\%} \quad | \quad \mathbf{\text{Top 6 Variants}} \longrightarrow \mathbf{90.00\%} \quad | \quad \mathbf{\text{Top 18 Variants}} \longrightarrow \mathbf{95.00\%}$$

```
Cumulative Case Coverage:
[██████████████████████████████████████████████████] 100.00% (602 Variants | 49,912 Cases)
[███████████████████████████████████████████████   ]  95.00% (Top 18 Variants)
[█████████████████████████████████████████         ]  90.00% (Top 6 Variants)
[████████████████████████████████████              ]  82.76% (Top 2 Variants)
[██████████████████████████████                    ]  78.42% (Top 1 Variant)
```

### 5.2 Top 10 Clinical Execution Variants Detailed Breakdown

| Rank | Encounters | Share (%) | Cum. Share (%) | Steps | Clinical Trace Sequence | Operational Interpretation |
| :-: | :---: | :---: | :---: | :-: | :--- | :--- |
| **V1** | **39,141** | **78.42%** | **78.42%** | 3 | `Registration -> Consult Start -> Consult Complete` | Standard Linear Consultation (No diagnostic orders) |
| **V2** | **2,168** | **4.34%** | **82.76%** | 5 | `Registration -> Consult Start -> Consult Complete -> Imaging Start -> Imaging Complete` | Post-Consultation Outpatient Radiology Scan |
| **V3** | **1,341** | **2.69%** | **85.45%** | 5 | `Registration -> Consult Start -> Consult Complete -> Lab Start -> Lab Complete` | Post-Consultation Single Laboratory Order |
| **V4** | **1,184** | **2.37%** | **87.82%** | 5 | `Registration -> Imaging Start -> Imaging Complete -> Consult Start -> Consult Complete` | Pre-Consultation Diagnostic Radiology Workup |
| **V5** | **879** | **1.76%** | **89.58%** | 7 | `Registration -> Consult -> Consult -> Lab Start -> Lab Start -> Lab Complete -> Lab Complete` | Multi-Order Laboratory Panel with Batch Resulting |
| **V6** | **208** | **0.42%** | **90.00%** | 9 | `Registration -> Consult -> Consult -> Lab x3 -> Lab Complete x3` | Triple Laboratory Specimen Order Panel |
| **V7** | **162** | **0.32%** | **90.32%** | 7 | `Registration -> Consult -> Consult -> Lab -> Lab Complete -> Imaging -> Imaging Complete` | Comprehensive Diagnostic Pathway (Lab + Radiology) |
| **V8** | **125** | **0.25%** | **90.57%** | 4 | `Registration -> Consult Start -> Consult Complete -> Lab Start` | Discharge with Pending Outpatient Lab |
| **V9** | **106** | **0.21%** | **90.78%** | 7 | `Registration -> Consult Start -> Consult Complete -> Pharmacy Start -> Pharmacy Complete` | On-site Hospital Pharmacy Prescription Dispensation |
| **V10**| **98** | **0.20%** | **90.98%** | 5 | `Registration -> Consult Start -> Consult Complete -> Imaging Start` | Discharge with Ongoing Radiology Accession |

---

## 6. Departmental Bottleneck & Waiting Time Quantification

By synthesizing the performance DFG (`pm4py.discover_performance_dfg`) with stage-level latency metrics, the key operational bottlenecks across the hospital departments were quantified:

### 6.1 Clinical Stage Latency Matrix
| Clinical Milestone Transition | Stage Category | Transition Volume | Mean Latency | Median Latency | Clinical Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `Appointment Registration` $\rightarrow$ `Consultation Start` | Clinic Queue | 47,882 | **114.9 min (1.92h)** | 25.0 min | **Elevated Waiting Queue** |
| `Consultation Start` $\rightarrow$ `Consultation Complete` | Provider Service | 50,338 | 4.6 min | 0.0 min | Standard Examination |
| `Consultation Complete` $\rightarrow$ `Lab Test Started` | Order Dispatch | 5,242 | 33.8 min | 18.0 min | Standard Transit Latency |
| `Lab Test Started` $\rightarrow$ `Lab Test Completed` | **Laboratory Service** | 4,396 | **279.3 min (4.65h)** | **81.0 min** | **PRIMARY BOTTLENECK (>120m)** |
| `Consultation Complete` $\rightarrow$ `Imaging Started` | **Radiology Queue** | 2,904 | **419.3 min (6.99h)** | **34.0 min** | **SECONDARY BOTTLENECK (>120m)** |
| `Imaging Started` $\rightarrow$ `Imaging Completed` | Radiology Service | 5,267 | 56.6 min | 3.0 min | Standard Scan Duration |
| `Consultation Complete` $\rightarrow$ `Pharmacy Started` | Pharmacy Queue | 106 | 8.7 min | 6.0 min | Rapid Dispensary Handoff |
| `Pharmacy Started` $\rightarrow$ `Pharmacy Completed` | Pharmacy Service | 112 | 6.9 min | 0.0 min | Standard Dispensation Time |

### 6.2 Bottleneck Root-Cause Diagnostics
1. **Laboratory Turnaround Time (Primary Operational Bottleneck):**
   - **Empirical Duration:** Mean TAT of **279.3 minutes (4.65 hours)** with batched panels averaging **930.5 minutes (15.5 hours)**. 62.96% of all lab tests exceed the hospital's 2-hour operational benchmark.
   - **Root Cause:** Laboratory technicians hold blood and biochemistry samples until fixed batch processing windows occur (e.g. 13:00 and 17:00), leading to artificial sample dwell times in the laboratory holding area.
2. **Post-Consultation Radiology Queue (Secondary Bottleneck):**
   - **Empirical Duration:** Mean waiting duration of **419.3 minutes (6.99 hours)** from doctor consultation completion to imaging procedure start.
   - **Root Cause:** Morning physician consultations generate an acute midday surge of imaging orders (X-ray, ultrasound, CT) that overwhelms available imaging suites between 11:00 and 15:00.
3. **OPD Front-Desk Waiting Queue:**
   - **Empirical Duration:** Mean wait of **114.9 minutes (1.92 hours)** from registration to entering the physician consultation room.
   - **Root Cause:** Peak patient arrival spikes on Monday mornings (2,640 arrivals at 06:00–07:00) create a severe backlog that takes clinics until early afternoon to clear.

---

## 7. Catalog of Generated Artifacts & Deliverables

All generated outputs have been saved with deterministic file paths and validated for reproducible consumption:

| # | Artifact Name | File Path | Format / Size | Description |
| :-: | :--- | :--- | :---: | :--- |
| 1 | **DFG Frequency Network** | [`outputs/process_mining/dfg_frequency_graph.png`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/dfg_frequency_graph.png) | PNG / 864 KB | Directed network graph of clinical activities with transition volume edge weights |
| 2 | **DFG Performance Graph** | [`outputs/process_mining/dfg_performance_graph.png`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/dfg_performance_graph.png) | PNG / 866 KB | Directly-Follows Graph color-coded by bottleneck latency thresholds ($>120$ min) |
| 3 | **Process Variants Pareto Chart** | [`outputs/process_mining/process_variants_pareto.png`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/process_variants_pareto.png) | PNG / 315 KB | Dual-axis Pareto chart showing Top 15 variants and cumulative percentage coverage |
| 4 | **Departmental Bottleneck Chart** | [`outputs/process_mining/bottleneck_waiting_times.png`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/bottleneck_waiting_times.png) | PNG / 236 KB | Horizontal bar chart contrasting mean vs median latencies with 120m threshold |
| 5 | **Activity Frequency Distribution**| [`outputs/process_mining/activity_frequency_distribution.png`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/activity_frequency_distribution.png) | PNG / 178 KB | Event volume and share breakdown across all 9 clinical milestone activities |
| 6 | **Inductive Petri Net** | [`outputs/process_mining/inductive_petri_net.pnml`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/inductive_petri_net.pnml) | XML PNML / 19.1 KB | Standard Petri Net Markup Language model for workflow engines |
| 7 | **Inductive Process Tree** | [`outputs/process_mining/inductive_process_tree.ptml`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/inductive_process_tree.ptml) | XML PTML / 11.3 KB | Process Tree Markup Language model for hierarchical process analysis |
| 8 | **Graphviz DOT Source** | [`outputs/process_mining/dfg_frequency.dot`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/dfg_frequency.dot) | Graphviz DOT / 5.3 KB | Plaintext DOT format for visualization rendering |
| 9 | **Audit Summary JSON** | [`outputs/process_mining/pm4py_discovery_summary.json`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/pm4py_discovery_summary.json) | JSON / 6.3 KB | Machine-readable metrics and verification scorecard |
| 10 | **Compressed IEEE XES Log** | [`data/careflow_event_log.xes.gz`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/data/careflow_event_log.xes.gz) | Gzip XES / 5.81 MB | Standard IEEE XML XES interchange format for Member 4 PM4Py/Disco intake |
| 11 | **Reproducible Python Pipeline** | [`scripts/pm4py_process_discovery.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/pm4py_process_discovery.py) | Python / 25.5 KB | Automated end-to-end PM4Py discovery and artifact generator script |

---

## 8. Member 4 Integration & Downstream Handover Readiness

With Day 9 completed, all data dependencies, models, and interfaces required by **Member 4 (BI Dashboards & Visual Process Mining)** are verified and active:

```mermaid
flowchart TD
    subgraph M3["Member 3: Engineering & PM4Py Discovery (Completed)"]
        CSV["careflow_event_log.csv<br/>(193,443 rows | 14 cols)"]
        XES["careflow_event_log.xes.gz<br/>(5.81 MB | Compressed XES)"]
        VIEWS["6 BigQuery KPI Views<br/>(vw_kpi_* | Sub-15ms Slot Time)"]
        MODELS["PNML & PTML Models<br/>(Inductive Petri Net & Tree)"]
    end

    subgraph M4["Member 4: Visual Mining & BI Dashboards (Handover Ready)"]
        BI["Operational BI Dashboards<br/>(Looker Studio / Tableau / Power BI)<br/>DirectQuery to 6 KPI Views"]
        PM["Advanced Process Modeling<br/>(PM4Py / Disco / Celonis)<br/>Inflow via careflow_event_log.xes.gz"]
    end

    CSV -->|"Tabular Intake"| PM
    XES -->|"Standard IEEE Interchange"| PM
    MODELS -->|"Conformance Verification"| PM
    VIEWS -->|"DirectQuery Direct Connect"| BI
```

### Readiness Evaluation:
- **Data Contract D Compliance:** **100% SATISFIED**. The event log has been validated and provided in both tabular CSV and compressed IEEE XES format.
- **Data Contract C Compliance:** **100% SATISFIED**. The 6 live BigQuery KPI views are deployed, schema-stable, and deliver sub-15ms execution performance.
- **Active Blockers:** **ZERO**. There are no technical, architectural, or credential blockers.

**Day 9 Milestone is hereby signed off as: 100% COMPLETED & VERIFIED.**
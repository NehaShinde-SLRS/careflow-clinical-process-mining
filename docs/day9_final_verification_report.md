# CareFlow Clinical Process Mining — Day 9 Final Verification Report

**Audit Date:** 5 November 2026  
**Auditor / Role:** Senior Process Mining Engineer / Member 3 (Data Engineering & Process Mining)  
**Milestone Deadline:** 8 November 2026 (Final Project Handover)  
**Target GCP Project:** `careflow-clinical-process-m`  
**Target BigQuery Dataset:** `careflow_opd` (Region: `US`)  
**Status:** **100% AUDITED, VERIFIED & SIGNED OFF**

---

## 1. Executive Deliverable Verification Scorecard

An exhaustive verification of all Day 9 PM4Py process discovery outputs was conducted across the filesystem, script codebase, and metadata logs. Every planned artifact is verified present, non-empty, and structurally valid.

| Deliverable | Target File Path | Size / Lines | Verification Check | Status |
| :--- | :--- | :---: | :--- | :---: |
| **Discovery Pipeline** | [`scripts/pm4py_process_discovery.py`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/scripts/pm4py_process_discovery.py) | 25.5 KB / 712 lines | Executes end-to-end without warnings or errors in 71.6s | **PASS** |
| **Discovery Documentation** | [`docs/day9_process_discovery.md`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/docs/day9_process_discovery.md) | 21.8 KB / 380 lines | Comprehensive documentation of discovery and bottlenecks | **PASS** |
| **Audit Metadata JSON** | [`outputs/process_mining/pm4py_discovery_summary.json`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/pm4py_discovery_summary.json) | 6.3 KB / 188 lines | Valid JSON syntax; machine-readable metrics | **PASS** |
| **Frequency DFG Chart** | [`outputs/process_mining/dfg_frequency_graph.png`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/dfg_frequency_graph.png) | 864 KB | 300 DPI high-resolution network graph (56 edges) | **PASS** |
| **Performance DFG Chart**| [`outputs/process_mining/dfg_performance_graph.png`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/dfg_performance_graph.png) | 866 KB | Color-coded bottleneck network graph with mean durations | **PASS** |
| **Variants Pareto Chart** | [`outputs/process_mining/process_variants_pareto.png`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/process_variants_pareto.png) | 315 KB | Dual-axis Top 15 variants bar + cumulative Pareto line | **PASS** |
| **Department Bottlenecks**| [`outputs/process_mining/bottleneck_waiting_times.png`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/bottleneck_waiting_times.png) | 236 KB | Horizontal bar chart of stage latencies vs 120m threshold | **PASS** |
| **Activity Frequencies** | [`outputs/process_mining/activity_frequency_distribution.png`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/activity_frequency_distribution.png) | 178 KB | Event volume and share breakdown across 9 activities | **PASS** |
| **Inductive Petri Net** | [`outputs/process_mining/inductive_petri_net.pnml`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/inductive_petri_net.pnml) | 19.1 KB | Standard XML PNML (33 places, 40 transitions, 94 arcs) | **PASS** |
| **Inductive Process Tree**| [`outputs/process_mining/inductive_process_tree.ptml`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/inductive_process_tree.ptml) | 11.3 KB | Standard XML PTML operator tree | **PASS** |
| **Graphviz DOT File** | [`outputs/process_mining/dfg_frequency.dot`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/outputs/process_mining/dfg_frequency.dot) | 5.3 KB | Plaintext DOT format for visualization rendering | **PASS** |
| **Compressed IEEE XES** | [`data/careflow_event_log.xes.gz`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/data/careflow_event_log.xes.gz) | 5.81 MB (6,088,119 B)| Valid Gzip-compressed XML XES (193,443 events, 49,912 cases)| **PASS** |

---

## 2. Event Log Data Integrity Verification

A strict read-only audit of the source event log ([`data/careflow_event_log.csv`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/data/careflow_event_log.csv)) confirmed zero modification or corruption:

- **File Modification Timestamp:** Maintained at `2024-10-24 22:35` (zero in-place overwrites).
- **File Size:** Exactly `34,658,350 bytes` (33.05 MB).
- **Row & Column Count:** Exactly **193,443 event records** across **14 columns**.
- **Case & Patient Population:** **49,912 unique outpatient cases** across **39,442 unique patients**.
- **Referential Completeness:** 0 null values across all 14 columns; 0 exact duplicate rows; 0 single-event cases.
- **Source Dataset Integrity:** [`data/HospitalOPD_cleaned.csv`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/data/HospitalOPD_cleaned.csv) verified intact at `11,216,919 bytes` (62,422 rows, 24 columns).

---

## 3. Empirical Consistency Cross-Verification

All process discovery metrics generated by PM4Py were cross-checked against the BigQuery warehouse marts (`careflow_opd.fct_clinical_encounters`, `careflow_opd.fct_process_transitions`) and previous Day 6 exploratory analysis:

| Analytical Dimension | BigQuery Marts / Day 6 Baseline | Day 9 PM4Py Discovery Result | Variance / Discrepancy |
| :--- | :---: | :---: | :---: |
| **Total Outpatient Cases** | 49,912 cases | **49,912 cases** | **0 (100.00% match)** |
| **Total Recorded Events** | 193,443 events | **193,443 events** | **0 (100.00% match)** |
| **Unique Process Variants** | 602 variants | **602 variants** | **0 (100.00% match)** |
| **Variant 1 Frequency** | 39,141 cases (78.42%) | **39,141 cases (78.42%)** | **0 (100.00% match)** |
| **Top 2 Variants Coverage** | 82.76% of encounters | **82.76% of encounters** | **0 (100.00% match)** |
| **Top 6 Variants Coverage** | 90.00% of encounters | **90.00% of encounters** | **0 (100.00% match)** |
| **Top 18 Variants Coverage**| 95.00% of encounters | **95.00% of encounters** | **0 (100.00% match)** |
| **Primary Lab TAT Bottleneck**| Mean 279.3 min (4.65 hours) | **Mean 279.3 min (4.65 hours)** | **0 (100.00% match)** |
| **Registration Waiting Time**| Mean 114.9 min (1.92 hours) | **Mean 114.9 min (1.92 hours)** | **0 (100.00% match)** |

---

## 4. Final Sign-off & Member 4 Handover Certification

1. **All Day 9 tasks are 100% completed and empirically verified.**
2. **There are zero pending items, unresolved bugs, or data gaps from Day 9.**
3. **Data Contract D** (IEEE XES event log interchange) and **Data Contract C** (6 BigQuery KPI views) are fully operational and ready for downstream BI dashboard connection and visual process mining tool intake by **Member 4**.

**Day 9 is officially certified: COMPLETE & CLOSED.**

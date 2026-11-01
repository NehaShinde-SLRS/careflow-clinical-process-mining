# CareFlow – PM4Py Process Discovery

## 1. Project Overview

CareFlow is a hospital process-mining and operational analytics project. The objective is to understand patient activity sequences, identify possible process bottlenecks, and support operational improvements.

This stage focuses on discovering activity flows using PM4Py, a Python process-mining library.

**Dataset:** Hospital outpatient activity data.

**Note:** The current dataset represents outpatient activity, not a verified Emergency Room workflow.

## 2. Objectives

- Install and import PM4Py.
- Load the original hospital outpatient dataset.
- Prepare a standardized event log.
- Map Case ID, Activity Name, and Timestamp.
- Discover a Directly-Follows Graph (DFG).
- Generate a process map showing activity transition frequencies.
- Compare the PM4Py process map with the earlier Sankey diagram.

## 3. Tools and Technologies

- Python
- Pandas
- PM4Py
- Matplotlib
- Jupyter Notebook

## 4. Input Dataset

Original dataset:

`HospitalOPD-noname.csv`

The dataset will be cleaned and transformed into a normalized event log containing:

- `Case_ID`
- `Activity_Name`
- `Timestamp`

Normalized event log output:

`careflow_normalized_event_log.csv`

The normalized event log should be kept locally if it contains patient-level or sensitive records.

## 5. Process Discovery Method

PM4Py will be used to discover a Directly-Follows Graph (DFG).

A DFG represents the relationships between consecutive activities in a case.

For example:

Appointment → Prescription → Lab → Pharmacy

The process map will display activity transitions and their frequencies based on the event log.

## 6. Expected Output Files

1. `pm4py_process_discovery.ipynb`
2. `careflow_pm4py_process_map.png`
3. `careflow_process_discovery_summary.csv`

## 7. Analysis and Interpretation

The process map will help identify:

- Frequently occurring activity transitions.
- Different activity sequences across cases.
- Common starting and ending activities.
- Possible repeated activity patterns.

The findings will describe observed outpatient activity patterns. A process map alone does not establish why a delay occurs.

## 8. Project Limitations

- The dataset represents outpatient activity rather than verified Emergency Room activity.
- Activity timestamps show recorded event timing but do not prove the cause of delays.
- Patient-level data should not be uploaded to a public GitHub repository without appropriate permission.
- Process discovery results depend on the quality and completeness of the event log.

## 9. Next Steps

The next stage is bottleneck and waiting-time analysis.

Transition times will be calculated between consecutive activities, and average and median transition durations will be examined to identify potentially slower parts of the outpatient process.

---

**Project:** CareFlow – Clinical Pathway Process Mining  
**Development Stage:** PM4Py Process Discovery

# CareFlow : Process Performance and Bottleneck Analysisupload

## 1. Objective

The objective of is to analyze outpatient workflow performance by calculating time gaps between consecutive recorded activities and identifying activity transitions that may require further investigation.

## 2. Input Dataset

**Input file:** `careflow_normalized_event_log.csv`

Dataset overview:

- Total events: 148,686
- Total cases: 49,912
- Activity types: 5
- Activities: Appointment, Prescription, Lab, Imaging, Pharmacy

## 3. Process Performance Analysis

### 3.1 Methodology

The following steps were performed:

1. Loaded the normalized outpatient event log.
2. Sorted events by Case ID and Timestamp.
3. Identified the next activity for each case.
4. Calculated the time difference between consecutive activities in minutes.
5. Grouped transitions by source and next activity.
6. Calculated transition counts, average, median, minimum, and maximum time gaps.
7. Identified unusually long timestamp gaps exceeding 24 hours.
8. Created a filtered summary excluding gaps greater than 24 hours.
9. Generated a horizontal bar chart showing average transition times.

### 3.2 Analysis Results

| Metric                               |  Result |
| ------------------------------------ | ------: |
| Total events                         | 148,686 |
| Total cases                          |  49,912 |
| Total transitions                    |  98,774 |
| Gaps greater than 24 hours           |     589 |
| Transitions retained after filtering |  98,185 |
| Transition types                     |      21 |

### 3.3 Important Transition Findings

The following transitions had relatively high average timestamp gaps after filtering:

| Activity Transition        | Count | Average Gap (Minutes) |
| -------------------------- | ----: | --------------------: |
| Prescription → Appointment |     3 |                667.00 |
| Lab → Appointment          |   125 |                192.80 |
| Lab → Prescription         |   369 |                107.00 |
| Lab → Imaging              |   409 |                106.12 |
| Appointment → Imaging      | 1,599 |                 70.61 |
| Appointment → Lab          |   354 |                 59.14 |
| Imaging → Appointment      |   288 |                 55.14 |
| Prescription → Imaging     | 2,850 |                 53.85 |

Prescription → Appointment has only three observations, so its average should be interpreted cautiously.

## 4. Bottleneck Candidate Analysis

### 4.1 Objective

Identify outpatient activity transitions with relatively high average timestamp gaps and sufficient observations for further investigation.

### 4.2 Methodology

1. Loaded the filtered process performance summary.
2. Selected transitions with at least 100 observations.
3. Sorted selected transitions by average timestamp gap in descending order.
4. Identified transitions with relatively high average gaps.
5. Generated a bottleneck candidate CSV file.
6. Created a horizontal bar chart to compare candidate transitions.

### 4.3 Bottleneck Candidate Results

A total of 17 transition types met the minimum observation threshold of 100.

| Activity Transition        | Transition Count | Average Gap (Minutes) | Median Gap (Minutes) |
| -------------------------- | ---------------: | --------------------: | -------------------: |
| Lab → Appointment          |              125 |                192.80 |               158.00 |
| Lab → Prescription         |              369 |                107.00 |                33.00 |
| Lab → Imaging              |              409 |                106.12 |                52.00 |
| Appointment → Imaging      |            1,599 |                 70.61 |                46.00 |
| Appointment → Lab          |              354 |                 59.14 |                29.50 |
| Imaging → Appointment      |              288 |                 55.14 |                18.00 |
| Prescription → Imaging     |            2,850 |                 53.85 |                34.00 |
| Imaging → Lab              |              614 |                 44.89 |                29.00 |
| Appointment → Prescription |           47,630 |                 43.20 |                25.00 |

### 4.4 Key Observations

**Lab-related transitions**

Lab → Appointment has the highest average gap among transitions meeting the 100-observation threshold, at 192.80 minutes.

Lab → Prescription and Lab → Imaging also show relatively high average gaps. These transitions may deserve further investigation.

**High-volume transitions**

Appointment → Prescription has the highest transition count, with 47,630 observations and an average gap of 43.20 minutes.

Because of its high volume, this transition is also important to examine.

## 5. Output Files

The following files were generated during :

1. `process_performance_analysis.ipynb`
2. `careflow_transition_waiting_time_summary.csv`
3. `careflow_process_performance_summary.csv`
4. `careflow_transition_waiting_time_chart.png`
5. `careflow_bottleneck_candidates.csv`
6. `careflow_bottleneck_analysis_chart.png`

## 6. Data Quality and Limitations

- The source dataset represents outpatient activity records, not a verified emergency-room event log.
- Some timestamps are separated by unusually long periods.
- Calculated values represent gaps between recorded activity timestamps, not confirmed patient waiting times.
- A timestamp gap alone cannot prove an operational bottleneck.
- The 24-hour exclusion and minimum count of 100 are analytical choices, not clinical standards.
- Filtering long gaps changes average timestamp-gap estimates.
- The dataset does not establish why a gap occurred.
- Further validation with hospital workflow information is required before recommending operational changes.

Patient-level event data and files containing case IDs must remain private and should not be uploaded to a public repository.

## 7. Conclusion

successfully completed the outpatient process performance and bottleneck candidate analysis.

The analysis generated transition summaries, identified unusually long timestamp gaps, and produced visualizations of average transition times and bottleneck candidates.

Lab-related transitions showed relatively high average timestamp gaps, while Appointment → Prescription had the largest transition volume.

These findings provide a starting point for further investigation of outpatient workflow patterns. They should not be treated as confirmed causes of patient delays or as proof of actual patient waiting times.

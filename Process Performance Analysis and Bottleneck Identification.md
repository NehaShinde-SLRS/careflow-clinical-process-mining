### CareFlow - Process Performance Analysis and Bottleneck Identification

### Overview

 focuses on analyzing outpatient process performance using the normalized event log. The analysis examines activity transitions, time gaps, appointment-level process durations, and activity frequencies to identify potential workflow bottlenecks.

### Objectives

* Analyze time gaps between consecutive activities.

* Measure recorded process duration for each appointment.

* Identify activity transitions with higher average time gaps.

* Analyze activity frequencies and transition patterns.

* Identify potential bottlenecks for further investigation.

* Prepare aggregate reports and visualizations.

### Work Completed

* Reviewed the normalized outpatient event log.

* Analyzed time differences between consecutive activities.

* Prepared transition performance summaries.

* Calculated appointment-level process durations.

* Analyzed activity frequencies.

* Identified potential bottleneck transitions based on observed time gaps.

* Prepared visualizations for transition gaps and process duration.

* Exported aggregate performance reports.

### Technologies Used

* Python

* Pandas

* NumPy

* Matplotlib

* Jupyter Notebook

### Input Dataset

`careflow_normalized_event_log.csv`

This file contains the normalized outpatient activity records prepared during Day 11.

### Expected Deliverables

| File name                                  | Description                                |
| ------------------------------------------ | ------------------------------------------ |
|    process_performance_analysis.ipynb      | Notebook containing performance analysis   |
| careflow_transition_performance.csv        | Summary of activity transition time gaps   |
| careflow_case_performance.csv              | Appointment-level process duration summary |
| careflow_activity_frequency.csv            | Activity frequency summary                 |
| careflow_transition_waiting_time.png       | Visualization of average transition gaps   |
| careflow_process_duration_distribution.png | Distribution of recorded process durations |

### Key Analysis Areas

* Transition Analysis: Understand time gaps between consecutive activities.

* Process Duration: Measure the time between the first and last recorded activity for each appointment.

* Activity Frequency: Identify the most frequently recorded activities.

* Potential Bottlenecks: Highlight transitions with higher average time gaps for further investigation.

* Visualization: Present process performance patterns through charts.

### Important Data Interpretation Note

The analysis uses recorded activity start timestamps. Time gaps are potential waiting-time indicators and do not directly measure actual activity duration or establish the causes of delays.

The dataset represents outpatient workflows, not emergency-room workflows. Findings from the actual outpatient dataset must remain separate from the synthetic BigQuery demonstration results.

### Privacy and Data Handling

Patient-level information must not be uploaded to the public GitHub repository.

Only upload notebooks, aggregate reports, and visualizations after checking that they contain no patient names, patient IDs, appointment IDs, or other identifiable information.

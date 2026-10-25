# CareFlow: Clinical Pathway Process Mining

## Project Overview

CareFlow is a data analytics project focused on exploring hospital outpatient department (OPD) activity records. The project examines repeated activities, timestamp quality, activity durations, and patient activity sequences to identify patterns and potential data quality issues.

## Repeated Activity Analysis

### Objective

Identify appointments with repeated recorded hospital activities.

### Key Findings

- Total unique appointments: 49,912.
- Total events in the event log: 136,176.
- Appointments with at least one repeated activity: 4,821.
- Prescription Started had repeated activities in 4,821 appointments.
- Lab Started had repeated activities in 4,132 appointments.
- Imaging Started had repeated activities in 187 appointments.
- Pharmacy Started had repeated activities in 82 appointments.

### Interpretation

Prescription and laboratory activities showed the largest numbers of repeated activities. Repetition may reflect multiple legitimate orders or potential data quality issues. Further investigation is needed before classifying repeated activities as errors.

### Output

- `careflow_repeated_activity_summary.xls`

## Timestamp Validation

### Objective

Validate activity timestamps and identify records where service start times occur before appointment start times.

### Interpretation

Timestamp validation helps identify records that may require further review. Unusual timestamp ordering does not automatically mean a record is incorrect. The findings should be interpreted in the context of the original data collection process.

### Output

- `careflow_timestamp_validation_summary.xls`

## Hospital Activity Duration Analysis

### Objective

Measure recorded durations for prescription, laboratory, imaging, and pharmacy activities using available start and end timestamps.

### Key Findings

- **Prescription:** 62,409 records had both timestamps; 52 had negative durations and 41,514 had zero-minute durations.
- **Laboratory:** 13,327 records had both timestamps; 732 exceeded 24 hours.
- **Imaging:** 5,513 records had both timestamps; 561 had zero-minute durations.
- **Pharmacy:** 302 records had both timestamps; 143 had zero-minute durations.
- The average recorded laboratory duration was 468.74 minutes, while the median was 125 minutes.
- The average recorded imaging duration was 96.68 minutes, while the median was 3 minutes.

### Interpretation

The differences between average and median durations suggest skewed duration distributions, particularly for laboratory and imaging activities. Zero-minute durations, negative durations, and unusually long durations should be investigated before drawing conclusions about clinical efficiency.

The average may be affected by a small number of unusually long recorded durations. The median provides additional context about the typical recorded duration.

### Outputs

- `careflow_activity_duration_summary.xls`
- `careflow_duration_quality_summary.xls`

## Overall Limitations

- Recorded timestamp differences may not represent actual patient waiting times or the full duration of clinical services.
- Zero-minute durations may reflect the recording process, timestamp precision, or other data issues.
- Negative durations require validation against the original records.
- Long durations are screening flags, not proof of errors.
- The analysis identifies patterns but does not establish the causes of unusual records or prove improvements in clinical efficiency.

## Data Privacy

Raw and cleaned patient-level datasets should not be uploaded to this public repository. Notebooks and summary files should be checked to ensure they do not expose patient identifiers, doctor names, appointment-level details, or other sensitive information.

## Project Outputs

The repository contains analysis notebooks, project documentation, and summary files produced during the project. These outputs support the exploration of hospital activity patterns and data quality.

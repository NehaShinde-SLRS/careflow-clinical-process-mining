# CareFlow — Dataset Understanding

## 1. Project Overview

CareFlow is a Clinical Pathway Process Mining project that analyzes healthcare event data to understand patient appointment pathways and related clinical activities.

## 2. Dataset Summary

The HospitalOPD dataset was inspected using Python, pandas, and Google Colab.

- Total records: 62,422
- Original columns: 25
- Unique patients: 39,442
- Unique appointments: 49,912
- Patients with multiple appointments: 7,120
- Appointments linked to multiple patients: 0

## 3. Important Columns

| Column | Description |
|---|---|
| patient_id | Identifies a patient |
| appointment_id | Identifies an appointment |
| appointment_start_datetime | Records the appointment start time |
| prescription_start_datetime | Records the prescription start time |
| lab_start_datetime | Records the laboratory activity start time |
| imaging_start_datetime | Records the imaging activity start time |
| pharmacy_start_datetime | Records the pharmacy activity start time |
| flow_name | Identifies the workflow type |

## 4. Initial Data Quality Findings

- The `Unnamed: 2` column is completely empty.
- No exact duplicate rows were identified.
- No duplicate record numbers were identified.
- Twelve records have missing prescription start timestamps.
- Many records have missing lab, imaging, and pharmacy timestamps.
- Some lab and imaging identifiers are associated with multiple appointments.

Repeated appointment IDs do not automatically mean that records are duplicates. Missing timestamps and event associations require validation during data cleaning.

## 5. Event Log Preparation

The dataset needs to be transformed into an event log for process mining. The proposed event log fields are:

- Case_ID
- Patient_ID
- Activity
- Timestamp
- Event_ID

The final Case_ID rule, activity labels, and event mappings must be validated with the team before creating the final event log.

## 6. Next Steps

- Validate the associations between appointments and clinical activities.
- Investigate missing timestamps.
- Confirm event-log mapping and case identification rules with the team.
- Prepare and validate the event log for process-mining analysis.

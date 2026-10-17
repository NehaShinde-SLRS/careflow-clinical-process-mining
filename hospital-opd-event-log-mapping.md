# HospitalOPD Event Log Mapping

## 1. Project Overview

CareFlow is a Clinical Pathway Process Mining project. The HospitalOPD dataset contains information about patient appointments and related healthcare activities, including prescriptions, laboratory tests, imaging, and pharmacy transactions.

The purpose of event log mapping is to convert the dataset into a structured format suitable for process mining.

## 2. Dataset Summary

- Dataset: HospitalOPD
- Original records: 62,422
- Original columns: 25
- Unique patients: 39,442
- Unique appointments: 49,912

These values are from the initial dataset analysis.

## 3. Event Log Structure

The process-mining event log should contain the following fields:

| Field | Purpose |
|---|---|
| Case_ID | Identifies the process instance being analyzed |
| Activity | Describes the healthcare activity performed |
| Timestamp | Records when the activity occurred |
| Event_ID | Helps identify the source event, where available |

## 4. Activities and Timestamp Columns

| Activity | Candidate timestamp column |
|---|---|
| Appointment | appointment_start_datetime |
| Prescription | prescription_start_datetime |
| Lab | lab_start_datetime |
| Imaging | imaging_start_datetime |
| Pharmacy | pharmacy_start_datetime |

These are candidate mappings and must be validated during data preparation.

## 5. Case ID Selection

The dataset contains both patient IDs and appointment IDs. A patient may have multiple appointments, so patient ID and appointment ID represent different concepts.

The final Case_ID rule must be confirmed with the team before generating the final event log. The selected rule should keep events associated with the correct appointment or clinical pathway.

## 6. Data Quality Considerations

Initial analysis identified the following issues:

- Some prescription records have missing start timestamps.
- Many rows do not contain lab, imaging, or pharmacy timestamps because those activities may not apply to every record.
- Some lab and imaging identifiers are associated with multiple appointments.
- Repeated records and event identifiers require validation before deduplication.

Missing timestamps must not be invented. Records should be handled according to agreed data-cleaning rules.

## 7. Next Steps

1. Confirm the case ID and event ID rules with the team.
2. Validate timestamps and repeated records.
3. Create and

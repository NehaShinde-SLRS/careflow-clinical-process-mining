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

| Field | Purpose |
|---|---|
| Case_ID | Identifies the process instance being analyzed |
| Activity | Describes the healthcare activity performed |
| Timestamp | Records when the activity occurred |
| Event_ID | Helps identify the source event, where available |

## 4. Activities and Timestamp Columns

| Activity | Candidate timestamp column |
|---|---|
| Appointment | `appointment_start_datetime` |
| Prescription | `prescription_start_datetime` |
| Lab | `lab_start_datetime` |
| Imaging | `imaging_start_datetime` |
| Pharmacy | `pharmacy_start_datetime` |

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
3. Construct a candidate event log using the validated activity and timestamp mappings.
4. Validate the candidate event log before using it for process mining.

## 8. Case Identifier Assessment — 24 October 2026

### 8.1 Objective

Identify a suitable case identifier for constructing the HospitalOPD event log.

### 8.2 Candidate Case Identifier

The `appointment_id` field is a candidate for the case identifier because the dataset contains 49,912 unique appointments and 39,442 unique patients.

### 8.3 Reasons for Considering Appointment ID

- One patient may have multiple appointments.
- The dataset assessment found no appointments linked to multiple patients.
- An appointment-level case identifier can help organize clinical activities associated with each appointment.

### 8.4 Validation Required

Before finalizing the case identifier:

1. Confirm that each clinical activity can be linked to the correct appointment.
2. Check for missing appointment identifiers in activity records.
3. Verify that events belonging to the same appointment can be ordered using their timestamps.
4. Investigate missing or inconsistent timestamps.
5. Confirm the case identifier with the project team.

### 8.5 Current Status

The appointment ID is a proposed case identifier, not yet a finalized decision. It will be confirmed after validating the relationships between appointments and clinical activities.

### 8.6 Expected Outcome

A documented candidate case identifier to guide the construction and validation of the CareFlow process-mining event log.

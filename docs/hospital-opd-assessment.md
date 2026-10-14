# HospitalOPD Dataset Assessment

## 1. Project Overview

CareFlow is a Clinical Pathway Process Mining project that analyzes healthcare workflows to understand patient treatment pathways.

## 2. Dataset Overview

The HospitalOPD dataset was inspected using Python and pandas in Google Colab.

- Total source rows: 62,422
- Total source columns: 25
- Unique patient IDs: 39,442
- Unique appointment IDs: 49,912
- Workflow types: 6

## 3. Important Columns

The dataset includes identifiers and timestamps for appointments, prescriptions, laboratory tests, imaging, and pharmacy events.

Key columns include:
- `patient_id`
- `appointment_id`
- `appointment_start_datetime`
- `prescription_order_id`
- `prescription_start_datetime`
- `lab_id`
- `lab_start_datetime`
- `imaging_request_id`
- `imaging_start_datetime`
- `pharmacy_sale_line_id`
- `pharmacy_start_datetime`
- `flow_name`

## 4. Initial Data Quality Findings

- The `Unnamed: 2` column was found to be completely empty.
- No duplicate `record_no` values were found in the initial check.
- Some laboratory and imaging identifiers are linked to multiple appointments belonging to the same patient.
- Some recorded events occur before their appointment timestamps.

These observations require further investigation before the event log is finalized.

## 5. Event Log Prototype

An initial event log was created for review.

- Event records: 123,957
- Unique appointment cases: 49,912
- Unique activities: 306

The prototype contains `Case_ID`, `Patient_ID`, `Activity`, `Timestamp`, and `Event_ID`.

## 6. Next Steps

- Validate event-to-appointment relationships.
- Investigate repeated laboratory and imaging events.
- Verify timestamp ordering and activity names.
- Finalize the event log after validation.
- Prepare the data for process-mining analysis.

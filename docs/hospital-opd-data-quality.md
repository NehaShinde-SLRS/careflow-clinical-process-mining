# HospitalOPD Data Quality Assessment

## 1. Dataset Overview

Our team has selected the HospitalOPD dataset for the CareFlow Clinical Pathway Process Mining project. I explored the dataset using Python and pandas in Google Colab.

- Total records: 62,422
- Total columns: 25
- Unique patients: 39,442
- Unique appointments: 49,912
- Workflow types: 6

## 2. Initial Data Quality Findings

- The `Unnamed: 2` column was completely empty.
- No duplicate `record_no` values were found during the initial check.
- Some laboratory event IDs are associated with multiple appointments for the same patient.
- Some imaging request IDs are associated with multiple appointments for the same patient.
- Some events occur before their appointment timestamps.

## 3. Process Mining Preparation

The dataset contains appointment, prescription, laboratory, imaging, and pharmacy information. An initial event-log prototype was created with Case_ID, Patient_ID, Activity, Timestamp, and Event_ID.

The prototype still requires validation before it can be used for final process-mining analysis.

## 4. Next Steps

- Verify how events are linked to appointments.
- Investigate repeated laboratory and imaging events.
- Review timestamps and activity names.
- Coordinate with the Python and Data Cleaning member.
- Prepare the validated event log for process mining.

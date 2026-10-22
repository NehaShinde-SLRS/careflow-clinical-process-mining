# HospitalOPD Dataset Quality Findings

## 1. Dataset Overview

- Total records: 62,422
- Unique patients: 39,442
- Unique appointments: 49,912
- Patients with multiple appointments: 7,120
- Appointments linked to multiple patients: 0

## 2. Timestamp Quality

| Activity | Valid timestamps | Missing or invalid |
|---|---:|---:|
| Appointment | 62,422 | 0 |
| Prescription | 62,410 | 12 |
| Lab | 18,029 | 44,393 |
| Imaging | 5,523 | 56,899 |
| Pharmacy | 302 | 62,120 |

## 3. Event ID Quality

| Activity | Available IDs | Unique IDs | Missing IDs |
|---|---:|---:|---:|
| Prescription | 62,422 | 50,568 | 0 |
| Lab | 18,029 | 17,083 | 44,393 |
| Imaging | 5,523 | 5,360 | 56,899 |
| Pharmacy | 302 | 262 | 62,120 |

## 4. Duplicate Record Check

- Exact duplicate rows: 0
- Duplicate record numbers: 0
- Duplicate appointment IDs: 12,510

Repeated appointment IDs do not automatically indicate duplicate events. They should be interpreted in the context of the dataset structure.

## 5. Initial Next Steps

1. Investigate the 12 missing prescription timestamps.
2. Validate links between appointments and clinical activities.
3. Confirm the event-log mapping before process mining.
4. Prepare a reliable event log for the project team.

---

## 6. Additional Data Quality Checks — 20 October 2026

### 6.1 Identifier Validation

- Total records: 62,422
- Unique patients: 39,442
- Unique appointments: 49,912
- Missing patient IDs: 0
- Missing appointment IDs: 0
- Appointments linked to multiple patients: 0
- Exact duplicate rows: 0
- Duplicate record numbers: 0

### 6.2 Workflow Type Validation

The dataset contains seven workflow types:

| Workflow type | Record count |
|---|---:|
| Appointment → Prescription | 40,164 |
| Appointment → Prescription → Lab | 16,434 |
| Appointment → Prescription → Imaging | 3,947 |
| Appointment → Prescription → Lab + Imaging | 1,575 |
| Appointment → Prescription → Pharmacy | 281 |
| Appointment → Prescription → Lab + Pharmacy | 20 |
| Appointment → Prescription → Imaging + Pharmacy | 1 |
| **Total** | **62,422** |

### 6.3 Lab Timestamp Validation

- Records containing lab start timestamps: 18,029
- Records with parseable lab start and end timestamps: 13,327
- End-before-start cases among those 13,327 records: 0
- Non-empty lab end values that could not be parsed using the current timestamp format: 4,702

The unusual lab end values require further investigation before their meaning can be confirmed.

### 6.4 Prescription Timestamp Validation

- Records with parseable prescription start and end timestamps: 62,409
- Records where the prescription end timestamp is earlier than the start timestamp: 52
- Unique prescription IDs involved in these records: 49
- Cause of the timestamp inconsistencies: Not yet confirmed

These records should be reviewed without automatically changing or deleting the original data.

### 6.5 Updated Next Steps

1. Investigate missing prescription timestamps and review prescription start/end inconsistencies.
2. Investigate unusual lab end timestamp formats.
3. Validate relationships between appointments and clinical activities.
4. Confirm the case identifier and event-log mapping before process mining.
5. Prepare and validate a reliable event log for the project team.
6. Preserve the original dataset for reference.
   ## 7. Cleaned Dataset Validation 

### Objective
Validate the cleaned HospitalOPD dataset received from Member 2 before using it for CareFlow process mining.

### Validation Activities
1. Received the cleaned dataset from the team member responsible for data cleaning.
2. Plan to compare the row and column counts with the original dataset.
3. Check missing patient and appointment identifiers.
4. Verify timestamp formats for appointment, prescription, lab, imaging, and pharmacy activities.
5. Review prescription start and end timestamp inconsistencies.
6. Investigate unusual lab end timestamp values.
7. Check for duplicate records and verify appointment-to-activity relationships.
8. Document any remaining data quality issues.

### Current Status
The cleaned dataset has been received from Member 2. Detailed validation results will be documented after comparing the cleaned dataset with the original HospitalOPD dataset.

### Expected Outcome
A validated dataset suitable for preparing the event log for the next stage of CareFlow process mining.
## 7. Cleaned Dataset Validation 

### 7.1 Dataset Structure

The cleaned HospitalOPD dataset was received from the team member responsible for data cleaning.

- Total records: 62,422
- Total columns: 24
- Unique patients: 39,442
- Unique appointments: 49,912
- Missing patient IDs: 0
- Missing appointment IDs: 0
- Exact duplicate rows: 0
- Duplicate record numbers: 0

The cleaned dataset contains one fewer column than the original dataset because the entirely empty `Unnamed: 2` column is no longer present.

### 7.2 Timestamp Validation

- Appointment start timestamps: 62,422 valid values
- Prescription start timestamps: 62,410 valid values; 12 missing
- Prescription end timestamps: 62,421 valid values; 1 missing
- Lab start timestamps: 18,029 valid values
- Lab end timestamps: 13,327 valid values
- Imaging start timestamps: 5,523 valid values
- Imaging end timestamps: 5,513 valid values
- Pharmacy start and end timestamps: 302 valid values each

The timestamp values listed above could be parsed using the current timestamp format.

### 7.3 Prescription Timestamp Inconsistencies

A comparison of prescription start and end timestamps identified 52 records where the end timestamp occurs before the start timestamp. These records require further investigation before the dataset is used for process mining.

### 7.4 Activity Timestamp Checks

No end-before-start inconsistencies were found among records with parseable lab, imaging, or pharmacy start and end timestamps.

### 7.5 Remaining Validation Tasks

1. Investigate missing prescription timestamps.
2. Review prescription records with inconsistent start and end times.
3. Confirm how unusual lab end values were handled during cleaning.
4. Validate relationships between appointments and clinical activities.
5. Confirm the case identifier and event-log mapping with the project team.

### Conclusion

The cleaned dataset retains 62,422 records and contains 24 columns. Initial checks found no missing patient or appointment identifiers and no exact duplicate rows. Additional timestamp and activity-link validation is required before constructing the final process-mining event log.

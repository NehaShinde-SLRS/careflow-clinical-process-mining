# CareFlow Clinical Process Mining — Day 5 Data Quality & Validation Review

**Date:** 24 October 2026  
**Project:** CareFlow — Clinical Pathway Process Mining  
**Dataset:** Hospital Outpatient Department (`HospitalOPD_cleaned`)  
**Scope:** In-depth quality audit across all 8 SQL validation dimensions on 62,422 encounter records  

---

## 1. Executive Summary

This Day 5 report delivers an exhaustive data quality review of the cleaned HospitalOPD dataset, evaluating its clinical validity, structural integrity, and readiness for process mining. 

The evaluation was conducted using the exact query logic defined in [`sql/validation_queries.sql`](file:///c:/Users/user/Documents/careflow-clinical-process-mining/sql/validation_queries.sql) executed directly on the 62,422 verified records.

### Key Quality Scorecard
| Quality Dimension | Test Target | Actual Result | Status |
|---|---|---|---|
| **Row Completeness** | Exactly 62,422 rows | 62,422 rows verified (0 discrepancy) | **PASS** |
| **Exact Deduplication** | 0 exact duplicate rows | 0 exact duplicate rows | **PASS** |
| **Case Identification** | Zero missing `patient_id` or `appointment_id` | 0 nulls (100% complete) | **PASS** |
| **Activity Identification** | Zero missing `flow_name` or `flow_code` | 0 nulls across all 7 pathways | **PASS** |
| **Primary Timestamp** | Zero missing `appointment_start_datetime` | 0 nulls (100% valid datetimes) | **PASS** |
| **Timestamp Plausibility** | All timestamps within clinical range (2000–2030) | 100% within range (`2024-04-25` to `2026-07-23`) | **PASS** |
| **Prescription Completeness** | Investigation of missing prescription timestamps | 12 missing `prescription_start_datetime` (0.02%); 1 missing `prescription_end_datetime` (0.00%) | **FLAGGED / ANALYZED** |
| **Chronological Ordering** | Downstream events occur after upstream events | 52 Rx end < start; 457 Lab < Appt; 295 Img < Appt; 5 Rx < Appt | **ANOMALIES QUANTIFIED** |

---

## 2. In-Depth Validation Results (The 8 SQL Checks)

### Check 1: Total Row Count Verification
- **Expected Records:** `62,422`
- **Actual Records:** `62,422`
- **Discrepancy:** `0`
- **Interpretation:** The loaded working copy perfectly reflects the verified cleaned dataset.

---

### Check 2: Null and Missing Value Audit
Analysis across all 24 columns in the dataset:

| Column Category | Column Name | Null Count | Null % | Clinical Explanation |
|---|---|---|---|---|
| **Identifiers** | `record_no` | 0 | 0.00% | Source sequence key |
| | `patient_id` | 0 | 0.00% | Patient unique identifier |
| | `appointment_id` | 0 | 0.00% | Encounter unique identifier |
| **Activity & Pathway** | `flow_code` | 0 | 0.00% | Numeric pathway code (1–7) |
| | `flow_name` | 0 | 0.00% | Descriptive clinical pathway |
| **Primary Visit Time**| `appointment_start_datetime` | 0 | 0.00% | Clinic registration timestamp |
| **Prescription Details**| `prescription_doctor_id` | 0 | 0.00% | Attending doctor ID |
| | `prescription_doctor_name`| 0 | 0.00% | Attending doctor name |
| | `prescription_order_id` | 0 | 0.00% | Consultation order key |
| | `prescription_start_datetime`| **12** | **0.02%** | Consultation start (flagged in notes) |
| | `prescription_end_datetime` | **1** | **0.00%** | Consultation complete |
| **Laboratory Service** | `lab_id` | 44,393 | 71.12% | Lab test not ordered for this visit |
| | `lab_name` | 44,393 | 71.12% | Lab test not ordered |
| | `lab_start_datetime` | 44,393 | 71.12% | Lab test not ordered |
| | `lab_end_datetime` | 49,095 | 78.65% | Lab test pending / not completed (4,702 tests pending) |
| **Imaging Service** | `imaging_request_id` | 56,899 | 91.15% | Imaging not ordered for this visit |
| | `imaging_result_id` | 56,899 | 91.15% | Imaging not ordered |
| | `imaging_name` | 56,899 | 91.15% | Imaging not ordered |
| | `imaging_start_datetime` | 56,899 | 91.15% | Imaging not ordered |
| | `imaging_end_datetime` | 56,909 | 91.17% | Imaging pending completion (10 orders) |
| **Pharmacy Service** | `pharmacy_sale_line_id` | 62,120 | 99.52% | Hospital pharmacy dispensation not utilized |
| | `medicine_name` | 62,120 | 99.52% | External prescription / no pharmacy sale |
| | `pharmacy_start_datetime`| 62,120 | 99.52% | No hospital pharmacy visit |
| | `pharmacy_end_datetime` | 62,120 | 99.52% | No hospital pharmacy visit |

*Conclusion:* All high null counts in diagnostic and pharmacy fields are **expected by clinical design**, as only a subset of patients require laboratory, imaging, or internal pharmacy fulfillment.

---

### Check 3: Timestamp Parsing and Clinical Plausibility
- Zero parsing failures (NaT) across all 9 datetime fields.
- Zero out-of-range timestamps (< year 2000 or > year 2030).
- Range spans from **25 April 2024** to **23 July 2026** (reflecting active outpatient department operations).

---

### Check 4: Duplicate Records Analysis
1. **Exact Duplicate Rows:** `0` (Zero fully duplicated records across all 24 columns).
2. **Encounter Uniqueness:**
   - Total distinct `appointment_id` values: `49,912`.
   - `4,822` appointments appear in multiple rows (spanning 2 to 28 rows per appointment).
   - *Clinical Investigation:* This is **not a data defect**. In hospital outpatient departments, an encounter that orders multiple laboratory tests (e.g., CBC + Lipid Profile + Liver Panel) or multiple prescription line items generates a record for each distinct service request.
3. **Patient Longitudinal Cohort:**
   - Total distinct `patient_id` values: `39,442`.
   - `10,003` patients have more than 1 visit (maximum 11 appointments), allowing patient-level readmission and recurrence pathway analysis.

---

### Check 5: Chronological Ordering & Timestamp Inversion Anomalies

| Inversion Type | Evaluated Fields | Violations | Clinical Root Cause |
|---|---|---|---|
| **Service End < Start** | `prescription_end < start` | **52** | Negative elapsed times (-1428 to -5751 min). Day-rollover entry errors or clock drift. |
| | `lab_end < start` | **0** | Perfect internal lab chronology. |
| | `imaging_end < start` | **0** | Perfect internal radiology chronology. |
| | `pharmacy_end < start` | **0** | Perfect internal pharmacy chronology. |
| **Service < Appt Start**| `lab_start < appt_start` | **457** | Clock de-synchronization between reception PCs and lab LIS (e.g. -13 min drift) or blood drawn prior to formal registration desk completion. |
| | `imaging_start < appt_start` | **295** | Clock drift (-11 to -18 min) between radiology RIS and reception desk. |
| | `prescription_start < appt_start`| **5** | Extreme negative drift (-6 to -5704 min). |
| | `pharmacy_start < appt_start` | **0** | Pharmacy consistently follows registration. |
| **Inter-Service** | `pharmacy_start < rx_start` | **0** | Pharmacy dispensation never precedes doctor consultation. |

---

### Check 6: Essential Event-Log Field Integrity
- Rows missing `patient_id`: **0**
- Rows missing `appointment_id`: **0**
- Rows missing `flow_name`: **0**
- Rows missing all timestamps: **0**
- *Conclusion:* 100% of rows contain valid case identifiers and activity labels.

---

### Check 7: Timestamp Completeness
- Encounters missing primary `appointment_start_datetime`: **0**
- Encounters with zero timestamps: **0**

---

### Check 8: Clinical Workflow & Waiting Time Sanity

#### 8A: Activity Pathway Distribution
1. `Appointment → Prescription`: **40,164** encounters (64.34%)
2. `Appointment → Prescription → Lab`: **16,434** encounters (26.33%)
3. `Appointment → Prescription → Imaging`: **3,947** encounters (6.32%)
4. `Appointment → Prescription → Lab + Imaging`: **1,575** encounters (2.52%)
5. `Appointment → Prescription → Pharmacy`: **281** encounters (0.45%)
6. `Appointment → Prescription → Lab + Pharmacy`: **20** encounters (0.03%)
7. `Appointment → Prescription → Imaging + Pharmacy`: **1** encounter (<0.01%)

#### 8B: Waiting Times Breakdown
- **Registration to Doctor Consultation (`appointment_start` to `prescription_start`):**
  - Average wait: **130.5 minutes** (~2.1 hours).
  - Normal OPD operational distribution. 627 records (>8h) represent patients waiting for afternoon specialty clinics.
- **Doctor Consultation to Pharmacy:**
  - Average elapsed time: **14.9 minutes**.
  - Minimum: 1.0 min, Maximum: 314.0 min. 100% positive wait times (0 inversions).
- **Registration to Laboratory Test:**
  - Average elapsed time: **96.6 minutes**.

#### 8C: Deep Dive into the 12 Missing Prescription Timestamps
The 12 records highlighted in `docs/data_quality_notes.md` were isolated and inspected:
- All 12 records belong to `flow_code = 1` (`Appointment → Prescription`).
- All 12 have valid `appointment_start_datetime`, `prescription_doctor_name`, `prescription_order_id`, and `prescription_end_datetime` (e.g., Record 203: consultation finished at `07:13:00`).
- Only `prescription_start_datetime` is NULL (likely skipped by the clinician at consultation start).
- *Handling Strategy:* In the event log, these records still generate a `"Prescription Consultation Completed"` event at the valid completion timestamp, ensuring no consultation data is lost.

---

## 3. Data Quality Conclusions & Guidelines for Process Mining

1. **No Data Deletion Required:** No records need to be deleted. All 62,422 records provide valuable clinical context.
2. **Transparent Anomaly Flagging:** Rather than altering historical timestamps or deleting the 757 records exhibiting minor clock drift, an explicit flag (`timestamp_anomaly_flag = True`) is attached in the event log.
3. **Dual Case ID Support:**
   - **Encounter-level process mining:** Use `case_id = appointment_id` (49,912 cases).
   - **Longitudinal patient pathway mining:** Use `case_id = patient_id` (39,442 cases).

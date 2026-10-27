-- =============================================================================
-- CareFlow Clinical Process Mining — Day 4 SQL Validation
-- File: sql/validation_queries.sql
-- =============================================================================
-- Purpose:
--   Validate the HospitalOPD dataset loaded into BigQuery.
--   All queries are written in BigQuery Standard SQL.
--
-- Target table:
--   `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
--
-- IMPORTANT — Before running:
--   Replace careflow-clinical-process-m with your actual GCP project ID.
--   All column names below are CONFIRMED from inspect_dataset.py on 2026-10-22.
--   No placeholder names remain.
--
-- CONFIRMED SCHEMA (24 columns — actual dataset, verified 2026-10-22):
--
--   record_no                   INTEGER   -- row sequence number (source ordering)
--   patient_id                  INTEGER   -- Case ID (patient level)
--   appointment_id              INTEGER   -- Case ID (visit/appointment level)
--   appointment_start_datetime  TIMESTAMP -- primary event timestamp
--   prescription_doctor_id      INTEGER   -- nullable
--   prescription_doctor_name    STRING    -- nullable
--   prescription_order_id       INTEGER   -- nullable
--   prescription_start_datetime TIMESTAMP -- nullable; flagged missing in docs
--   prescription_end_datetime   TIMESTAMP -- nullable
--   lab_id                      INTEGER   -- nullable (null = no lab test)
--   lab_name                    STRING    -- nullable
--   lab_start_datetime          TIMESTAMP -- nullable
--   lab_end_datetime            TIMESTAMP -- nullable
--   imaging_request_id          INTEGER   -- nullable (null = no imaging)
--   imaging_result_id           INTEGER   -- nullable
--   imaging_name                STRING    -- nullable
--   imaging_start_datetime      TIMESTAMP -- nullable
--   imaging_end_datetime        TIMESTAMP -- nullable
--   pharmacy_sale_line_id       INTEGER   -- nullable (null = no pharmacy)
--   medicine_name               STRING    -- nullable
--   pharmacy_start_datetime     TIMESTAMP -- nullable
--   pharmacy_end_datetime       TIMESTAMP -- nullable
--   flow_code                   INTEGER   -- activity code (event-log Activity)
--   flow_name                   STRING    -- activity label (event-log Activity)
--
-- EVENT-LOG FIELD MAPPING (confirmed):
--   Case ID   -> patient_id  (patient-level) OR appointment_id (visit-level)
--   Activity  -> flow_name   (human-readable), flow_code (numeric)
--   Timestamp -> appointment_start_datetime (primary)
--               + service-specific start/end timestamps
--
-- COLUMN COUNT NOTE:
--   The actual dataset has 24 columns, not 25 as stated in project docs.
--   The 25th column ('Unnamed: 2') was an empty column removed from a
--   working copy during earlier data cleaning. Its absence is expected.
--
-- ORDERING FIELD:
--   `record_no` is the original sequential row number from the source file.
--   It is used to validate event ordering where timestamp ordering alone
--   is insufficient.  If record_no does not correspond to clinical event
--   order, this limitation is noted in each relevant check.
-- =============================================================================


-- =============================================================================
-- CHECK 1: Total Row Count
-- =============================================================================
-- Tests:    Whether the BigQuery table contains the expected number of records.
-- Expected: 62,422 rows (confirmed by file inspection on 2026-10-22).
-- Interpret:
--   actual_row_count = 62422 AND discrepancy = 0  -> PASS
--   discrepancy <> 0                              -> FAIL — check load job logs
-- =============================================================================

SELECT
  COUNT(*)         AS actual_row_count,
  62422            AS expected_row_count,
  COUNT(*) - 62422 AS discrepancy,
  CASE
    WHEN COUNT(*) = 62422 THEN 'PASS'
    ELSE 'FAIL — row count mismatch'
  END              AS check_result
FROM
  `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`;


-- =============================================================================
-- CHECK 2: Column-Level Null Counts (Essential Event-Log Fields)
-- =============================================================================
-- Tests:    Missing values in each field required for the event log.
--           From member3_data_requirements.md: Case ID, Activity, and at least
--           one Timestamp must be non-null for a row to be usable.
-- Interpret:
--   null_or_empty_count = 0 for patient_id, appointment_id -> PASS.
--   null_or_empty_count = 0 for flow_name, flow_code       -> PASS.
--   Timestamp nulls for lab/imaging/pharmacy are EXPECTED when those
--   services were not used for a given appointment — this is NOT an error.
--   prescription_start_datetime nulls were specifically flagged in
--   data_quality_notes.md and require investigation.
-- =============================================================================

SELECT
  'patient_id'                                            AS column_name,
  COUNTIF(patient_id IS NULL)                             AS null_or_empty_count,
  COUNT(*)                                                AS total_rows,
  ROUND(COUNTIF(patient_id IS NULL) * 100.0 / COUNT(*), 2) AS null_pct
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'appointment_id',
  COUNTIF(appointment_id IS NULL),
  COUNT(*),
  ROUND(COUNTIF(appointment_id IS NULL) * 100.0 / COUNT(*), 2)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'flow_name',
  COUNTIF(flow_name IS NULL OR TRIM(flow_name) = ''),
  COUNT(*),
  ROUND(COUNTIF(flow_name IS NULL OR TRIM(flow_name) = '') * 100.0 / COUNT(*), 2)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'flow_code',
  COUNTIF(flow_code IS NULL),
  COUNT(*),
  ROUND(COUNTIF(flow_code IS NULL) * 100.0 / COUNT(*), 2)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'appointment_start_datetime',
  COUNTIF(appointment_start_datetime IS NULL),
  COUNT(*),
  ROUND(COUNTIF(appointment_start_datetime IS NULL) * 100.0 / COUNT(*), 2)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'prescription_start_datetime  [FLAGGED — see docs]',
  COUNTIF(prescription_start_datetime IS NULL),
  COUNT(*),
  ROUND(COUNTIF(prescription_start_datetime IS NULL) * 100.0 / COUNT(*), 2)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'lab_start_datetime           [nullable by design]',
  COUNTIF(lab_start_datetime IS NULL),
  COUNT(*),
  ROUND(COUNTIF(lab_start_datetime IS NULL) * 100.0 / COUNT(*), 2)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'imaging_start_datetime       [nullable by design]',
  COUNTIF(imaging_start_datetime IS NULL),
  COUNT(*),
  ROUND(COUNTIF(imaging_start_datetime IS NULL) * 100.0 / COUNT(*), 2)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'pharmacy_start_datetime      [nullable by design]',
  COUNTIF(pharmacy_start_datetime IS NULL),
  COUNT(*),
  ROUND(COUNTIF(pharmacy_start_datetime IS NULL) * 100.0 / COUNT(*), 2)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

ORDER BY
  null_pct DESC;


-- =============================================================================
-- CHECK 3: Timestamp Validity — Out-of-Range or Implausible Timestamps
-- =============================================================================
-- Tests:    Whether any timestamp field contains values outside a plausible
--           clinical date range.  Range set to 2000-01-01 to 2030-12-31.
--           Adjust if the dataset covers a different period.
-- Interpret:
--   out_of_range_count = 0 -> PASS for that column.
--   out_of_range_count > 0 -> FAIL — examine flagged rows; may indicate
--                             parsing errors or data entry issues.
-- =============================================================================

SELECT
  'appointment_start_datetime'                                        AS column_name,
  COUNTIF(
    appointment_start_datetime < TIMESTAMP '2000-01-01 00:00:00'
    OR appointment_start_datetime > TIMESTAMP '2030-12-31 23:59:59') AS out_of_range_count,
  COUNTIF(appointment_start_datetime IS NULL)                         AS null_count,
  MIN(appointment_start_datetime)                                     AS min_value,
  MAX(appointment_start_datetime)                                     AS max_value
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'prescription_start_datetime',
  COUNTIF(
    prescription_start_datetime < TIMESTAMP '2000-01-01 00:00:00'
    OR prescription_start_datetime > TIMESTAMP '2030-12-31 23:59:59'),
  COUNTIF(prescription_start_datetime IS NULL),
  MIN(prescription_start_datetime),
  MAX(prescription_start_datetime)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'prescription_end_datetime',
  COUNTIF(
    prescription_end_datetime < TIMESTAMP '2000-01-01 00:00:00'
    OR prescription_end_datetime > TIMESTAMP '2030-12-31 23:59:59'),
  COUNTIF(prescription_end_datetime IS NULL),
  MIN(prescription_end_datetime),
  MAX(prescription_end_datetime)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'lab_start_datetime',
  COUNTIF(
    lab_start_datetime < TIMESTAMP '2000-01-01 00:00:00'
    OR lab_start_datetime > TIMESTAMP '2030-12-31 23:59:59'),
  COUNTIF(lab_start_datetime IS NULL),
  MIN(lab_start_datetime),
  MAX(lab_start_datetime)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'lab_end_datetime',
  COUNTIF(
    lab_end_datetime < TIMESTAMP '2000-01-01 00:00:00'
    OR lab_end_datetime > TIMESTAMP '2030-12-31 23:59:59'),
  COUNTIF(lab_end_datetime IS NULL),
  MIN(lab_end_datetime),
  MAX(lab_end_datetime)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'imaging_start_datetime',
  COUNTIF(
    imaging_start_datetime < TIMESTAMP '2000-01-01 00:00:00'
    OR imaging_start_datetime > TIMESTAMP '2030-12-31 23:59:59'),
  COUNTIF(imaging_start_datetime IS NULL),
  MIN(imaging_start_datetime),
  MAX(imaging_start_datetime)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'imaging_end_datetime',
  COUNTIF(
    imaging_end_datetime < TIMESTAMP '2000-01-01 00:00:00'
    OR imaging_end_datetime > TIMESTAMP '2030-12-31 23:59:59'),
  COUNTIF(imaging_end_datetime IS NULL),
  MIN(imaging_end_datetime),
  MAX(imaging_end_datetime)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'pharmacy_start_datetime',
  COUNTIF(
    pharmacy_start_datetime < TIMESTAMP '2000-01-01 00:00:00'
    OR pharmacy_start_datetime > TIMESTAMP '2030-12-31 23:59:59'),
  COUNTIF(pharmacy_start_datetime IS NULL),
  MIN(pharmacy_start_datetime),
  MAX(pharmacy_start_datetime)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'pharmacy_end_datetime',
  COUNTIF(
    pharmacy_end_datetime < TIMESTAMP '2000-01-01 00:00:00'
    OR pharmacy_end_datetime > TIMESTAMP '2030-12-31 23:59:59'),
  COUNTIF(pharmacy_end_datetime IS NULL),
  MIN(pharmacy_end_datetime),
  MAX(pharmacy_end_datetime)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

ORDER BY
  out_of_range_count DESC;


-- =============================================================================
-- CHECK 4A: Exact Duplicate Rows
-- =============================================================================
-- Tests:    Rows where ALL column values are identical.
-- Interpret:
--   rows_in_duplicate_groups = 0 -> PASS.
--   rows_in_duplicate_groups > 0 -> FAIL — data_quality_notes.md noted no
--                                   duplicates at initial check; any duplicates
--                                   here may indicate a load issue.
-- =============================================================================

WITH row_duplicates AS (
  SELECT
    record_no,
    patient_id,
    appointment_id,
    appointment_start_datetime,
    prescription_order_id,
    prescription_start_datetime,
    lab_id,
    lab_start_datetime,
    imaging_request_id,
    imaging_start_datetime,
    pharmacy_sale_line_id,
    pharmacy_start_datetime,
    flow_code,
    flow_name,
    COUNT(*) OVER (
      PARTITION BY
        patient_id,
        appointment_id,
        appointment_start_datetime,
        prescription_order_id,
        lab_id,
        imaging_request_id,
        pharmacy_sale_line_id,
        flow_code
    ) AS occurrence_count
  FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
)
SELECT
  COUNTIF(occurrence_count > 1)  AS rows_in_duplicate_groups,
  COUNT(*)                       AS total_rows,
  CASE
    WHEN COUNTIF(occurrence_count > 1) = 0 THEN 'PASS'
    ELSE 'FAIL — duplicate rows detected'
  END                            AS check_result
FROM row_duplicates;


-- =============================================================================
-- CHECK 4B: Repeated Case-Activity Combinations (Logical Duplicates)
-- =============================================================================
-- Tests:    Whether the same patient_id + flow_name combination appears more
--           than once.  This may be expected (a patient can visit multiple
--           times) or may indicate data issues depending on case_id definition.
-- Interpret:
--   Use appointment_id as the Case ID for visit-level uniqueness.
--   Repeated patient_id + flow_name is expected across different appointments.
--   Repeated appointment_id + flow_name is unexpected and requires review.
-- =============================================================================

-- 4B-i: appointment_id + flow_name (should be unique per appointment)
SELECT
  appointment_id,
  flow_name,
  COUNT(*) AS occurrence_count
FROM
  `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
GROUP BY
  appointment_id,
  flow_name
HAVING
  COUNT(*) > 1
ORDER BY
  occurrence_count DESC
LIMIT 50;


-- =============================================================================
-- CHECK 5: Event Ordering and Chronological Consistency Within Each Case
-- =============================================================================
-- Tests:    Whether event timestamps follow a clinically plausible sequence.
--           Expected clinical order (optional steps in brackets):
--             appointment_start_datetime
--             -> [prescription_start_datetime]
--             -> [prescription_end_datetime]
--             -> [lab_start_datetime -> lab_end_datetime]
--             -> [imaging_start_datetime -> imaging_end_datetime]
--             -> [pharmacy_start_datetime -> pharmacy_end_datetime]
--
-- ORDERING FIELD NOTE:
--   `record_no` is the original sequential row number from the source file.
--   It reflects insertion order in the source, not guaranteed clinical order.
--   Timestamp ordering (below) is the primary validity check.
--   Where record_no ordering and timestamp ordering disagree, investigate.
--
-- Interpret:
--   violated_ordering_count = 0 -> No timestamp inversions detected.
--   violated_ordering_count > 0 -> Rows where a downstream timestamp is
--                                  earlier than an upstream timestamp.
-- =============================================================================

-- 5A: End before start — within each service (should never happen)
SELECT
  'prescription_end_before_start'                        AS violation_type,
  COUNT(*)                                               AS violated_ordering_count
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
WHERE
  prescription_end_datetime IS NOT NULL
  AND prescription_start_datetime IS NOT NULL
  AND prescription_end_datetime < prescription_start_datetime

UNION ALL

SELECT
  'lab_end_before_start',
  COUNT(*)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
WHERE
  lab_end_datetime IS NOT NULL
  AND lab_start_datetime IS NOT NULL
  AND lab_end_datetime < lab_start_datetime

UNION ALL

SELECT
  'imaging_end_before_start',
  COUNT(*)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
WHERE
  imaging_end_datetime IS NOT NULL
  AND imaging_start_datetime IS NOT NULL
  AND imaging_end_datetime < imaging_start_datetime

UNION ALL

SELECT
  'pharmacy_end_before_start',
  COUNT(*)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
WHERE
  pharmacy_end_datetime IS NOT NULL
  AND pharmacy_start_datetime IS NOT NULL
  AND pharmacy_end_datetime < pharmacy_start_datetime

UNION ALL

-- 5B: Service timestamps before appointment start (not clinically possible)
SELECT
  'prescription_before_appointment',
  COUNT(*)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
WHERE
  prescription_start_datetime IS NOT NULL
  AND appointment_start_datetime IS NOT NULL
  AND prescription_start_datetime < appointment_start_datetime

UNION ALL

SELECT
  'lab_before_appointment',
  COUNT(*)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
WHERE
  lab_start_datetime IS NOT NULL
  AND appointment_start_datetime IS NOT NULL
  AND lab_start_datetime < appointment_start_datetime

UNION ALL

SELECT
  'imaging_before_appointment',
  COUNT(*)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
WHERE
  imaging_start_datetime IS NOT NULL
  AND appointment_start_datetime IS NOT NULL
  AND imaging_start_datetime < appointment_start_datetime

UNION ALL

SELECT
  'pharmacy_before_appointment',
  COUNT(*)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
WHERE
  pharmacy_start_datetime IS NOT NULL
  AND appointment_start_datetime IS NOT NULL
  AND pharmacy_start_datetime < appointment_start_datetime

UNION ALL

-- 5C: Pharmacy before prescription (pharmacy logically follows prescription)
SELECT
  'pharmacy_before_prescription',
  COUNT(*)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
WHERE
  pharmacy_start_datetime IS NOT NULL
  AND prescription_start_datetime IS NOT NULL
  AND pharmacy_start_datetime < prescription_start_datetime

ORDER BY
  violated_ordering_count DESC;


-- =============================================================================
-- CHECK 6: Missing or Null Case Identifiers and Activity Names
-- =============================================================================
-- Tests:    Rows that cannot be included in the event log because they lack
--           a case ID or an activity name.  Both fields are required.
-- Interpret:
--   rows_missing_patient_id = 0    -> PASS
--   rows_missing_appointment_id = 0 -> PASS
--   rows_missing_flow_name = 0     -> PASS
--   Any non-zero value is a FAIL — those rows are unusable for process mining.
-- =============================================================================

SELECT
  COUNTIF(patient_id IS NULL)                             AS rows_missing_patient_id,
  COUNTIF(appointment_id IS NULL)                         AS rows_missing_appointment_id,
  COUNTIF(flow_name IS NULL OR TRIM(flow_name) = '')      AS rows_missing_flow_name,
  COUNTIF(flow_code IS NULL)                              AS rows_missing_flow_code,
  COUNTIF(
    patient_id IS NULL
    AND appointment_id IS NULL
  )                                                       AS rows_missing_all_case_ids,
  COUNT(*)                                                AS total_rows
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`;


-- =============================================================================
-- CHECK 7: Cases With Invalid or Inconsistent Timestamps
-- =============================================================================
-- Tests:    Cases where the primary appointment timestamp is NULL (unusable
--           for event-log ordering) and cases with no timestamps at all.
-- Interpret:
--   cases_with_null_appointment_time -> cannot determine when the visit started.
--   cases_with_no_timestamps         -> rows with zero usable timestamps; unusable.
-- =============================================================================

SELECT
  COUNT(DISTINCT CASE
    WHEN appointment_start_datetime IS NULL THEN appointment_id
    END)                                AS cases_with_null_appointment_time,
  COUNT(DISTINCT CASE
    WHEN appointment_start_datetime IS NULL
      AND prescription_start_datetime IS NULL
      AND lab_start_datetime IS NULL
      AND imaging_start_datetime IS NULL
      AND pharmacy_start_datetime IS NULL
    THEN appointment_id
    END)                                AS cases_with_no_timestamps_at_all,
  COUNT(DISTINCT appointment_id)        AS total_distinct_appointments,
  COUNT(DISTINCT patient_id)            AS total_distinct_patients
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`;


-- =============================================================================
-- CHECK 8A: Activity (flow_name) Value Consistency
-- =============================================================================
-- Tests:    All distinct flow_name values present in the dataset.
--           Sample values observed in the source: 'Appointment -> Prescription'
--           Review all returned values against the agreed activity vocabulary.
-- Interpret:
--   Any value not in the agreed-upon activity list requires correction or mapping.
--   Unicode arrow characters (e.g., '->' vs actual arrow) should be consistent.
-- =============================================================================

SELECT
  flow_name                                                           AS activity_value,
  flow_code                                                           AS activity_code,
  COUNT(*)                                                            AS row_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2)                  AS pct_of_total
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
GROUP BY
  flow_name,
  flow_code
ORDER BY
  row_count DESC;


-- =============================================================================
-- CHECK 8B: Case Count and Average Events per Case
-- =============================================================================
-- Tests:    How many unique cases exist and whether the event distribution
--           is reasonable.  Very high or very low event counts per case may
--           indicate a wrong choice of Case ID field.
--           Two case ID options are compared:
--             appointment_id — visit-level (one appointment = one case)
--             patient_id     — patient-level (may span multiple appointments)
-- =============================================================================

-- 8B-i: appointment_id as Case ID
WITH appt_event_counts AS (
  SELECT
    appointment_id,
    COUNT(*) AS event_count
  FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
  GROUP BY appointment_id
)
SELECT
  'appointment_id'               AS case_id_field,
  COUNT(DISTINCT appointment_id) AS total_distinct_cases,
  MIN(event_count)               AS min_events_per_case,
  MAX(event_count)               AS max_events_per_case,
  ROUND(AVG(event_count), 2)     AS avg_events_per_case,
  APPROX_QUANTILES(event_count, 100)[OFFSET(50)] AS median_events_per_case
FROM appt_event_counts

UNION ALL

-- 8B-ii: patient_id as Case ID
WITH patient_event_counts AS (
  SELECT
    patient_id,
    COUNT(*) AS event_count
  FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
  GROUP BY patient_id
)
SELECT
  'patient_id',
  COUNT(DISTINCT patient_id),
  MIN(event_count),
  MAX(event_count),
  ROUND(AVG(event_count), 2),
  APPROX_QUANTILES(event_count, 100)[OFFSET(50)]
FROM patient_event_counts;


-- =============================================================================
-- CHECK 8C: Waiting Time Sanity Check (OPD Process Mining)
-- =============================================================================
-- Tests:    Elapsed minutes between appointment start and each downstream event.
--           Implausibly long or negative waiting times indicate data issues.
-- Interpret:
--   Negative wait times -> timestamp inversion (also caught in Check 5).
--   Very large wait times (> 480 min / 8 hours for OPD) -> investigate.
--   Expected OPD range: 0-480 minutes per clinical guidance.
--   Adjust thresholds based on actual clinical context.
-- =============================================================================

SELECT
  'appointment -> prescription_start'                 AS transition,
  COUNT(*)                                            AS rows_with_both_timestamps,
  ROUND(MIN(TIMESTAMP_DIFF(
    prescription_start_datetime, appointment_start_datetime, MINUTE)), 1) AS min_wait_min,
  ROUND(MAX(TIMESTAMP_DIFF(
    prescription_start_datetime, appointment_start_datetime, MINUTE)), 1) AS max_wait_min,
  ROUND(AVG(TIMESTAMP_DIFF(
    prescription_start_datetime, appointment_start_datetime, MINUTE)), 1) AS avg_wait_min,
  COUNTIF(TIMESTAMP_DIFF(
    prescription_start_datetime, appointment_start_datetime, MINUTE) < 0) AS negative_wait,
  COUNTIF(TIMESTAMP_DIFF(
    prescription_start_datetime, appointment_start_datetime, MINUTE) > 480) AS over_8hr
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
WHERE
  prescription_start_datetime IS NOT NULL
  AND appointment_start_datetime IS NOT NULL

UNION ALL

SELECT
  'appointment -> lab_start',
  COUNT(*),
  ROUND(MIN(TIMESTAMP_DIFF(lab_start_datetime, appointment_start_datetime, MINUTE)), 1),
  ROUND(MAX(TIMESTAMP_DIFF(lab_start_datetime, appointment_start_datetime, MINUTE)), 1),
  ROUND(AVG(TIMESTAMP_DIFF(lab_start_datetime, appointment_start_datetime, MINUTE)), 1),
  COUNTIF(TIMESTAMP_DIFF(lab_start_datetime, appointment_start_datetime, MINUTE) < 0),
  COUNTIF(TIMESTAMP_DIFF(lab_start_datetime, appointment_start_datetime, MINUTE) > 480)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
WHERE
  lab_start_datetime IS NOT NULL
  AND appointment_start_datetime IS NOT NULL

UNION ALL

SELECT
  'appointment -> imaging_start',
  COUNT(*),
  ROUND(MIN(TIMESTAMP_DIFF(imaging_start_datetime, appointment_start_datetime, MINUTE)), 1),
  ROUND(MAX(TIMESTAMP_DIFF(imaging_start_datetime, appointment_start_datetime, MINUTE)), 1),
  ROUND(AVG(TIMESTAMP_DIFF(imaging_start_datetime, appointment_start_datetime, MINUTE)), 1),
  COUNTIF(TIMESTAMP_DIFF(imaging_start_datetime, appointment_start_datetime, MINUTE) < 0),
  COUNTIF(TIMESTAMP_DIFF(imaging_start_datetime, appointment_start_datetime, MINUTE) > 480)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
WHERE
  imaging_start_datetime IS NOT NULL
  AND appointment_start_datetime IS NOT NULL

UNION ALL

SELECT
  'appointment -> pharmacy_start',
  COUNT(*),
  ROUND(MIN(TIMESTAMP_DIFF(pharmacy_start_datetime, appointment_start_datetime, MINUTE)), 1),
  ROUND(MAX(TIMESTAMP_DIFF(pharmacy_start_datetime, appointment_start_datetime, MINUTE)), 1),
  ROUND(AVG(TIMESTAMP_DIFF(pharmacy_start_datetime, appointment_start_datetime, MINUTE)), 1),
  COUNTIF(TIMESTAMP_DIFF(pharmacy_start_datetime, appointment_start_datetime, MINUTE) < 0),
  COUNTIF(TIMESTAMP_DIFF(pharmacy_start_datetime, appointment_start_datetime, MINUTE) > 480)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
WHERE
  pharmacy_start_datetime IS NOT NULL
  AND appointment_start_datetime IS NOT NULL

UNION ALL

SELECT
  'prescription_start -> pharmacy_start',
  COUNT(*),
  ROUND(MIN(TIMESTAMP_DIFF(pharmacy_start_datetime, prescription_start_datetime, MINUTE)), 1),
  ROUND(MAX(TIMESTAMP_DIFF(pharmacy_start_datetime, prescription_start_datetime, MINUTE)), 1),
  ROUND(AVG(TIMESTAMP_DIFF(pharmacy_start_datetime, prescription_start_datetime, MINUTE)), 1),
  COUNTIF(TIMESTAMP_DIFF(pharmacy_start_datetime, prescription_start_datetime, MINUTE) < 0),
  COUNTIF(TIMESTAMP_DIFF(pharmacy_start_datetime, prescription_start_datetime, MINUTE) > 480)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
WHERE
  pharmacy_start_datetime IS NOT NULL
  AND prescription_start_datetime IS NOT NULL

ORDER BY
  transition;


-- =============================================================================
-- CHECK 8D: Missing Prescription Timestamp Investigation
-- =============================================================================
-- SPECIFIC to data_quality_notes.md flag:
--   "missing prescription timestamps and timestamp inconsistencies"
-- Tests:    Rows with pharmacy activity but no prescription start (logical gap).
--           Rows with prescription start but no pharmacy (incomplete pathway).
-- Interpret:
--   pharmacy_without_prescription > 0 -> possible walk-in pharmacy or error.
--   prescription_without_pharmacy  > 0 -> prescription not fulfilled or data gap.
-- =============================================================================

SELECT
  COUNTIF(
    pharmacy_start_datetime IS NOT NULL
    AND prescription_start_datetime IS NULL
  )                                        AS pharmacy_without_prescription,
  COUNTIF(
    prescription_start_datetime IS NOT NULL
    AND pharmacy_start_datetime IS NULL
  )                                        AS prescription_without_pharmacy,
  COUNTIF(
    prescription_start_datetime IS NULL
    AND pharmacy_start_datetime IS NULL
  )                                        AS neither_prescription_nor_pharmacy,
  COUNTIF(
    prescription_start_datetime IS NOT NULL
    AND pharmacy_start_datetime IS NOT NULL
  )                                        AS both_prescription_and_pharmacy,
  COUNT(*)                                 AS total_rows
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`;


-- =============================================================================
-- CHECK 8E: Fully Null Service Columns
-- =============================================================================
-- Tests:    Whether any column is entirely null across all rows.
--           The 'Unnamed: 2' column noted in project notes was removed before
--           cleaning and should NOT appear in the BigQuery table.
--           Service columns (lab, imaging, pharmacy) will be partially null
--           because not every patient uses every service — that is expected.
-- Interpret:
--   status = 'FULLY NULL' for a service ID column -> investigate.
--   status = 'FULLY NULL' for lab_id/imaging_request_id/pharmacy_sale_line_id
--   would be unexpected and may indicate a load schema mismatch.
-- =============================================================================

SELECT 'record_no'                   AS col, COUNTIF(record_no IS NULL)                   AS null_count, COUNT(*) AS total, CASE WHEN COUNTIF(record_no IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END AS status FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'patient_id',                       COUNTIF(patient_id IS NULL),                       COUNT(*), CASE WHEN COUNTIF(patient_id IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'appointment_id',                   COUNTIF(appointment_id IS NULL),                   COUNT(*), CASE WHEN COUNTIF(appointment_id IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'appointment_start_datetime',       COUNTIF(appointment_start_datetime IS NULL),       COUNT(*), CASE WHEN COUNTIF(appointment_start_datetime IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'prescription_doctor_id',           COUNTIF(prescription_doctor_id IS NULL),           COUNT(*), CASE WHEN COUNTIF(prescription_doctor_id IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'prescription_doctor_name',         COUNTIF(prescription_doctor_name IS NULL),         COUNT(*), CASE WHEN COUNTIF(prescription_doctor_name IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'prescription_order_id',            COUNTIF(prescription_order_id IS NULL),            COUNT(*), CASE WHEN COUNTIF(prescription_order_id IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'prescription_start_datetime',      COUNTIF(prescription_start_datetime IS NULL),      COUNT(*), CASE WHEN COUNTIF(prescription_start_datetime IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'prescription_end_datetime',        COUNTIF(prescription_end_datetime IS NULL),        COUNT(*), CASE WHEN COUNTIF(prescription_end_datetime IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'lab_id',                           COUNTIF(lab_id IS NULL),                           COUNT(*), CASE WHEN COUNTIF(lab_id IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'lab_name',                         COUNTIF(lab_name IS NULL),                         COUNT(*), CASE WHEN COUNTIF(lab_name IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'lab_start_datetime',               COUNTIF(lab_start_datetime IS NULL),               COUNT(*), CASE WHEN COUNTIF(lab_start_datetime IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'lab_end_datetime',                 COUNTIF(lab_end_datetime IS NULL),                 COUNT(*), CASE WHEN COUNTIF(lab_end_datetime IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'imaging_request_id',               COUNTIF(imaging_request_id IS NULL),               COUNT(*), CASE WHEN COUNTIF(imaging_request_id IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'imaging_result_id',                COUNTIF(imaging_result_id IS NULL),                COUNT(*), CASE WHEN COUNTIF(imaging_result_id IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'imaging_name',                     COUNTIF(imaging_name IS NULL),                     COUNT(*), CASE WHEN COUNTIF(imaging_name IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'imaging_start_datetime',           COUNTIF(imaging_start_datetime IS NULL),           COUNT(*), CASE WHEN COUNTIF(imaging_start_datetime IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'imaging_end_datetime',             COUNTIF(imaging_end_datetime IS NULL),             COUNT(*), CASE WHEN COUNTIF(imaging_end_datetime IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'pharmacy_sale_line_id',            COUNTIF(pharmacy_sale_line_id IS NULL),            COUNT(*), CASE WHEN COUNTIF(pharmacy_sale_line_id IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'medicine_name',                    COUNTIF(medicine_name IS NULL),                    COUNT(*), CASE WHEN COUNTIF(medicine_name IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'pharmacy_start_datetime',          COUNTIF(pharmacy_start_datetime IS NULL),          COUNT(*), CASE WHEN COUNTIF(pharmacy_start_datetime IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'pharmacy_end_datetime',            COUNTIF(pharmacy_end_datetime IS NULL),            COUNT(*), CASE WHEN COUNTIF(pharmacy_end_datetime IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'flow_code',                        COUNTIF(flow_code IS NULL),                        COUNT(*), CASE WHEN COUNTIF(flow_code IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`
UNION ALL
SELECT 'flow_name',                        COUNTIF(flow_name IS NULL),                        COUNT(*), CASE WHEN COUNTIF(flow_name IS NULL) = COUNT(*) THEN 'FULLY NULL' ELSE 'OK' END FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

ORDER BY null_count DESC;


-- =============================================================================
-- VALIDATION SUMMARY VIEW (run after all individual checks complete)
-- =============================================================================
-- Creates a single snapshot of key validation metrics for documentation.
-- Run this last and record the results in docs/day3_day4_report.md.
-- =============================================================================

SELECT
  'total_rows'                                             AS metric,
  CAST(COUNT(*) AS STRING)                                 AS value
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'distinct_appointments',
  CAST(COUNT(DISTINCT appointment_id) AS STRING)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'distinct_patients',
  CAST(COUNT(DISTINCT patient_id) AS STRING)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'distinct_flow_names',
  CAST(COUNT(DISTINCT flow_name) AS STRING)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'rows_missing_appointment_start',
  CAST(COUNTIF(appointment_start_datetime IS NULL) AS STRING)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'rows_missing_flow_name',
  CAST(COUNTIF(flow_name IS NULL OR TRIM(flow_name) = '') AS STRING)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'rows_missing_prescription_start  [flagged]',
  CAST(COUNTIF(prescription_start_datetime IS NULL) AS STRING)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'appointments_with_lab',
  CAST(COUNT(DISTINCT CASE WHEN lab_id IS NOT NULL THEN appointment_id END) AS STRING)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'appointments_with_imaging',
  CAST(COUNT(DISTINCT CASE WHEN imaging_request_id IS NOT NULL THEN appointment_id END) AS STRING)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

UNION ALL

SELECT
  'appointments_with_pharmacy',
  CAST(COUNT(DISTINCT CASE WHEN pharmacy_sale_line_id IS NOT NULL THEN appointment_id END) AS STRING)
FROM `careflow-clinical-process-m.careflow_opd.hospital_opd_cleaned`

ORDER BY metric;

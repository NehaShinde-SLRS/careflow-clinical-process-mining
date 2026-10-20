-- =====================================================================
-- CareFlow: Clinical Pathway Process Mining - BigQuery & SQL Deliverable
-- Target Dataset: `careflow_dw.cleaned_hospital_opd`
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Pathway Flow Distribution and Patient Reach
-- Evaluates transaction volumes, distinct patient reach, and share %
-- ---------------------------------------------------------------------
SELECT 
    flow_code,
    flow_name,
    COUNT(*) AS total_records,
    COUNT(DISTINCT appointment_id) AS distinct_encounters,
    COUNT(DISTINCT patient_id) AS distinct_patients,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage_share
FROM `careflow_dw.cleaned_hospital_opd`
GROUP BY flow_code, flow_name
ORDER BY total_records DESC;


-- ---------------------------------------------------------------------
-- 2. Aggregate Event Occurrences by Departmental Activity
-- Unpivots stage milestones across the clinical care journey
-- ---------------------------------------------------------------------
WITH unpivoted_activities AS (
    SELECT 'Appointment Check-in' AS activity_name, appointment_id 
    FROM `careflow_dw.cleaned_hospital_opd` 
    WHERE appointment_start_datetime IS NOT NULL

    UNION ALL

    SELECT 'Doctor Consultation' AS activity_name, appointment_id 
    FROM `careflow_dw.cleaned_hospital_opd` 
    WHERE prescription_start_datetime IS NOT NULL

    UNION ALL

    SELECT 'Prescription Finalized' AS activity_name, appointment_id 
    FROM `careflow_dw.cleaned_hospital_opd` 
    WHERE prescription_end_datetime IS NOT NULL

    UNION ALL

    SELECT CONCAT('Lab: ', lab_name) AS activity_name, appointment_id 
    FROM `careflow_dw.cleaned_hospital_opd` 
    WHERE lab_name IS NOT NULL

    UNION ALL

    SELECT CONCAT('Imaging: ', imaging_name) AS activity_name, appointment_id 
    FROM `careflow_dw.cleaned_hospital_opd` 
    WHERE imaging_name IS NOT NULL

    UNION ALL

    SELECT CONCAT('Pharmacy: ', medicine_name) AS activity_name, appointment_id 
    FROM `careflow_dw.cleaned_hospital_opd` 
    WHERE medicine_name IS NOT NULL
)
SELECT 
    activity_name,
    COUNT(*) AS total_occurrences,
    COUNT(DISTINCT appointment_id) AS distinct_encounters
FROM unpivoted_activities
GROUP BY activity_name
ORDER BY total_occurrences DESC;


-- ---------------------------------------------------------------------
-- 3. Departmental Waiting Times & Transition Durations (Minutes)
-- Computes stage transition metrics and potential bottleneck delays
-- ---------------------------------------------------------------------
SELECT 
    flow_name,
    COUNT(DISTINCT appointment_id) AS total_encounters,
    -- Queue Wait Time: Check-in to Doctor Consultation Start
    ROUND(AVG(DATETIME_DIFF(prescription_start_datetime, appointment_start_datetime, MINUTE)), 1) AS avg_wait_to_consult_mins,
    -- Doctor Consultation & Prescription Length
    ROUND(AVG(DATETIME_DIFF(prescription_end_datetime, prescription_start_datetime, MINUTE)), 1) AS avg_consult_duration_mins,
    -- Post-Consultation Wait for Lab Test Start
    ROUND(AVG(DATETIME_DIFF(lab_start_datetime, prescription_end_datetime, MINUTE)), 1) AS avg_wait_to_lab_mins,
    -- Laboratory Turnaround Time (Processing & Verification)
    ROUND(AVG(DATETIME_DIFF(lab_end_datetime, lab_start_datetime, MINUTE)), 1) AS avg_lab_tat_mins,
    -- Post-Consultation Wait for Imaging Procedure Start
    ROUND(AVG(DATETIME_DIFF(imaging_start_datetime, prescription_end_datetime, MINUTE)), 1) AS avg_wait_to_imaging_mins,
    -- Total Length of Stay in OPD
    ROUND(AVG(DATETIME_DIFF(
        COALESCE(pharmacy_end_datetime, lab_end_datetime, imaging_end_datetime, prescription_end_datetime),
        appointment_start_datetime, 
        MINUTE
    )), 1) AS avg_total_journey_mins
FROM `careflow_dw.cleaned_hospital_opd`
GROUP BY flow_name
ORDER BY total_encounters DESC;


-- ---------------------------------------------------------------------
-- 4. Physician Caseload & Consultation Performance
-- Evaluates doctor workload and consultation length
-- ---------------------------------------------------------------------
SELECT 
    prescription_doctor_id,
    prescription_doctor_name,
    COUNT(DISTINCT appointment_id) AS total_patients_seen,
    ROUND(AVG(DATETIME_DIFF(prescription_end_datetime, prescription_start_datetime, MINUTE)), 1) AS avg_consult_mins,
    ROUND(MIN(DATETIME_DIFF(prescription_end_datetime, prescription_start_datetime, MINUTE)), 1) AS min_consult_mins,
    ROUND(MAX(DATETIME_DIFF(prescription_end_datetime, prescription_start_datetime, MINUTE)), 1) AS max_consult_mins
FROM `careflow_dw.cleaned_hospital_opd`
GROUP BY prescription_doctor_id, prescription_doctor_name
HAVING total_patients_seen >= 100
ORDER BY total_patients_seen DESC;


-- ---------------------------------------------------------------------
-- 5. Top Diagnostic Laboratory Tests & Turnaround Times (TAT)
-- Assesses diagnostic order frequencies and test turnaround
-- ---------------------------------------------------------------------
SELECT 
    lab_name,
    COUNT(*) AS total_orders,
    ROUND(AVG(DATETIME_DIFF(lab_end_datetime, lab_start_datetime, MINUTE)), 1) AS avg_tat_mins,
    ROUND(AVG(DATETIME_DIFF(lab_end_datetime, lab_start_datetime, HOUR)), 1) AS avg_tat_hours
FROM `careflow_dw.cleaned_hospital_opd`
WHERE lab_name IS NOT NULL AND lab_end_datetime IS NOT NULL
GROUP BY lab_name
ORDER BY total_orders DESC
LIMIT 15;


-- ---------------------------------------------------------------------
-- 6. Intermediate Event Log Transformation (For PM4Py Process Mining)
-- Formats data into a normalized event log schema
-- ---------------------------------------------------------------------
WITH staged AS (
    SELECT * FROM `careflow_dw.cleaned_hospital_opd`
),
events AS (
    SELECT 
        appointment_id AS case_id,
        patient_id,
        'Appointment Check-in' AS activity,
        appointment_start_datetime AS timestamp,
        'Front Desk' AS resource,
        'Registration' AS lifecycle_stage,
        flow_code, flow_name
    FROM staged
    WHERE appointment_start_datetime IS NOT NULL

    UNION ALL

    SELECT 
        appointment_id AS case_id,
        patient_id,
        'Doctor Consultation' AS activity,
        prescription_start_datetime AS timestamp,
        prescription_doctor_name AS resource,
        'Consultation' AS lifecycle_stage,
        flow_code, flow_name
    FROM staged
    WHERE prescription_start_datetime IS NOT NULL

    UNION ALL

    SELECT 
        appointment_id AS case_id,
        patient_id,
        CONCAT('Lab - ', lab_name) AS activity,
        lab_start_datetime AS timestamp,
        'Pathology Lab' AS resource,
        'Diagnostics' AS lifecycle_stage,
        flow_code, flow_name
    FROM staged
    WHERE lab_name IS NOT NULL AND lab_start_datetime IS NOT NULL

    UNION ALL

    SELECT 
        appointment_id AS case_id,
        patient_id,
        CONCAT('Imaging - ', imaging_name) AS activity,
        imaging_start_datetime AS timestamp,
        'Radiology Dept' AS resource,
        'Diagnostics' AS lifecycle_stage,
        flow_code, flow_name
    FROM staged
    WHERE imaging_name IS NOT NULL AND imaging_start_datetime IS NOT NULL

    UNION ALL

    SELECT 
        appointment_id AS case_id,
        patient_id,
        CONCAT('Pharmacy - ', medicine_name) AS activity,
        pharmacy_start_datetime AS timestamp,
        'Hospital Pharmacy' AS resource,
        'Treatment' AS lifecycle_stage,
        flow_code, flow_name
    FROM staged
    WHERE medicine_name IS NOT NULL AND pharmacy_start_datetime IS NOT NULL
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY case_id, timestamp) AS event_id,
    case_id,
    patient_id,
    activity,
    timestamp,
    resource,
    lifecycle_stage,
    flow_code,
    flow_name
FROM events;

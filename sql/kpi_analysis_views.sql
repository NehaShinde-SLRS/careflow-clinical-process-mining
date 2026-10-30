-- =============================================================================
-- CareFlow Clinical Process Mining — Day 3 SQL KPI Analysis Views
-- File: sql/kpi_analysis_views.sql
-- =============================================================================
-- Purpose:
--   Analytical SQL queries and view definitions for clinical process mining KPIs
--   in BigQuery dataset `careflow_opd`.
--
-- Target Dataset:
--   `careflow-clinical-process-m.careflow_opd`
--
-- Underlying Source Views / Tables:
--   - `careflow_opd.stg_hospital_opd` (Staging View)
--   - `careflow_opd.fct_clinical_encounters` (Encounter Fact Table)
--   - `careflow_opd.fct_process_transitions` (Process Transition Fact Table)
--   - `careflow_opd.dim_clinical_providers` (Provider Dimension Table)
-- =============================================================================


-- =============================================================================
-- KPI VIEW 1: Total Patient Encounters & Patient Volume Summary
-- =============================================================================
-- Measures:
--   - Total unique encounters (appointment_id)
--   - Total unique patients (patient_id)
--   - Encounters per patient (re-visit rate)
--   - Service utilization counts (Lab, Imaging, Pharmacy)
-- =============================================================================

CREATE OR REPLACE VIEW `careflow-clinical-process-m.careflow_opd.vw_kpi_total_encounters` AS
SELECT
    COUNT(DISTINCT appointment_id) AS total_encounters,
    COUNT(DISTINCT patient_id) AS total_unique_patients,
    ROUND(COUNT(DISTINCT appointment_id) / COUNT(DISTINCT patient_id), 2) AS encounters_per_patient,
    COUNTIF(has_lab = 1) AS encounters_with_lab,
    ROUND(COUNTIF(has_lab = 1) * 100.0 / COUNT(DISTINCT appointment_id), 2) AS pct_with_lab,
    COUNTIF(has_imaging = 1) AS encounters_with_imaging,
    ROUND(COUNTIF(has_imaging = 1) * 100.0 / COUNT(DISTINCT appointment_id), 2) AS pct_with_imaging,
    COUNTIF(has_pharmacy = 1) AS encounters_with_pharmacy,
    ROUND(COUNTIF(has_pharmacy = 1) * 100.0 / COUNT(DISTINCT appointment_id), 2) AS pct_with_pharmacy,
    SUM(total_records) AS total_source_records
FROM
    `careflow-clinical-process-m.careflow_opd.fct_clinical_encounters`;


-- =============================================================================
-- KPI VIEW 2: Clinical Pathway & Activity Distribution
-- =============================================================================
-- Measures:
--   - Encounter volume across all 7 clinical pathway flows
--   - Proportion of patient traffic traversing each clinical sequence
-- =============================================================================

CREATE OR REPLACE VIEW `careflow-clinical-process-m.careflow_opd.vw_kpi_activity_counts` AS
SELECT
    flow_code,
    flow_name,
    COUNT(DISTINCT appointment_id) AS total_appointments,
    SUM(total_records) AS total_records,
    ROUND(COUNT(DISTINCT appointment_id) * 100.0 / SUM(COUNT(DISTINCT appointment_id)) OVER(), 2) AS pathway_share_pct
FROM
    `careflow-clinical-process-m.careflow_opd.fct_clinical_encounters`
GROUP BY
    flow_code,
    flow_name
ORDER BY
    total_appointments DESC;


-- =============================================================================
-- KPI VIEW 3: Average Stage Waiting Times & Duration Analysis
-- =============================================================================
-- Measures:
--   - Average, minimum, and maximum waiting times between registration and
--     each service department (Consultation, Lab, Imaging, Pharmacy).
--   - Counts of outliers (>480 minutes / 8 hours) and negative inversions.
-- =============================================================================

CREATE OR REPLACE VIEW `careflow-clinical-process-m.careflow_opd.vw_kpi_waiting_times` AS
SELECT
    'Registration to Consultation' AS wait_stage,
    COUNTIF(prescription_start_time IS NOT NULL) AS valid_encounters,
    ROUND(AVG(wait_to_consultation_minutes), 1) AS avg_wait_minutes,
    MIN(wait_to_consultation_minutes) AS min_wait_minutes,
    MAX(wait_to_consultation_minutes) AS max_wait_minutes,
    COUNTIF(wait_to_consultation_minutes > 480) AS outlier_wait_gt_8hr,
    COUNTIF(wait_to_consultation_minutes < 0) AS negative_inversion_count
FROM
    `careflow-clinical-process-m.careflow_opd.fct_clinical_encounters`
WHERE
    prescription_start_time IS NOT NULL

UNION ALL

SELECT
    'Registration to Lab Start',
    COUNTIF(lab_start_time IS NOT NULL),
    ROUND(AVG(wait_to_lab_minutes), 1),
    MIN(wait_to_lab_minutes),
    MAX(wait_to_lab_minutes),
    COUNTIF(wait_to_lab_minutes > 480),
    COUNTIF(wait_to_lab_minutes < 0)
FROM
    `careflow-clinical-process-m.careflow_opd.fct_clinical_encounters`
WHERE
    lab_start_time IS NOT NULL

UNION ALL

SELECT
    'Registration to Imaging Start',
    COUNTIF(imaging_start_time IS NOT NULL),
    ROUND(AVG(wait_to_imaging_minutes), 1),
    MIN(wait_to_imaging_minutes),
    MAX(wait_to_imaging_minutes),
    COUNTIF(wait_to_imaging_minutes > 480),
    COUNTIF(wait_to_imaging_minutes < 0)
FROM
    `careflow-clinical-process-m.careflow_opd.fct_clinical_encounters`
WHERE
    imaging_start_time IS NOT NULL

UNION ALL

SELECT
    'Registration to Pharmacy Start',
    COUNTIF(pharmacy_start_time IS NOT NULL),
    ROUND(AVG(wait_to_pharmacy_minutes), 1),
    MIN(wait_to_pharmacy_minutes),
    MAX(wait_to_pharmacy_minutes),
    COUNTIF(wait_to_pharmacy_minutes > 480),
    COUNTIF(wait_to_pharmacy_minutes < 0)
FROM
    `careflow-clinical-process-m.careflow_opd.fct_clinical_encounters`
WHERE
    pharmacy_start_time IS NOT NULL;


-- =============================================================================
-- KPI VIEW 4: Average Process Cycle Time Across Pathways
-- =============================================================================
-- Measures:
--   - Total elapsed cycle time from initial patient check-in through final
--     service discharge across each clinical pathway.
-- =============================================================================

CREATE OR REPLACE VIEW `careflow-clinical-process-m.careflow_opd.vw_kpi_process_cycle_time` AS
SELECT
    flow_code,
    flow_name,
    COUNT(DISTINCT appointment_id) AS total_encounters,
    ROUND(AVG(total_cycle_time_minutes), 1) AS avg_cycle_time_minutes,
    MIN(total_cycle_time_minutes) AS min_cycle_time_minutes,
    MAX(total_cycle_time_minutes) AS max_cycle_time_minutes,
    COUNTIF(total_cycle_time_minutes > 480) AS cycle_time_gt_8hr,
    COUNTIF(total_cycle_time_minutes <= 120) AS cycle_time_under_2hr
FROM
    `careflow-clinical-process-m.careflow_opd.fct_clinical_encounters`
GROUP BY
    flow_code,
    flow_name
ORDER BY
    flow_code;


-- =============================================================================
-- KPI VIEW 5: Patient Throughput (Temporal Analysis)
-- =============================================================================
-- Measures:
--   - Patient arrival volume aggregated by year, month, day of week, and hour.
--   - Enables identification of peak outpatient arrival windows.
-- =============================================================================

CREATE OR REPLACE VIEW `careflow-clinical-process-m.careflow_opd.vw_kpi_patient_throughput` AS
SELECT
    EXTRACT(YEAR FROM appointment_start_time) AS arrival_year,
    EXTRACT(MONTH FROM appointment_start_time) AS arrival_month,
    EXTRACT(DAYOFWEEK FROM appointment_start_time) AS day_of_week_num,
    CASE EXTRACT(DAYOFWEEK FROM appointment_start_time)
        WHEN 1 THEN 'Sunday'
        WHEN 2 THEN 'Monday'
        WHEN 3 THEN 'Tuesday'
        WHEN 4 THEN 'Wednesday'
        WHEN 5 THEN 'Thursday'
        WHEN 6 THEN 'Friday'
        WHEN 7 THEN 'Saturday'
    END AS day_of_week_name,
    EXTRACT(HOUR FROM appointment_start_time) AS arrival_hour,
    COUNT(DISTINCT appointment_id) AS total_encounter_throughput,
    COUNT(DISTINCT patient_id) AS unique_patient_throughput
FROM
    `careflow-clinical-process-m.careflow_opd.fct_clinical_encounters`
GROUP BY
    1, 2, 3, 4, 5
ORDER BY
    arrival_year,
    arrival_month,
    day_of_week_num,
    arrival_hour;


-- =============================================================================
-- KPI VIEW 6: Transition Durations & Process Bottlenecks
-- =============================================================================
-- Measures:
--   - Transition duration metrics across each specific stage hop in the OPD.
--   - Bottleneck frequency (transitions taking > 120 minutes).
--   - Sequence inversions (transitions with negative durations).
-- =============================================================================

CREATE OR REPLACE VIEW `careflow-clinical-process-m.careflow_opd.vw_kpi_process_bottlenecks` AS
SELECT
    from_stage,
    to_stage,
    COUNT(*) AS total_transitions,
    ROUND(AVG(duration_minutes), 1) AS avg_duration_minutes,
    MIN(duration_minutes) AS min_duration_minutes,
    MAX(duration_minutes) AS max_duration_minutes,
    COUNTIF(is_bottleneck = 1) AS bottleneck_count_gt_2hr,
    ROUND(COUNTIF(is_bottleneck = 1) * 100.0 / COUNT(*), 2) AS bottleneck_rate_pct,
    COUNTIF(is_negative_transition = 1) AS negative_inversion_count
FROM
    `careflow-clinical-process-m.careflow_opd.fct_process_transitions`
GROUP BY
    from_stage,
    to_stage
ORDER BY
    total_transitions DESC;

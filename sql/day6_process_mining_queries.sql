-- =============================================================================
-- CareFlow Clinical Process Mining — Day 6 Process Mining SQL Analysis
-- File: sql/day6_process_mining_queries.sql
-- =============================================================================
-- Purpose:
--   Reusable BigQuery Standard SQL queries for advanced process mining analysis:
--   1. Process Discovery & Directly-Follows Graph (DFG)
--   2. Process Variants Analysis & Trace Extraction
--   3. Bottleneck and Waiting Time Percentile Distribution
--   4. Rework, Self-Loops, and Repeated Cycle Detection
--   5. Process Conformance & Pathway Deviation Analysis
--   6. Executive Process Mining KPIs
--
-- Target Dataset:
--   `careflow-clinical-process-m.careflow_opd`
-- Underlying Tables/Views:
--   - `careflow_opd.fct_process_transitions`
--   - `careflow_opd.fct_clinical_encounters`
--   - `careflow_opd.stg_hospital_opd`
-- =============================================================================


-- =============================================================================
-- 1. PROCESS DISCOVERY: DIRECTLY-FOLLOWS GRAPH (DFG) & EDGE METRICS
-- =============================================================================
-- Computes edge frequency, unique case support, mean and median duration between
-- consecutive clinical stages across all encounters.

SELECT
    from_stage,
    to_stage,
    COUNT(*) AS transition_frequency,
    COUNT(DISTINCT appointment_id) AS unique_case_support,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS transition_share_pct,
    ROUND(AVG(duration_minutes), 1) AS mean_duration_minutes,
    APPROX_QUANTILES(duration_minutes, 100)[OFFSET(50)] AS median_duration_minutes,
    APPROX_QUANTILES(duration_minutes, 100)[OFFSET(90)] AS p90_duration_minutes,
    COUNTIF(duration_minutes < 0) AS negative_inversion_count,
    COUNTIF(is_bottleneck = 1) AS bottleneck_count_gt_2hr
FROM
    `careflow-clinical-process-m.careflow_opd.fct_process_transitions`
GROUP BY
    from_stage,
    to_stage
ORDER BY
    transition_frequency DESC;


-- =============================================================================
-- 2. PROCESS VARIANTS ANALYSIS: CASE TRACE EXTRACTION & PARETO METRICS
-- =============================================================================
-- Aggregates stages chronologically to reconstruct complete case variant traces.

WITH case_traces AS (
    SELECT
        appointment_id,
        STRING_AGG(from_stage, ' -> ' ORDER BY transition_step ASC) AS partial_trace,
        ARRAY_AGG(to_stage ORDER BY transition_step DESC)[OFFSET(0)] AS final_stage,
        MAX(transition_step) AS total_transitions
    FROM
        `careflow-clinical-process-m.careflow_opd.fct_process_transitions`
    GROUP BY
        appointment_id
),
full_traces AS (
    SELECT
        t.appointment_id,
        CONCAT(t.partial_trace, ' -> ', t.final_stage) AS full_variant_trace,
        e.total_cycle_time_minutes,
        e.flow_code,
        e.flow_name
    FROM
        case_traces t
    INNER JOIN
        `careflow-clinical-process-m.careflow_opd.fct_clinical_encounters` e
        ON t.appointment_id = e.appointment_id
)
SELECT
    full_variant_trace,
    COUNT(*) AS case_volume,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS variant_share_pct,
    ROUND(AVG(total_cycle_time_minutes), 1) AS mean_cycle_time_min,
    APPROX_QUANTILES(total_cycle_time_minutes, 100)[OFFSET(50)] AS median_cycle_time_min
FROM
    full_traces
GROUP BY
    full_variant_trace
ORDER BY
    case_volume DESC
LIMIT 20;


-- =============================================================================
-- 3. BOTTLENECK & WAITING TIME DISTRIBUTION (PERCENTILE BREAKDOWN)
-- =============================================================================
-- Identifies departmental handoffs experiencing significant delays.

SELECT
    CONCAT(from_stage, ' -> ', to_stage) AS process_transition,
    COUNT(*) AS total_handoffs,
    ROUND(AVG(duration_minutes), 1) AS mean_duration_min,
    ROUND(AVG(duration_minutes) / 60.0, 2) AS mean_duration_hours,
    APPROX_QUANTILES(duration_minutes, 100)[OFFSET(25)] AS p25_minutes,
    APPROX_QUANTILES(duration_minutes, 100)[OFFSET(50)] AS median_minutes,
    APPROX_QUANTILES(duration_minutes, 100)[OFFSET(75)] AS p75_minutes,
    APPROX_QUANTILES(duration_minutes, 100)[OFFSET(90)] AS p90_minutes,
    APPROX_QUANTILES(duration_minutes, 100)[OFFSET(99)] AS p99_minutes,
    ROUND(COUNTIF(is_bottleneck = 1) * 100.0 / COUNT(*), 2) AS bottleneck_rate_pct
FROM
    `careflow-clinical-process-m.careflow_opd.fct_process_transitions`
GROUP BY
    from_stage,
    to_stage
HAVING
    COUNT(*) >= 100
ORDER BY
    mean_duration_min DESC;


-- =============================================================================
-- 4. REWORK AND REPEATED CLINICAL ORDERS
-- =============================================================================
-- Identifies multi-order diagnostics, repeated consultations, and re-entrant visits.

SELECT
    'Multi-Order Laboratory Tests (>1 test in visit)' AS rework_pattern,
    COUNTIF(total_lab_orders > 1) AS affected_encounters,
    ROUND(COUNTIF(total_lab_orders > 1) * 100.0 / COUNT(*), 2) AS affected_pct
FROM
    `careflow-clinical-process-m.careflow_opd.fct_clinical_encounters`

UNION ALL

SELECT
    'Multi-Order Imaging Procedures (>1 procedure in visit)',
    COUNTIF(total_imaging_orders > 1),
    ROUND(COUNTIF(total_imaging_orders > 1) * 100.0 / COUNT(*), 2)
FROM
    `careflow-clinical-process-m.careflow_opd.fct_clinical_encounters`

UNION ALL

SELECT
    'Multi-Line Pharmacy Sales (>1 medicine dispensed)',
    COUNTIF(total_pharmacy_lines > 1),
    ROUND(COUNTIF(total_pharmacy_lines > 1) * 100.0 / COUNT(*), 2)
FROM
    `careflow-clinical-process-m.careflow_opd.fct_clinical_encounters`

UNION ALL

SELECT
    'Repeated Source Line Records (>1 line per visit)',
    COUNTIF(total_records > 1),
    ROUND(COUNTIF(total_records > 1) * 100.0 / COUNT(*), 2)
FROM
    `careflow-clinical-process-m.careflow_opd.fct_clinical_encounters`;


-- =============================================================================
-- 5. PROCESS CONFORMANCE: PATHWAY DEVIATIONS & INVERSIONS
-- =============================================================================
-- Flags encounters deviating from canonical clinical sequence (e.g. out-of-order diagnostics).

SELECT
    e.flow_code,
    e.flow_name,
    COUNT(*) AS total_encounters,
    COUNTIF(e.has_timestamp_inversion = 1) AS non_conforming_inversions,
    ROUND(COUNTIF(e.has_timestamp_inversion = 1) * 100.0 / COUNT(*), 2) AS inversion_rate_pct,
    COUNTIF(e.is_outlier_wait = 1) AS outlier_wait_gt_8hr,
    ROUND(COUNTIF(e.is_outlier_wait = 1) * 100.0 / COUNT(*), 2) AS outlier_rate_pct,
    ROUND(AVG(e.total_cycle_time_minutes), 1) AS mean_cycle_time_min
FROM
    `careflow-clinical-process-m.careflow_opd.fct_clinical_encounters` e
GROUP BY
    e.flow_code,
    e.flow_name
ORDER BY
    total_encounters DESC;


-- =============================================================================
-- 6. EXECUTIVE PROCESS MINING KPI SCORECARD
-- =============================================================================

SELECT
    COUNT(DISTINCT e.appointment_id) AS total_encounters,
    COUNT(DISTINCT e.patient_id) AS total_unique_patients,
    ROUND(AVG(e.total_cycle_time_minutes), 1) AS mean_cycle_time_min,
    APPROX_QUANTILES(e.total_cycle_time_minutes, 100)[OFFSET(50)] AS median_cycle_time_min,
    ROUND(AVG(e.wait_to_consultation_minutes), 1) AS mean_wait_to_doctor_min,
    APPROX_QUANTILES(e.wait_to_consultation_minutes, 100)[OFFSET(50)] AS median_wait_to_doctor_min,
    ROUND(AVG(e.consultation_duration_minutes), 1) AS mean_consultation_duration_min,
    ROUND(AVG(e.lab_duration_minutes), 1) AS mean_lab_turnaround_min,
    ROUND(AVG(e.imaging_duration_minutes), 1) AS mean_imaging_duration_min,
    COUNTIF(e.has_timestamp_inversion = 1) AS total_inversion_cases,
    ROUND(COUNTIF(e.has_timestamp_inversion = 1) * 100.0 / COUNT(*), 2) AS inversion_case_rate_pct
FROM
    `careflow-clinical-process-m.careflow_opd.fct_clinical_encounters` e;

-- Fact model for Clinical Encounters (Outpatient Visits)
-- Grain: One row per unique outpatient visit (appointment_id)

with source as (
    select * from {{ ref('stg_hospital_opd') }}
),

encounter_agg as (
    select
        appointment_id,
        min(patient_id) as patient_id,
        
        -- Primary clinician mapping (guarantees paired doctor ID and name)
        array_agg(prescription_doctor_id order by record_no asc)[offset(0)] as doctor_id,
        array_agg(prescription_doctor_name order by record_no asc)[offset(0)] as doctor_name,
        
        -- Encounter timestamps
        min(appointment_start_time) as appointment_start_time,
        min(prescription_start_time) as prescription_start_time,
        max(prescription_end_time) as prescription_end_time,
        min(lab_start_time) as lab_start_time,
        max(lab_end_time) as lab_end_time,
        min(imaging_start_time) as imaging_start_time,
        max(imaging_end_time) as imaging_end_time,
        min(pharmacy_start_time) as pharmacy_start_time,
        max(pharmacy_end_time) as pharmacy_end_time,
        
        -- Pathway flow attributes (paired to maximum pathway reach)
        max(flow_code) as flow_code,
        array_agg(flow_name order by flow_code desc, record_no asc)[offset(0)] as flow_name,
        count(*) as total_records,
        
        -- Service utilization flags and counts
        max(case when lab_id is not null then 1 else 0 end) as has_lab,
        max(case when imaging_request_id is not null then 1 else 0 end) as has_imaging,
        max(case when pharmacy_sale_line_id is not null then 1 else 0 end) as has_pharmacy,
        count(distinct lab_id) as total_lab_orders,
        count(distinct imaging_request_id) as total_imaging_orders,
        count(distinct pharmacy_sale_line_id) as total_pharmacy_lines

    from source
    group by appointment_id
),

encounter_metrics as (
    select
        appointment_id,
        patient_id,
        doctor_id,
        doctor_name,
        appointment_start_time,
        prescription_start_time,
        prescription_end_time,
        lab_start_time,
        lab_end_time,
        imaging_start_time,
        imaging_end_time,
        pharmacy_start_time,
        pharmacy_end_time,
        flow_code,
        flow_name,
        total_records,
        has_lab,
        has_imaging,
        has_pharmacy,
        total_lab_orders,
        total_imaging_orders,
        total_pharmacy_lines,

        -- Stage Waiting Times (minutes from registration)
        timestamp_diff(prescription_start_time, appointment_start_time, minute) as wait_to_consultation_minutes,
        timestamp_diff(prescription_end_time, prescription_start_time, minute) as consultation_duration_minutes,
        timestamp_diff(lab_start_time, appointment_start_time, minute) as wait_to_lab_minutes,
        timestamp_diff(lab_end_time, lab_start_time, minute) as lab_duration_minutes,
        timestamp_diff(imaging_start_time, appointment_start_time, minute) as wait_to_imaging_minutes,
        timestamp_diff(imaging_end_time, imaging_start_time, minute) as imaging_duration_minutes,
        timestamp_diff(pharmacy_start_time, appointment_start_time, minute) as wait_to_pharmacy_minutes,
        timestamp_diff(pharmacy_end_time, pharmacy_start_time, minute) as pharmacy_duration_minutes,

        -- Total Encounter Process Cycle Time (minutes from registration to latest activity completion)
        timestamp_diff(
            greatest(
                coalesce(prescription_end_time, appointment_start_time),
                coalesce(lab_end_time, appointment_start_time),
                coalesce(imaging_end_time, appointment_start_time),
                coalesce(pharmacy_end_time, appointment_start_time)
            ),
            appointment_start_time,
            minute
        ) as total_cycle_time_minutes,

        -- Empirical Data Quality & Outlier Flags
        case 
            when prescription_start_time < appointment_start_time
                 or lab_start_time < appointment_start_time
                 or imaging_start_time < appointment_start_time
                 or prescription_end_time < prescription_start_time
            then 1 else 0 
        end as has_timestamp_inversion,
        
        case 
            when timestamp_diff(prescription_start_time, appointment_start_time, minute) > 480 
            then 1 else 0 
        end as is_outlier_wait

    from encounter_agg
)

select * from encounter_metrics

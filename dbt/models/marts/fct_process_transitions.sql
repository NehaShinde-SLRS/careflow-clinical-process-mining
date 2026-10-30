-- Fact model for Clinical Process Transitions
-- Grain: One row per sequential stage-to-stage transition within an encounter
-- Logic: Sequences stages by canonical clinical pathway order (stage_order asc) to accurately
--        detect process inversions and negative durations (e.g. Lab started before Registration).

with source as (
    select * from {{ ref('stg_hospital_opd') }}
),

-- Aggregate encounter-level milestone timestamps
encounter_milestones as (
    select
        appointment_id,
        min(patient_id) as patient_id,
        min(appointment_start_time) as registration_time,
        min(prescription_start_time) as consultation_start_time,
        max(prescription_end_time) as consultation_end_time,
        min(lab_start_time) as lab_start_time,
        max(lab_end_time) as lab_end_time,
        min(imaging_start_time) as imaging_start_time,
        max(imaging_end_time) as imaging_end_time,
        min(pharmacy_start_time) as pharmacy_start_time,
        max(pharmacy_end_time) as pharmacy_end_time
    from source
    group by appointment_id
),

-- Unpivot non-null milestones with canonical clinical stage ordering
milestone_events as (
    select appointment_id, patient_id, 'Registration' as stage_name, 1 as stage_order, registration_time as stage_time from encounter_milestones where registration_time is not null
    union all
    select appointment_id, patient_id, 'Consultation Start', 2, consultation_start_time from encounter_milestones where consultation_start_time is not null
    union all
    select appointment_id, patient_id, 'Consultation Complete', 3, consultation_end_time from encounter_milestones where consultation_end_time is not null
    union all
    select appointment_id, patient_id, 'Lab Start', 4, lab_start_time from encounter_milestones where lab_start_time is not null
    union all
    select appointment_id, patient_id, 'Lab Complete', 5, lab_end_time from encounter_milestones where lab_end_time is not null
    union all
    select appointment_id, patient_id, 'Imaging Start', 6, imaging_start_time from encounter_milestones where imaging_start_time is not null
    union all
    select appointment_id, patient_id, 'Imaging Complete', 7, imaging_end_time from encounter_milestones where imaging_end_time is not null
    union all
    select appointment_id, patient_id, 'Pharmacy Start', 8, pharmacy_start_time from encounter_milestones where pharmacy_start_time is not null
    union all
    select appointment_id, patient_id, 'Pharmacy Complete', 9, pharmacy_end_time from encounter_milestones where pharmacy_end_time is not null
),

-- Sequence based on canonical clinical pathway stage order
ordered_stages as (
    select
        appointment_id,
        patient_id,
        stage_name,
        stage_time,
        stage_order,
        row_number() over (
            partition by appointment_id 
            order by stage_order asc
        ) as stage_seq
    from milestone_events
),

-- Pair sequential stages to calculate transition duration and detect inversions
transitions as (
    select
        concat(cast(s1.appointment_id as string), '_step_', cast(s1.stage_seq as string)) as transition_id,
        s1.appointment_id,
        s1.patient_id,
        s1.stage_seq as transition_step,
        s1.stage_name as from_stage,
        s1.stage_time as from_timestamp,
        s2.stage_name as to_stage,
        s2.stage_time as to_timestamp,
        timestamp_diff(s2.stage_time, s1.stage_time, minute) as duration_minutes,
        case when s2.stage_time < s1.stage_time then 1 else 0 end as is_negative_transition,
        case when timestamp_diff(s2.stage_time, s1.stage_time, minute) > 120 then 1 else 0 end as is_bottleneck
    from ordered_stages s1
    inner join ordered_stages s2
        on s1.appointment_id = s2.appointment_id
        and s2.stage_seq = s1.stage_seq + 1
)

select * from transitions

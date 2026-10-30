-- Dimension model for Clinical Providers (Attending Doctors)
-- Grain: One row per unique doctor (prescription_doctor_id)

with source as (
    select * from {{ ref('stg_hospital_opd') }}
),

provider_summary as (
    select
        prescription_doctor_id as doctor_id,
        prescription_doctor_name as doctor_name,
        count(distinct appointment_id) as total_appointments,
        count(*) as total_encounter_records,
        count(distinct patient_id) as total_patients_treated,
        min(prescription_start_time) as first_consultation_time,
        max(prescription_start_time) as last_consultation_time,
        round(avg(case 
            when prescription_start_time is not null 
                 and prescription_end_time is not null 
                 and prescription_end_time >= prescription_start_time
            then timestamp_diff(prescription_end_time, prescription_start_time, minute)
            else null
        end), 2) as avg_consultation_duration_minutes
    from source
    where prescription_doctor_id is not null
    group by prescription_doctor_id, prescription_doctor_name
)

select * from provider_summary

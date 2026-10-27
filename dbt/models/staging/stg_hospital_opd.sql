-- Staging model for Hospital OPD encounters
-- Standardizes types and provides clean baseline table for process mining analytics

with source as (
    select * from {{ source('careflow_raw', 'hospital_opd_cleaned') }}
),

renamed as (
    select
        cast(record_no as int64) as record_no,
        cast(patient_id as int64) as patient_id,
        cast(appointment_id as int64) as appointment_id,
        cast(appointment_start_datetime as timestamp) as appointment_start_time,
        
        -- Prescription consultation
        cast(prescription_doctor_id as int64) as prescription_doctor_id,
        cast(prescription_doctor_name as string) as prescription_doctor_name,
        cast(prescription_order_id as int64) as prescription_order_id,
        cast(prescription_start_datetime as timestamp) as prescription_start_time,
        cast(prescription_end_datetime as timestamp) as prescription_end_time,
        
        -- Laboratory
        cast(lab_id as int64) as lab_id,
        cast(lab_name as string) as lab_name,
        cast(lab_start_datetime as timestamp) as lab_start_time,
        cast(lab_end_datetime as timestamp) as lab_end_time,
        
        -- Imaging
        cast(imaging_request_id as int64) as imaging_request_id,
        cast(imaging_result_id as int64) as imaging_result_id,
        cast(imaging_name as string) as imaging_name,
        cast(imaging_start_datetime as timestamp) as imaging_start_time,
        cast(imaging_end_datetime as timestamp) as imaging_end_time,
        
        -- Pharmacy
        cast(pharmacy_sale_line_id as int64) as pharmacy_sale_line_id,
        cast(medicine_name as string) as medicine_name,
        cast(pharmacy_start_datetime as timestamp) as pharmacy_start_time,
        cast(pharmacy_end_datetime as timestamp) as pharmacy_end_time,
        
        -- Flow attributes
        cast(flow_code as int64) as flow_code,
        cast(flow_name as string) as flow_name

    from source
)

select * from renamed

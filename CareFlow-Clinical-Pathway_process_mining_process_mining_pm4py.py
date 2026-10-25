"""
CareFlow: Clinical Pathway Process Mining
Member 4 Deliverable: PM4Py Discovery, Event Log Transformation & Bottleneck Analysis
Branch: member4-process-dashboard
"""

import pandas as pd
import numpy as np

def create_event_log(csv_path='data/cleaned_HospitalOPD.csv'):
    """
    Transforms wide-format hospital outpatient records into a long-format event log
    conforming to PM4Py standards (case:concept:name, concept:name, time:timestamp, org:resource).
    """
    df = pd.read_csv(csv_path)
    
    events = []
    
    # 1. Registration / Check-in
    e1 = df[['appointment_id', 'patient_id', 'appointment_start_datetime', 'flow_name']].copy()
    e1['activity'] = 'Appointment Check-in'
    e1['resource'] = 'Front Desk'
    e1['timestamp'] = e1['appointment_start_datetime']
    events.append(e1[['appointment_id', 'patient_id', 'activity', 'timestamp', 'resource', 'flow_name']])
    
    # 2. Doctor Consultation
    e2 = df[['appointment_id', 'patient_id', 'prescription_start_datetime', 'prescription_doctor_name', 'flow_name']].copy()
    e2['activity'] = 'Doctor Consultation'
    e2['resource'] = e2['prescription_doctor_name']
    e2['timestamp'] = e2['prescription_start_datetime']
    events.append(e2[['appointment_id', 'patient_id', 'activity', 'timestamp', 'resource', 'flow_name']].dropna(subset=['timestamp']))
    
    # 3. Prescription Finalized
    e3 = df[['appointment_id', 'patient_id', 'prescription_end_datetime', 'prescription_doctor_name', 'flow_name']].copy()
    e3['activity'] = 'Prescription Finalized'
    e3['resource'] = e3['prescription_doctor_name']
    e3['timestamp'] = e3['prescription_end_datetime']
    events.append(e3[['appointment_id', 'patient_id', 'activity', 'timestamp', 'resource', 'flow_name']].dropna(subset=['timestamp']))
    
    # 4. Lab Tests
    df_lab = df[df['lab_name'].notnull()].copy()
    e4 = df_lab[['appointment_id', 'patient_id', 'lab_start_datetime', 'lab_name', 'flow_name']].copy()
    e4['activity'] = 'Lab - ' + e4['lab_name'].astype(str)
    e4['resource'] = 'Pathology Department'
    e4['timestamp'] = e4['lab_start_datetime']
    events.append(e4[['appointment_id', 'patient_id', 'activity', 'timestamp', 'resource', 'flow_name']].dropna(subset=['timestamp']))
    
    # 5. Radiology / Imaging
    df_img = df[df['imaging_name'].notnull()].copy()
    e5 = df_img[['appointment_id', 'patient_id', 'imaging_start_datetime', 'imaging_name', 'flow_name']].copy()
    e5['activity'] = 'Imaging - ' + e5['imaging_name'].astype(str)
    e5['resource'] = 'Radiology Department'
    e5['timestamp'] = e5['imaging_start_datetime']
    events.append(e5[['appointment_id', 'patient_id', 'activity', 'timestamp', 'resource', 'flow_name']].dropna(subset=['timestamp']))
    
    # 6. In-house Pharmacy Dispensing
    df_pharm = df[df['medicine_name'].notnull()].copy()
    e6 = df_pharm[['appointment_id', 'patient_id', 'pharmacy_start_datetime', 'medicine_name', 'flow_name']].copy()
    e6['activity'] = 'Pharmacy - ' + e6['medicine_name'].astype(str)
    e6['resource'] = 'Hospital Pharmacy'
    e6['timestamp'] = e6['pharmacy_start_datetime']
    events.append(e6[['appointment_id', 'patient_id', 'activity', 'timestamp', 'resource', 'flow_name']].dropna(subset=['timestamp']))
    
    event_log = pd.concat(events, ignore_index=True)
    event_log['timestamp'] = pd.to_datetime(event_log['timestamp'])
    event_log = event_log.sort_values(by=['appointment_id', 'timestamp']).reset_index(drop=True)
    
    # Rename to PM4Py standard naming conventions
    event_log.rename(columns={
        'appointment_id': 'case:concept:name',
        'activity': 'concept:name',
        'timestamp': 'time:timestamp',
        'resource': 'org:resource'
    }, inplace=True)
    
    print(f"PM4Py Event Log Generated: {len(event_log):,} events across {event_log['case:concept:name'].nunique():,} cases.")
    return event_log

def run_process_mining(event_log):
    """
    Analyzes pathway variants and transition frequencies.
    """
    try:
        import pm4py
        from pm4py.algo.filtering.log.variants import variants_filter
        
        # Discover Directly-Follows Graph (DFG)
        dfg, start_activities, end_activities = pm4py.discover_dfg(event_log)
        print("Discovered Directly-Follows Graph (DFG) transitions.")
        print(f"Start Activities: {start_activities}")
        print(f"End Activities: {end_activities}")
        
        # Get Variants / Common Paths
        variants = pm4py.get_variants(event_log)
        print(f"Total Unique Process Pathways Discovered: {len(variants):,}")
        
    except ImportError:
        print("PM4Py is not installed in the current environment. To install: pip install pm4py")

if __name__ == '__main__':
    log = create_event_log('data/cleaned_HospitalOPD.csv')
    log.to_csv('data/pm4py_hospital_event_log.csv', index=False)
    print("Saved normalized event log to data/pm4py_hospital_event_log.csv")
    run_process_mining(log)

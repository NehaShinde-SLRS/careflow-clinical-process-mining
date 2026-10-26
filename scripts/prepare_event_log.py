"""
CareFlow Clinical Process Mining — Day 6
Script: prepare_event_log.py

Purpose:
    Transforms the wide HospitalOPD dataset into a clean, chronologically
    ordered event log suitable for clinical process mining (e.g. PM4Py, ProM,
    Celonis, Disco).

Event Log Standard Format:
    - case_id: Appointment identifier (primary process instance / encounter level)
    - patient_id: Patient identifier (enables patient longitudinal journey analysis)
    - activity: Consistent, descriptive clinical activity name
    - activity_category: Registration, Consultation, Laboratory, Imaging, Pharmacy
    - lifecycle: 'start' or 'complete'
    - timestamp: Valid ISO-8601 formatted datetime string
    - resource: Doctor name or servicing department
    - service_id: Order or service key (prescription_order_id, lab_id, etc.)
    - service_name: Specific test/medication name (lab_name, imaging_name, medicine_name)
    - flow_code: Encounter pathway code (1-7)
    - flow_name: Encounter pathway label
    - source_record_no: Traceability link to original dataset row
    - timestamp_anomaly_flag: Flagged if event occurs prior to appointment registration

Safety & Quality Rules:
    - The original CSV (data/HospitalOPD_cleaned.csv) is never modified.
    - No timestamps are invented or imputed.
    - Events without valid timestamps are safely excluded and transparently logged.
    - Events within each case are sorted chronologically by timestamp, with stable
      ordering for concurrent timestamps (registration -> start -> complete).
    - Source record traceability is preserved.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# Reconfigure stdout/stderr for UTF-8 in Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_CSV = PROJECT_ROOT / "data" / "HospitalOPD_cleaned.csv"
OUTPUT_CSV = PROJECT_ROOT / "data" / "careflow_event_log.csv"

SEPARATOR = "=" * 72


def section(title: str) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        print(f"[ERROR] Input CSV not found: {path}")
        sys.exit(1)
    print(f"  Loading input dataset: {path}")
    df = pd.read_csv(path, low_memory=False, encoding='utf-8')
    print(f"  Loaded {len(df):,} records, {len(df.columns)} columns.")
    return df


def build_event_log(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms the wide table into an event-level dataframe.
    """
    section("Building Event Log from Encounter Records")
    
    events = []
    skipped_events_missing_ts = 0

    # 1. Appointment Registration Events
    # Distinct per appointment_id + appointment_start_datetime
    appts = df[['record_no', 'appointment_id', 'patient_id', 'appointment_start_datetime', 'flow_code', 'flow_name']].drop_duplicates(subset=['appointment_id', 'appointment_start_datetime'])
    for _, r in appts.iterrows():
        events.append({
            'case_id': r['appointment_id'],
            'patient_id': r['patient_id'],
            'activity': 'Appointment Registration',
            'activity_category': 'Registration',
            'lifecycle': 'complete',
            'timestamp': r['appointment_start_datetime'],
            'resource': 'Reception / OPD Clinic',
            'service_id': str(r['appointment_id']),
            'service_name': 'OPD Registration',
            'flow_code': r['flow_code'],
            'flow_name': r['flow_name'],
            'source_record_no': r['record_no'],
            'appt_time': r['appointment_start_datetime']
        })

    # 2. Prescription Consultation Events (Start & Complete)
    rx_cols = ['record_no', 'appointment_id', 'patient_id', 'appointment_start_datetime',
               'prescription_order_id', 'prescription_doctor_id', 'prescription_doctor_name',
               'prescription_start_datetime', 'prescription_end_datetime', 'flow_code', 'flow_name']
    rx_df = df[rx_cols].drop_duplicates(subset=['appointment_id', 'prescription_order_id', 'prescription_start_datetime', 'prescription_end_datetime'])
    
    for _, r in rx_df.iterrows():
        # Consultation Start
        if pd.notnull(r['prescription_start_datetime']) and str(r['prescription_start_datetime']).strip() != '':
            events.append({
                'case_id': r['appointment_id'],
                'patient_id': r['patient_id'],
                'activity': 'Prescription Consultation Started',
                'activity_category': 'Consultation',
                'lifecycle': 'start',
                'timestamp': str(r['prescription_start_datetime']).strip(),
                'resource': str(r['prescription_doctor_name']) if pd.notnull(r['prescription_doctor_name']) else 'Doctor',
                'service_id': str(r['prescription_order_id']) if pd.notnull(r['prescription_order_id']) else '',
                'service_name': 'Prescription Order',
                'flow_code': r['flow_code'],
                'flow_name': r['flow_name'],
                'source_record_no': r['record_no'],
                'appt_time': r['appointment_start_datetime']
            })
        else:
            skipped_events_missing_ts += 1

        # Consultation Complete
        if pd.notnull(r['prescription_end_datetime']) and str(r['prescription_end_datetime']).strip() != '':
            events.append({
                'case_id': r['appointment_id'],
                'patient_id': r['patient_id'],
                'activity': 'Prescription Consultation Completed',
                'activity_category': 'Consultation',
                'lifecycle': 'complete',
                'timestamp': str(r['prescription_end_datetime']).strip(),
                'resource': str(r['prescription_doctor_name']) if pd.notnull(r['prescription_doctor_name']) else 'Doctor',
                'service_id': str(r['prescription_order_id']) if pd.notnull(r['prescription_order_id']) else '',
                'service_name': 'Prescription Order',
                'flow_code': r['flow_code'],
                'flow_name': r['flow_name'],
                'source_record_no': r['record_no'],
                'appt_time': r['appointment_start_datetime']
            })
        else:
            skipped_events_missing_ts += 1

    # 3. Laboratory Events (Start & Complete)
    lab_cols = ['record_no', 'appointment_id', 'patient_id', 'appointment_start_datetime',
                'lab_id', 'lab_name', 'lab_start_datetime', 'lab_end_datetime', 'flow_code', 'flow_name']
    lab_df = df[df['lab_id'].notnull()][lab_cols].drop_duplicates(subset=['appointment_id', 'lab_id', 'lab_start_datetime', 'lab_end_datetime'])
    
    for _, r in lab_df.iterrows():
        # Lab Test Start
        if pd.notnull(r['lab_start_datetime']) and str(r['lab_start_datetime']).strip() != '':
            events.append({
                'case_id': r['appointment_id'],
                'patient_id': r['patient_id'],
                'activity': 'Lab Test Started',
                'activity_category': 'Laboratory',
                'lifecycle': 'start',
                'timestamp': str(r['lab_start_datetime']).strip(),
                'resource': 'Laboratory Department',
                'service_id': str(r['lab_id']),
                'service_name': str(r['lab_name']) if pd.notnull(r['lab_name']) else 'Lab Test',
                'flow_code': r['flow_code'],
                'flow_name': r['flow_name'],
                'source_record_no': r['record_no'],
                'appt_time': r['appointment_start_datetime']
            })
        else:
            skipped_events_missing_ts += 1

        # Lab Test Complete
        if pd.notnull(r['lab_end_datetime']) and str(r['lab_end_datetime']).strip() != '':
            events.append({
                'case_id': r['appointment_id'],
                'patient_id': r['patient_id'],
                'activity': 'Lab Test Completed',
                'activity_category': 'Laboratory',
                'lifecycle': 'complete',
                'timestamp': str(r['lab_end_datetime']).strip(),
                'resource': 'Laboratory Department',
                'service_id': str(r['lab_id']),
                'service_name': str(r['lab_name']) if pd.notnull(r['lab_name']) else 'Lab Test',
                'flow_code': r['flow_code'],
                'flow_name': r['flow_name'],
                'source_record_no': r['record_no'],
                'appt_time': r['appointment_start_datetime']
            })
        else:
            skipped_events_missing_ts += 1

    # 4. Imaging Events (Start & Complete)
    img_cols = ['record_no', 'appointment_id', 'patient_id', 'appointment_start_datetime',
                'imaging_request_id', 'imaging_name', 'imaging_start_datetime', 'imaging_end_datetime', 'flow_code', 'flow_name']
    img_df = df[df['imaging_request_id'].notnull()][img_cols].drop_duplicates(subset=['appointment_id', 'imaging_request_id', 'imaging_start_datetime', 'imaging_end_datetime'])
    
    for _, r in img_df.iterrows():
        # Imaging Start
        if pd.notnull(r['imaging_start_datetime']) and str(r['imaging_start_datetime']).strip() != '':
            events.append({
                'case_id': r['appointment_id'],
                'patient_id': r['patient_id'],
                'activity': 'Imaging Started',
                'activity_category': 'Imaging',
                'lifecycle': 'start',
                'timestamp': str(r['imaging_start_datetime']).strip(),
                'resource': 'Radiology / Imaging Department',
                'service_id': str(r['imaging_request_id']),
                'service_name': str(r['imaging_name']) if pd.notnull(r['imaging_name']) else 'Imaging Scan',
                'flow_code': r['flow_code'],
                'flow_name': r['flow_name'],
                'source_record_no': r['record_no'],
                'appt_time': r['appointment_start_datetime']
            })
        else:
            skipped_events_missing_ts += 1

        # Imaging Complete
        if pd.notnull(r['imaging_end_datetime']) and str(r['imaging_end_datetime']).strip() != '':
            events.append({
                'case_id': r['appointment_id'],
                'patient_id': r['patient_id'],
                'activity': 'Imaging Completed',
                'activity_category': 'Imaging',
                'lifecycle': 'complete',
                'timestamp': str(r['imaging_end_datetime']).strip(),
                'resource': 'Radiology / Imaging Department',
                'service_id': str(r['imaging_request_id']),
                'service_name': str(r['imaging_name']) if pd.notnull(r['imaging_name']) else 'Imaging Scan',
                'flow_code': r['flow_code'],
                'flow_name': r['flow_name'],
                'source_record_no': r['record_no'],
                'appt_time': r['appointment_start_datetime']
            })
        else:
            skipped_events_missing_ts += 1

    # 5. Pharmacy Events (Start & Complete)
    ph_cols = ['record_no', 'appointment_id', 'patient_id', 'appointment_start_datetime',
               'pharmacy_sale_line_id', 'medicine_name', 'pharmacy_start_datetime', 'pharmacy_end_datetime', 'flow_code', 'flow_name']
    ph_df = df[df['pharmacy_sale_line_id'].notnull()][ph_cols].drop_duplicates(subset=['appointment_id', 'pharmacy_sale_line_id', 'pharmacy_start_datetime', 'pharmacy_end_datetime'])
    
    for _, r in ph_df.iterrows():
        # Pharmacy Dispensation Start
        if pd.notnull(r['pharmacy_start_datetime']) and str(r['pharmacy_start_datetime']).strip() != '':
            events.append({
                'case_id': r['appointment_id'],
                'patient_id': r['patient_id'],
                'activity': 'Pharmacy Dispensation Started',
                'activity_category': 'Pharmacy',
                'lifecycle': 'start',
                'timestamp': str(r['pharmacy_start_datetime']).strip(),
                'resource': 'OPD Pharmacy',
                'service_id': str(r['pharmacy_sale_line_id']),
                'service_name': str(r['medicine_name']) if pd.notnull(r['medicine_name']) else 'Medication Dispensation',
                'flow_code': r['flow_code'],
                'flow_name': r['flow_name'],
                'source_record_no': r['record_no'],
                'appt_time': r['appointment_start_datetime']
            })
        else:
            skipped_events_missing_ts += 1

        # Pharmacy Dispensation Complete
        if pd.notnull(r['pharmacy_end_datetime']) and str(r['pharmacy_end_datetime']).strip() != '':
            events.append({
                'case_id': r['appointment_id'],
                'patient_id': r['patient_id'],
                'activity': 'Pharmacy Dispensation Completed',
                'activity_category': 'Pharmacy',
                'lifecycle': 'complete',
                'timestamp': str(r['pharmacy_end_datetime']).strip(),
                'resource': 'OPD Pharmacy',
                'service_id': str(r['pharmacy_sale_line_id']),
                'service_name': str(r['medicine_name']) if pd.notnull(r['medicine_name']) else 'Medication Dispensation',
                'flow_code': r['flow_code'],
                'flow_name': r['flow_name'],
                'source_record_no': r['record_no'],
                'appt_time': r['appointment_start_datetime']
            })
        else:
            skipped_events_missing_ts += 1

    event_df = pd.DataFrame(events)
    print(f"  Generated {len(event_df):,} event instances.")
    print(f"  Safely excluded {skipped_events_missing_ts:,} potential sub-events lacking valid timestamps.")
    
    # Anomaly flag: timestamp prior to appointment registration
    event_df['dt_timestamp'] = pd.to_datetime(event_df['timestamp'])
    event_df['dt_appt'] = pd.to_datetime(event_df['appt_time'])
    event_df['timestamp_anomaly_flag'] = event_df['dt_timestamp'] < event_df['dt_appt']

    # Sort order definition for concurrent timestamps
    lifecycle_rank = {'complete': 2, 'start': 1}
    category_rank = {
        'Registration': 1,
        'Consultation': 2,
        'Laboratory': 3,
        'Imaging': 4,
        'Pharmacy': 5
    }
    event_df['lifecycle_order'] = event_df['lifecycle'].map(lifecycle_rank).fillna(0)
    event_df['category_order'] = event_df['activity_category'].map(category_rank).fillna(9)

    # Chronological sort within each case
    event_df = event_df.sort_values(
        by=['case_id', 'dt_timestamp', 'category_order', 'lifecycle_order', 'source_record_no']
    ).reset_index(drop=True)

    # Event sequence index within case
    event_df['event_order'] = event_df.groupby('case_id').cumcount() + 1

    # Clean up auxiliary columns
    drop_cols = ['dt_timestamp', 'dt_appt', 'appt_time', 'lifecycle_order', 'category_order']
    event_df = event_df.drop(columns=drop_cols)

    return event_df


def verify_event_log(df: pd.DataFrame) -> None:
    section("Event Log Verification")
    
    total_events = len(df)
    unique_cases = df['case_id'].nunique()
    unique_patients = df['patient_id'].nunique()
    
    print(f"  Total event rows        : {total_events:,}")
    print(f"  Distinct cases (Appts)  : {unique_cases:,}")
    print(f"  Distinct patients       : {unique_patients:,}")
    print(f"  Average events per case : {total_events / unique_cases:.2f}")
    
    # Check nulls
    null_cases = df['case_id'].isnull().sum()
    null_activities = df['activity'].isnull().sum()
    null_ts = df['timestamp'].isnull().sum()
    print(f"  Null case IDs           : {null_cases} {'[OK]' if null_cases == 0 else '[FAIL]'}")
    print(f"  Null activities         : {null_activities} {'[OK]' if null_activities == 0 else '[FAIL]'}")
    print(f"  Null timestamps         : {null_ts} {'[OK]' if null_ts == 0 else '[FAIL]'}")
    
    # Activities summary
    print("\n  Event breakdown by Activity:")
    act_counts = df['activity'].value_counts()
    for act, cnt in act_counts.items():
        print(f"    - {act:<38}: {cnt:>7,} ({cnt/total_events*100:>5.2f}%)")

    # Anomaly summary
    anomalies = df['timestamp_anomaly_flag'].sum()
    print(f"\n  Timestamp sequence anomalies (pre-registration): {anomalies:,} ({anomalies/total_events*100:.2f}%)")


def export_event_log(df: pd.DataFrame, target_path: Path) -> None:
    section(f"Exporting Event Log to CSV")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(target_path, index=False, encoding='utf-8')
    size_mb = target_path.stat().st_size / (1024 * 1024)
    print(f"  Saved: {target_path}")
    print(f"  File size: {target_path.stat().st_size:,} bytes ({size_mb:.2f} MB)")
    print(f"  Total exported rows: {len(df):,}")


def main():
    section("CareFlow Clinical Process Mining — Day 6 Event Log Preparation")
    source_df = load_dataset(INPUT_CSV)
    event_log_df = build_event_log(source_df)
    verify_event_log(event_log_df)
    export_event_log(event_log_df, OUTPUT_CSV)
    print(f"\n  [SUCCESS] Day 6 Event Log Preparation Completed successfully.")


if __name__ == '__main__':
    main()

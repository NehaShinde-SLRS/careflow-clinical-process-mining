# HospitalOPD Dataset Quality Findings

## 1. Dataset Overview

- Total records: 62,422
- Unique patients: 39,442
- Unique appointments: 49,912
- Patients with multiple appointments: 7,120
- Appointments linked to multiple patients: 0

## 2. Timestamp Quality

| Activity | Valid timestamps | Missing or invalid |
|---|---:|---:|
| Appointment | 62,422 | 0 |
| Prescription | 62,410 | 12 |
| Lab | 18,029 | 44,393 |
| Imaging | 5,523 | 56,899 |
| Pharmacy | 302 | 62,120 |

## 3. Event ID Quality

| Activity | Available IDs | Unique IDs | Missing IDs |
|---|---:|---:|---:|
| Prescription | 62,422 | 50,568 | 0 |
| Lab | 18,029 | 17,083 | 44,393 |
| Imaging | 5,523 | 5,360 | 56,899 |
| Pharmacy | 302 | 262 | 62,120 |

## 4. Duplicate Record Check

- Exact duplicate rows: 0
- Duplicate record numbers: 0
- Duplicate appointment IDs: 12,510

Repeated appointment IDs do not automatically indicate duplicate events.

## 5. Next Steps

1. Investigate the 12 missing prescription timestamps.
2. Validate links between appointments and clinical activities.
3. Confirm the event-log mapping before process mining.
4. Prepare a reliable event log for the project team.

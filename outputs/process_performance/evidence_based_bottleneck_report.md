# CareFlow Outpatient Process Performance & Bottleneck Analysis Report

**Generated:** 5 November 2026 | **Cohort:** 49,912 Outpatient Encounters

## 1. Executive Performance Highlights

- **Mean Patient Journey Duration:** **294.7 minutes (4.91 hours)** (Median: 39.0 min; P90: 198.0 min / 3.30 hrs).
- **Active Service vs Passive Queue:** Active clinical service accounts for only **111.6 minutes** (16.07% Process Cycle Efficiency), meaning patients spend **184.0 minutes** passively waiting.
- **Primary System Bottleneck:** **Clinical Laboratory Turnaround Time (TAT)** averages **279.3 minutes (4.65 hours)**; **62.96% of all lab orders exceed 2 hours**.
- **Secondary Bottleneck:** **Post-Consultation Radiology Queue** averages **419.3 minutes (6.99 hours)** from doctor consult completion to imaging procedure start.
- **Queue Buildup Driver:** Monday morning arrival spikes (2,640 arrivals at 06:00-07:00) cause cascading delays extending into afternoon clinics.

## 2. Departmental Bottleneck Ranking

| Rank | Stage | Department | Volume | Mean Latency | Median | Delayed (>Thresh) | Severe (>8 hrs) |
| :-: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | Laboratory Turnaround Time (TAT) | Clinical Lab | 4,795 | 930.5 min | 164.0 min | 3,019 (63.0%) | 971 (20.3%) |
| 2 | Post-Consultation Imaging Queue | Radiology Queue | 3,284 | 595.2 min | 39.0 min | 417 (12.7%) | 229 (7.0%) |
| 3 | Registration to Consultation Wait | OPD Front Desk | 49,896 | 129.8 min | 27.0 min | 3,461 (6.9%) | 445 (0.9%) |
| 4 | Imaging Procedure TAT | Radiology Service | 5,315 | 111.0 min | 3.0 min | 109 (2.1%) | 55 (1.0%) |
| 5 | Consultation to Pharmacy Queue | Pharmacy Queue | 108 | 9.7 min | 6.0 min | 6 (5.6%) | 0 (0.0%) |

## 3. Diagnostic Compounding Delay Effect

| Clinical Service Pathway | Encounters | Mean Journey (min) | Mean Journey (hrs) | Mean Wait (min) | PCE Efficiency (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Consultation Only (No Diagnostics) | 41,318 | 177.3 | 2.95 | 171.7 | 9.9% |
| Consultation + Lab Only | 3,790 | 1057.1 | 17.62 | 109.0 | 73.8% |
| Consultation + Imaging Only | 3,799 | 425.6 | 7.09 | 287.3 | 11.5% |
| Consultation + Lab + Imaging | 1,005 | 1753.7 | 29.23 | 577.8 | 68.5% |

## 4. Key Strategic Recommendations

1. **Continuous-Flow Phlebotomy Batching:** Transition laboratory analyzer runs from batch releases (13:00 / 17:00) to continuous rolling batches (30-minute cycles) to reduce laboratory TAT from 4.65 hours to <90 minutes.
2. **Radiology Capacity Leveling:** Implement order quota smoothing for outpatient X-ray and ultrasound to prevent midday overload following morning physician clinics.
3. **Staggered Clinic Arrivals:** Shift appointment slots away from the 06:00-07:00 Monday morning peak to flatten the registration queue intake curve.

Create Synthetic Hospital Event Log Table
-- Query 0: Create Synthetic Hospital Event Log Table
CREATE TABLE
  `careflow-analytics-513310.careflow_dataset.hospital_event_log`
AS

SELECT *
FROM UNNEST([
  STRUCT('CASE001' AS Case_ID, 'Appointment' AS Activity_Name,
         TIMESTAMP('2026-10-01 09:00:00+00') AS Timestamp),
  STRUCT('CASE001', 'Prescription',
         TIMESTAMP('2026-10-01 09:10:00+00')),
  STRUCT('CASE001', 'Lab',
         TIMESTAMP('2026-10-01 09:25:00+00')),
  STRUCT('CASE001', 'Pharmacy',
         TIMESTAMP('2026-10-01 09:45:00+00')),

  STRUCT('CASE002', 'Appointment',
         TIMESTAMP('2026-10-01 10:00:00+00')),
  STRUCT('CASE002', 'Lab',
         TIMESTAMP('2026-10-01 10:15:00+00')),
  STRUCT('CASE002', 'Prescription',
         TIMESTAMP('2026-10-01 10:40:00+00')),

  STRUCT('CASE003', 'Appointment',
         TIMESTAMP('2026-10-01 11:00:00+00')),
  STRUCT('CASE003', 'Imaging',
         TIMESTAMP('2026-10-01 11:20:00+00')),
  STRUCT('CASE003', 'Lab',
         TIMESTAMP('2026-10-01 11:50:00+00')),

  STRUCT('CASE004', 'Appointment',
         TIMESTAMP('2026-10-01 12:00:00+00')),
  STRUCT('CASE004', 'Prescription',
         TIMESTAMP('2026-10-01 12:15:00+00')),
  STRUCT('CASE004', 'Prescription',
         TIMESTAMP('2026-10-01 12:30:00+00')),

  STRUCT('CASE005', 'Appointment',
         TIMESTAMP('2026-10-01 13:00:00+00')),
  STRUCT('CASE005', 'Imaging',
         TIMESTAMP('2026-10-01 13:20:00+00')),
  STRUCT('CASE005', 'Pharmacy',
         TIMESTAMP('2026-10-01 13:50:00+00'))
]);

-- Query 1: Activity Frequency Analysis
SELECT
    Activity_Name,
    COUNT(*) AS Total_Events
FROM
    `careflow-analytics-513310.careflow_dataset.hospital_event_log`
GROUP BY
    Activity_Name
ORDER BY
    Total_Events DESC;

-- Query 2: Activity Transition Analysis
WITH ordered_events AS (
    SELECT
        Case_ID,
        Activity_Name,
        Timestamp,
        LEAD(Activity_Name) OVER (
            PARTITION BY Case_ID
            ORDER BY Timestamp
        ) AS Next_Activity,
        LEAD(Timestamp) OVER (
            PARTITION BY Case_ID
            ORDER BY Timestamp
        ) AS Next_Timestamp
    FROM
        `careflow-analytics-513310.careflow_dataset.hospital_event_log`
)

SELECT
    Activity_Name,
    Next_Activity,
    COUNT(*) AS Transition_Count,
    ROUND(
        AVG(
            TIMESTAMP_DIFF(
                Next_Timestamp,
                Timestamp,
                MINUTE
            )
        ), 2
    ) AS Average_Transition_Minutes
FROM ordered_events
WHERE Next_Activity IS NOT NULL
GROUP BY Activity_Name, Next_Activity
ORDER BY Transition_Count DESC;

-- Query 3: Case-Level Summary Analysis
SELECT
  Case_ID,
  COUNT(*) AS Total_Events,
  COUNT(DISTINCT Activity_Name) AS Unique_Activities,
  MIN(Timestamp) AS First_Event_Time,
  MAX(Timestamp) AS Last_Event_Time,
  TIMESTAMP_DIFF(
    MAX(Timestamp),
    MIN(Timestamp),
    MINUTE
  ) AS Case_Duration_Minutes
FROM
  `careflow-analytics-513310.careflow_dataset.hospital_event_log`
GROUP BY
  Case_ID
ORDER BY
  Case_ID;

-- Query 4: Data Quality Validation Analysis
SELECT
  COUNT(*) AS Total_Rows,
  COUNTIF(Case_ID IS NULL) AS Null_Case_ID,
  COUNTIF(Activity_Name IS NULL) AS Null_Activity_Name,
  COUNTIF(Timestamp IS NULL) AS Null_Timestamp,
  COUNT(DISTINCT Case_ID) AS Unique_Cases,
  COUNT(DISTINCT Activity_Name) AS Unique_Activities
FROM
  `careflow-analytics-513310.careflow_dataset.hospital_event_log`;

-- Query 5: Chronological Event Order Validation
WITH ordered_events AS (
  SELECT
    Case_ID,
    Activity_Name,
    Timestamp,
    LAG(Timestamp) OVER (
      PARTITION BY Case_ID
      ORDER BY Timestamp
    ) AS Previous_Timestamp
  FROM
    `careflow-analytics-513310.careflow_dataset.hospital_event_log`
)
SELECT
  Case_ID,
  Activity_Name,
  Timestamp,
  Previous_Timestamp
FROM
  ordered_events
WHERE
  Previous_Timestamp IS NOT NULL
  AND Timestamp < Previous_Timestamp;
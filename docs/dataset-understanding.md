# CareFlow — Dataset Understanding

## 1. Project Overview

CareFlow is a Clinical Pathway Process Mining project that analyzes healthcare event logs to understand patient treatment pathways.

## 2. Dataset Summary

The Sepsis Treatment Careflow dataset was loaded and analyzed using Python, pandas, and Google Colab.

- Initial event records: 15,190
- Unique cases: 1,049
- Unique activities: 16
- Exact duplicate rows identified: 7
- Records after removing duplicates: 15,183
- Missing values in key columns: 0

## 3. Data Dictionary

| Column | Description |
|---|---|
| Case_ID | Identifies a patient case |
| Activity | Represents a healthcare event |
| Timestamp | Records the date and time of an event |

## 4. Data Cleaning

The dataset was inspected for missing values and exact duplicate records. The Timestamp column was converted to datetime format, and seven exact duplicate rows were removed.

The cleaned dataset was sorted by Case_ID and Timestamp and saved as a separate CSV file.

## 5. Timestamp Range

- Start: 7 November 2013
- End: 5 June 2015

## 6. Data Quality Verification

After cleaning, the dataset contained 15,183 records, 1,049 unique cases, and 16 unique activities. No missing values or exact duplicate rows remained in the cleaned dataset.

## 7. Next Steps

- Complete the dataset source and license verification.
- Assess the dataset's suitability for process mining.
- Share the dataset findings with the team.
- Support the next stages of clinical pathway process analysis.

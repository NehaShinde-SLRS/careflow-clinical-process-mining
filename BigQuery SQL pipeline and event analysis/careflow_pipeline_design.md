# CareFlow – SQL Pipeline Design

## 1. Project Overview

CareFlow is a hospital process-mining and operational analytics project. The purpose of this stage is to use SQL queries to analyze hospital activity records, understand activity transitions, summarize cases, and validate data quality.

The current project dataset represents hospital outpatient activity. The results should therefore be interpreted as outpatient activity patterns, not verified Emergency Room findings.

## 2. SQL Pipeline Overview

The Day 10 SQL pipeline follows these steps:

1. **Data Preparation:** Prepare the event data with case identifiers, activity names, and timestamps.
2. **BigQuery Table:** Store the synthetic demonstration event data in a BigQuery table.
3. **SQL Analysis:** Run SQL queries to analyze activity frequency, transitions, case summaries, and data quality.
4. **Result Export:** Save the query outputs as CSV files.
5. **Documentation:** Record the SQL process and analysis results for future process-mining work.

## 3. BigQuery Details

- Google Cloud Project: `careflow-analytics-513310`
- BigQuery Dataset: `careflow_dataset`
- BigQuery Table: `hospital_event_log`

**Note:** The BigQuery event table contains synthetic demonstration data. It is separate from the original outpatient dataset.

## 4. SQL Queries and Outputs

| SQL analysis | Output file |
|---|---|
| Activity Frequency Analysis | `sql_activity_summary.csv` |
| Case-Level Summary Analysis | `sql_case_summary.csv` |
| Activity Transition Analysis | `sql_transition_analysis.csv` |
| Data Quality Validation | `sql_validation_summary.csv` |

The SQL statements used for these analyses are documented in `careflow_analysis.sql`.

## 5. Data Quality Validation

The synthetic BigQuery demonstration dataset was checked for:

- Total number of events
- Missing case identifiers
- Missing activity names
- Missing timestamps
- Unique cases
- Unique activities
- Chronological event ordering

The validation results are documented in `sql_validation_summary.csv`.

## 6. Tools and Technologies

- Python
- Pandas
- SQL
- Google BigQuery
- Jupyter Notebook
- GitHub

## 7. Project Limitations

- The BigQuery table is a synthetic demonstration dataset.
- The original hospital dataset represents outpatient activity.
- Event timestamps show recorded timing but do not establish the cause of delays.
- The analysis does not prove a specific waiting-time improvement.
- Patient-level or identifiable healthcare data should not be uploaded to a public repository without appropriate permission.

## 8. Next Steps

The next stage will use PM4Py to discover directly-follows relationships between activities and generate a process map from the normalized outpatient event log.

---

**Project:** CareFlow – Clinical Pathway Process Mining  
**Stage:** SQL Pipeline Validation

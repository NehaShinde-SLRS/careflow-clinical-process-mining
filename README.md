# 🏥 CareFlow: Hospital OPD Clinical Pathway Process Mining & Analytics

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/BigQuery-SQL-orange.svg)](https://cloud.google.com/bigquery)
[![Process Mining](https://img.shields.io/badge/Process_Mining-PM4Py-brightgreen.svg)](https://pm4py.fit.fraunhofer.de/)
[![BI Tool](https://img.shields.io/badge/Power_BI-Desktop-F2C811.svg)](https://powerbi.microsoft.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end Healthcare Data Analytics & Process Mining project analyzing **62,418 outpatient department (OPD) transaction records** across **39,442 unique patients** and **49,912 clinical encounters**. 

This repository implements data cleaning, BigQuery analytical modeling, automated process mining using `PM4Py`, and an executive Power BI dashboard to diagnose clinical waiting times and patient flow bottlenecks.

---

## 📌 Executive Summary & Key Metrics
* **Total Transactions:** 62,418 records (cleaned, validated, and deduplicated)
* **Clinical Encounters:** 49,912 distinct outpatient visits across 39,442 unique patients
* **Primary Care Pathway:** 64.35% of encounters follow the direct *Appointment ➔ Prescription* route
* **Diagnostic Demand:** 26.32% required Laboratory testing; 6.32% required Imaging/Ultrasound
* **Operational Bottlenecks:** Doctor consultation duration averages **4.0 minutes (median)**, whereas Pathology Lab Turnaround Time (TAT) extends to **2.0 – 7.8 hours**
* **Surge Patterns:** Bimodal patient check-in surges identified between **5:00 AM – 8:00 AM** (>16,000 arrivals) and **12:00 PM – 3:00 PM**

---

## 🗂️ Repository Structure

```text
├── data/
│   ├── uncleaned_HospitalOPD.csv            # Raw OPD transactions with export artifacts
│   └── cleaned_HospitalOPD.csv              # Production-cleaned dataset (62,418 rows)
│
├── notebooks/
│   └── data_cleaning.ipynb                  # Data audit, cleaning & validation notebook
│
├── process_mining/
│   └── process_mining_pm4py.py              # Event log generator & PM4Py process discovery script
│
├── sql/
│   └── careflow_analytics_queries.sql       # BigQuery SQL queries (TAT, waiting times, activity logs)
│
├── dashboard/
│   ├── careflow_POWERBI_dashboard.pbix      # Interactive 2-page Power BI dashboard
│   └── CareFlow_PowerBI_Dashboard_Specification.docx # DAX formulas & layout documentation
│
├── docs/
│   ├── Hospital_OPD_Data_Cleaning_Report.docx  # Detailed cleaning audit & data dictionary
│   └── CareFlow_SQL_Queries_and_dbt_Models.docx # BigQuery & dbt transformation framework
│
├── LICENSE                                  # MIT Open-Source License
└── README.md                                # Project documentation

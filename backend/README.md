# AI-Powered Data Quality Audit and Cleaning Assistant

## Abstract
The AI-Powered Data Quality Audit and Cleaning Assistant is a web-based application designed to analyze and improve the quality of raw datasets. It automatically detects issues such as missing values, duplicate records, incorrect formats, and outliers, then applies suitable cleaning techniques and provides a data quality score along with recommendations.

## Purpose
The main purpose of this project is to reduce manual effort in data preprocessing and ensure that datasets are clean, consistent, and ready for analysis or machine learning tasks.

## Usefulness
This system is useful for students, data analysts, researchers, and businesses who work with large datasets, as it simplifies the data cleaning process and improves accuracy and efficiency in decision-making.

## Tech Stack
- **Backend:** Python, Flask
- **Data Processing:** Pandas, NumPy
- **Frontend:** HTML, CSS, JavaScript

## Features
- Upload any CSV file for instant analysis
- Detects missing values, duplicate rows, outliers (IQR method), and format issues (whitespace, mixed casing, inconsistent date formats)
- Calculates an overall Data Quality Score (0–100)
- Generates human-readable recommendations
- One-click cleaning: removes duplicates, fills missing values, trims whitespace, caps outliers
- Download the cleaned dataset as a new CSV file
- Handles invalid inputs gracefully (empty files, wrong file types)

## How to Run
1. Clone or download this project
2. Navigate to the `backend` folder
3. Create and activate a virtual environment:
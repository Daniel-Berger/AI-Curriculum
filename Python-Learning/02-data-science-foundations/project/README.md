# Phase 2 Project: Complete EDA Pipeline

## Overview
Build a complete Exploratory Data Analysis (EDA) pipeline that processes a real-world style dataset, performs data quality checks, generates statistical summaries, creates visualizations, and documents findings.

## Learning Objectives
- Apply NumPy and Pandas skills to real data
- Follow a systematic EDA workflow
- Create meaningful visualizations with Matplotlib/Seaborn
- Perform feature engineering
- Write clean, well-structured data analysis code

## Dataset
The project uses a synthetic employee dataset (`sample_data.csv`) with intentional data quality issues (missing values, outliers, mixed types) that mirror real-world data.

## Project Structure
```
project/
├── README.md              # This file
├── sample_data.csv        # Dataset
├── eda_pipeline.py        # Main EDA pipeline
└── test_eda.py            # Tests
```

## How to Run
```bash
# Run the full EDA pipeline
python eda_pipeline.py

# Run tests
pytest test_eda.py -v
```

## Requirements
- numpy, pandas, matplotlib, seaborn
- Install: `uv pip install -e ".[data-science]"`

## Deliverables
1. Data quality report (missing values, duplicates, outliers)
2. Statistical summary of all variables
3. Correlation analysis
4. At least 4 visualizations saved as PNG files
5. Feature engineering recommendations

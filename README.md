# COVID-19 Global Impact Dashboard

A complete data-analytics portfolio project based on the Veda Technology internship brief.

## Project objective
Analyze COVID-19 cases, deaths and vaccination rollout over time; normalize country comparisons by population; derive rolling averages, case-fatality rate and doubling time; and communicate findings through an interactive dashboard.

## Tools
- Python: Pandas, NumPy, Matplotlib
- Excel: cleaned data, summaries, data dictionary
- Power BI / Tableau: dashboard-ready dataset and DAX measures
- Report: PDF executive summary + methodology

## Folder structure
```text
COVID19_Global_Impact_Dashboard/
├── data/
│   ├── raw/
│   │   ├── covid_demo_raw.csv
│   │   └── owid-covid-data.csv          # created by downloader
│   └── processed/
│       ├── covid_cleaned_analysis.csv
│       └── owid_covid_cleaned.csv       # created from real OWID data
├── docs/
├── notebooks/
├── outputs/
│   ├── dashboard_preview.png
│   ├── COVID19_Global_Impact_Dashboard.xlsx
│   └── charts
├── powerbi/
│   └── DAX_Measures.txt
└── src/
    ├── download_owid_data.py
    ├── clean_owid_data.py
    └── build_project.py
```

## Important data note
The included preview charts/workbook use a clearly labelled synthetic demo dataset so the project can be opened immediately. For a real internship submission, run:

```bash
python src/download_owid_data.py
python src/clean_owid_data.py
```

The production source is Our World in Data's COVID-19 dataset. OWID documents the COVID-19 Data Explorer and downloadable complete dataset. The dashboard should be refreshed from the downloaded file before final submission.

## Key derived metrics
- New cases per million
- New deaths per million
- Cumulative cases/deaths per million
- 7-day rolling average
- Case fatality rate
- Approximate case doubling time
- Vaccination coverage

## Dashboard layout
1. KPI row: Total Cases | Total Deaths | Vaccinated % | CFR
2. Trend: 7-day cases/deaths per million
3. Country comparison: cases per million
4. Country comparison: deaths per million
5. Vaccination vs deaths scatter plot
6. Country/date filters

## Submission checklist
- [x] Cleaned dataset structure
- [x] Documented assumptions
- [x] 5+ plain-language insights
- [x] Dashboard preview
- [x] Excel workbook
- [x] Power BI DAX measures
- [x] Executive summary/report
- [x] Reproducible OWID download + cleaning scripts

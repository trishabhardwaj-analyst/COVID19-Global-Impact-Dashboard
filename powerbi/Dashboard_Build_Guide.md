# Power BI Dashboard Build Guide

## Page 1 — Executive Overview
**Title:** COVID-19 Global Impact Dashboard

**Slicers:** Date, Country, Continent, Year

**KPI Cards**
- Total Cases
- Total Deaths
- Vaccinated %
- Case Fatality Rate

**Visual 1 — Global Trend**
Line chart with Date on X-axis and `cases_7d_avg_per_million`, `deaths_7d_avg_per_million` as values.

**Visual 2 — Cases by Country**
Horizontal bar chart; Top N = 10; value = `total_cases_per_million`.

**Visual 3 — Deaths by Country**
Horizontal bar chart; Top N = 10; value = `total_deaths_per_million`.

**Visual 4 — Vaccination vs Mortality**
Scatter chart: X = vaccination %, Y = deaths per million, Details = location.

## Page 2 — Country Deep Dive
- Country slicer
- Daily cases and deaths rolling-average line chart
- Vaccination coverage line
- Total cases/deaths cards
- Doubling time table

## Page 3 — Findings
Use 5 callout cards:
1. Peak wave timing
2. Highest cases per million
3. Highest deaths per million
4. Highest vaccination coverage
5. Outlier worth investigating

## Formatting
Use a clean white background, dark blue headings and a single accent color. Keep spacing consistent, use 16:9 canvas, and avoid unnecessary chart borders.

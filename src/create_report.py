from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.units import inch
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'
report=OUT/'COVID19_Global_Impact_Dashboard_Report.pdf'
df=pd.read_csv(ROOT/'data'/'processed'/'covid_cleaned_analysis.csv')
summary=df.sort_values('date').groupby('location').tail(1).sort_values('total_cases_per_million',ascending=False)

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleCenter', parent=styles['Title'], alignment=TA_CENTER, fontSize=22, leading=26, spaceAfter=18))
styles.add(ParagraphStyle(name='H1x', parent=styles['Heading1'], fontSize=17, leading=21, spaceBefore=10, spaceAfter=8))
styles.add(ParagraphStyle(name='H2x', parent=styles['Heading2'], fontSize=13, leading=16, spaceBefore=8, spaceAfter=5))
styles.add(ParagraphStyle(name='Bodyx', parent=styles['BodyText'], fontSize=9.5, leading=14, spaceAfter=7))
styles.add(ParagraphStyle(name='Small', parent=styles['BodyText'], fontSize=8, leading=11, textColor=colors.grey))

story=[]
story.append(Paragraph('COVID-19 Global Impact Dashboard',styles['TitleCenter']))
story.append(Paragraph('Data Analytics Internship Project — Executive Summary & Technical Report',styles['H2x']))
story.append(Spacer(1,8))
story.append(Image(str(OUT/'dashboard_preview.png'),width=7.1*inch,height=4.45*inch))
story.append(Spacer(1,8))
story.append(Paragraph('<b>Project question:</b> How did COVID-19 cases, mortality and vaccination rollout vary across countries and over time, and what changes when we normalize by population?',styles['Bodyx']))
story.append(Paragraph('<b>Important data note:</b> The preview workbook and charts bundled with this package use a clearly labelled synthetic portfolio dataset so the project is immediately reproducible in this environment. For a real-world submission, refresh the pipeline with the official Our World in Data dataset using the included downloader and cleaner scripts.',styles['Bodyx']))
story.append(PageBreak())

story.append(Paragraph('1. Executive Summary',styles['H1x']))
for txt in [
'This project implements the complete analytics pipeline requested in the internship brief: data acquisition, cleaning, missing-value handling, metric engineering, population normalization, time-series smoothing, country comparison, visualization and plain-language interpretation.',
'The dashboard focuses on six decision-useful views: global rolling trends, cases per million, deaths per million, vaccination coverage versus mortality, a country deep dive, and monthly trend context.',
'The analysis deliberately uses per-million measures because raw totals are dominated by population size. Rolling seven-day averages are used to reduce day-to-day reporting noise.',
'Vaccination and mortality are compared descriptively. The relationship should not be interpreted as a causal estimate because COVID reporting, testing, age structure, healthcare access, variants and vaccination definitions vary across countries.'
]: story.append(Paragraph(txt,styles['Bodyx']))

story.append(Paragraph('2. Project Objectives',styles['H1x']))
objectives=['Clean messy real-world time-series data','Handle missing values and inconsistent reporting','Derive 7-day rolling averages','Calculate cases/deaths per million','Calculate case fatality rate and approximate doubling time','Compare vaccination rollout across countries','Build an interactive Power BI/Tableau-ready dashboard','Communicate 3–5 insights to a non-technical audience']
for o in objectives: story.append(Paragraph('• '+o,styles['Bodyx']))

story.append(Paragraph('3. Dataset & Methodology',styles['H1x']))
story.append(Paragraph('Production source: Our World in Data COVID-19 Data Explorer / complete COVID-19 dataset. OWID documents downloadable CSV data and notes that confirmed case/death data are sourced from the World Health Organization in its current explorer. The included scripts use the OWID public CSV endpoint and preserve a reproducible acquisition step.',styles['Bodyx']))
story.append(Paragraph('Portfolio preview: 12 countries, daily observations from 2020-01-01 through 2023-12-31, 17,532 rows. The demo data is synthetic and is included only to demonstrate the complete project structure and visuals.',styles['Bodyx']))

story.append(Paragraph('Core transformations',styles['H2x']))
method=[['Metric','Formula / treatment'],['Cases per million','Confirmed cases ÷ population × 1,000,000'],['Deaths per million','Confirmed deaths ÷ population × 1,000,000'],['7-day average','Rolling mean over the previous 7 daily observations'],['Case fatality rate','Cumulative deaths ÷ cumulative cases × 100'],['Doubling time','ln(2) ÷ ln(1 + daily case growth rate)'],['Vaccination coverage','People vaccinated ÷ population × 100']]
t=Table(method,colWidths=[1.8*inch,5.0*inch]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#D9EAF7')),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),0.25,colors.grey),('VALIGN',(0,0),(-1,-1),'TOP'),('FONTSIZE',(0,0),(-1,-1),8.5),('BOTTOMPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5)])); story.append(t)

story.append(PageBreak())
story.append(Paragraph('4. Dashboard Visuals',styles['H1x']))
for title,img in [('Global rolling trend','01_global_trend.png'),('Cases per million','02_cases_per_million.png'),('Deaths per million','03_deaths_per_million.png'),('Vaccination vs deaths','04_vax_vs_deaths.png')]:
    story.append(Paragraph(title,styles['H2x']))
    story.append(Image(str(OUT/img),width=6.7*inch,height=3.35*inch))
    story.append(Spacer(1,5))

story.append(PageBreak())
story.append(Paragraph('5. Key Insights — Portfolio Interpretation',styles['H1x']))
insights=[
'Peak intensity is concentrated in the major wave periods, reinforcing the value of time-series trend analysis instead of relying on cumulative totals alone.',
'Population normalization changes the country ranking. A large country can lead raw totals while another country can have a higher burden per million people.',
'Vaccination coverage increases strongly after rollout begins. In the portfolio data, later periods generally show lower deaths relative to case volume; this is an observational pattern, not a causal conclusion.',
'The seven-day rolling average produces a cleaner communication layer than raw daily values, especially when reporting schedules create spikes and gaps.',
'Countries with high mortality per million should be treated as investigation priorities rather than automatically labelled as poor performers; reporting quality, demographics, healthcare capacity and epidemic timing all matter.'
]
for i,x in enumerate(insights,1): story.append(Paragraph(f'<b>{i}.</b> {x}',styles['Bodyx']))

story.append(Paragraph('6. Quality Checks & Assumptions',styles['H1x']))
checks=['Converted dates to a consistent datetime type','Sorted records by country and date before rolling calculations','Used numeric coercion for count fields','Protected ratios against division by zero','Used per-million normalization for cross-country comparisons','Kept the synthetic demo clearly separate from the production OWID refresh pipeline','Avoided causal language when interpreting vaccination versus mortality']
for x in checks: story.append(Paragraph('✓ '+x,styles['Bodyx']))

story.append(PageBreak())
story.append(Paragraph('7. Power BI Implementation',styles['H1x']))
story.append(Paragraph('The package contains DAX measures and a visual build guide. Recommended page structure:',styles['Bodyx']))
for x in ['Page 1 — Executive Overview: KPI cards, global trend, cases/deaths per million, vaccination scatter, slicers.','Page 2 — Country Deep Dive: selected-country trend, vaccination line, doubling time and summary table.','Page 3 — Findings: five insight cards and methodology notes.']:
    story.append(Paragraph('• '+x,styles['Bodyx']))
story.append(Paragraph('Recommended slicers: Date, Country, Continent and Year. Keep the canvas 16:9 with consistent spacing and a restrained visual hierarchy.',styles['Bodyx']))

story.append(Paragraph('8. Deliverables Included',styles['H1x']))
for x in ['Excel workbook with cleaned demo data, country summary, monthly summary, insights and data dictionary','Dashboard preview PNG','Production OWID downloader and cleaning scripts','Jupyter notebook for analysis','Power BI DAX measures','Power BI dashboard build guide','README with setup and submission checklist']:
    story.append(Paragraph('• '+x,styles['Bodyx']))

story.append(Paragraph('9. Final Submission Recommendation',styles['H1x']))
story.append(Paragraph('Before submitting to Veda Technology, run the two OWID scripts so the final workbook and dashboard are based on the real public dataset rather than the included demo data. Then export the Power BI dashboard to PDF/PNG, add the screenshots to the report, and include the GitHub repository with the same folder structure.',styles['Bodyx']))
story.append(Spacer(1,10))
story.append(Paragraph('Source: Our World in Data, COVID-19 Data Explorer — https://ourworldindata.org/explorers/covid',styles['Small']))

doc=SimpleDocTemplate(str(report),pagesize=A4,rightMargin=36,leftMargin=36,topMargin=36,bottomMargin=36,title='COVID-19 Global Impact Dashboard Report')
doc.build(story)
print(report)

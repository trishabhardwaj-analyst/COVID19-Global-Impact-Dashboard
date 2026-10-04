import os, math, json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/'data'/'raw'
PROC = ROOT/'data'/'processed'
OUT = ROOT/'outputs'
for p in [RAW, PROC, OUT]: p.mkdir(parents=True, exist_ok=True)

np.random.seed(42)

countries = {
    'India': (1380000000, 0.0000070, 0.000000050),
    'United States': (331000000, 0.0000060, 0.000000045),
    'Brazil': (212000000, 0.0000065, 0.000000055),
    'United Kingdom': (67000000, 0.0000080, 0.000000060),
    'Germany': (83000000, 0.0000060, 0.000000040),
    'France': (68000000, 0.0000065, 0.000000045),
    'Italy': (60000000, 0.0000060, 0.000000050),
    'Canada': (38000000, 0.0000055, 0.000000040),
    'Japan': (126000000, 0.0000040, 0.000000030),
    'South Africa': (60000000, 0.0000070, 0.000000055),
    'Australia': (26000000, 0.0000035, 0.000000025),
    'Mexico': (128000000, 0.0000065, 0.000000055),
}

dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')
rows=[]

def gaussian(x, mu, sigma): return math.exp(-0.5*((x-mu)/sigma)**2)

for country,(pop,case_base,death_base) in countries.items():
    cumulative_cases = 0.0
    cumulative_deaths = 0.0
    for d in dates:
        t = (d - dates[0]).days
        # wave peaks: early 2020, late 2020, spring 2021, late 2021, early/mid 2022
        wave = (0.95*gaussian(t,110,45) + 1.8*gaussian(t,300,55) +
                2.2*gaussian(t,470,55) + 3.0*gaussian(t,700,70) +
                4.2*gaussian(t,820,80) + 2.0*gaussian(t,1050,90))
        season = 0.85 + 0.15*math.sin(2*math.pi*t/365)
        regional_factor = 1.0 + np.random.normal(0,0.08)
        new_cases = max(0, pop*case_base*wave*season*regional_factor)
        # Vaccination rollout from 2021; saturation varies by country.
        rollout = 0 if d < pd.Timestamp('2021-01-01') else 1/(1+math.exp(-(t-560)/90))
        vax_cap = {'India':72,'United States':81,'Brazil':82,'United Kingdom':78,'Germany':78,'France':76,'Italy':80,'Canada':84,'Japan':84,'South Africa':51,'Australia':87,'Mexico':67}[country]
        vax_pct = min(vax_cap, vax_cap*rollout)
        # deaths track cases with delay and fall as vaccination coverage rises
        base_fatality = {'India':0.0090,'United States':0.0120,'Brazil':0.0130,'United Kingdom':0.0105,'Germany':0.0095,'France':0.0105,'Italy':0.0140,'Canada':0.0100,'Japan':0.0090,'South Africa':0.0145,'Australia':0.0060,'Mexico':0.0135}[country]
        fatality = base_fatality * (1 - 0.55*(vax_pct/100))
        new_deaths = max(0, new_cases * fatality * (1.1 + 0.15*gaussian(t,320,60)))
        cumulative_cases += new_cases
        cumulative_deaths += new_deaths
        total_vax = pop * vax_pct/100
        total_doses = total_vax * (1.35 + 0.15*min(vax_pct/80,1))
        rows.append([country,d,pop,new_cases,new_deaths,cumulative_cases,cumulative_deaths,total_vax,total_doses,vax_pct])

df = pd.DataFrame(rows, columns=['location','date','population','new_cases','new_deaths','total_cases','total_deaths','people_vaccinated','total_vaccinations','people_vaccinated_pct'])
# Make metrics more realistic and readable.
df['new_cases_per_million'] = df['new_cases']/df['population']*1e6
df['new_deaths_per_million'] = df['new_deaths']/df['population']*1e6
df['total_cases_per_million'] = df['total_cases']/df['population']*1e6
df['total_deaths_per_million'] = df['total_deaths']/df['population']*1e6
df['case_fatality_rate_pct'] = np.where(df['total_cases']>0, df['total_deaths']/df['total_cases']*100, np.nan)
df['cases_7d_avg_per_million'] = df.groupby('location')['new_cases_per_million'].transform(lambda s:s.rolling(7,min_periods=1).mean())
df['deaths_7d_avg_per_million'] = df.groupby('location')['new_deaths_per_million'].transform(lambda s:s.rolling(7,min_periods=1).mean())
df['cases_growth_rate_pct'] = df.groupby('location')['total_cases'].pct_change().replace([np.inf,-np.inf],np.nan)*100
df['doubling_time_days'] = np.where(df['cases_growth_rate_pct']>0, np.log(2)/(np.log1p(df['cases_growth_rate_pct']/100)), np.nan)
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.to_period('M').astype(str)
df['wave'] = pd.cut(df['date'], [pd.Timestamp('2019-12-31'),pd.Timestamp('2020-08-31'),pd.Timestamp('2021-05-31'),pd.Timestamp('2022-03-31'),pd.Timestamp('2023-12-31')], labels=['Wave 1','Wave 2','Wave 3','Omicron/late wave'])

# Save demo raw + processed
raw_cols=['location','date','population','new_cases','new_deaths','total_cases','total_deaths','people_vaccinated','total_vaccinations','people_vaccinated_pct']
df[raw_cols].to_csv(RAW/'covid_demo_raw.csv', index=False)
df.to_csv(PROC/'covid_cleaned_analysis.csv', index=False)

# Summaries
country_summary = df.sort_values('date').groupby('location').tail(1)[['location','population','total_cases','total_deaths','total_cases_per_million','total_deaths_per_million','people_vaccinated_pct','case_fatality_rate_pct']].sort_values('total_cases_per_million', ascending=False)
monthly = df.groupby(['month']).agg(new_cases=('new_cases','sum'),new_deaths=('new_deaths','sum'),vaccinated_people=('people_vaccinated','max')).reset_index()
monthly['cases_7d_equivalent'] = monthly['new_cases']/30.44
monthly['deaths_7d_equivalent'] = monthly['new_deaths']/30.44

# Insights based on demo data
peak_cases = df.groupby('date')['new_cases_per_million'].mean().idxmax()
peak_deaths = df.groupby('date')['new_deaths_per_million'].mean().idxmax()
insights = pd.DataFrame({
 'Insight': [
   'The highest average daily case intensity occurs around the major 2022 wave in this portfolio dataset.',
   'Vaccination coverage rises sharply from 2021 onward and coincides with lower deaths per case later in the series.',
   'Per-million normalization changes country rankings substantially compared with raw totals.',
   'The dashboard emphasizes rolling averages because daily COVID reporting is noisy and irregular.',
   'Case fatality rate is descriptive, not causal; testing coverage and reporting practices affect the metric.'
 ],
 'Evidence': [str(peak_cases.date()), str(peak_deaths.date()), 'See Country Summary sheet', '7-day rolling metrics included', 'Methodology note']
})

# Charts
plt.rcParams.update({'figure.figsize':(12,6),'axes.titlesize':14,'axes.labelsize':10})

global_daily=df.groupby('date').agg(cases=('new_cases_per_million','mean'),deaths=('new_deaths_per_million','mean')).reset_index()
fig,ax=plt.subplots(); ax.plot(global_daily.date,global_daily.cases,label='Cases / million'); ax.plot(global_daily.date,global_daily.deaths,label='Deaths / million'); ax.set_title('COVID-19 Global Impact — 7-day intensity proxy'); ax.set_ylabel('Daily per million'); ax.legend(); ax.grid(alpha=.2); fig.tight_layout(); fig.savefig(OUT/'01_global_trend.png',dpi=180); plt.close(fig)

fig,ax=plt.subplots(); top=country_summary.sort_values('total_cases_per_million',ascending=True); ax.barh(top.location,top.total_cases_per_million); ax.set_title('Cumulative Confirmed Cases per Million'); ax.set_xlabel('Cases per million'); fig.tight_layout(); fig.savefig(OUT/'02_cases_per_million.png',dpi=180); plt.close(fig)

fig,ax=plt.subplots(); top=country_summary.sort_values('total_deaths_per_million',ascending=True); ax.barh(top.location,top.total_deaths_per_million); ax.set_title('Cumulative Confirmed Deaths per Million'); ax.set_xlabel('Deaths per million'); fig.tight_layout(); fig.savefig(OUT/'03_deaths_per_million.png',dpi=180); plt.close(fig)

latest=df.groupby('location').tail(1)
fig,ax=plt.subplots(); ax.scatter(latest.people_vaccinated_pct, latest.total_deaths_per_million); 
for _,r in latest.iterrows(): ax.annotate(r.location,(r.people_vaccinated_pct,r.total_deaths_per_million),fontsize=8,xytext=(4,4),textcoords='offset points')
ax.set_title('Vaccination Coverage vs Cumulative Deaths per Million'); ax.set_xlabel('People vaccinated (%)'); ax.set_ylabel('Deaths per million'); ax.grid(alpha=.2); fig.tight_layout(); fig.savefig(OUT/'04_vax_vs_deaths.png',dpi=180); plt.close(fig)

india=df[df.location=='India']
fig,ax=plt.subplots(); ax.plot(india.date,india.cases_7d_avg_per_million,label='Cases 7-day avg / million'); ax.plot(india.date,india.deaths_7d_avg_per_million,label='Deaths 7-day avg / million'); ax.set_title('India — Rolling COVID-19 Trend'); ax.set_xlabel('Date'); ax.legend(); ax.grid(alpha=.2); fig.tight_layout(); fig.savefig(OUT/'05_india_trend.png',dpi=180); plt.close(fig)

fig,ax=plt.subplots(); ax.plot(monthly.month,monthly.new_cases,label='Monthly new cases'); ax.plot(monthly.month,monthly.new_deaths*100,label='Monthly deaths ×100'); ax.set_title('Monthly Global Trend'); ax.set_ylabel('Reported events'); ax.tick_params(axis='x',rotation=75); ax.legend(); ax.grid(alpha=.2); fig.tight_layout(); fig.savefig(OUT/'06_monthly_trend.png',dpi=180); plt.close(fig)

# Dashboard composite
fig = plt.figure(figsize=(16,10)); gs=fig.add_gridspec(2,3,hspace=.28,wspace=.24)
axes=[fig.add_subplot(gs[0,0]),fig.add_subplot(gs[0,1]),fig.add_subplot(gs[0,2]),fig.add_subplot(gs[1,0]),fig.add_subplot(gs[1,1]),fig.add_subplot(gs[1,2])]
axes[0].plot(global_daily.date,global_daily.cases); axes[0].plot(global_daily.date,global_daily.deaths); axes[0].set_title('Global 7-day Trend'); axes[0].tick_params(axis='x',rotation=35); axes[0].grid(alpha=.15)
t=country_summary.sort_values('total_cases_per_million',ascending=True); axes[1].barh(t.location,t.total_cases_per_million); axes[1].set_title('Cases / Million')
t=country_summary.sort_values('total_deaths_per_million',ascending=True); axes[2].barh(t.location,t.total_deaths_per_million); axes[2].set_title('Deaths / Million')
axes[3].scatter(latest.people_vaccinated_pct,latest.total_deaths_per_million); axes[3].set_title('Vaccination vs Deaths'); axes[3].set_xlabel('Vaccinated %'); axes[3].set_ylabel('Deaths / M')
axes[4].plot(india.date,india.cases_7d_avg_per_million); axes[4].plot(india.date,india.deaths_7d_avg_per_million); axes[4].set_title('India Trend'); axes[4].tick_params(axis='x',rotation=35); axes[4].grid(alpha=.15)
axes[5].plot(monthly.month,monthly.new_cases/1e6); axes[5].set_title('Monthly New Cases (M)'); axes[5].tick_params(axis='x',rotation=75); axes[5].grid(alpha=.15)
fig.suptitle('COVID-19 Global Impact Dashboard — Portfolio Preview',fontsize=20,fontweight='bold'); fig.savefig(OUT/'dashboard_preview.png',dpi=180,bbox_inches='tight'); plt.close(fig)

# Excel workbook
wb=Workbook(); ws=wb.active; ws.title='README'
readme_rows=[
 ['COVID-19 Global Impact Dashboard','Portfolio-ready analytics workbook'],
 ['Dataset status','DEMO / reproducible template'],
 ['Source for production refresh','Our World in Data COVID-19 dataset'],
 ['Purpose','Clean time-series data, derive per-million and rolling metrics, compare countries, and support Power BI/Tableau.'],
 ['Important','Replace demo raw data with the live OWID CSV using src/download_owid_data.py before submitting as a real-world analysis.']]
for r in readme_rows: ws.append(r)
for cell in ws[1]: cell.font=Font(bold=True,size=14)

sheets={'Cleaned_Data':df.head(5000),'Country_Summary':country_summary,'Monthly_Summary':monthly,'Insights':insights}
for name,data in sheets.items():
    sh=wb.create_sheet(name)
    for row in [list(data.columns)]+data.astype(object).where(pd.notna(data),None).values.tolist(): sh.append(row)
    for c in sh[1]: c.font=Font(bold=True); c.fill=PatternFill('solid',fgColor='D9EAF7')
    sh.freeze_panes='A2'
    for col in range(1,min(sh.max_column,12)+1): sh.column_dimensions[get_column_letter(col)].width=18

# Data dictionary
sh=wb.create_sheet('Data_Dictionary')
dictionary=[
 ('location','Country/region name'),('date','Observation date'),('population','Population used for normalization'),('new_cases','Daily new confirmed cases'),('new_deaths','Daily new confirmed deaths'),('total_cases','Cumulative confirmed cases'),('total_deaths','Cumulative confirmed deaths'),('people_vaccinated','People receiving at least one dose'),('total_vaccinations','Total vaccine doses administered'),('people_vaccinated_pct','People vaccinated as % of population'),('new_cases_per_million','Daily new cases per million'),('new_deaths_per_million','Daily new deaths per million'),('total_cases_per_million','Cumulative cases per million'),('total_deaths_per_million','Cumulative deaths per million'),('case_fatality_rate_pct','Cumulative deaths divided by cumulative cases'),('cases_7d_avg_per_million','7-day rolling average of daily cases per million'),('deaths_7d_avg_per_million','7-day rolling average of daily deaths per million'),('doubling_time_days','Approximate case doubling time derived from daily growth')]
for r in [('Field','Definition')]+dictionary: sh.append(r)
for c in sh[1]: c.font=Font(bold=True)

wb.save(OUT/'COVID19_Global_Impact_Dashboard.xlsx')

# Project metadata
meta={'generated_on':pd.Timestamp.now().isoformat(),'countries':len(countries),'date_start':str(dates.min().date()),'date_end':str(dates.max().date()),'rows':len(df),'status':'demo portfolio dataset; replace via OWID downloader'}
(OUT/'project_metadata.json').write_text(json.dumps(meta,indent=2))
print(json.dumps(meta,indent=2))

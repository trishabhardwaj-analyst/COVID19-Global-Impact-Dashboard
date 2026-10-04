from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data'/'raw'/'owid-covid-data.csv'
OUT=ROOT/'data'/'processed'/'owid_covid_cleaned.csv'

if not RAW.exists():
    raise FileNotFoundError('Run download_owid_data.py first.')

df=pd.read_csv(RAW, parse_dates=['date'])
keep=['iso_code','continent','location','date','population','new_cases','new_deaths','total_cases','total_deaths','people_vaccinated','people_fully_vaccinated','total_vaccinations','new_cases_smoothed','new_deaths_smoothed','new_cases_per_million','new_deaths_per_million','total_cases_per_million','total_deaths_per_million','people_vaccinated_per_hundred','people_fully_vaccinated_per_hundred']
keep=[c for c in keep if c in df.columns]
df=df[keep].copy()
# Keep countries and recognized aggregates separately; exclude income groups and other non-country aggregates for country comparison.
if 'iso_code' in df.columns:
    df=df[df['iso_code'].fillna('').str.len()==3].copy()

df=df.sort_values(['location','date'])
for c in ['new_cases','new_deaths','total_cases','total_deaths','people_vaccinated','total_vaccinations']:
    if c in df.columns:
        df[c]=pd.to_numeric(df[c],errors='coerce')

# Derived metrics
g=df.groupby('location', group_keys=False)
if 'new_cases_per_million' not in df.columns:
    df['new_cases_per_million']=df['new_cases']/df['population']*1e6
if 'new_deaths_per_million' not in df.columns:
    df['new_deaths_per_million']=df['new_deaths']/df['population']*1e6
if 'total_cases_per_million' not in df.columns:
    df['total_cases_per_million']=df['total_cases']/df['population']*1e6
if 'total_deaths_per_million' not in df.columns:
    df['total_deaths_per_million']=df['total_deaths']/df['population']*1e6

df['cases_7d_avg_per_million']=g['new_cases_per_million'].transform(lambda s:s.rolling(7,min_periods=1).mean())
df['deaths_7d_avg_per_million']=g['new_deaths_per_million'].transform(lambda s:s.rolling(7,min_periods=1).mean())
df['case_fatality_rate_pct']=np.where(df['total_cases']>0,df['total_deaths']/df['total_cases']*100,np.nan)
df['cases_growth_rate_pct']=g['total_cases'].pct_change()*100
df['doubling_time_days']=np.where(df['cases_growth_rate_pct']>0,np.log(2)/np.log1p(df['cases_growth_rate_pct']/100),np.nan)
df['year']=df['date'].dt.year
df['month']=df['date'].dt.to_period('M').astype(str)

df.to_csv(OUT,index=False)
print(f'Saved {len(df):,} cleaned rows to {OUT}')

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/'data'/'raw'
RAW.mkdir(parents=True, exist_ok=True)
URL = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
OUT = RAW/'owid-covid-data.csv'
print('Downloading OWID COVID-19 dataset...')
df = pd.read_csv(URL, storage_options={'User-Agent':'COVID-19 Global Impact Dashboard project'})
df.to_csv(OUT, index=False)
print(f'Saved {len(df):,} rows to {OUT}')
print('Date range:', df['date'].min(), 'to', df['date'].max())
print('Columns:', len(df.columns))

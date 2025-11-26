import pandas as pd
import yfinance as yf
from lme_data import scrape_lme_data

def basis_spread_calc():

    # Load data
    comex_daily = yf.download('HG=F', start='2015-01-01', auto_adjust = False, progress = False)['Adj Close']
    lme_daily   = scrape_lme_data()['three_month']

    # Ensure datetime index
    comex_daily.index = pd.to_datetime(comex_daily.index)
    lme_daily.index   = pd.to_datetime(lme_daily.index)

    # Resample BOTH to business days + forward fill
    comex_daily = comex_daily.resample('B').last().ffill()
    lme_daily   = lme_daily.resample('B').last().ffill()

    # Now merge (inner join gives overlapping, aligned dates)
    df = pd.concat([comex_daily, lme_daily], axis=1, join='inner')
    df.columns = ['COMEX', 'LME_3M']

    # Convert COMEX to USD/tonne
    df['COMEX_tonne'] = (df['COMEX'] * 2204.62).round(2)

    # Basis
    df['Basis_USD_t'] = df['COMEX_tonne'] - df['LME_3M']

    return df

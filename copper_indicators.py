import pandas as pd 
import numpy as np 
import yfinance as yf
from lme_data import scrape_lme_data
from visible_inv_data import load_visible_inv
from cftc_net_shorts import load_net_shorts_data
from copper_basis_spread import basis_spread_calc

class CopperIndicators:
    ''''
    Covers 4 indicators for gauging the whether the copper markets are in a short squeeze or not - 
    1. Backwardation (%): Calculated as (LME Cash-3M Spread / 3M Prices) as per LME convention; Historical period - past 5 years; Frequency - Daily
    2. Visible Inventory: Sum of copper inventory reported by LME and COMEX at the end of every week; Historical period - past 10 years; Frequency - Weekly 
    3. CFTC Net Shorts (Inverted): Calculated as (Total Short Positions - Total Long Positions) on Copper futures as reported by the CFTC every week; Historical period - past 8 years; Frequency - Weekly
    4. Basis Spread: Calculated as the spread between COMEX near-month copper futures and LME 3-month copper futures; Historical period - past 10 years, Frequency - Daily

    Returns the percentile ranks of the latest values for each indicator compared to their historical data 
    '''
    def __init__(self):
        self.lme      = scrape_lme_data()       # has cash, 3m, spread
        self.inv      = load_visible_inv()      # LME + COMEX summed
        self.cftc     = load_net_shorts_data()  # inverted net shorts
        self.basis    = basis_spread_calc()     # COMEX − LME in USD/t

    def get_all(self):
        # Backwardation (5Y)
        bck = self.lme['cash_3m_spread'] / self.lme['three_month']
        bck_5y = bck[bck.index >= bck.index[-1] - pd.DateOffset(years=5)]
        backwardation_pct = float((bck_5y <= bck_5y.iloc[-1]).mean() * 100)
    
        # Inventory tightness (10Y)
        # Raw % of history with lower stocks than today
        inv_10y = self.inv['visible_inv']
        inv_10y = inv_10y[inv_10y.index >= inv_10y.index[-1] - pd.DateOffset(years=10)]
        inv_pct_raw = (inv_10y <= inv_10y.iloc[-1]).mean() * 100          # lower inventory = higher risk
        inventory_tightness = float(100 - inv_pct_raw)                          # invert → high = tight
    
        # CFTC net shorts (8Y) 
        cftc_8y = self.cftc['Net_Shorts']
        cftc_8y = cftc_8y[cftc_8y.index >= cftc_8y.index[-1] - pd.DateOffset(years=8)]
        cftc_pct = float((cftc_8y <= cftc_8y.iloc[-1]).mean() * 100)
    
        # COMEX-LME basis (10Y) 
        basis_10y = self.basis['Basis_USD_t']
        basis_10y = basis_10y[basis_10y.index >= basis_10y.index[-1] - pd.DateOffset(years=10)]
        basis_pct_raw = float((basis_10y <= basis_10y.iloc[-1]).mean() * 100)
        basis_points = min(basis_pct_raw, 25.0)                           # capped bonus

        return {
        'backwardation_pct':       round(backwardation_pct, 1),
        'inventory_tightness':     round(inventory_tightness, 1),
        'cftc_pct':                round(cftc_pct, 1),
        'basis_pct':               round(basis_points, 1),
        }

    def compute_percentiles_from_raw(self, raw):
        # Backwardation (5Y)
        cash = raw.get('cash_price', self.lme['cash'].iloc[-1])
        three_m = raw.get('three_m_price', self.lme['three_month'].iloc[-1])
        current_bck = (cash - three_m) / three_m
    
        bck_series = (self.lme['cash'] - self.lme['three_month']) / self.lme['three_month']
        cutoff = bck_series.index[-1] - pd.DateOffset(years=5)
        bck_5y = bck_series[bck_series.index >= cutoff]
        backwardation_pct = float((bck_5y <= current_bck).mean() * 100)
    
        # Inventory tightness (10Y) — inverted
        inv = raw.get('inventory_tonnes', self.inv['visible_inv'].iloc[-1])
        inv_series = self.inv['visible_inv']
        cutoff = inv_series.index[-1] - pd.DateOffset(years=10)
        inv_10y = inv_series[inv_series.index >= cutoff]
        inv_tightness = float((inv_10y >= inv).mean() * 100)  # lower inv = higher score
        inventory_score = 100 - inv_tightness
    
        # CFTC net shorts (8Y)
        net_short = raw.get('net_shorts', self.cftc['Net_Shorts'].iloc[-1])
        cftc_series = self.cftc['Net_Shorts']
        cutoff = cftc_series.index[-1] - pd.DateOffset(years=8)
        cftc_8y = cftc_series[cftc_series.index >= cutoff]
        cftc_pct = float((cftc_8y <= net_short).mean() * 100)
    
        # Basis (10Y)
        basis_t = 0
        if 'comex_price_usd_lb' in raw:
            lme3m = raw.get('three_m_price', self.lme['three_month'].iloc[-1])
            basis_t = (raw['comex_price_usd_lb'] * 2204.62) - lme3m
    
            basis_series = self.basis['Basis_USD_t']
            cutoff = basis_series.index[-1] - pd.DateOffset(years=10)
            basis_10y = basis_series[basis_series.index >= cutoff]
            basis_pct = float((basis_10y <= basis_t).mean() * 100)
        else:
            basis_pct = self.get_all()['basis_pct']
    
        return {
        'backwardation_pct': round(backwardation_pct, 1),
        'inventory_tightness': round(inventory_score, 1),
        'cftc_pct': round(cftc_pct, 1),
        'basis_pct': round(basis_pct, 1)
        }
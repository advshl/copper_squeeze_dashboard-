import pandas as pd
import numpy as np 

def load_net_shorts_data():
    '''
    Imports the net shorts data on Copper from the period 2017 to 2025 (November) as reported by the CFTC 
    
    Data has been already aggregated from the CTFC website and saved in the cftc_copper_net_shorts_2017_2025.csv for convenience

    Net Shorts = Total Reported Short Positions - Total Reported Long Positions 
    '''

    df_net_shorts = pd.read_csv('cftc_copper_net_shorts_2017_2025.csv', index_col = 'Date', parse_dates = ['Date'])
    
    return df_net_shorts
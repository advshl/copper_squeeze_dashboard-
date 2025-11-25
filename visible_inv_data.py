import pandas as pd 
import numpy as np 

def load_visible_inv():
    '''
    Function to load the weekly data for visible copper stocks on LME and COMEX exchanges from 2015 to 2025 (November)
    
    Visible Weekly Inventory = COMEX Weekly Inventory + LME Weekly Inventory
    
    LME Inventory data has been scrapped from westmettal.com and verified; Saved in lme_copper_data.csv
    
    COMEX Inventory data has been downloaded from datatrack.trendforce.com and verified; Saved in comex_copper_inventory.csv

    Function loads both databases, resamples them to weekly data, aligns datetime indices them, concatenates them and calculates the weekly visible copper inventory
    
    '''
    
    # Load COMEX inventory data
    df_comex = pd.read_csv('comex_copper_inventory.csv', index_col = 'date', parse_dates = ['date'])
    df_comex.rename(columns = {'COMEX Inventory: Copper (short ton)' : 'comex_inventory'}, inplace = True)

    # Converting to metric tons from short tons
    df_comex['comex_inventory'] = (df_comex.comex_inventory * 0.90718474).round(0)

    # Remove timezone (or convert to naive)
    df_comex.index = df_comex.index.tz_localize(None)

    # Load LME inventory data
    df_lme = pd.read_csv('lme_copper_data.csv', index_col = 'date', parse_dates = ['date'])['lme_copper_stock']

    # Resample daily data to weekly data
    df_lme_weekly = df_lme.resample('W-FRI').last()
    df_comex_weekly = df_comex.resample('W-FRI').last()

    # Concatenating both dataframes to get the visible inventory database
    df_inv = pd.concat([df_lme_weekly, df_comex_weekly], axis=1)

    # Totalling both stocks
    df_inv['visible_inv'] = df_inv.lme_copper_stock + df_inv.comex_inventory

    return df_inv
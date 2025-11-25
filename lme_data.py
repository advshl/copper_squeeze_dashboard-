import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

def scrape_lme_data():
    """
    Scrape LME Copper data from westmetall.com and calculate Cash-3M spread from westmetall.com; Data has been verified 
    """
    url = "https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Cu_cash"

    # print("Fetching data from ", {url})
    
    # Send GET request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all tables
    tables = soup.find_all('table')
    
    all_data = []
    
    for table in tables:
        rows = table.find_all('tr')
        
        for row in rows[1:]:  # Skip header row
            cols = row.find_all('td')
            if len(cols) >= 3:
                date_str = cols[0].get_text(strip=True)
                cash = cols[1].get_text(strip=True)
                three_month = cols[2].get_text(strip=True)
                lme_copper_stock = cols[3].get_text(strip=True)
                
                # Skip if it's a header row or empty
                if date_str.lower() in ['date', 'copper'] or not date_str:
                    continue
                
                # Parse date
                try:
                    # Convert "31. October 2025" to datetime
                    date_clean = date_str.replace('.', '')
                    date_obj = datetime.strptime(date_clean, '%d %B %Y')
                    
                    # Filter for years 2020-2025
                    if 2015 <= date_obj.year <= 2025:
                        # Clean numeric values
                        cash_clean = float(cash.replace(',', ''))
                        three_month_clean = float(three_month.replace(',', ''))
                        lme_copper_stock_clean = float(lme_copper_stock.replace(',', ''))
                        
                        all_data.append({
                            'date': date_obj,
                            'cash': cash_clean,
                            'three_month': three_month_clean,
                            'lme_copper_stock': lme_copper_stock_clean
                        })
                except (ValueError, AttributeError) as e:
                    continue
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Sort by date
    df = df.sort_values('date').reset_index(drop=True)

    # Converting date column to datetime format and setting it as the index
    df.date = pd.to_datetime(df.date)
    df.set_index('date', drop = True, inplace = True)
    
    # Calculate Cash-3M Spread
    df['cash_3m_spread'] = df['cash'] - df['three_month']

    
    # print(f"\nSuccessfully scraped {len(df)} records from {df.index.min().date()} to {df.index.max().date()}")
    
    return df
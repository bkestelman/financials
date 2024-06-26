import requests
import pandas as pd
import json
import re
from datetime import datetime

def get_financial_data(ticker):
    cik_url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={ticker}&Find=Search&owner=exclude&action=getcompany"
    response = requests.get(cik_url, headers={'User-Agent': 'My User Agent 1.0'})
    cik_search = re.search(r'CIK=(\d{10})', response.text)
    if not cik_search:
        print(f"Could not find CIK for ticker {ticker}")
        return None
    cik = cik_search.group(1)
    print(f"Found CIK: {cik}")

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json"
    print(f"Requesting data from: {url}")
    
    response = requests.get(url, headers={'User-Agent': 'My User Agent 1.0'})
    
    if response.status_code != 200:
        print(f"Failed to retrieve data: HTTP {response.status_code}")
        return None

    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Failed to decode JSON.")
        return None

    financials = {}
    facts = data.get('facts', {}).get('us-gaap', {})
    
    metrics = [
        'RevenueFromContractWithCustomerExcludingAssessedTax',
        'NetIncomeLoss'
    ]

    for metric in metrics:
        if metric in facts:
            print(f"Processing metric: {metric}")
            units = facts[metric].get('units', {})
            if 'USD' in units:
                # Filter for 10-K filings
                annual_values = [v for v in units['USD'] if v.get('form') == '10-K']
                annual_values.sort(key=lambda x: x['end'], reverse=True)
                
                print(f"Found {len(annual_values)} 10-K values for {metric}")
                
                last_3_years = annual_values[:3]
                
                financials[metric] = [year['val'] for year in last_3_years]
            else:
                print(f"No USD values found for {metric}")
        else:
            print(f"Metric {metric} not found in the data")

    return financials

def save_to_csv(data, filename):
    rows = []
    for metric, values in data.items():
        row = [metric] + values + ['N/A'] * (3 - len(values))  # Pad with 'N/A' if less than 3 years of data
        rows.append(row)
    
    df = pd.DataFrame(rows, columns=['Metric', 'Latest 10-K Value', '1 Year Ago Value', '2 Years Ago Value'])
    df.to_csv(filename, index=False)

# Example usage
ticker = 'AAPL'  # Apple Inc.
financial_data = get_financial_data(ticker)

if financial_data:
    save_to_csv(financial_data, f'{ticker}_financials.csv')
    print(f"Financial data for {ticker} has been saved to {ticker}_financials.csv")
else:
    print(f"No financial data found for {ticker}")

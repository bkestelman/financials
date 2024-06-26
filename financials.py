import requests
import pandas as pd
import json
import re

def get_financial_data(ticker):
    # First, we need to get the CIK number
    cik_url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={ticker}&Find=Search&owner=exclude&action=getcompany"
    response = requests.get(cik_url, headers={'User-Agent': 'My User Agent 1.0'})
    cik_search = re.search(r'CIK=(\d{10})', response.text)
    if not cik_search:
        print(f"Could not find CIK for ticker {ticker}")
        return None
    cik = cik_search.group(1)

    # Now we can use the CIK to get the financial data
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json"
    
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
    
    # List of common financial metrics to extract
    metrics = [
        'Assets', 'Liabilities', 'StockholdersEquity',
        'CashAndCashEquivalentsAtCarryingValue',
        'RevenueFromContractWithCustomerExcludingAssessedTax',
        'CostOfGoodsAndServicesSold', 'GrossProfit',
        'OperatingIncomeLoss', 'NetIncomeLoss',
        'EarningsPerShareBasic', 'EarningsPerShareDiluted'
    ]

    for metric in metrics:
        if metric in facts:
            units = facts[metric].get('units', {})
            if 'USD' in units:
                # Get the most recent value
                value = sorted(units['USD'], key=lambda x: x['end'])[-1]['val']
                financials[metric] = value
            elif 'USD/shares' in units:
                # For per-share metrics
                value = sorted(units['USD/shares'], key=lambda x: x['end'])[-1]['val']
                financials[metric] = value

    return financials

def save_to_csv(data, filename):
    df = pd.DataFrame(list(data.items()), columns=['Metric', 'Value'])
    df.to_csv(filename, index=False)

# Example usage
ticker = 'AAPL'  # Apple Inc.
financial_data = get_financial_data(ticker)

if financial_data:
    save_to_csv(financial_data, f'{ticker}_financials.csv')
    print(f"Financial data for {ticker} has been saved to {ticker}_financials.csv")
else:
    print(f"No financial data found for {ticker}")

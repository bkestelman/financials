import requests
import pandas as pd
import json
import re

def get_cik(ticker):
    cik_url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={ticker}&Find=Search&owner=exclude&action=getcompany"
    response = requests.get(cik_url, headers={'User-Agent': 'My User Agent 1.0'})
    cik_search = re.search(r'CIK=(\d{10})', response.text)
    if not cik_search:
        print(f"Could not find CIK for ticker {ticker}")
        return None
    return cik_search.group(1)

def get_financial_data(ticker):
    cik = get_cik(ticker)
    if not cik:
        return None

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

    metrics = [
        'RevenueFromContractWithCustomerExcludingAssessedTax',
        'NetIncomeLoss',
        'PaymentsOfDividends',
        'EarningsPerShareBasic',
        'EarningsPerShareDiluted',
        'WeightedAverageNumberOfSharesOutstandingBasic',
        'CommonStockSharesOutstanding'
    ]

    report_dates = set()  # Use a set to collect unique dates

    for metric in metrics:
        if metric in facts:
            units = facts[metric].get('units', {})
            if 'USD' in units or 'USD/shares' in units or 'shares' in units:
                values = units.get('USD') or units.get('USD/shares') or units.get('shares')
                annual_values = [v for v in values if v.get('form') == '10-K']
                annual_values.sort(key=lambda x: x['end'], reverse=True)
                financials[metric] = [(year['val'], year['end']) for year in annual_values[:3]]
                report_dates.update(year['end'] for year in annual_values[:3])
            else:
                print(f"No appropriate units found for {metric}")
        else:
            print(f"Metric {metric} not found in the data")

    # Add report dates
    financials['ReportDate'] = sorted(report_dates, reverse=True)[:3]  # Get the last 3 unique dates

    return financials

def save_to_csv(data, filename):
    rows = []
    for metric, values in data.items():
        if metric == 'ReportDate':
            row = [metric] + values + ['N/A'] * (3 - len(values))
        else:
            row = [metric] + [val[0] for val in values] + ['N/A'] * (3 - len(values))
        rows.append(row)

    df = pd.DataFrame(rows, columns=['Metric', 'Latest 10-K Value', '1 Year Ago Value', '2 Years Ago Value'])
    df.to_csv(filename, index=False)

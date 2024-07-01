import requests
from datetime import datetime, timedelta

def get_adjusted_close(ticker, api_key, date):
    base_url = "https://www.alphavantage.co/query"
    function = "TIME_SERIES_WEEKLY_ADJUSTED"
    
    params = {
        "function": function,
        "symbol": ticker,
        "apikey": api_key
    }

    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if "Weekly Adjusted Time Series" in data:
            # Convert input date to datetime object
            target_date = datetime.strptime(date, "%Y-%m-%d")
            
            # Find the closest available date on or before the requested date
            available_dates = sorted(data["Weekly Adjusted Time Series"].keys(), reverse=True)
            closest_date = next((d for d in available_dates if datetime.strptime(d, "%Y-%m-%d") <= target_date), None)
            
            if closest_date:
                adjusted_close = data["Weekly Adjusted Time Series"][closest_date]["5. adjusted close"]
                return float(adjusted_close), closest_date
            else:
                print(f"No data found on or before {date} for {ticker}")
                return None, None
        else:
            print(f"No weekly time series found for {ticker}")
            return None, None
    else:
        print(f"Failed to retrieve data: HTTP {response.status_code}")
        return None, None

def save_to_csv(data, filename):
    import pandas as pd
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

if __name__ == "__main__":
    api_key = "YOUR_ALPHA_VANTAGE_API_KEY"
    ticker = "AAPL"
    date = "2023-06-30"  # Example date
    adjusted_close, actual_date = get_adjusted_close(ticker, api_key, date)
    
    if adjusted_close:
        data = [{"Ticker": ticker, "ReportDate": date, "ActualDate": actual_date, "AdjustedClose": adjusted_close}]
        save_to_csv(data, f'{ticker}_market_data.csv')
        print(f"Market data for {ticker} has been saved to {ticker}_market_data.csv")
    else:
        print(f"Failed to retrieve market data for {ticker}")

from sec_edgar import get_financial_data, save_to_csv as save_sec_data
from alpha_vantage import get_adjusted_close, save_to_csv as save_av_data

def main():
    ticker = "AAPL"
    api_key = "ZEMW0TBXKGIFOSVT"

    # Get SEC Edgar data
    financial_data = get_financial_data(ticker)
    if financial_data:
        save_sec_data(financial_data, f'{ticker}_sec_financials.csv')
        print(f"SEC financial data for {ticker} has been saved to {ticker}_sec_financials.csv")

        # Get AlphaVantage data for each report date
        market_data = []
        for date in financial_data['ReportDate']:
            adjusted_close, actual_date = get_adjusted_close(ticker, api_key, date)
            if adjusted_close:
                market_data.append({
                    "Ticker": ticker,
                    "ReportDate": date,
                    "ActualDate": actual_date,
                    "AdjustedClose": adjusted_close
                })
            else:
                print(f"Failed to retrieve market data for {ticker} on {date}")

        if market_data:
            save_av_data(market_data, f'{ticker}_market_data.csv')
            print(f"Market data for {ticker} has been saved to {ticker}_market_data.csv")
        else:
            print(f"No market data found for {ticker}")
    else:
        print(f"No SEC financial data found for {ticker}")

if __name__ == "__main__":
    main()

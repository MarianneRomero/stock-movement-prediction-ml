import yfinance as yf

tickers = ["AAPL", "MSFT", "GOOG", "AMZN", "SPY"]

print("Downloading historical stock data...")
data = yf.download(tickers, start="2020-01-01", end="2025-01-01")

data.to_csv("../data/stock_data_raw.csv")
print(f"Raw data saved to data/stock_data_raw.csv")

print("Creating target variables...")
for ticker in tickers:
    data[('Target', ticker)] = (data[('Close', ticker)].shift(-1) > data[('Close', ticker)]).astype(int)

# Drop last row (targets for last day are NaN)
data = data.iloc[:-1]

data.to_csv("../data/stock_data_with_target.csv")
print(f"Processed data with targets saved to data/stock_data_with_target.csv")

print("Sample data:")
print(data.head())
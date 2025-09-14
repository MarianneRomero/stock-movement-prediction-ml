import yfinance as yf
import os
import yaml
from pathlib import Path


project_root = Path(__file__).resolve().parents[2]
config_path = project_root / "config.yaml"

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

tickers = config['tickers']
macro_tickers = config['macro_tickers']
market_indices = config['market_indices']

start_date = "2020-01-01"
end_date = "2025-01-01"


raw_data_path = project_root / config["data"]["raw"]
interim_data_path = project_root / config["data"]["interim"]
os.makedirs(raw_data_path, exist_ok=True)
os.makedirs(interim_data_path, exist_ok=True)


print("Downloading stock data...")
stock_data = yf.download(tickers, start=start_date, end=end_date)
stock_data.stack(level=1).reset_index()
stock_data.to_csv(raw_data_path / "stock_data_raw.csv")

print("Downloading macro data...")
macro_data = yf.download(macro_tickers, start=start_date, end=end_date)['Close']
macro_data.rename(columns={'^VIX':'VIX', 'CL=F':'WTI_Oil', '^TNX':'US10Y'}, inplace=True)
macro_data = macro_data.ffill()
macro_data.to_csv(raw_data_path / "macro_data_raw.csv")

print("Downloading market data...")
market_data = yf.download(market_indices, start=start_date, end=end_date)['Close']
market_data.rename(columns={'^GSPC':'GSPC', '^NDX':'NDX', '^RUT':'RUT', '^DJI':'DJI'}, inplace=True)
market_data.to_csv(raw_data_path / "market_data_raw.csv")

# Merge stock and macro data
stock_data_long_format = stock_data.stack(level=1).reset_index()
stock_data_long_format = stock_data_long_format.merge(macro_data.reset_index(), on='Date', how='left')
stock_data_long_format = stock_data_long_format.merge(market_data.reset_index(), on='Date', how='left')

# Creating target variables
# defining three classes to eliminate noise: up, down, flat
# threshold = 0.005  # 0.5%
# future_return = (stock_data_long_format.groupby('Ticker')['Close'].shift(-1) / stock_data_long_format['Close']) - 1
# stock_data_long_format['Target'] = 1  # default
# stock_data_long_format.loc[future_return > threshold, 'Target'] = 2
# stock_data_long_format.loc[future_return < -threshold, 'Target'] = 0


# 3-day horizon
future_return_3d = (stock_data_long_format.groupby('Ticker')['Close'].shift(-3) / stock_data_long_format['Close']) - 1
threshold_3d = 0.002
stock_data_long_format['Target'] = 1
stock_data_long_format.loc[future_return_3d > threshold_3d, 'Target'] = 2
stock_data_long_format.loc[future_return_3d < -threshold_3d, 'Target'] = 0

# stock_data_long_format['Target'] = stock_data_long_format.groupby('Ticker')['Close'].shift(-1) > stock_data_long_format['Close']
# stock_data_long_format['Target'] = stock_data_long_format['Target'].astype(int)
# stock_data_long_format = stock_data_long_format.dropna(subset=['Target'])



stock_data_long_format.to_csv(interim_data_path / "data_with_target.csv")
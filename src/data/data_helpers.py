import yaml
from pathlib import Path
import yfinance as yf

project_root = Path(__file__).resolve().parents[2]
config_path = project_root / "config.yaml"

with open(config_path, "r") as f:
    config = yaml.safe_load(f)


tickers = config['tickers']
macro_tickers = config['macro_tickers']
market_indices = config['market_indices']


def load_data(start_date, end_date):
    print("Downloading stock data...")
    stock_data = yf.download(tickers, start=start_date, end=end_date)
    stock_data.stack(level=1).reset_index()

    print("Downloading macro data...")
    macro_data = yf.download(macro_tickers, start=start_date, end=end_date)['Close']
    macro_data.rename(columns={'^VIX':'VIX', 'CL=F':'WTI_Oil', '^TNX':'US10Y'}, inplace=True)
    macro_data = macro_data.ffill()

    print("Downloading market data...")
    market_data = yf.download(market_indices, start=start_date, end=end_date)['Close']
    market_data.rename(columns={'^GSPC':'GSPC', '^NDX':'NDX', '^RUT':'RUT', '^DJI':'DJI'}, inplace=True)


    stock_data_long_format = stock_data.stack(level=1).reset_index()
    stock_data_long_format = stock_data_long_format.merge(macro_data.reset_index(), on='Date', how='left')
    stock_data_long_format = stock_data_long_format.merge(market_data.reset_index(), on='Date', how='left')

    print("Adding target variable for 3-day horizon...")
    stock_data_long_format["Target"] = stock_data_long_format.groupby('Ticker')['Close'].pct_change(3).shift(-3)

    return stock_data_long_format
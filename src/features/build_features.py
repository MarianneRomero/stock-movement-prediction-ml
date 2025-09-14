import yaml
from pathlib import Path
import pandas as pd
import talib

project_root = Path(__file__).resolve().parents[2]
config_path = project_root / "config.yaml"

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

interim_data_path = raw_data_path = project_root / config["data"]["interim"] / "data_with_target.csv"
processed_data_path = raw_data_path = project_root / config["data"]["processed"] / "data_with_fts.csv"


data = pd.read_csv(interim_data_path, index_col=0)


# ===== Macro features =====

macro_tickers = ['VIX', 'WTI_Oil', 'US10Y']  # VIX, WTI Oil, 10Y Treasury

data['VIX_ret'] = data['VIX'].pct_change()
data['WTI_ret'] = data['WTI_Oil'].pct_change()
data['TNX_ret'] = data['US10Y'].pct_change()

data['VIX_5d_mean'] = data['VIX'].rolling(5).mean()
data['WTI_5d_std'] = data['WTI_Oil'].rolling(5).std()


# ===== Market indices features =====

market_indices = ["GSPC", "NDX", "RUT", "DJI"]

for idx in market_indices:
    data[f'{idx}_return_1d'] = data[idx].pct_change()
    data[f'{idx}_return_5d'] = data[idx].pct_change(5)


# =====  Stock features =====

data['return_1d'] = data.groupby('Ticker')['Close'].pct_change()
data['return_3d'] = data.groupby('Ticker')['Close'].pct_change(3)
data['return_5d'] = data.groupby('Ticker')['Close'].pct_change(5)
data['return_10d'] = data.groupby('Ticker')['Close'].pct_change(10)

data['ma_5'] = data.groupby('Ticker')['Close'].transform(lambda x: x.rolling(window=5).mean())
data['ma_20'] = data.groupby('Ticker')['Close'].transform(lambda x: x.rolling(window=20).mean())

data['price_ma5_ratio'] = data['Close'] / data['ma_5']
data['price_ma20_ratio'] = data['Close'] / data['ma_20']

data['volume_ratio'] = (
    data['Volume'] / 
    data.groupby('Ticker')['Volume'].transform(lambda x: x.rolling(20).mean())
)

data['price_volume'] = data['return_1d'] * data['Volume']

data['rsi'] = data.groupby('Ticker')['Close'].transform(
    lambda x: talib.RSI(x.values, timeperiod=14)
)

data['macd'] = data.groupby('Ticker')['Close'].transform(lambda x: x.ewm(span=12, adjust=False).mean() - x.ewm(span=26, adjust=False).mean())
data['macd_signal'] = data.groupby('Ticker')['macd'].transform(lambda x: x.ewm(span=9, adjust=False).mean())
data['macd_hist'] = data['macd'] - data['macd_signal'] 




data = data.dropna()


data.to_csv(processed_data_path)
import pandas as pd
import talib

def create_features(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()

    # ===== Macro features =====
    macro_tickers = ['VIX', 'WTI_Oil', 'US10Y']
    df['VIX_ret'] = df['VIX'].pct_change()
    df['WTI_ret'] = df['WTI_Oil'].pct_change()
    df['TNX_ret'] = df['US10Y'].pct_change()
    df['VIX_5d_mean'] = df['VIX'].rolling(5).mean()
    df['WTI_5d_std'] = df['WTI_Oil'].rolling(5).std()

    # ===== Market indices features =====
    market_indices = ["GSPC", "NDX", "RUT", "DJI"]
    for idx in market_indices:
        df[f'{idx}_return_1d'] = df[idx].pct_change()
        df[f'{idx}_return_5d'] = df[idx].pct_change(5)

    # ===== Stock returns =====
    for period in [1, 3, 5, 10]:
        df[f'return_{period}d'] = df.groupby('Ticker')['Close'].pct_change(period)

    # ===== Rolling volatility =====
    df['rolling_std_5'] = df.groupby('Ticker')['Close'].transform(lambda x: x.rolling(5).std())
    df['rolling_std_10'] = df.groupby('Ticker')['Close'].transform(lambda x: x.rolling(10).std())

    # ===== Moving averages and ratios =====
    df['ma_5'] = df.groupby('Ticker')['Close'].transform(lambda x: x.rolling(5).mean())
    df['ma_20'] = df.groupby('Ticker')['Close'].transform(lambda x: x.rolling(20).mean())
    df['price_ma5_ratio'] = df['Close'] / df['ma_5']
    df['price_ma20_ratio'] = df['Close'] / df['ma_20']
    df['MA5_MA20_diff'] = df['ma_5'] - df['ma_20']
    df['MA5_MA20_ratio'] = df['ma_5'] / df['ma_20']

    # ===== Volume features =====
    df['vol_MA5'] = df.groupby('Ticker')['Volume'].transform(lambda x: x.rolling(5).mean())
    df['vol_MA20'] = df.groupby('Ticker')['Volume'].transform(lambda x: x.rolling(20).mean())
    df['vol_ratio_5'] = df['Volume'] / df['vol_MA5']
    df['vol_ratio_20'] = df['Volume'] / df['vol_MA20']
    df['price_volume'] = df['return_1d'] * df['Volume']

    # ===== Momentum indicators =====
    df['rsi'] = df.groupby('Ticker')['Close'].transform(lambda x: talib.RSI(x.values, timeperiod=14))
    df['macd'] = df.groupby('Ticker')['Close'].transform(lambda x: x.ewm(span=12, adjust=False).mean() - x.ewm(span=26, adjust=False).mean())
    df['macd_signal'] = df.groupby('Ticker')['macd'].transform(lambda x: x.ewm(span=9, adjust=False).mean())
    df['macd_hist'] = df['macd'] - df['macd_signal']
    df.drop(columns=['macd_signal'], inplace=True)

    # ===== True Range & ATR =====
    df['tr'] = df['High'] - df['Low']
    df['tr1'] = abs(df['High'] - df['Close'].shift(1))
    df['tr2'] = abs(df['Low'] - df['Close'].shift(1))
    df['true_range'] = df[['tr', 'tr1', 'tr2']].max(axis=1)
    df['ATR_14'] = df.groupby('Ticker')['true_range'].transform(lambda x: x.rolling(14).mean())
    df['ATR_7'] = df.groupby('Ticker')['true_range'].transform(lambda x: x.rolling(7).mean())
    df.drop(columns=['tr','tr1','tr2','true_range'], inplace=True)

    # ===== Bollinger Bands =====
    ma20 = df.groupby('Ticker')['Close'].transform(lambda x: x.rolling(20).mean())
    std20 = df.groupby('Ticker')['Close'].transform(lambda x: x.rolling(20).std())
    df['BB_width'] = (2 * std20) / ma20

    # ===== Price Range Features =====
    df['range_pct'] = (df['High'] - df['Low']) / df['Close']
    df['OC_pct'] = (df['Close'] - df['Open']) / df['Close']
    df['range_5d'] = df.groupby('Ticker').apply(lambda x: (x['High'].rolling(5).max() - x['Low'].rolling(5).min()) / x['Close']).reset_index(level=0, drop=True)

    # ===== Fill NaNs =====
    df.bfill(inplace=True)
    df.ffill(inplace=True)

    return df

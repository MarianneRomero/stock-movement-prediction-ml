from sklearn.preprocessing import OneHotEncoder
import yaml
from pathlib import Path
from datetime import date, timedelta
import joblib
from features.feature_helpers import create_features
from data.data_helpers import load_data
import pandas as pd

project_root = Path(__file__).resolve().parents[2]
config_path = project_root / "config.yaml"

with open(config_path, "r") as f:
    config = yaml.safe_load(f)


tickers = config['tickers']
macro_tickers = config['macro_tickers']
market_indices = config['market_indices']

feature_columns = config['features']['returns']\
    + config['features']['rolling_volatility']\
    + config['features']['moving_avg']\
    + config['features']['momentum_indicators']\
    + config['features']['macro_features']\
    + config['features']['volume_features']\
    + config['features']['market_index_features']\
    + config['features']['atr']\
    + config['features']['bb']\
    + config['features']['price_range']
# add one-hot encoded values


model = joblib.load(Path(__file__).resolve().parent / "xgb_model.pkl")

class PredictionBuilder:

    new_data = None
    daily_returns_df = None
    feature_columns = feature_columns
    portfolio_returns_df = None


    def __init__(self):
        yesterday = date.today() - timedelta(days=1)
        self.new_data = self.get_new_data("2025-01-02", yesterday.strftime("%Y-%m-%d"))
        self._compute_daily_returns_per_stock()
        # Compute portfolio-level daily returns
        self._compute_portfolio_returns()
    

    def get_new_data(self, start_date, end_date):
        # get data from yhfinance
        data = load_data(start_date, end_date)
        data_with_fts = create_features(data)

        # one-hot encore ticker values

        encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
        encoded_values = encoder.fit_transform(data_with_fts[['Ticker']])
        new_cols = encoder.get_feature_names_out(['Ticker'])
        # self.feature_columns += new_cols.tolist()

        tickers_encoded = pd.DataFrame(encoded_values, columns=new_cols, index=data_with_fts.index)
        data_with_fts = pd.concat([data_with_fts, tickers_encoded], axis=1)

        # make predictions
        X_backtesting = data_with_fts[feature_columns]
        data_with_fts["Prediction"] = model.predict(X_backtesting)

        return data_with_fts
    

    def _compute_daily_returns_per_stock(self, top_pct=0.2, bottom_pct=0.2):
        """
        Compute daily returns per stock using regression predictions.
        """
        df = self.new_data.copy()
        df['StrategyReturn'] = 0.0

        for date, group in df.groupby('Date'):
            group = group.copy()
            n_stocks = len(group)
            n_top = max(1, int(top_pct * n_stocks))
            n_bottom = max(1, int(bottom_pct * n_stocks))

            top_stocks = group.nlargest(n_top, 'Prediction')['Ticker']
            bottom_stocks = group.nsmallest(n_bottom, 'Prediction')['Ticker']

            df.loc[(df['Date'] == date) & (df['Ticker'].isin(top_stocks)), 'StrategyReturn'] = \
                group.loc[group['Ticker'].isin(top_stocks), 'Target']
            df.loc[(df['Date'] == date) & (df['Ticker'].isin(bottom_stocks)), 'StrategyReturn'] = \
                -group.loc[group['Ticker'].isin(bottom_stocks), 'Target']
        
        df = df.sort_values(['Ticker', 'Date'])
        
        # Create a mask for traded days
        df['Traded'] = df['StrategyReturn'] != 0
        
        # Cumulative return only counting traded days
        df['CumulativeReturn'] = df.groupby('Ticker').apply(
            lambda x: (1 + x[x['Traded']]['StrategyReturn']).cumprod().reindex(x.index, method='ffill').fillna(1) - 1
        ).reset_index(level=0, drop=True)
        
        self.daily_returns_df = df

    def _compute_portfolio_returns(self):
        """
        Compute aggregate portfolio returns across all stocks for each day.
        Assumes equal weighting across positions.
        """
        # Get daily portfolio return (average of all active positions each day)
        portfolio_daily = self.daily_returns_df.groupby('Date').agg({
            'StrategyReturn': ['mean', 'sum', 'count'],  # mean for equal weight, sum for total
            'Traded': 'sum'  # number of positions
        }).reset_index()
        
        portfolio_daily.columns = ['Date', 'DailyReturn_EqualWeight', 'DailyReturn_Sum', 
                                'TotalPositions', 'ActivePositions']
        
        # Cumulative portfolio return (what you actually earned)
        portfolio_daily['CumulativeReturn'] = (1 + portfolio_daily['DailyReturn_EqualWeight']).cumprod() - 1
        
        self.portfolio_returns_df = portfolio_daily
    

    def get_portfolio_performance(self):
        """Return portfolio-level performance over time."""
        df = self.portfolio_returns_df.copy()
        df['Date'] = df['Date'].astype(str)
        return {
            "portfolioReturns": df.to_dict(orient='records')
        }

    
    def get_daily_returns_per_stock(self):
        # Ensure Date is string for JSON
        df = self.daily_returns_df.copy()
        df['Date'] = df['Date'].astype(str)
        return {"dailyReturns": df[['Date', 'Ticker', 'Prediction', 'Target', 'StrategyReturn', 'CumulativeReturn']].to_dict(orient='records')}
    
    
    def get_stats(self):
        avgTrade = self.get_avg_trade()
        stdDev = self.daily_returns_df["StrategyReturn"].std()
        sharpe = avgTrade / stdDev

        return {
            "totalReturn": self.get_total_return(),
            # "buyHoldReturn": finalBuyHold,
            "sharpe": sharpe,
            "winRate": self.get_win_rate(),
            "maxDrawdown": self.get_portfolio_max_drawdown(),
            "totalTrades": self.get_total_trades(),
            "avgTrade": avgTrade
        }
    

    def get_win_rate(self):
        """Get win rate (trades with StrategyReturn > 0)"""
        positive_trades = (self.daily_returns_df["StrategyReturn"] > 0).sum()
        total_trades = (self.daily_returns_df["StrategyReturn"] != 0).sum()
        return positive_trades / total_trades
    
    def get_avg_trade(self):
        trades = self.daily_returns_df.loc[self.daily_returns_df["StrategyReturn"] != 0, "StrategyReturn"]
        return trades.mean()
    
    def get_total_trades(self):
        return int((self.daily_returns_df["StrategyReturn"] != 0).sum())
    
    def get_total_return(self):
        # compounded, averaged over all stocks
        daily_portfolio_returns = self.daily_returns_df.groupby("Date")["StrategyReturn"].mean()
        return  (1 + daily_portfolio_returns).prod() - 1
    
    def get_portfolio_max_drawdown(self):
        """Calculate the maximum drawdown of the entire portfolio."""
        if self.portfolio_returns_df.empty:
            return 0.0
        
        # Use your portfolio daily return column (adjust the column name as needed)
        returns = self.portfolio_returns_df["DailyReturn_EqualWeight"]  # or whatever your portfolio return column is
        
        # Compute cumulative returns
        cum_returns = (1 + returns).cumprod()
        
        # Compute drawdowns
        rolling_max = cum_returns.cummax()
        drawdowns = (cum_returns - rolling_max) / rolling_max
        
        # Return the worst drawdown
        return drawdowns.min()



    def get_stock_performance(self):
        """
        Compute per-stock metrics using StrategyReturn.
        FIXED: Annualized Sharpe ratio and proper handling of edge cases.
        """
        stock_perf = []
        
        for ticker, group in self.daily_returns_df.groupby('Ticker'):
            # Only look at days when stock was actually traded
            trades_df = group[group['StrategyReturn'] != 0]
            trades = len(trades_df)
            
            if trades == 0:
                continue  # Skip stocks never traded
            
            wins = (trades_df['StrategyReturn'] > 0).sum()
            avg_return = trades_df['StrategyReturn'].mean()
            std_return = trades_df['StrategyReturn'].std()
            
            # FIXED: Proper Sharpe ratio calculation
            # Annualized Sharpe (assuming 252 trading days)
            if std_return > 0 and trades > 1:
                sharpe = (avg_return / std_return) * (252 ** 0.5)
            else:
                sharpe = 0.0  # Undefined for constant returns or single trade
            
            # Total return for this stock (last cumulative return value when traded)
            total_return = trades_df['CumulativeReturn'].iloc[-1] if trades > 0 else 0.0
            
            stock_perf.append({
                'ticker': ticker,
                'trades': trades,
                'winRate': round(wins / trades, 2),
                'avgReturn': round(avg_return, 4),
                'totalReturn': round(total_return, 4),
                'sharpe': round(sharpe, 2)
            })
        
        return {"stockPerformance": stock_perf}
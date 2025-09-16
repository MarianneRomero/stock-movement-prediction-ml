import yaml
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

project_root = Path(__file__).resolve().parents[2]
config_path = project_root / "config.yaml"

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

prediction_path = Path(__file__).resolve().parents[2]/ "experiments" / "run2" / "trading_sim_data.csv"
data = pd.read_csv(prediction_path, index_col=0)

holding_horizon = config['trading']['holding_horizon']
threshold_flat = config['trading']['threshold_flat']

# Step 1: Compute soft positions
data['Position'] = data['Prob_Up'] - data['Prob_Down']

# Set position to 0 if Flat is highest
data.loc[data[['Prob_Up', 'Prob_Down', 'Prob_Flat']].idxmax(axis=1) == 'Prob_Flat', 'Position'] = 0

# Step 2: Compute forward returns
data = data.sort_values(['Ticker', 'Date'])
data['Forward_Return'] = data.groupby('Ticker')['Close'].shift(-holding_horizon) / data['Close'] - 1

# Drop last rows with NaN forward returns
data = data.dropna(subset=['Forward_Return'])

# Step 3: Calculate per-row P&L
data['PnL'] = data['Position'] * data['Forward_Return']

# Step 4: Aggregate portfolio returns per day
portfolio_returns = data.groupby('Date')['PnL'].mean().reset_index() # don't want to calculate sum across tickers
portfolio_returns.rename(columns={'PnL': 'Portfolio_Return'}, inplace=True)

# Step 5: Cumulative returns
portfolio_returns['Cumulative_Return'] = (
    (1 + portfolio_returns['Portfolio_Return']).cumprod() - 1
)



# Sharpe ratio
daily_mean = portfolio_returns['Portfolio_Return'].mean()
daily_std = portfolio_returns['Portfolio_Return'].std()
sharpe_ratio = (daily_mean / daily_std) * np.sqrt(252)  # annualized

print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
print(f"Total cumulative return: {portfolio_returns['Cumulative_Return'].iloc[-1]:.2%}")


# ===== Vizualization =====

# Portfolio equity curve
plt.figure(figsize=(12, 6))
plt.plot(portfolio_returns['Date'], portfolio_returns['Cumulative_Return'], label='Portfolio Cumulative Return', color='blue')
plt.title('Portfolio Equity Curve')
plt.xlabel('Date')
plt.ylabel('Cumulative Return')
plt.legend()
plt.grid(True)
plt.show()

# Per-stock cumulative PnL

per_stock_pnl = data.groupby(['Date', 'Ticker'])['PnL'].mean().unstack(fill_value=0)
per_stock_cum = (1 + per_stock_pnl).cumprod() - 1

plt.figure(figsize=(14, 7))
for ticker in per_stock_cum.columns:
    plt.plot(per_stock_cum.index, per_stock_cum[ticker], label=ticker)
plt.title('Per-Stock Cumulative Returns (Compounded)')
plt.xlabel('Date')
plt.ylabel('Cumulative Return')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.show()

# Daily portfolio returns distribution
plt.figure(figsize=(10, 5))
plt.hist(portfolio_returns['Portfolio_Return'], bins=50, color='green', alpha=0.7)
plt.title('Daily Portfolio Returns Distribution')
plt.xlabel('Daily Return')
plt.ylabel('Frequency')
plt.grid(True)
plt.show()

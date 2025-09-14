# stock-movement-prediction-ml

## Goal

Build a machine learning-driven trading simulation that predicts short-term stock movements and simulates a multi-stock portfolio using probability-weighted positions

## Trading strategy

This project implements a multi-stock, probability-weighted trading strategy driven by a machine learning model.

1. **ML Model Predictions**

- A classifier (XGBoost) predicts the probability of each stock moving up, flat, or down over a future horizon (3 days).

- Instead of hard buy/sell signals, the model outputs soft probabilities for each class.

2. **Soft Probability-Based Positions**

- For each stock and day, a position size is computed as: `Position = Prob_Up - Prob_Down`

- Positive → buy, negative → sell.

- Flat signals or low-confidence predictions are skipped.

3. **Forward Returns and P&L**

- Each position is held for the predicted horizon (e.g., 3 days).

- P&L is calculated as `Position × Forward_Return`, representing the profit or loss realized over that holding period.

3. **Portfolio Aggregation**

P&L from all active positions is summed per day to simulate a portfolio-level equity curve.

`Model Probabilities -> Soft Positions -> Multiply by Forward Return -> Daily PnL -> Compound -> Cumulative Return`

- **daily soft positions**: `Position = Prob_Up - Prob_Down` (skip trades if flat probability is highest)
- **foward return**: `Forward_Return = (Close in 3 days / Close today) - 1` (actual market return for the 3-day horizon defined)
- **daily PnL**: `PnL = Position * Forward_Return`
- **per-stock compounded return**: `cumulative_return[t] = (1 + daily_return_1) * (1 + daily_return_2) * ... - 1`

Average across all stocks per day to get the portfolio daily return.

4. **Machine Learning Integration**

- The ML model captures complex, nonlinear patterns in historical prices, volumes, market indices, and macroeconomic data.

- Using probabilities instead of hard classes allows the strategy to weight positions by confidence, resulting in smoother returns and better risk-adjusted performance.


## Flow of execution

1. `data/data_loader.py`
Load and save the raw data.

2. `features/build_features.py`
Calculate all the features and save data to a new file.

3. `data/split_data.py`
Split the data in training/testing sets.

4. `models/train_model.py`
Train the model on the saved data and save the trained model.

4. `models/predict_model.py`
Use the model to make predictions on the testing data. These predictions will be saved to new files and will be used for the trading simulation.

5. `trading_simulation/format_data`
Get the output data and process it to make it into the appropriate format for the simulation.

6. `trading_simulation/trading_simulation.py`
Perform the trading simulation with the given strategy using the predictions made by the model.
This allows us to perform backtesting of the ML model and trading strategy with the test data.
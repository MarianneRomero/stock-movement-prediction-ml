import yaml
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder


project_root = Path(__file__).resolve().parents[2]
config_path = project_root / "config.yaml"

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

processed_data_path = project_root / config["data"]["processed"]
data_with_fts_path = processed_data_path / "data_with_fts.csv"

print("Loading data...")
data = pd.read_csv(data_with_fts_path, index_col=0)

# ===== One-hot encode the ticker values =====

encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
encoded_values = encoder.fit_transform(data[['Ticker']])
new_cols = encoder.get_feature_names_out(['Ticker'])

tickers_encoded = pd.DataFrame(encoded_values, columns=new_cols, index=data.index)

data = pd.concat(
    [data, tickers_encoded],
    axis=1
)


# ===== Do training/test split =====

feature_columns = config['features']['retuns']\
    + config['features']['rolling_volatility']\
    + config['features']['moving_avg']\
    + config['features']['momentum_indicators']\
    + config['features']['macro_features']\
    + config['features']['volume_features']\
    + config['features']['market_index_features']\
    + config['features']['atr']\
    + config['features']['bb']\
    + config['features']['price_range']\
    + new_cols.tolist()

test_split = config['evaluation']['test_split']

X = data[feature_columns + ['Date', 'Close', 'Ticker']]
y = data['Target']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_split, shuffle=False)

# ===== Save values for training =====

X_train[feature_columns].to_csv(processed_data_path / 'X_train.csv')
X_test[feature_columns].to_csv(processed_data_path / 'X_test.csv')
y_train.to_csv(processed_data_path / 'y_train.csv')
y_test.to_csv(processed_data_path / 'y_test.csv')


# ===== Save data for trading simulation =====
X_test[['Date', 'Close', 'Ticker']].to_csv(processed_data_path / 'X_test_sim.csv')
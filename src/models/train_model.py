import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.utils import compute_class_weight
import yaml
from pathlib import Path
import pandas as pd
import joblib
from sklearn.preprocessing import OneHotEncoder


project_root = Path(__file__).resolve().parents[2]
config_path = project_root / "config.yaml"

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

processed_data_path = project_root / config["data"]["processed"]
data_with_fts_path = processed_data_path / "data_with_fts.csv"

print("Loading data with features")
data = pd.read_csv(data_with_fts_path, index_col=0)


# one-hot encore ticker values

encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
encoded_values = encoder.fit_transform(data[['Ticker']])
new_cols = encoder.get_feature_names_out(['Ticker'])

tickers_encoded = pd.DataFrame(encoded_values, columns=new_cols, index=data.index)
data = pd.concat([data, tickers_encoded], axis=1)

# get all feature columns

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
    # + new_cols.tolist()


# prevent data leakage from using same-day data
data[feature_columns] = data.groupby('Ticker')[feature_columns].shift(1) 
data.dropna()


# training data

X_train = data[feature_columns]
y_train = data["Target"]


# Account for class imbalance

classes = np.unique(y_train)
weights_array = compute_class_weight("balanced", classes=classes, y=y_train)
class_weights = dict(zip(classes, weights_array))
sample_weight = y_train.map(class_weights)


# Train model on entire dataset

print("Training model...")
model = RandomForestRegressor(n_estimators=200, max_depth=8)
model.fit(X_train, y_train, sample_weight=sample_weight)


# Save model to make predicitons in the future

joblib.dump(model, Path(__file__).resolve().parent / "xgb_model.pkl")
print("Model saved to xgb_model.pkl")

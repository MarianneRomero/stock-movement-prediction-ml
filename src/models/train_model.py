import numpy as np
from sklearn.utils import compute_class_weight
import yaml
from pathlib import Path
import pandas as pd
from xgboost import XGBClassifier
import joblib


project_root = Path(__file__).resolve().parents[2]
config_path = project_root / "config.yaml"

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

processed_data_path = project_root / config["data"]["processed"]

print("Loading training data...")
X_train = pd.read_csv(processed_data_path / "X_train.csv", index_col=0) 
y_train = pd.read_csv(processed_data_path / "y_train.csv", index_col=0)["Target"]


# ===== Account for class imbalance =====

classes = np.unique(y_train)
weights_array = compute_class_weight("balanced", classes=classes, y=y_train)
class_weights = dict(zip(classes, weights_array))
sample_weight = y_train.map(class_weights)


# ===== Train model =====

print("Training model...")
model_params = config["model"]["params"]
model = XGBClassifier(**model_params)
model.fit(X_train, y_train, sample_weight=sample_weight)



# ===== Save model =====

joblib.dump(model, Path(__file__).resolve().parent / "xgb_model.pkl")
print("Model saved to xgb_model.pkl")

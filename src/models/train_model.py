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
X_train = pd.read_csv(processed_data_path / "X_train.csv")
y_train = pd.read_csv(processed_data_path / "y_train.csv")["Target"]


# ===== Account for class imbalance =====

class_counts = y_train.value_counts().to_dict()
n_total = len(y_train)
n_classes = len(class_counts)

# Compute weights
class_weights = {cls: n_total / (count * n_classes) for cls, count in class_counts.items()}
weights = y_train.map(class_weights)


# ===== Train model =====

print("Training model...")
model_params = config["model"]["params"]
model = XGBClassifier(**model_params)
model.fit(X_train, y_train, sample_weight=weights)



# ===== Save model =====

joblib.dump(model, Path(__file__).resolve().parent / "xgb_model.pkl")
print("Model saved to xgb_model.pkl")

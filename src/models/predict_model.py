import joblib
import pandas as pd
from pathlib import Path
import yaml
import shutil

project_root = Path(__file__).resolve().parents[2]
config_path = project_root / "config.yaml"

with open(config_path, "r") as f:
    config = yaml.safe_load(f)


print("Loading test data...")
processed_data_path = project_root / config["data"]["processed"]
X_test = pd.read_csv(processed_data_path / "X_test.csv")
y_test = pd.read_csv(processed_data_path / "y_test.csv")

print("Loading trained model...")
model = joblib.load(Path(__file__).resolve().parent / "xgb_model.pkl")

print("Making predictions...")
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)


# ===== Saving predictions =====
prediction_dir = Path(__file__).resolve().parents[2]/ "experiments" / "run1"
prediction_dir.mkdir(parents=True, exist_ok=True) 

print("Saving this run's predictions")
df_pred = pd.DataFrame(y_pred, columns=["Target"])
df_pred.to_csv(prediction_dir / "predictions.csv")

df_prob = pd.DataFrame(y_proba, columns=['Prob_Down', 'Prob_Flat', 'Prob_Up'])
df_prob.to_csv(prediction_dir / "predictions_prob.csv")

print("Copying this run's config")
shutil.copy(config_path, prediction_dir)
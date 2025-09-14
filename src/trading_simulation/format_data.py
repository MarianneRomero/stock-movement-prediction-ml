import yaml
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parents[2]
config_path = project_root / "config.yaml"

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

processed_data_path = project_root / config["data"]["processed"] / 'X_test_sim.csv'
prediction_path = Path(__file__).resolve().parents[2]/ "experiments" / "run1"

print("Loading data...")
X_test_sim = pd.read_csv(processed_data_path, index_col=0)
y_proba = pd.read_csv(prediction_path / "predictions_prob.csv", index_col=0)
y_proba = y_proba.to_numpy()

X_test_sim['Prob_Down'] = y_proba[:, 0]
X_test_sim['Prob_Flat'] = y_proba[:, 1]
X_test_sim['Prob_Up']   = y_proba[:, 2]

X_test_sim.to_csv(prediction_path / "trading_sim_data.csv")
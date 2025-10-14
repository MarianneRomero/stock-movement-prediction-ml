import yaml
from pathlib import Path
import pandas as pd
from feature_helpers import create_features

project_root = Path(__file__).resolve().parents[2]
config_path = project_root / "config.yaml"

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

interim_data_path = raw_data_path = project_root / config["data"]["interim"] / "data_with_target.csv"
processed_data_path = raw_data_path = project_root / config["data"]["processed"] / "data_with_fts.csv"


df = pd.read_csv(interim_data_path, index_col=0)

df = create_features(df)

df.to_csv(processed_data_path)
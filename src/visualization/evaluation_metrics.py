import joblib
import yaml
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
from sklearn.metrics import balanced_accuracy_score

from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    roc_curve, auc
)
from sklearn.preprocessing import label_binarize


project_root = Path(__file__).resolve().parents[2]
config_path = project_root / "config.yaml"

with open(config_path, "r") as f:
    config = yaml.safe_load(f)




# --------------------------
# 1. Load predictions & model
# --------------------------

processed_data_path = project_root / config["data"]["processed"]
prediction_path = Path(__file__).resolve().parents[2]/ "experiments" / "run1"

y_pred = pd.read_csv(prediction_path / "predictions.csv", index_col=0)
y_proba = pd.read_csv(prediction_path / "predictions_prob.csv", index_col=0)
y_proba = y_proba.to_numpy()
y_test = pd.read_csv(processed_data_path / "y_test.csv", index_col=0)


model = joblib.load(Path(__file__).resolve().parents[1] / 'models' / "xgb_model.pkl")

# --------------------------
# 2. Evaluation Metrics
# --------------------------
print("✅ Accuracy:", accuracy_score(y_test, y_pred))
print("✅ Balanced accuracy:", balanced_accuracy_score(y_test, y_pred))

print("\n📊 Classification Report:\n",
      classification_report(y_test, y_pred,
                            target_names=["Down", "Flat", "Up"]))

# --------------------------
# 3. Visualizations
# --------------------------

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print(cm)
'''
plt.figure(figsize=(6,4))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["Down", "Flat", "Up"],
            yticklabels=["Down", "Flat", "Up"])
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()

# Multi-class ROC Curves
y_test_bin = label_binarize(y_test, classes=[0,1,2])

plt.figure(figsize=(7,6))
for i, class_name in enumerate(["Down", "Flat", "Up"]):
    fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_proba[:, i])
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, label=f"{class_name} (AUC = {roc_auc:.2f})")

plt.plot([0,1], [0,1], linestyle="--", color="grey")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("Multi-class ROC Curves")
plt.legend()
plt.show()

# Probability Distribution
proba_df = pd.DataFrame(y_proba, columns=["Down", "Flat", "Up"])
proba_df.plot(kind="hist", bins=20, alpha=0.5, stacked=True)
plt.title("Prediction Probability Distribution")
plt.xlabel("Probability")
plt.show()

# --------------------------
# 4. XGBoost Feature Importance
# --------------------------
xgb.plot_importance(model)
plt.title("Feature Importance")
plt.show()

'''

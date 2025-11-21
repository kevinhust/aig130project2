"""
Configuration settings for Bitcoin Price Prediction Pipeline
"""
import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"
PLOTS_DIR = RESULTS_DIR / "plots"

# Create directories if they don't exist
for directory in [DATA_DIR, MODELS_DIR, RESULTS_DIR, PLOTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Data settings
DATA_FILE = "btc_1h_data_2018_to_2025.csv"
RANDOM_SEED = 42

# Feature engineering settings
MOVING_AVERAGE_WINDOWS = [5, 10]
LAG_FEATURES = [1, 2]

# Model settings
TRAIN_TEST_SPLIT_RATIO = 0.8

# Model hyperparameters
MODEL_PARAMS = {
    "decision_tree": {
        "random_state": RANDOM_SEED,
        "max_depth": 10
    },
    "random_forest": {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 20,
        "min_samples_leaf": 10,
        "random_state": RANDOM_SEED,
        "n_jobs": -1
    },
    "linear_regression": {}
}

# Visualization settings
PLOT_STYLE = 'seaborn-v0_8'
FIGURE_DPI = 100
PLOT_SAMPLE_SIZE = 500  # Number of predictions to show in plots

# Evaluation metrics
METRICS = ["RMSE", "MAE", "R²", "MAPE"]

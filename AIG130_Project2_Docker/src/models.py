"""
Machine learning models for Bitcoin price prediction
"""
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import logging
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """Handles model training and prediction"""

    def __init__(self, model_params: Dict[str, Dict[str, Any]]):
        """
        Initialize ModelTrainer with model configurations

        Args:
            model_params: Dictionary of model parameters
        """
        self.model_params = model_params
        self.models = {}
        self.scaler = StandardScaler()
        self.fitted = False

    def initialize_models(self):
        """Initialize all regression models"""
        self.models = {
            'Linear Regression': LinearRegression(**self.model_params.get('linear_regression', {})),
            'Decision Tree': DecisionTreeRegressor(**self.model_params.get('decision_tree', {})),
            'Random Forest': RandomForestRegressor(**self.model_params.get('random_forest', {}))
        }
        logger.info(f"Initialized {len(self.models)} models")

    def fit_scaler(self, X_train):
        """Fit the feature scaler on training data"""
        self.scaler.fit(X_train)
        logger.info("Fitted StandardScaler on training data")

    def transform_features(self, X):
        """Transform features using fitted scaler"""
        return self.scaler.transform(X)

    def train_models(self, X_train, y_train):
        """
        Train all models on the training data

        Args:
            X_train: Training features
            y_train: Training target

        Returns:
            Dictionary of trained models
        """
        if not self.models:
            self.initialize_models()

        # Scale features
        X_train_scaled = self.transform_features(X_train)

        # Train each model
        for name, model in self.models.items():
            logger.info(f"Training {name}...")
            model.fit(X_train_scaled, y_train)
            logger.info(f"{name} training completed")

        self.fitted = True
        return self.models

    def predict(self, model_name: str, X):
        """
        Make predictions using a specific model

        Args:
            model_name: Name of the model to use
            X: Features to predict on

        Returns:
            Predictions array
        """
        if not self.fitted:
            raise ValueError("Models must be trained before prediction")

        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")

        X_scaled = self.transform_features(X)
        predictions = self.models[model_name].predict(X_scaled)

        return predictions

    def predict_all(self, X):
        """
        Make predictions using all models

        Args:
            X: Features to predict on

        Returns:
            Dictionary of predictions for each model
        """
        predictions = {}
        X_scaled = self.transform_features(X)

        for name, model in self.models.items():
            predictions[name] = model.predict(X_scaled)
            logger.info(f"Generated predictions for {name}")

        return predictions

    def save_models(self, save_dir: Path):
        """
        Save trained models and scaler to disk

        Args:
            save_dir: Directory to save models
        """
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save scaler
        scaler_path = save_dir / "scaler.pkl"
        joblib.dump(self.scaler, scaler_path)
        logger.info(f"Saved scaler to {scaler_path}")

        # Save each model
        for name, model in self.models.items():
            model_path = save_dir / f"{name.lower().replace(' ', '_')}.pkl"
            joblib.dump(model, model_path)
            logger.info(f"Saved {name} to {model_path}")

    def load_models(self, load_dir: Path):
        """
        Load trained models and scaler from disk

        Args:
            load_dir: Directory to load models from
        """
        # Load scaler
        scaler_path = load_dir / "scaler.pkl"
        self.scaler = joblib.load(scaler_path)
        logger.info(f"Loaded scaler from {scaler_path}")

        # Load models
        model_files = {
            'Linear Regression': 'linear_regression.pkl',
            'Decision Tree': 'decision_tree.pkl',
            'Random Forest': 'random_forest.pkl'
        }

        for name, filename in model_files.items():
            model_path = load_dir / filename
            if model_path.exists():
                self.models[name] = joblib.load(model_path)
                logger.info(f"Loaded {name} from {model_path}")

        self.fitted = True

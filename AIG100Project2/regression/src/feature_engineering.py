"""
Feature engineering for Bitcoin price prediction
"""
import pandas as pd
import numpy as np
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_features(
    df: pd.DataFrame,
    ma_windows: List[int] = [5, 10],
    lag_periods: List[int] = [1, 2]
) -> pd.DataFrame:
    """
    Create technical indicators and lag features for Bitcoin price prediction

    Args:
        df: Input DataFrame with OHLCV data
        ma_windows: List of moving average window sizes
        lag_periods: List of lag periods for creating lag features

    Returns:
        DataFrame with engineered features
    """
    df_features = df.copy()

    logger.info("Creating features...")

    # Price changes
    df_features['price_change'] = df_features['Close'] - df_features['Open']
    df_features['price_change_pct'] = (
        (df_features['Close'] - df_features['Open']) / df_features['Open'] * 100
    )

    # Volatility
    df_features['volatility'] = (
        (df_features['High'] - df_features['Low']) / df_features['Open'] * 100
    )

    # Moving averages
    for window in ma_windows:
        df_features[f'ma_{window}'] = df_features['Close'].rolling(window=window).mean()
        logger.info(f"Created MA({window})")

    # Lag features
    for lag in lag_periods:
        df_features[f'close_lag_{lag}'] = df_features['Close'].shift(lag)
        logger.info(f"Created lag feature: lag_{lag}")

    # Target variable: Next hour's close price
    df_features['target_close'] = df_features['Close'].shift(-1)

    # Remove rows with NaN values (due to rolling windows and shifts)
    initial_rows = len(df_features)
    df_features = df_features.dropna()
    final_rows = len(df_features)

    logger.info(f"Removed {initial_rows - final_rows} rows with NaN values")
    logger.info(f"Final feature dataset: {df_features.shape[0]} rows, {df_features.shape[1]} columns")

    return df_features


def get_feature_columns(df: pd.DataFrame) -> List[str]:
    """
    Get list of feature columns (exclude target and original close)

    Args:
        df: DataFrame with features

    Returns:
        List of feature column names
    """
    exclude_cols = ['Close', 'target_close']
    feature_cols = [col for col in df.columns if col not in exclude_cols]

    logger.info(f"Selected {len(feature_cols)} features: {feature_cols}")
    return feature_cols


def split_features_target(df: pd.DataFrame, feature_cols: List[str]):
    """
    Split DataFrame into features and target

    Args:
        df: DataFrame with features and target
        feature_cols: List of feature column names

    Returns:
        Tuple of (X, y) where X is features and y is target
    """
    X = df[feature_cols]
    y = df['target_close']

    logger.info(f"Features shape: {X.shape}")
    logger.info(f"Target shape: {y.shape}")

    return X, y


def chronological_train_test_split(X: pd.DataFrame, y: pd.Series, split_ratio: float = 0.8):
    """
    Split time series data chronologically (important for time series!)

    Args:
        X: Feature DataFrame
        y: Target Series
        split_ratio: Ratio of training data (0-1)

    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
    """
    split_index = int(len(X) * split_ratio)

    X_train = X[:split_index]
    X_test = X[split_index:]
    y_train = y[:split_index]
    y_test = y[split_index:]

    logger.info(f"Training set: {len(X_train)} samples ({X_train.index[0]} to {X_train.index[-1]})")
    logger.info(f"Test set: {len(X_test)} samples ({X_test.index[0]} to {X_test.index[-1]})")

    return X_train, X_test, y_train, y_test

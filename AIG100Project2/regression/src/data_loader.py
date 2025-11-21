"""
Data loading and preprocessing for Bitcoin price prediction
"""
import numpy as np
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_bitcoin_data(data_path: Path) -> pd.DataFrame:
    """
    Load Bitcoin historical price data from CSV file

    Args:
        data_path: Path to the CSV file

    Returns:
        DataFrame with Bitcoin OHLCV data
    """
    try:
        df = pd.read_csv(data_path, index_col=0, parse_dates=True)
        logger.info(f"Loaded Bitcoin data: {df.shape[0]} rows, {df.shape[1]} columns")
        logger.info(f"Date range: {df.index[0]} to {df.index[-1]}")
        return df
    except FileNotFoundError:
        logger.warning(f"Data file not found at {data_path}. Generating synthetic data...")
        return generate_synthetic_bitcoin_data()


def generate_synthetic_bitcoin_data(n_samples: int = 25120, seed: int = 42) -> pd.DataFrame:
    """
    Generate realistic synthetic Bitcoin price data for demonstration

    Args:
        n_samples: Number of hourly samples to generate
        seed: Random seed for reproducibility

    Returns:
        DataFrame with synthetic Bitcoin OHLCV data
    """
    np.random.seed(seed)

    # Create realistic Bitcoin price data
    base_price = 50000
    price_trend = np.linspace(base_price, 120000, n_samples)
    noise = np.random.normal(0, 2000, n_samples)
    volatility = np.random.normal(1, 0.05, n_samples)

    # Generate OHLCV data
    close_prices = price_trend + noise
    open_prices = close_prices * np.random.uniform(0.98, 1.02, n_samples)
    high_prices = np.maximum(open_prices, close_prices) * np.random.uniform(1.0, 1.03, n_samples)
    low_prices = np.minimum(open_prices, close_prices) * np.random.uniform(0.97, 1.0, n_samples)
    volume = np.random.uniform(1000000, 5000000, n_samples) * volatility

    # Create DataFrame with datetime index
    dates = pd.date_range(start='2023-01-01', periods=n_samples, freq='H')
    df = pd.DataFrame({
        'Open': open_prices,
        'High': high_prices,
        'Low': low_prices,
        'Close': close_prices,
        'Volume': volume
    }, index=dates)

    logger.info(f"Generated synthetic Bitcoin data: {df.shape[0]} rows")
    logger.info(f"Date range: {df.index[0]} to {df.index[-1]}")

    return df


def validate_data(df: pd.DataFrame) -> bool:
    """
    Validate Bitcoin data quality

    Args:
        df: DataFrame to validate

    Returns:
        True if data is valid, raises ValueError otherwise
    """
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']

    # Check required columns
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Check for missing values
    if df[required_columns].isnull().any().any():
        raise ValueError("Data contains missing values")

    # Check for valid price relationships
    if not (df['High'] >= df['Low']).all():
        raise ValueError("High prices must be >= Low prices")

    if not (df['High'] >= df['Open']).all() or not (df['High'] >= df['Close']).all():
        raise ValueError("High prices must be >= Open and Close prices")

    if not (df['Low'] <= df['Open']).all() or not (df['Low'] <= df['Close']).all():
        raise ValueError("Low prices must be <= Open and Close prices")

    logger.info("Data validation passed")
    return True

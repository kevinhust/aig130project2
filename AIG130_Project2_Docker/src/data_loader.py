"""
Data loading and preprocessing for Bitcoin price prediction
"""
import numpy as np
import pandas as pd
from pathlib import Path
import logging
import os
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_from_s3(bucket: str, key: str, local_path: Path) -> pd.DataFrame:
    """
    Load data from AWS S3 bucket

    Args:
        bucket: S3 bucket name
        key: S3 object key
        local_path: Local path to save the downloaded file

    Returns:
        DataFrame with Bitcoin OHLCV data
    """
    try:
        import boto3
        from botocore.exceptions import ClientError

        logger.info(f"Loading data from S3: s3://{bucket}/{key}")

        # Create S3 client
        s3_client = boto3.client('s3')

        # Download file from S3
        local_path.parent.mkdir(parents=True, exist_ok=True)
        s3_client.download_file(bucket, key, str(local_path))

        logger.info(f"Downloaded data from S3 to {local_path}")

        # Load and return the dataframe
        df = pd.read_csv(local_path, index_col=0, parse_dates=True)
        logger.info(f"Loaded Bitcoin data from S3: {df.shape[0]} rows, {df.shape[1]} columns")
        logger.info(f"Date range: {df.index[0]} to {df.index[-1]}")
        return df

    except ImportError:
        logger.error("boto3 not installed. Install with: pip install boto3")
        raise
    except ClientError as e:
        logger.error(f"Error downloading from S3: {e}")
        logger.warning("Falling back to synthetic data generation...")
        return generate_synthetic_bitcoin_data()
    except Exception as e:
        logger.error(f"Unexpected error loading from S3: {e}")
        logger.warning("Falling back to synthetic data generation...")
        return generate_synthetic_bitcoin_data()


def load_bitcoin_data(data_path: Path) -> pd.DataFrame:
    """
    Load Bitcoin historical price data from CSV file or S3

    Checks USE_S3 environment variable to determine data source.
    If USE_S3=true, loads from S3 bucket specified in environment variables.
    Otherwise, loads from local file path.

    Args:
        data_path: Path to the CSV file (used if not loading from S3)

    Returns:
        DataFrame with Bitcoin OHLCV data
    """
    # Check if we should load from S3
    use_s3 = os.environ.get("USE_S3", "false").lower() == "true"

    if use_s3:
        # Load from S3
        s3_bucket = os.environ.get("S3_BUCKET", "aig130-p2-ml-data-bucket")
        s3_key = os.environ.get("S3_KEY", "data/btc_1h_data_2018_to_2025.csv")

        logger.info("USE_S3 environment variable detected - loading from S3")
        return load_from_s3(s3_bucket, s3_key, data_path)

    # Load from local file
    try:
        df = pd.read_csv(data_path, index_col=0, parse_dates=True)
        logger.info(f"Loaded Bitcoin data from local file: {df.shape[0]} rows, {df.shape[1]} columns")
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

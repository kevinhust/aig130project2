"""
Model evaluation and metrics calculation
"""
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_metrics(y_true, y_pred) -> Dict[str, float]:
    """
    Calculate regression metrics

    Args:
        y_true: True values
        y_pred: Predicted values

    Returns:
        Dictionary of metrics
    """
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    metrics = {
        'RMSE': rmse,
        'MAE': mae,
        'R²': r2,
        'MAPE': mape
    }

    return metrics


def evaluate_models(models_predictions: Dict, y_true) -> pd.DataFrame:
    """
    Evaluate all models and return comparison DataFrame

    Args:
        models_predictions: Dictionary of {model_name: predictions}
        y_true: True values

    Returns:
        DataFrame with metrics for each model
    """
    results = {}

    for model_name, y_pred in models_predictions.items():
        metrics = calculate_metrics(y_true, y_pred)
        results[model_name] = metrics

        logger.info(f"\n{model_name} Performance:")
        logger.info(f"  RMSE: ${metrics['RMSE']:,.2f}")
        logger.info(f"  MAE: ${metrics['MAE']:,.2f}")
        logger.info(f"  R²: {metrics['R²']:.4f}")
        logger.info(f"  MAPE: {metrics['MAPE']:.3f}%")

    # Create comparison DataFrame
    comparison_df = pd.DataFrame(results).T

    return comparison_df


def find_best_models(comparison_df: pd.DataFrame) -> Dict[str, str]:
    """
    Identify best model for each metric

    Args:
        comparison_df: DataFrame with model metrics

    Returns:
        Dictionary of {metric: best_model_name}
    """
    best_models = {}

    for metric in comparison_df.columns:
        if metric == 'R²':
            # Higher is better for R²
            best_models[metric] = comparison_df[metric].idxmax()
        else:
            # Lower is better for RMSE, MAE, MAPE
            best_models[metric] = comparison_df[metric].idxmin()

    logger.info("\nBest Models by Metric:")
    for metric, model in best_models.items():
        value = comparison_df.loc[model, metric]
        if metric == 'R²':
            logger.info(f"  {metric}: {model} ({value:.4f})")
        elif metric in ['RMSE', 'MAE']:
            logger.info(f"  {metric}: {model} (${value:,.2f})")
        else:
            logger.info(f"  {metric}: {model} ({value:.3f}%)")

    return best_models


def save_results(comparison_df: pd.DataFrame, output_path):
    """
    Save evaluation results to CSV

    Args:
        comparison_df: DataFrame with model metrics
        output_path: Path to save results
    """
    comparison_df.to_csv(output_path)
    logger.info(f"Results saved to {output_path}")


def print_summary(comparison_df: pd.DataFrame):
    """
    Print a formatted summary of model performance

    Args:
        comparison_df: DataFrame with model metrics
    """
    print("\n" + "="*70)
    print("MODEL PERFORMANCE SUMMARY")
    print("="*70)
    print(comparison_df.round(4).to_string())
    print("="*70)

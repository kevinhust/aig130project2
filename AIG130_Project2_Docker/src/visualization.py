"""
Visualization functions for Bitcoin price prediction results
"""
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Docker
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_plot_style(style='seaborn-v0_8'):
    """Setup matplotlib style"""
    plt.style.use(style)
    sns.set_palette("husl")


def plot_metrics_comparison(comparison_df: pd.DataFrame, save_path: Path):
    """
    Create bar charts comparing model metrics

    Args:
        comparison_df: DataFrame with model metrics
        save_path: Path to save the plot
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Bitcoin Price Prediction - Model Performance Comparison',
                 fontsize=16, fontweight='bold')

    metrics = ['RMSE', 'R²', 'MAE', 'MAPE']
    colors = ['skyblue', 'lightgreen', 'orange', 'pink']
    positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

    for metric, color, pos in zip(metrics, colors, positions):
        ax = axes[pos]
        values = comparison_df[metric]

        ax.bar(comparison_df.index, values, color=color)
        ax.set_title(f'{metric} Comparison {"(Higher is Better)" if metric == "R²" else "(Lower is Better)"}')
        ax.set_ylabel(metric if metric not in ['RMSE', 'MAE'] else f'{metric} ($)')
        ax.tick_params(axis='x', rotation=45)

        # Add value labels
        for i, v in enumerate(values):
            if metric in ['RMSE', 'MAE']:
                label = f'${v:,.0f}'
            elif metric == 'R²':
                label = f'{v:.3f}'
            else:
                label = f'{v:.2f}%'
            ax.text(i, v + (abs(v) * 0.02), label, ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    logger.info(f"Metrics comparison plot saved to {save_path}")
    plt.close()


def plot_predictions_vs_actual(y_test, predictions_dict: Dict, save_path: Path, sample_size: int = 500):
    """
    Plot actual vs predicted prices

    Args:
        y_test: True test values
        predictions_dict: Dictionary of {model_name: predictions}
        save_path: Path to save the plot
        sample_size: Number of samples to plot
    """
    plt.figure(figsize=(15, 8))

    # Use last N samples for clarity
    actual_sample = y_test.iloc[-sample_size:]

    plt.plot(actual_sample.index, actual_sample, 'k-',
             linewidth=2, label='Actual Prices', alpha=0.8)

    colors = ['blue', 'red', 'green']
    for i, (name, pred) in enumerate(predictions_dict.items()):
        pred_sample = pred[-sample_size:]
        plt.plot(actual_sample.index, pred_sample, color=colors[i % len(colors)],
                 linewidth=1.5, label=f'{name} Predictions', alpha=0.7)

    plt.title(f'Bitcoin Price Prediction - Actual vs Predicted (Last {sample_size} Hours)',
              fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Bitcoin Price ($)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    logger.info(f"Predictions vs actual plot saved to {save_path}")
    plt.close()


def plot_feature_importance(models: Dict, feature_cols: list, save_path: Path):
    """
    Plot feature importance for each model

    Args:
        models: Dictionary of trained models
        feature_cols: List of feature column names
        save_path: Path to save the plot
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('Feature Importance Analysis', fontsize=16, fontweight='bold')

    # Linear Regression coefficients
    if 'Linear Regression' in models:
        lr_model = models['Linear Regression']
        lr_importance = pd.DataFrame({
            'Feature': feature_cols,
            'Coefficient': lr_model.coef_
        }).sort_values('Coefficient', key=abs, ascending=False)

        axes[0].barh(lr_importance['Feature'], lr_importance['Coefficient'])
        axes[0].set_title('Linear Regression Coefficients')
        axes[0].set_xlabel('Coefficient Value')

    # Decision Tree feature importance
    if 'Decision Tree' in models:
        dt_model = models['Decision Tree']
        dt_importance = pd.DataFrame({
            'Feature': feature_cols,
            'Importance': dt_model.feature_importances_
        }).sort_values('Importance', ascending=False)

        axes[1].barh(dt_importance['Feature'], dt_importance['Importance'])
        axes[1].set_title('Decision Tree Feature Importance')
        axes[1].set_xlabel('Importance')

    # Random Forest feature importance
    if 'Random Forest' in models:
        rf_model = models['Random Forest']
        rf_importance = pd.DataFrame({
            'Feature': feature_cols,
            'Importance': rf_model.feature_importances_
        }).sort_values('Importance', ascending=False)

        axes[2].barh(rf_importance['Feature'], rf_importance['Importance'])
        axes[2].set_title('Random Forest Feature Importance')
        axes[2].set_xlabel('Importance')

    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    logger.info(f"Feature importance plot saved to {save_path}")
    plt.close()


def plot_residuals(y_test, predictions_dict: Dict, save_path: Path):
    """
    Plot residual distributions

    Args:
        y_test: True test values
        predictions_dict: Dictionary of {model_name: predictions}
        save_path: Path to save the plot
    """
    n_models = len(predictions_dict)
    fig, axes = plt.subplots(1, n_models, figsize=(6 * n_models, 5))
    if n_models == 1:
        axes = [axes]

    fig.suptitle('Residual Analysis', fontsize=16, fontweight='bold')

    for ax, (name, pred) in zip(axes, predictions_dict.items()):
        residuals = y_test - pred
        ax.hist(residuals, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        ax.axvline(x=0, color='red', linestyle='--', linewidth=2)
        ax.set_title(f'{name}\nMean Residual: ${residuals.mean():,.2f}')
        ax.set_xlabel('Residual ($)')
        ax.set_ylabel('Frequency')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    logger.info(f"Residuals plot saved to {save_path}")
    plt.close()


def generate_all_plots(comparison_df, y_test, predictions_dict, models, feature_cols, plots_dir: Path):
    """
    Generate all visualization plots

    Args:
        comparison_df: DataFrame with model metrics
        y_test: True test values
        predictions_dict: Dictionary of predictions
        models: Dictionary of trained models
        feature_cols: List of feature names
        plots_dir: Directory to save plots
    """
    setup_plot_style()

    logger.info("Generating visualization plots...")

    plot_metrics_comparison(comparison_df, plots_dir / "metrics_comparison.png")
    plot_predictions_vs_actual(y_test, predictions_dict, plots_dir / "predictions_vs_actual.png")
    plot_feature_importance(models, feature_cols, plots_dir / "feature_importance.png")
    plot_residuals(y_test, predictions_dict, plots_dir / "residuals.png")

    logger.info(f"All plots saved to {plots_dir}")

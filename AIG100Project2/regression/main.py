#!/usr/bin/env python3
"""
Bitcoin Price Prediction - Main Pipeline Script

This script orchestrates the entire ML pipeline for Bitcoin price prediction:
1. Data loading
2. Feature engineering
3. Model training
4. Evaluation
5. Visualization
"""
import argparse
import logging
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from src.data_loader import load_bitcoin_data, validate_data
from src.feature_engineering import (
    create_features,
    get_feature_columns,
    split_features_target,
    chronological_train_test_split
)
from src.models import ModelTrainer
from src.evaluate import evaluate_models, find_best_models, save_results, print_summary
from src.visualization import generate_all_plots

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Bitcoin Price Prediction Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--mode',
        type=str,
        choices=['train', 'inference', 'evaluate'],
        default='train',
        help='Pipeline mode: train (full pipeline), inference (predictions only), evaluate (metrics only)'
    )

    parser.add_argument(
        '--data-path',
        type=str,
        default=str(config.DATA_DIR / config.DATA_FILE),
        help='Path to Bitcoin CSV data file'
    )

    parser.add_argument(
        '--skip-plots',
        action='store_true',
        help='Skip generating visualization plots'
    )

    parser.add_argument(
        '--save-models',
        action='store_true',
        default=True,
        help='Save trained models to disk'
    )

    parser.add_argument(
        '--load-models',
        type=str,
        help='Load models from specified directory'
    )

    return parser.parse_args()


def main():
    """Main pipeline execution"""
    args = parse_arguments()

    logger.info("="*70)
    logger.info("BITCOIN PRICE PREDICTION PIPELINE")
    logger.info("="*70)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Data path: {args.data_path}")

    # Step 1: Load and validate data
    logger.info("\n[1/6] Loading Bitcoin data...")
    data_path = Path(args.data_path)
    df = load_bitcoin_data(data_path)
    validate_data(df)

    # Step 2: Feature engineering
    logger.info("\n[2/6] Engineering features...")
    df_features = create_features(
        df,
        ma_windows=config.MOVING_AVERAGE_WINDOWS,
        lag_periods=config.LAG_FEATURES
    )

    feature_cols = get_feature_columns(df_features)
    X, y = split_features_target(df_features, feature_cols)

    # Step 3: Split data
    logger.info("\n[3/6] Splitting data...")
    X_train, X_test, y_train, y_test = chronological_train_test_split(
        X, y, split_ratio=config.TRAIN_TEST_SPLIT_RATIO
    )

    # Step 4: Train models
    logger.info("\n[4/6] Training models...")
    trainer = ModelTrainer(config.MODEL_PARAMS)

    if args.load_models:
        logger.info(f"Loading models from {args.load_models}")
        trainer.load_models(Path(args.load_models))
    else:
        trainer.initialize_models()
        trainer.fit_scaler(X_train)
        trainer.train_models(X_train, y_train)

        if args.save_models:
            trainer.save_models(config.MODELS_DIR)

    # Step 5: Evaluate models
    logger.info("\n[5/6] Evaluating models...")
    predictions_dict = trainer.predict_all(X_test)

    comparison_df = evaluate_models(predictions_dict, y_test)
    best_models = find_best_models(comparison_df)

    # Save results
    results_file = config.RESULTS_DIR / "model_comparison.csv"
    save_results(comparison_df, results_file)
    print_summary(comparison_df)

    # Step 6: Generate visualizations
    if not args.skip_plots:
        logger.info("\n[6/6] Generating visualizations...")
        generate_all_plots(
            comparison_df,
            y_test,
            predictions_dict,
            trainer.models,
            feature_cols,
            config.PLOTS_DIR
        )
    else:
        logger.info("\n[6/6] Skipping visualizations (--skip-plots flag)")

    logger.info("\n" + "="*70)
    logger.info("PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("="*70)
    logger.info(f"Results saved to: {config.RESULTS_DIR}")
    logger.info(f"Models saved to: {config.MODELS_DIR}")
    logger.info(f"Plots saved to: {config.PLOTS_DIR}")
    logger.info("="*70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}", exc_info=True)
        sys.exit(1)

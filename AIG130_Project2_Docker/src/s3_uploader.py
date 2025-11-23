"""
S3 Uploader Module
Uploads results, models, and plots to S3 bucket
"""
import os
import logging
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def upload_directory_to_s3(local_dir: Path, s3_bucket: str, s3_prefix: str) -> int:
    """
    Upload all files from a directory to S3

    Args:
        local_dir: Local directory path
        s3_bucket: S3 bucket name
        s3_prefix: S3 key prefix (folder path in S3)

    Returns:
        Number of files uploaded
    """
    if not local_dir.exists():
        logger.warning(f"Directory does not exist: {local_dir}")
        return 0

    s3_client = boto3.client('s3')
    uploaded_count = 0

    # Walk through all files in directory
    for file_path in local_dir.rglob('*'):
        if file_path.is_file():
            # Calculate relative path for S3 key
            relative_path = file_path.relative_to(local_dir)
            s3_key = f"{s3_prefix}/{relative_path}".replace("\\", "/")

            try:
                logger.info(f"Uploading {file_path.name} to s3://{s3_bucket}/{s3_key}")
                s3_client.upload_file(
                    str(file_path),
                    s3_bucket,
                    s3_key
                )
                uploaded_count += 1
                logger.info(f"✓ Uploaded: {file_path.name}")
            except ClientError as e:
                logger.error(f"Failed to upload {file_path.name}: {e}")

    return uploaded_count


def upload_results_to_s3(
    results_dir: Path,
    models_dir: Path,
    plots_dir: Path,
    s3_bucket: str,
    run_id: str = None
) -> dict:
    """
    Upload all pipeline results to S3

    Args:
        results_dir: Results directory path
        models_dir: Models directory path
        plots_dir: Plots directory path
        s3_bucket: S3 bucket name
        run_id: Optional run identifier (timestamp or commit SHA)

    Returns:
        Dictionary with upload statistics
    """
    if run_id is None:
        from datetime import datetime
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    logger.info("="*70)
    logger.info("UPLOADING RESULTS TO S3")
    logger.info("="*70)
    logger.info(f"S3 Bucket: {s3_bucket}")
    logger.info(f"Run ID: {run_id}")
    logger.info("")

    stats = {
        'results': 0,
        'models': 0,
        'plots': 0,
        'total': 0
    }

    # Upload results
    logger.info("Uploading results...")
    stats['results'] = upload_directory_to_s3(
        results_dir,
        s3_bucket,
        f"results/{run_id}"
    )

    # Upload models
    logger.info("\nUploading models...")
    stats['models'] = upload_directory_to_s3(
        models_dir,
        s3_bucket,
        f"models/{run_id}"
    )

    # Upload plots
    logger.info("\nUploading plots...")
    stats['plots'] = upload_directory_to_s3(
        plots_dir,
        s3_bucket,
        f"plots/{run_id}"
    )

    stats['total'] = stats['results'] + stats['models'] + stats['plots']

    logger.info("")
    logger.info("="*70)
    logger.info("S3 UPLOAD COMPLETE")
    logger.info("="*70)
    logger.info(f"Results files: {stats['results']}")
    logger.info(f"Model files: {stats['models']}")
    logger.info(f"Plot files: {stats['plots']}")
    logger.info(f"Total files uploaded: {stats['total']}")
    logger.info("")
    logger.info("Download results:")
    logger.info(f"  aws s3 sync s3://{s3_bucket}/results/{run_id}/ ./downloaded_results/")
    logger.info(f"  aws s3 sync s3://{s3_bucket}/models/{run_id}/ ./downloaded_models/")
    logger.info(f"  aws s3 sync s3://{s3_bucket}/plots/{run_id}/ ./downloaded_plots/")
    logger.info("="*70)

    return stats

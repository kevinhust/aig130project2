# Multi-stage Dockerfile for Bitcoin Price Prediction Pipeline
# Stage 1: Builder - Install dependencies
FROM python:3.10-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt


# Stage 2: Runtime - Create minimal production image
FROM python:3.10-slim

# Add metadata labels
LABEL maintainer="your-email@example.com"
LABEL description="Bitcoin Price Prediction ML Pipeline"
LABEL version="1.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/home/appuser/.local/bin:$PATH \
    MPLBACKEND=Agg

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /app/data /app/models /app/results /app/results/plots && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser config.py .
COPY --chown=appuser:appuser main.py .
COPY --chown=appuser:appuser src/ ./src/

# Copy data file (optional - for local testing only)
# In production, data is loaded from S3 using USE_S3=true environment variable
# Comment out the line below when deploying to AWS (data loaded from S3)
COPY --chown=appuser:appuser data/btc_1h_data_2018_to_2025.csv ./data/

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command - run the training pipeline
CMD ["python", "main.py", "--mode", "train"]

# Alternative: Use ENTRYPOINT for more flexibility
# ENTRYPOINT ["python", "main.py"]
# CMD ["--mode", "train"]

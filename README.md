# Bitcoin Price Prediction - Dockerized ML Pipeline

**AIG130 Project 2: Machine Learning Containerization**

This project containerizes a Bitcoin price prediction pipeline using Docker for reproducibility, collaboration, and scalability.

## Quick Start

### 1. Build the Docker Image
```bash
docker build -t bitcoin-predictor:latest .
```

### 2. Run the Pipeline
```bash
docker-compose up bitcoin-predictor
```

### 3. View Results
```bash
# Check evaluation metrics
cat results/model_comparison.csv

# View plots
ls results/plots/
```

## Project Structure

```
regression/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Orchestration config
├── requirements.txt        # Python dependencies
├── config.py              # Configuration settings
├── main.py                # Pipeline entry point
├── src/                   # Source modules
│   ├── data_loader.py
│   ├── feature_engineering.py
│   ├── models.py
│   ├── evaluate.py
│   └── visualization.py
├── data/                  # Input data
├── models/                # Saved models
└── results/               # Outputs and plots
```

## Models

Three regression models are trained and compared:
- **Linear Regression** (Best: R² = 0.79, RMSE = $2,047)
- **Decision Tree**
- **Random Forest**

## Features

- Technical indicators (moving averages, volatility)
- Lag features (previous prices)
- OHLCV data (Open, High, Low, Close, Volume)

## Outputs

- `results/model_comparison.csv` - Performance metrics
- `models/*.pkl` - Trained model files
- `results/plots/*.png` - Visualization charts

## Documentation

See **DOCKER_DOCUMENTATION.md** for comprehensive details:
- Section 1: Pipeline Review and Enhancements
- Section 2: Dockerfile Implementation
- Section 3: Build and Run Commands
- Section 4: Testing and Validation Steps
- Section 5: Advantages/Disadvantages Analysis

## Requirements

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM
- 2 CPU cores

## Author

Zhihuai Wang - AIG130 NNA - Student #178000238

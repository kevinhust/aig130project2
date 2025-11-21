# AIG130 Project 2 - Bitcoin Price Prediction Docker Deployment

**Student**: Zhihuai Wang
**Student #**: 178000238
**Course**: AIG130 NNA
**Date**: 2025-11-20

---

## Project Overview

This is an independent Docker containerization project (AIG130 Project 2) that builds upon the Bitcoin price prediction model from AIG100 Project 2. The focus is on creating a production-ready, containerized ML pipeline that demonstrates best practices in reproducibility, collaboration, and deployment.

## Relationship to Original Project

- **Original Project**: AIG100 Project 2 (Jupyter notebook-based ML analysis)
- **Source**: `/AIG100Project2/AIG100_Project2_Zhihuaiwang.ipynb`
- **This Project**: Docker containerization of the Bitcoin regression component
- **Location**: Extracted to independent folder for clean deployment

## Key Improvements

1. **Modularization**: Converted monolithic notebook to modular Python scripts
2. **Containerization**: Docker-based deployment for reproducibility
3. **CLI Interface**: Command-line arguments for flexibility
4. **Production-Ready**: Multi-stage builds, non-root user, health checks
5. **Documentation**: Comprehensive guides for all use cases

## Quick Start

```bash
# Build
docker build -t bitcoin-predictor:latest .

# Run
docker-compose up bitcoin-predictor

# View Results
cat results/model_comparison.csv
```

## Directory Structure

```
AIG130_Project2_Docker/
├── config.py              # Configuration
├── main.py                # Entry point
├── Dockerfile             # Container definition
├── docker-compose.yml     # Orchestration
├── requirements.txt       # Dependencies
├── src/                   # Source modules
├── data/                  # Input data
├── models/                # Saved models (generated)
├── results/               # Outputs (generated)
└── Documentation files
```

## Documentation

- **DOCKER_DOCUMENTATION.md** - Complete technical guide (7,000+ words)
- **QUICKSTART.md** - Beginner-friendly guide
- **README.md** - Project overview
- **PROJECT_INFO.md** - This file

## Models Trained

- Linear Regression (R² = 0.79) ✅ Best
- Decision Tree
- Random Forest

## Submission Contents

This folder contains all files needed for:
1. Building the Docker image
2. Running the ML pipeline
3. Evaluating results
4. Understanding the implementation
5. Replicating on any platform

---

**Note**: This project is self-contained and can be deployed independently from the original AIG100 project folder.

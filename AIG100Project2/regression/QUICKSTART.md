# Quick Start Guide - Bitcoin Price Prediction Docker

## For Beginners: Step-by-Step

### Prerequisites
- Install Docker Desktop from https://www.docker.com/products/docker-desktop/
- Open Terminal (Mac/Linux) or PowerShell (Windows)

### Step 1: Navigate to Project
```bash
cd "/Users/kevinwang/Desktop/Cloud ML Project2/AIG100Project2/regression"
```

### Step 2: Build Docker Image
```bash
docker build -t bitcoin-predictor:latest .
```
⏱️ Takes 5-10 minutes first time (faster afterwards)

### Step 3: Run the Pipeline
```bash
docker-compose up bitcoin-predictor
```

### Step 4: View Results
```bash
# See performance metrics
cat results/model_comparison.csv

# View saved plots
open results/plots/  # Mac
explorer results\plots\  # Windows
```

## Expected Output

### Console Output
```
[1/6] Loading Bitcoin data...
[2/6] Engineering features...
[3/6] Splitting data...
[4/6] Training models...
[5/6] Evaluating models...
[6/6] Generating visualizations...
PIPELINE COMPLETED SUCCESSFULLY
```

### Files Created
```
models/
├── linear_regression.pkl
├── decision_tree.pkl
├── random_forest.pkl
└── scaler.pkl

results/
├── model_comparison.csv
└── plots/
    ├── metrics_comparison.png
    ├── predictions_vs_actual.png
    ├── feature_importance.png
    └── residuals.png
```

### Performance Metrics
```csv
,RMSE,MAE,R²,MAPE
Linear Regression,2046.91,1640.74,0.7913,1.456
Decision Tree,11036.61,9768.25,-5.0659,8.484
Random Forest,8707.15,7578.91,-2.7755,6.570
```

**Winner: Linear Regression** 🏆

## Troubleshooting

### Docker Build Fails
```bash
# Clean build (no cache)
docker build --no-cache -t bitcoin-predictor:latest .
```

### Container Won't Start
```bash
# Check Docker is running
docker ps

# View logs
docker logs bitcoin-ml-pipeline
```

### Permission Denied on Results
```bash
# Fix permissions
chmod -R 755 results/ models/
```

### Want to Run Again
```bash
# Quick re-run
docker-compose up bitcoin-predictor

# Or with docker run
docker run --rm \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/results:/app/results \
  bitcoin-predictor:latest
```

## Advanced Usage

### Run Without Plots
```bash
docker run --rm bitcoin-predictor:latest \
  python main.py --skip-plots
```

### Interactive Debugging
```bash
docker run -it --rm bitcoin-predictor:latest /bin/bash
# Inside container:
python main.py
```

### Use Custom Data
```bash
docker run --rm \
  -v /path/to/your/data:/app/data:ro \
  -v $(pwd)/results:/app/results \
  bitcoin-predictor:latest \
  python main.py --data-path /app/data/your_btc_data.csv
```

## Clean Up

```bash
# Remove container
docker-compose down

# Remove image
docker rmi bitcoin-predictor:latest

# Remove all Docker data
docker system prune -a
```

## Need Help?

- Full documentation: `DOCKER_DOCUMENTATION.md`
- Test locally: `./test_local.sh`
- View project structure: `tree -L 2` or `ls -R`

## Summary

| Command | Purpose |
|---------|---------|
| `docker build -t bitcoin-predictor .` | Build image |
| `docker-compose up` | Run pipeline |
| `cat results/model_comparison.csv` | View metrics |
| `docker-compose down` | Stop container |
| `docker system prune -a` | Clean up |

**Total Time: ~10-15 minutes for first run**

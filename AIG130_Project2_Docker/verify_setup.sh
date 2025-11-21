#!/bin/bash
# Verification script to ensure all files are in place

echo "==========================================="
echo "AIG130 Project 2 - Setup Verification"
echo "==========================================="
echo ""

# Check required files
echo "Checking required files..."
required_files=(
    "Dockerfile"
    "docker-compose.yml"
    "requirements.txt"
    "config.py"
    "main.py"
    "src/__init__.py"
    "src/data_loader.py"
    "src/feature_engineering.py"
    "src/models.py"
    "src/evaluate.py"
    "src/visualization.py"
    "data/btc_1h_data_2018_to_2025.csv"
)

all_present=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - MISSING"
        all_present=false
    fi
done

echo ""

# Check directories
echo "Checking directories..."
required_dirs=("src" "data" "models" "results" "results/plots")
for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir/"
    else
        echo "❌ $dir/ - MISSING"
        all_present=false
    fi
done

echo ""

# Check documentation
echo "Checking documentation..."
docs=("README.md" "DOCKER_DOCUMENTATION.md" "QUICKSTART.md" "PROJECT_INFO.md")
for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        echo "✅ $doc"
    else
        echo "⚠️  $doc - MISSING (optional)"
    fi
done

echo ""
echo "==========================================="

if [ "$all_present" = true ]; then
    echo "✅ All required files present!"
    echo ""
    echo "Next steps:"
    echo "1. Build: docker build -t bitcoin-predictor:latest ."
    echo "2. Run:   docker-compose up bitcoin-predictor"
    echo "3. Check: cat results/model_comparison.csv"
    echo ""
    echo "See QUICKSTART.md for detailed instructions."
else
    echo "❌ Some files are missing. Please check above."
fi

echo "==========================================="

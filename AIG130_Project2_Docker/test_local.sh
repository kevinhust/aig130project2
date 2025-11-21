#!/bin/bash
# Quick test script to validate the pipeline locally before Docker

echo "======================================"
echo "Testing Bitcoin Prediction Pipeline"
echo "======================================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run the pipeline
echo ""
echo "Running pipeline..."
python main.py --mode train

# Check if outputs were created
echo ""
echo "Checking outputs..."

if [ -f "results/model_comparison.csv" ]; then
    echo "✅ Results CSV created"
    echo ""
    cat results/model_comparison.csv
else
    echo "❌ Results CSV not found"
    exit 1
fi

if [ -d "results/plots" ] && [ "$(ls -A results/plots)" ]; then
    echo "✅ Plots created: $(ls results/plots/ | wc -l) files"
else
    echo "⚠️  No plots found"
fi

if [ -d "models" ] && [ "$(ls -A models)" ]; then
    echo "✅ Models saved: $(ls models/ | wc -l) files"
else
    echo "⚠️  No models found"
fi

echo ""
echo "======================================"
echo "✅ Pipeline test completed successfully!"
echo "======================================"

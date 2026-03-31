#!/bin/bash
# Run benchmarks script

set -e

echo "Running Token Optimizer Benchmarks"
echo "=================================="

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "pytest not found. Installing..."
    pip install pytest pytest-benchmark
fi

# Run benchmark tests
pytest tests/benchmarks/ -v --tb=short -m benchmark

echo ""
echo "✓ Benchmarks complete!"

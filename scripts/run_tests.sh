#!/bin/bash
# Run tests script

set -e

echo "Running Token Optimizer Tests"
echo "============================="

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "pytest not found. Installing..."
    pip install pytest pytest-cov
fi

# Default to all tests
TEST_ARGS="${1:-.}"

# Run tests with coverage
pytest "$TEST_ARGS" -v --tb=short --cov=src --cov-report=term-missing

echo ""
echo "✓ Tests complete!"

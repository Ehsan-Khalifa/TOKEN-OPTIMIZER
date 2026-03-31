#!/bin/bash
# Setup script for token-optimizer

set -e

echo "Token Optimizer Setup"
echo "===================="

# Check Python version
python_version=$(python --version 2>&1)
echo "Detected: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install package with all dependencies
echo "Installing package..."
pip install -e ".[all]" 2>/dev/null || pip install -e "."

# Install dev dependencies
echo "Installing dev dependencies..."
pip install -r requirements-dev.txt 2>/dev/null || true

# Setup environment file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Update .env with your API keys!"
fi

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your API keys"
echo "2. Run: make test"
echo "3. Or: pytest tests/ -v"

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -e ".[all]" 2>/dev/null || pip install -e "."

# Expose port for any services
EXPOSE 8000

# Default command
CMD ["python", "-m", "pytest", "tests/", "-v"]

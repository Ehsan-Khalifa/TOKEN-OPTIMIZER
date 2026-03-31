# Makefile for token-optimizer project

.PHONY: help install install-dev setup-env test test-unit test-integration test-benchmarks lint format type-check security-check build docker-build docker-run docker-dev clean

help:
	@echo "Token Optimizer - Development Commands"
	@echo "======================================"
	@echo "install              Install package"
	@echo "install-dev          Install with dev dependencies"
	@echo "test                 Run all tests"
	@echo "test-unit            Run unit tests only"
	@echo "test-integration     Run integration tests only"
	@echo "test-benchmarks      Run benchmark tests"
	@echo "lint                 Run linters (ruff)"
	@echo "format               Format code (black, isort)"
	@echo "type-check           Run type checker (mypy)"
	@echo "security-check       Run security checks"
	@echo "build                Build package"
	@echo "docker-build         Build Docker image"
	@echo "docker-run           Run tests in Docker"
	@echo "docker-dev           Start dev container"
	@echo "clean                Clean build artifacts"

install:
	pip install -e ".[all]"

install-dev:
	pip install -e ".[all]"
	pip install -r requirements-dev.txt

setup-env:
	cp .env.example .env
	@echo "Created .env file - update with your API keys"

test:
	pytest tests/ -v --tb=short

test-unit:
	pytest tests/unit/ -v --tb=short

test-integration:
	pytest tests/integration/ -v --tb=short -m "not requires_api"

test-benchmarks:
	pytest tests/benchmarks/ -v --tb=short -m benchmark

lint:
	ruff check src/ tests/

format:
	black src/ tests/
	isort src/ tests/

type-check:
	mypy src/ --ignore-missing-imports || true

security-check:
	bandit -r src/ -ll || true

build:
	python -m build

docker-build:
	docker build -f docker/Dockerfile -t token-optimizer:latest .

docker-run:
	docker run --rm token-optimizer:latest

docker-dev:
	docker-compose -f docker/docker-compose.yml run -it dev

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache

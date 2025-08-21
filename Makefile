# Makefile for Sidekick AI
# Common development and deployment tasks

.PHONY: help install install-dev test test-cov lint format clean run setup-env install-playwright

# Default target
help:
	@echo "Sidekick AI - Available commands:"
	@echo ""
	@echo "Setup:"
	@echo "  setup-env        - Copy environment template and install dependencies"
	@echo "  install          - Install production dependencies"
	@echo "  install-dev      - Install development dependencies"
	@echo "  install-playwright - Install Playwright browsers"
	@echo ""
	@echo "Development:"
	@echo "  run              - Run the application"
	@echo "  test             - Run tests"
	@echo "  test-cov         - Run tests with coverage"
	@echo "  lint             - Run linting checks"
	@echo "  format           - Format code with Black"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean            - Clean up generated files"
	@echo "  dist             - Build distribution package"

# Environment setup
setup-env:
	@echo "Setting up environment..."
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "Created .env file from template. Please edit it with your API keys."; \
	else \
		echo ".env file already exists."; \
	fi
	@echo "Installing dependencies..."
	@pip install -r requirements.txt
	@echo "Environment setup complete!"

# Install production dependencies
install:
	@echo "Installing production dependencies..."
	@pip install -r requirements.txt

# Install development dependencies
install-dev:
	@echo "Installing development dependencies..."
	@pip install -r requirements.txt
	@pip install -e ".[dev]"

# Install Playwright browsers
install-playwright:
	@echo "Installing Playwright browsers..."
	@playwright install

# Run the application
run:
	@echo "Starting Sidekick AI..."
	@python src/main.py

# Run tests
test:
	@echo "Running tests..."
	@pytest tests/ -v

# Run tests with coverage
test-cov:
	@echo "Running tests with coverage..."
	@pytest tests/ --cov=src --cov-report=html --cov-report=term

# Run linting
lint:
	@echo "Running linting checks..."
	@flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503
	@mypy src/ --ignore-missing-imports

# Format code
format:
	@echo "Formatting code with Black..."
	@black src/ tests/ --line-length=88

# Clean up generated files
clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.pyd" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "Cleanup complete!"

# Build distribution package
dist:
	@echo "Building distribution package..."
	@python setup.py sdist bdist_wheel

# Development workflow
dev: install-dev install-playwright
	@echo "Development environment ready!"

# Production setup
prod: install install-playwright
	@echo "Production environment ready!"

# Quick start (setup everything and run)
quickstart: setup-env install-playwright run

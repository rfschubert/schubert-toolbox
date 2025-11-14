# Makefile for Schubert Toolbox Python project
# Provides convenient commands for development tasks
# Documentation: ../docs/python/LINTING.md

SHELL := /bin/bash
.PHONY: help install lint lint-fix test test-cov clean format check security unused

# Default target
help:
	@echo "Schubert Toolbox Python - Available commands:"
	@echo ""
	@echo "  install     - Install dependencies and setup development environment"
	@echo "  lint        - Run all linting checks (no fixes)"
	@echo "  lint-fix    - Run linting with automatic fixes"
	@echo "  format      - Format code using ruff"
	@echo "  check       - Run type checking with mypy"
	@echo "  security    - Run security checks with bandit"
	@echo "  unused      - Check for unused imports"
	@echo "  test        - Run tests"
	@echo "  test-cov    - Run tests with coverage"
	@echo "  clean       - Clean up generated files"
	@echo ""
	@echo "  Documentation: ../docs/python/LINTING.md"
	@echo ""

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -e ".[dev]" || pip install ruff mypy pre-commit bandit pytest pytest-cov
	@echo "Setting up pre-commit hooks..."
	pre-commit install || echo "Pre-commit not available, skipping hooks setup"

# Linting commands
lint:
	@echo "Running linting checks..."
	@source venv/bin/activate && python lint.py --check src/

lint-fix:
	@echo "Running linting with fixes..."
	@source venv/bin/activate && python lint.py --fix src/

format:
	@echo "Formatting code..."
	@source venv/bin/activate && python lint.py --ruff --fix src/

check:
	@echo "Running type checks..."
	@source venv/bin/activate && python lint.py --mypy src/

security:
	@echo "Running security checks..."
	@source venv/bin/activate && python lint.py --security src/

unused:
	@echo "Checking for unused imports..."
	@source venv/bin/activate && python lint.py --unused src/

# Testing commands
test:
	@echo "Running tests..."
	@source venv/bin/activate && python -m pytest tests/ -v

test-cov:
	@echo "Running tests with coverage..."
	@source venv/bin/activate && python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# Cleanup
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/

# Quick development workflow
dev-setup: install
	@echo "Development environment ready!"

# Pre-commit workflow
pre-commit: lint-fix test
	@echo "Pre-commit checks completed!"

# CI workflow
ci: lint test
	@echo "CI checks completed!"

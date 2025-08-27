# Makefile for priority-config
.PHONY: help install agreement test test-verbose lint format build clean publish-test publish example all

help:
	@echo "Priority-Config Development Commands:"
	@echo "  install        - Install package in development mode"
	@echo "  agreement      - Check source-test agreements"
	@echo "  test           - Run tests"
	@echo "  test-verbose   - Run tests with verbose output"
	@echo "  test-coverage  - Run tests with coverage report"
	@echo "  lint           - Run code linting with ruff"
	@echo "  format         - Format code with ruff"
	@echo "  typecheck      - Run type checking with mypy"
	@echo "  build          - Build package for distribution"
	@echo "  clean          - Remove build artifacts and cache files"
	@echo "  example        - Run getting started example"
	@echo "  publish-test   - Publish to test PyPI"
	@echo "  publish        - Publish to production PyPI"
	@echo "  all            - Run full development cycle (lint, test, build)"

install:
	pip install -e ".[dev]"
	pre-commit install

agreement:
	tests/custom/test_src_test_agreement.py

test-changed:
	@echo "Running tests affected by code changes..."
	pytest --testmon tests/ -v --cov-report=term-missing

test-full:
	@echo "Running tests with coverage..."
	pytest tests/ -v --cov-report=term-missing

coverage-html:
	@echo "Generating HTML coverage report..."
	pytest tests/ --cov=src/priority_config --cov-report=html:tests/reports/htmlcov --cov-report=term-missing

ci-container:
	@echo "🏗️ Running CI on HPC with containers (direct)..."
	./tests/github_actions/run_ci_container.sh

ci-act:
	@echo "⚡ Running GitHub Actions locally with Singularity..."
	./tests/github_actions/run_ci_act_and_container.sh

ci-local:
	@echo "🚀 Running local CI emulator (Python-based)..."
	./tests/github_actions/run_ci_local.sh

lint:
	@echo "Running linting and formatting..."
	ruff check src/ tests/
	ruff format src/ tests/

clean:
	@echo "Cleaning cache files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .mypy_cache .pytest_cache tests/reports/htmlcov tests/reports/coverage.json tests/github/local_ci_report.json build/ dist/ *.egg-info/ 2>/dev/null || true
	chmod -R +w .ruff_cache 2>/dev/null || true
	rm -rf .ruff_cache 2>/dev/null || true

build:
	@echo "Building package..."
	python -m build

upload-pypi-test:
	@echo "Uploading to Test PyPI..."
	python -m twine upload --repository testpypi dist/*

upload-pypi:
	@echo "Uploading to PyPI..."
	python -m twine upload dist/*

release: build upload-pypi clean
	@echo "Package released to PyPI!"

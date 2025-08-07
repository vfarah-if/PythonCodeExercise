.PHONY: help setup install test watch lint lint-fix pylint format clean all demo

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup    - Install uv and create virtual environment"
	@echo "  make install  - Install project dependencies"
	@echo "  make test     - Run tests once"
	@echo "  make watch    - Run tests in watch mode (continuous testing)"
	@echo "  make lint     - Run ruff linter"
	@echo "  make lint-fix - Fix auto-fixable linting issues"
	@echo "  make pylint   - Run pylint for additional code quality checks"
	@echo "  make format   - Format code with ruff"
	@echo "  make clean    - Remove cache files and virtual environment"
	@echo "  make demo     - Run the Clean Architecture demo application"
	@echo "  make all      - Clean, setup, install, and start watch mode"

# Install uv if not present and create virtual environment
setup:
	@echo "🔧 Setting up Python environment..."
	@if ! command -v uv &> /dev/null; then \
		echo "📦 Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "✅ uv installed successfully"; \
		echo "⚠️  Please restart your terminal or run: source $$HOME/.cargo/env"; \
	else \
		echo "✅ uv is already installed"; \
	fi
	@echo "🐍 Creating virtual environment with Python 3.12..."
	@uv venv --python 3.12
	@echo "✅ Virtual environment created"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@uv sync
	@echo "✅ Dependencies installed"

# Run tests once
test:
	@echo "🧪 Running tests..."
	@uv run pytest -v

# Run tests in watch mode
watch:
	@echo "👀 Starting test watch mode..."
	@echo "Tests will automatically rerun when you save files."
	@echo "Press Ctrl+C to stop."
	@uv run ptw --config /dev/null --clear --runner "pytest" -- -x --ff -q

# Run linter
lint:
	@echo "🔍 Running linter..."
	@uv run ruff check src tests

# Fix auto-fixable linting issues
lint-fix:
	@echo "🔧 Fixing auto-fixable linting issues..."
	@uv run ruff check --fix src tests
	@echo "✅ Auto-fixable issues resolved"

# Run pylint for additional code quality checks
pylint:
	@echo "🔍 Running pylint for code quality analysis..."
	@uv run pylint $$(git ls-files '*.py') || echo "⚠️  Some pylint warnings found - check output above"

# Format code
format:
	@echo "✨ Formatting code..."
	@uv run ruff format src tests
	@echo "✅ Code formatted"

# Run the Clean Architecture demo
demo:
	@echo "🏗️  Starting Clean Architecture Demo..."
	@echo "This demonstrates clean architecture principles in Python"
	@echo "----------------------------------------"
	@uv run python -m src.clean_architecture_example.main

# Clean up generated files and caches
clean:
	@echo "🧹 Cleaning up..."
	@rm -rf .venv
	@rm -rf .pytest_cache
	@rm -rf .ruff_cache
	@rm -rf __pycache__
	@rm -rf src/__pycache__
	@rm -rf tests/__pycache__
	@rm -rf data/users  # Clean demo data directory
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Full setup and start development
all: clean setup install
	@echo "🚀 Setup complete! Starting watch mode..."
	@$(MAKE) watch
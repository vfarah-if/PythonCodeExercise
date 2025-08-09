.PHONY: help setup install test watch lint lint-fix format clean all setup-env setup-env-dry setup-env-help setup-env-init setup-env-example setup-brew-software setup-brew-all install-setup-env-global uninstall-setup-env-global

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup    - Install uv and create virtual environment"
	@echo "  make install  - Install project dependencies"
	@echo "  make test     - Run tests once"
	@echo "  make watch    - Run tests in watch mode (continuous testing)"
	@echo "  make lint     - Run ruff linter"
	@echo "  make lint-fix - Fix auto-fixable linting issues"
	@echo "  make format   - Format code with ruff"
	@echo "  make clean    - Remove cache files and virtual environment"
	@echo "  make all      - Clean, setup, install, and start watch mode"
	@echo ""
	@echo "Setup Environment CLI:"
	@echo "  make setup-env         - Run setup-environment CLI with ~/dev folder"
	@echo "  make setup-env-dry     - Run setup-environment CLI in dry-run mode"
	@echo "  make setup-env-help    - Show setup-environment CLI help and usage"
	@echo "  make setup-env-init    - Generate .env template file"
	@echo "  make setup-env-example - Generate .env.example template file"
	@echo ""
	@echo "Software Installation:"
	@echo "  make setup-brew-software - Install configured development software interactively"
	@echo "  make setup-brew-all      - Install all configured software without prompts"
	@echo "  make install-setup-env-global   - Install setup-environment CLI tool globally"
	@echo "  make uninstall-setup-env-global - Uninstall setup-environment CLI tool"

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

# Format code
format:
	@echo "✨ Formatting code..."
	@uv run ruff format src tests
	@echo "✅ Code formatted"

# Clean up generated files and caches
clean:
	@echo "🧹 Cleaning up..."
	@rm -rf .venv
	@rm -rf .pytest_cache
	@rm -rf .ruff_cache
	@rm -rf __pycache__
	@rm -rf src/__pycache__
	@rm -rf tests/__pycache__
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

# Run setup-environment CLI
setup-env:
	@echo "🌱 Running setup-environment CLI..."
	@if [ ! -d "$$HOME/test" ]; then \
		echo "📁 Creating ~/test directory..."; \
		mkdir -p "$$HOME/test"; \
	fi
	@uv run setup-environment --dev-folder "$$HOME/test"

# Run setup-environment CLI in dry-run mode
setup-env-dry:
	@echo "🔍 Running setup-environment CLI in dry-run mode..."
	@if [ ! -d "$$HOME/test" ]; then \
		echo "📁 Creating ~/test directory..."; \
		mkdir -p "$$HOME/test"; \
	fi
	@uv run setup-environment --dev-folder "$$HOME/test" --dry-run

# Show setup-environment CLI help
setup-env-help:
	@echo "📚 Setup Environment CLI Help:"
	@echo "================================"
	@uv run setup-environment --help

# Generate .env template file
setup-env-init:
	@echo "📝 Generating .env template file..."
	@uv run setup-environment --generate-env
	@echo "💡 Edit .env with your repository URLs, then run 'make setup-env'"

# Generate .env.example template file
setup-env-example:
	@echo "📝 Generating .env.example template file..."
	@uv run setup-environment --generate-env-example
	@echo "💡 Copy .env.example to .env and customise with your repositories"

# Install development software interactively
setup-brew-software:
	@echo "🛠️  Installing development software..."
	@echo "This will check for and install: python+uv, git+config+ssh, nvm+node, gh, awscli, azure-cli, zsh, terraform, oh-my-zsh, iterm2, slack"
	@echo "You'll be prompted before each installation."
	@if [ ! -d "/tmp" ]; then mkdir -p "/tmp"; fi
	@uv run setup-environment --dev-folder /tmp --skip-npmrc
	@echo "⚠️  Note: Skipped Git repository cloning (only software installation)"

# Install all development software without prompts
setup-brew-all:
	@echo "🚀 Installing all development software automatically..."
	@echo "This will install: python+uv, git+config+ssh, nvm+node, gh, awscli, azure-cli, zsh, terraform, oh-my-zsh, iterm2, slack"
	@echo "No prompts - installing everything configured as required or optional"
	@if [ ! -d "/tmp" ]; then mkdir -p "/tmp"; fi
	@uv run setup-environment --dev-folder /tmp --skip-npmrc --install-all-software
	@echo "⚠️  Note: Skipped Git repository cloning (only software installation)"

# Install setup-environment CLI globally
install-setup-env-global:
	@echo "🌍 Installing setup-environment CLI globally..."
	@echo ""
	@echo "📚 About setup-environment CLI:"
	@echo "  The setup-environment tool automates developer environment setup including:"
	@echo "  • Installing development software (via Homebrew)"
	@echo "  • Cloning and organising Git repositories"
	@echo "  • Setting up SSH keys and Git configuration"
	@echo "  • Configuring Node.js, Python, and other tools"
	@echo ""
	@echo "🔧 Installation options:"
	@echo ""
	@echo "Option 1: Install with uvx (recommended for global tools):"
	@echo "  uvx install --from . setup-environment"
	@echo ""
	@echo "Option 2: Install with uv tool (creates isolated environment):"
	@echo "  uv tool install ."
	@echo ""
	@echo "Option 3: Install with pipx (if you prefer pipx):"
	@echo "  pipx install ."
	@echo ""
	@echo "📦 Installing with uv tool..."
	@if ! command -v uv &> /dev/null; then \
		echo "❌ uv is not installed. Please run 'make setup' first."; \
		exit 1; \
	fi
	@uv tool install . --force
	@echo ""
	@echo "✅ setup-environment CLI installed globally!"
	@echo ""
	@echo "📍 The command 'setup-environment' is now available system-wide"
	@echo ""
	@echo "💡 Usage examples:"
	@echo "  setup-environment --help                    # Show help"
	@echo "  setup-environment --dev-folder ~/dev        # Set up dev environment"
	@echo "  setup-environment --generate-env            # Generate .env template"
	@echo "  setup-environment --dry-run                 # Preview actions"
	@echo ""
	@echo "🔍 To verify installation:"
	@which setup-environment
	@setup-environment --version 2>/dev/null || setup-environment --help | head -n 1

# Uninstall setup-environment CLI globally
uninstall-setup-env-global:
	@echo "🗑️  Uninstalling setup-environment CLI globally..."
	@echo ""
	@if ! command -v uv &> /dev/null; then \
		echo "❌ uv is not installed. Cannot proceed with uninstallation."; \
		exit 1; \
	fi
	@if command -v setup-environment &> /dev/null; then \
		echo "📍 Found setup-environment at: $$(which setup-environment)"; \
		echo ""; \
		uv tool uninstall setup-environment; \
		echo ""; \
		if command -v setup-environment &> /dev/null; then \
			echo "⚠️  setup-environment still exists. It may have been installed with a different tool."; \
			echo "💡 Try these alternative uninstall methods:"; \
			echo "  pipx uninstall setup-environment    # If installed with pipx"; \
			echo "  pip uninstall python-code-exercise  # If installed with pip"; \
		else \
			echo "✅ setup-environment CLI successfully uninstalled!"; \
		fi; \
	else \
		echo "ℹ️  setup-environment is not installed globally."; \
		echo "Nothing to uninstall."; \
	fi
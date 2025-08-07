# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Documentation Standards

### UK English Convention
When creating or updating documentation in this project:
- Use UK English spelling conventions (e.g., "practise" as verb, "practice" as noun, "organisation", "behaviour", "licence", "minimise", "initialisation", "parametrised", "verbalise", "customisation")
- Common UK spellings to use:
  - colour (not color)
  - flavour (not flavor)
  - honour (not honor)
  - centre (not center)
  - metre (not meter)
  - analyse (not analyze)
  - organisation (not organization)
  - specialise (not specialize)
  - optimise (not optimize)
  - synchronise (not synchronize)

## Project Overview

This is a Python kata practice environment designed for Test-Driven Development (TDD) exercises. It uses modern Python tooling to provide a smooth development experience similar to JavaScript testing frameworks.

## Core Commands

### Development Workflow
```bash
# Initial setup (one-time)
make setup

# Install/update dependencies
make install

# Run tests in watch mode (primary development mode)
make watch

# Run tests once
make test

# Lint code
make lint

# Format code
make format

# Clean and reinstall
make all
```

### Direct Testing Commands
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_sum.py

# Run tests matching pattern
uv run pytest -k "test_pattern"

# Run with verbose output
uv run pytest -v
```

## Project Architecture

### Directory Structure
```
/
├── src/                 # Source code packages
│   └── [kata_name]/    # Individual kata modules
│       ├── __init__.py # Package initialisation
│       └── *.py        # Implementation files
├── tests/              # Test files (mirrors src structure)
│   └── test_*.py       # Test files (prefix with test_)
├── pyproject.toml      # Project configuration and dependencies
├── Makefile           # Development automation
└── .python-version    # Python version specification (3.12)
```

### Key Design Decisions

#### Technology Stack

**uv (Package Manager)**
- Chosen for its exceptional speed (10-100x faster than pip)
- Provides reproducible builds with lock files
- Integrated virtual environment management
- Modern replacement for pip, pip-tools, pipx, poetry, and pyenv
- Actively maintained by Astral (creators of ruff)

**pytest (Testing Framework)**
- Industry standard for Python testing
- Simple assertion-based syntax reduces boilerplate
- Powerful fixtures system for test data management
- Excellent error reporting and debugging
- Rich plugin ecosystem (pytest-watch, pytest-cov, etc.)
- Preferred over unittest for its simplicity and features

**pytest-watch (Continuous Testing)**
- Provides Jest-like watch mode for Python
- Automatically reruns tests on file changes
- Essential for TDD workflow
- Configurable file watching patterns

**ruff (Linting & Formatting)**
- Fastest Python linter available (written in Rust)
- Replaces multiple tools: flake8, pylint, black, isort
- Single tool for both linting and formatting
- Minimal configuration with sensible defaults
- Same team as uv ensures ecosystem consistency

### Testing Conventions

1. **Test File Naming**: All test files must start with `test_`
2. **Test Function Naming**: Test functions should start with `test_` and be descriptive
3. **Test Organisation**: Group related tests in classes when appropriate
4. **Assertions**: Use simple `assert` statements, pytest provides excellent diffs
5. **Fixtures**: Use fixtures for reusable test data and setup

### Code Style

- Follow PEP 8 (enforced by ruff)
- Use type hints for function signatures
- Keep functions small and focused (ideal for katas)
- Write descriptive test names that document behaviour

## Common Development Tasks

### Adding a New Kata

1. Create the kata module:
```bash
mkdir -p src/my_kata
touch src/my_kata/__init__.py
touch src/my_kata/solution.py
```

2. Create the test file:
```bash
touch tests/test_my_kata.py
```

3. Start with a failing test (Red phase)
4. Implement minimal code to pass (Green phase)
5. Refactor while keeping tests green

### Running Specific Tests

```bash
# Run a specific test class
uv run pytest tests/test_sum.py::TestSumFunction

# Run a specific test method
uv run pytest tests/test_sum.py::TestSumFunction::test_positive_numbers

# Run tests with specific marker
uv run pytest -m "slow"
```

### Debugging Tests

```bash
# Drop into debugger on failure
uv run pytest --pdb

# Show local variables on failure
uv run pytest -l

# Increase verbosity
uv run pytest -vv

# Show print statements
uv run pytest -s
```

## Best Practices for Kata Development

1. **Always start with a test** - Write the test before the implementation
2. **Keep tests simple** - Each test should verify one behaviour
3. **Use descriptive names** - Test names should explain what they verify
4. **Minimise test setup** - Use fixtures for complex setup
5. **Test edge cases** - Empty inputs, negative numbers, large values
6. **Refactor regularly** - Clean up code while tests are green

## Troubleshooting

### Common Issues

**uv not found**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or with homebrew
brew install uv
```

**Import errors**
```bash
# Ensure you're using uv run
uv run pytest  # Correct
pytest        # May fail if venv not activated
```

**Tests not discovered**
- Ensure test files start with `test_`
- Ensure test functions start with `test_`
- Check that `__init__.py` exists in packages

## Performance Considerations

- uv caches packages globally, reducing redundant downloads
- pytest caches test discovery for faster subsequent runs
- ruff is extremely fast and won't slow down development
- Use `pytest-xdist` for parallel test execution if needed

## Integration with IDEs

### VS Code
- Install Python extension
- Select interpreter: `.venv/bin/python`
- Configure test discovery for pytest
- Enable ruff for linting

### PyCharm
- Mark `src` as Sources Root
- Mark `tests` as Test Sources Root
- Configure pytest as test runner
- Enable ruff inspections

## Continuous Integration

For CI/CD pipelines:
```bash
# Install dependencies
uv sync

# Run tests with coverage
uv run pytest --cov=src --cov-report=xml

# Run linting
uv run ruff check src tests

# Check formatting
uv run ruff format --check src tests
```
# PythonCodeExercise

A modern Python kata practice environment using uv and pytest for Test-Driven Development (TDD) exercises.

## Overview

This project provides a reusable, well-documented kata framework for practising Python coding skills. It emphasises:
- Test-Driven Development (TDD)
- Pair programming practices
- Modern Python tooling with uv
- Continuous testing workflow

## Quick Start

```bash
# One-time setup
make setup

# Install dependencies
make install

# Run tests in watch mode (recommended for kata practice)
make watch

# Or run tests once
make test
```

## Prerequisites

- Python 3.12 or higher
- macOS, Linux, or Windows with WSL

## Project Structure

```
PythonCodeExercise/
├── Makefile              # Development workflow commands
├── pyproject.toml        # Project configuration and dependencies
├── .python-version       # Python version specification
├── src/                  # Source code
│   └── sum/             # Example kata module
│       ├── __init__.py
│       └── sum.py       # Simple sum function
├── tests/               # Test suite
│   └── test_sum.py      # Tests for sum kata
├── README.md            # This file
└── CLAUDE.md            # Claude Code AI assistant guidance
```

## Available Commands

### Makefile Commands

| Command | Description |
|---------|-------------|
| `make setup` | Install uv if not present and create virtual environment |
| `make install` | Install project dependencies |
| `make test` | Run tests once |
| `make watch` | Run tests in watch mode (auto-rerun on changes) |
| `make lint` | Check code with ruff linter |
| `make format` | Format code with ruff |
| `make clean` | Remove cache files and virtual environment |
| `make all` | Clean install and start watch mode |

### Direct uv Commands

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_sum.py

# Run tests matching pattern
uv run pytest -k "test_sum"
```

## Kata Practice Workflow

### 1. Choose or Create a Kata

Create a new module in `src/` for your kata:
```bash
mkdir -p src/my_kata
touch src/my_kata/__init__.py
touch src/my_kata/my_kata.py
touch tests/test_my_kata.py
```

### 2. Follow the TDD Cycle

1. **Red**: Write a failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve the code while keeping tests green

### 3. Use Watch Mode

```bash
make watch
```

This automatically reruns tests when you save files, providing instant feedback.

## Pair Programming Guidelines

### Driver-Navigator Pattern

**Driver** (at keyboard):
- Types the code
- Focuses on syntax and implementation details
- Asks questions when uncertain

**Navigator** (observer):
- Reviews code in real-time
- Thinks strategically about design
- Suggests improvements and catches errors
- Manages the todo list

### Rotation

Switch roles every:
- 15-20 minutes (recommended)
- After completing a test cycle
- When stuck on a problem

### Communication Tips

1. **Think aloud**: Verbalise your thought process
2. **Ask questions**: "What if we..." / "Should we consider..."
3. **Be specific**: Point to exact lines when discussing code
4. **Stay engaged**: Both participants should be actively involved

## Testing Best Practices

### Test Organisation

```python
# tests/test_my_kata.py
import pytest
from src.my_kata.my_kata import my_function

class TestMyFunction:
    """Group related tests in classes"""
    
    def test_should_handle_empty_input(self):
        """Use descriptive test names"""
        assert my_function([]) == expected_result
    
    def test_should_raise_on_invalid_input(self):
        """Test error cases"""
        with pytest.raises(ValueError):
            my_function(invalid_input)
```

### Assertion Styles

```python
# Simple assertions (pytest will show helpful diffs)
assert result == expected

# Multiple assertions
assert all([
    condition1,
    condition2,
    condition3
])

# Custom assertion messages
assert result == expected, f"Expected {expected}, got {result}"
```

### Test Fixtures

```python
@pytest.fixture
def sample_data():
    """Reusable test data"""
    return [1, 2, 3, 4, 5]

def test_sum_with_fixture(sample_data):
    assert sum_function(sample_data) == 15
```

## Why These Tools?

### uv
- **Speed**: 10-100x faster than pip
- **Reliability**: Built-in lock files for reproducible builds
- **Simplicity**: Combines package and virtual environment management
- **Modern**: Active development by the team behind ruff

### pytest
- **Simplicity**: No boilerplate, just `assert` statements
- **Power**: Rich plugin ecosystem and fixtures
- **Debugging**: Excellent error messages and introspection
- **Industry Standard**: Most popular Python testing framework

### ruff
- **Performance**: Fastest Python linter available
- **Comprehensive**: Replaces flake8, black, isort, and more
- **Configurable**: Sensible defaults with extensive customisation
- **Maintained**: By the same team as uv

## Example Kata: Sum Function

The project includes a simple sum function as an example:

```python
# src/sum/sum.py
def sum_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
```

With comprehensive tests:

```python
# tests/test_sum.py
def test_sum_positive_numbers():
    assert sum_numbers(2, 3) == 5

def test_sum_negative_numbers():
    assert sum_numbers(-1, -1) == -2
```

## Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [pytest Documentation](https://docs.pytest.org/)
- [ruff Documentation](https://docs.astral.sh/ruff/)
- [Python Testing Best Practices](https://realpython.com/pytest-python-testing/)
- [Kata Catalog](https://www.codewars.com/) - Find coding challenges

## Contributing

1. Follow TDD practices
2. Ensure all tests pass before committing
3. Use descriptive commit messages
4. Keep katas simple and focused on one concept

## Licence

This project is for educational purposes. Feel free to use it as a template for your own kata practice.
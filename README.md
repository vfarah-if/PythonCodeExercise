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

## Creating This Project From Scratch

If you want to understand how this project was built or create something similar, here's the step-by-step process using uv:

### Step 1: Install uv and Initialise Project

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project directory
mkdir PythonCodeExercise
cd PythonCodeExercise

# Initialise with uv (creates basic pyproject.toml)
uv init

# Set Python version
echo "3.12" > .python-version
```

### Step 2: Add Core Dependencies

```bash
# Add testing framework
uv add pytest pytest-watch pytest-cov

# Add linting/formatting tool
uv add ruff

# Add development dependencies (optional)
uv add --dev ipython pytest-xdist pytest-mock
```

This automatically updates your `pyproject.toml` with the dependencies.

### Step 3: Configure Tools in pyproject.toml

After uv creates the basic file, you manually add tool configurations:

```toml
# Add these sections to pyproject.toml:

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
# ... more pytest config

[tool.ruff]
target-version = "py312"
line-length = 88
# ... more ruff config

[tool.coverage.run]
source = ["src"]
# ... more coverage config
```

### Step 4: Create Project Structure

```bash
# Create source and test directories
mkdir -p src/sum tests

# Create __init__.py file (IMPORTANT - see why below)
touch src/sum/__init__.py

# Create your first module
touch src/sum/sum.py

# Create your first test
touch tests/test_sum.py
```

**Why `__init__.py`?** This file is crucial for Python packages:
- **Makes the directory a package**: Without it, Python won't recognise `sum` as an importable package
- **Simplifies imports**: Allows `from src.sum import sum_numbers` instead of `from src.sum.sum import sum_numbers`
- **Controls the public API**: Use `__all__` to explicitly define what gets exported
- **Professional structure**: Follows Python packaging best practices

Example `__init__.py` content:
```python
"""Sum kata module for practising TDD."""

from .sum import sum_numbers, sum_list, sum_positive

__all__ = ["sum_numbers", "sum_list", "sum_positive"]  # Explicitly declare public API
```

### Step 5: Add Build Configuration

For packaging, add to `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src"]
```

### Step 6: Create Makefile for Workflow

Create a `Makefile` to standardise common commands (optional but recommended).

### Understanding pyproject.toml Creation

**Important:** Developers rarely write `pyproject.toml` from scratch. The typical workflow is:

1. **Use a tool to initialise** (`uv init`, `poetry init`, `pdm init`)
2. **Add dependencies via commands** (`uv add`, `poetry add`, etc.)
3. **Copy tool configurations** from documentation or other projects
4. **Iterate and refine** as the project grows

The comprehensive `pyproject.toml` in this project represents what you'd build up over time, not what you'd write initially. Most projects start minimal and grow as needed.

#### Python Package Manager Comparison

When choosing a package manager for your Python project, consider these popular options:

| Feature | **uv** | **Poetry** | **PDM** |
|---------|--------|------------|---------|
| **Speed** | ⚡ 10-100x faster than pip | 🐢 Slower, especially for large deps | 🏃 Faster than Poetry, slower than uv |
| **Written in** | Rust (blazing fast) | Python (slower) | Python (moderate speed) |
| **Lock Files** | ✅ `uv.lock` | ✅ `poetry.lock` | ✅ `pdm.lock` |
| **Virtual Env Management** | ✅ Built-in | ✅ Built-in | ✅ Built-in |
| **Python Version Management** | ✅ Built-in | ❌ Needs pyenv | ✅ Built-in |
| **PEP Compliance** | ✅ PEP 517/518/621 | ⚠️ Some custom behaviour | ✅ Strict PEP 582/621 |
| **Install Global Tools** | ✅ `uvx` (like npx) | ❌ Not supported | ❌ Not supported |
| **Workspace/Monorepo** | ✅ Native support | ⚠️ Limited | ✅ Native support |
| **Released** | 2024 (newest) | 2018 (mature) | 2020 (stable) |
| **Backed by** | Astral (ruff team) | Independent | Independent |
| **Learning Curve** | 📗 Easy (pip-like) | 📙 Moderate | 📗 Easy |
| **Ecosystem** | 🌱 Growing rapidly | 🌳 Large, established | 🌿 Growing |

#### Command Syntax Comparison

| Task | **uv** | **Poetry** | **PDM** |
|------|--------|------------|---------|
| Initialise project | `uv init` | `poetry new` / `poetry init` | `pdm init` |
| Add dependency | `uv add requests` | `poetry add requests` | `pdm add requests` |
| Add dev dependency | `uv add --dev pytest` | `poetry add --dev pytest` | `pdm add -d pytest` |
| Install deps | `uv sync` | `poetry install` | `pdm install` |
| Run command | `uv run python app.py` | `poetry run python app.py` | `pdm run python app.py` |
| Update deps | `uv lock --upgrade` | `poetry update` | `pdm update` |
| Build package | `uv build` | `poetry build` | `pdm build` |

#### When to Use Each Tool

**Choose uv if you want:**
- ⚡ Fastest possible performance
- 🎯 Simple, pip-like commands
- 🔧 All-in-one tool (packages + Python versions)
- 🚀 Modern tool with active development
- 📦 Drop-in pip replacement

**Choose Poetry if you want:**
- 🏢 Industry standard with wide adoption
- 📚 Extensive documentation and tutorials
- 🔌 Rich plugin ecosystem
- 🎨 Opinionated, guided workflow
- 👥 Large community support

**Choose PDM if you want:**
- 📏 Strict PEP compliance
- 🐍 Pure Python implementation
- 📁 PEP 582 `__pypackages__` support
- 🔄 Easy migration from pip
- 🏗️ Good for monorepos

#### Why This Project Uses uv

We chose **uv** for this kata practice environment because:
1. **Speed matters for TDD**: Fast dependency installation keeps the flow going
2. **Simplicity**: Familiar pip-like commands reduce learning curve
3. **Modern**: Latest best practices and active development
4. **Unified tool**: Manages packages AND Python versions
5. **Same team as ruff**: Consistent, high-quality tooling ecosystem

For kata practice where quick iteration is key, uv's speed advantage (10-100x faster) makes a noticeable difference in developer experience.

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
│   └── sum/             # Example kata module (reference only - create your own!)
│       ├── __init__.py  # Package initialiser (see below)
│       └── sum.py       # Example implementation
├── tests/               # Test suite
│   └── test_sum.py      # Example tests for reference
├── README.md            # This file
└── CLAUDE.md            # Claude Code AI assistant guidance
```

**Workflow:** The `sum` module serves as a reference. For actual kata practice:
1. Create a new branch: `git checkout -b kata/your-kata-name`
2. Add your module: `src/your_kata/`
3. Write tests: `tests/test_your_kata.py`
4. Practice TDD with `make watch`

### Understanding Python Package Structure

The `__init__.py` files in this project serve critical purposes:

1. **Package Recognition**: Tells Python that a directory should be treated as a package
2. **Import Simplification**: Enables cleaner import statements
3. **API Control**: Defines what's publicly available from the package
4. **Documentation**: Provides package-level documentation

#### Example: How `__init__.py` Improves Imports

**Without `__init__.py`:**
```python
# Ugly, reveals internal structure
from src.sum.sum import sum_numbers, sum_list, sum_positive
```

**With properly configured `__init__.py`:**
```python
# Clean, hides implementation details
from src.sum import sum_numbers, sum_list, sum_positive
```

#### Benefits for Kata Practice

- **Focus on Learning**: Clean imports let you focus on the kata, not the file structure
- **Scalability**: Easy to add new functions without changing import statements in tests
- **Best Practices**: Learn professional Python package structure from the start
- **Maintainability**: Control what's public vs internal implementation

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

### 1. Start a New Kata Branch

**Important:** The `sum` module is just an example. For each new kata, create a new branch:

```bash
# Create a new branch for your kata
git checkout -b kata/mars-rover

# Or for another kata
git checkout -b kata/fizz-buzz
```

### 2. Create Your Kata Module

Create a new module in `src/` for your kata (e.g., `mars_rover`, `fizz_buzz`, `bowling_game`):

```bash
# Example: Mars Rover kata
mkdir -p src/mars_rover
touch src/mars_rover/__init__.py
touch src/mars_rover/mars_rover.py
touch tests/test_mars_rover.py
```

Configure `__init__.py` for your kata:
```python
# src/mars_rover/__init__.py
"""Mars Rover kata module for practising OOP and state management."""

from .mars_rover import Rover, Position, Direction

__all__ = ["Rover", "Position", "Direction"]  # Export what's needed
```

This ensures clean imports in your tests:
```python
# tests/test_mars_rover.py
from src.mars_rover import Rover, Position, Direction  # Clean import!
```

**Note:** Keep the `sum` module as a reference example, but create your own modules for actual kata practice.

### 3. Follow the TDD Cycle

1. **Red**: Write a failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve the code while keeping tests green

### 4. Use Watch Mode

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

## Example Kata: Sum Functions (Reference Implementation)

**Note:** The `sum` module is provided as a reference example to demonstrate project structure and testing patterns. When practising katas, create your own modules in separate branches rather than modifying this example.

The project includes three sum functions as examples:

```python
# src/sum/sum.py
def sum_numbers(a: int | float, b: int | float) -> int | float:
    """Add two numbers together."""
    return a + b

def sum_list(numbers: list[int | float]) -> int | float:
    """Calculate the sum of a list of numbers."""
    if not numbers:
        raise ValueError("Cannot sum an empty list")
    return sum(numbers)

def sum_positive(numbers: list[int | float]) -> int | float:
    """Calculate the sum of only positive numbers in a list."""
    return sum(n for n in numbers if n > 0)
```

With comprehensive tests demonstrating various testing patterns:

```python
# tests/test_sum.py
def test_sum_positive_numbers():
    assert sum_numbers(2, 3) == 5

def test_sum_list_with_mixed():
    assert sum_list([1, -2, 3, -4, 5]) == 3

def test_sum_positive_filters_negative():
    assert sum_positive([1, -2, 3, -4, 5]) == 9
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
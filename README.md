# PythonCodeExercise

A modern Python kata practice environment using uv and pytest for Test-Driven Development (TDD) exercises.

## Overview

This project provides a reusable, well-documented kata framework for practising Python coding skills. It emphasises:
- Test-Driven Development (TDD)
- Pair programming practices
- Modern Python tooling with uv
- Continuous testing workflow

## Quick Start

`make all` to start watching code changes

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

# Create __init__.py file only if you need API exports (see why below)
touch src/sum/__init__.py

# Create your first module
touch src/sum/sum.py

# Create your first test
touch tests/test_sum.py
```

**When to use `__init__.py`?** This file is optional in modern Python:
- **API Control**: Create it only when you want to export a clean public API
- **Simplifies imports**: Allows `from src.sum import sum_numbers` instead of `from src.sum.sum import sum_numbers`
- **Namespace packages**: Python 3.3+ supports packages without `__init__.py` files
- **This project**: Uses namespace packages - only 1 `__init__.py` file exists (with actual content)

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
│       ├── __init__.py  # The only __init__.py file (has actual API exports)
│       └── sum.py       # Example implementation
├── src/clean_architecture_example/  # Clean Architecture demo (complete example)
│   ├── domain/          # Business logic and entities (no __init__.py needed!)
│   ├── application/     # Use cases and DTOs  
│   ├── infrastructure/  # Data persistence and external services
│   ├── presentation/    # CLI interface and API
│   └── shared/         # Cross-cutting concerns (DI, exceptions)
├── tests/               # Test suite
│   └── test_sum.py      # Example tests for reference
├── .pylintrc           # Pylint configuration for code quality
├── README.md            # This file
├── CLAUDE.md            # Claude Code AI assistant guidance
└── CLEAN-ARCHITECTURE.md  # Clean Architecture implementation guide
```

**Workflow:** The `sum` module serves as a reference. For actual kata practice:
1. Create a new branch: `git checkout -b kata/your-kata-name`
2. Add your module: `src/your_kata/`
3. Write tests: `tests/test_your_kata.py`
4. Practice TDD with `make watch`

### Understanding Python Package Structure

#### The `__init__.py` Reality Check

If you're coming from .NET or other modern languages, you might find Python's `__init__.py` files frustrating. **You're not wrong** - they feel like unnecessary boilerplate from the 1990s!

**Why These Files Exist:**
- Python's module system predates modern package management
- Explicit package declaration was considered "safer" than implicit
- Prevents accidental directory-to-package conversion

**The Modern Reality:**
- **This project eliminated 36 empty `__init__.py` files** - only 1 remains with actual content
- Uses Python 3.3+ "namespace packages" for cleaner directory structure
- Tooling configured to work properly without the marker files
- **Much cleaner** - no more empty boilerplate!

#### We Eliminated Them! 

**This project successfully removed all empty `__init__.py` files** with proper tooling configuration:

```bash
# We deleted all empty __init__.py files
find src -name "__init__.py" -size 0 -delete

# Everything still works!
make test   # ✅ 106 passed
make lint   # ✅ All checks passed  
make pylint # ✅ 10.00/10 rating
make demo   # ✅ Clean architecture demo works
```

**How We Made It Work:**

1. **Pylint Configuration** - Added namespace package support in `.pylintrc`
2. **PYTHONPATH Setup** - Configured import resolution in Makefile
3. **Disabled Irrelevant Warnings** - Ignored missing `__init__.py` errors
4. **Kept Essential Files** - Only `src/sum/__init__.py` remains (has actual API exports)

**The Results:**

| Before | After |
|--------|-------|
| 37 `__init__.py` files (36 empty) | 1 `__init__.py` file (with content) |
| Empty boilerplate everywhere | Clean directory structure |
| Traditional packages | Modern namespace packages |
| Works but feels dated | Works and feels modern |

#### Our Approach: Modern Python

**We eliminated the empty files** because:
1. **Cleaner structure** - no more meaningless marker files
2. **Modern Python** - uses namespace packages (Python 3.3+)
3. **Proper tooling** - configured linters to work correctly
4. **Best of both worlds** - modern approach with full tool support

#### The One File That Matters

Only one `__init__.py` file in this project actually contains code:

```python
# src/sum/__init__.py - The only non-empty one
"""Sum kata module for practising TDD."""

from .sum import sum_numbers, sum_list, sum_positive

__all__ = ["sum_numbers", "sum_list", "sum_positive"]
```

This enables clean imports:
```python
# Instead of: from src.sum.sum import sum_numbers
from src.sum import sum_numbers  # Much cleaner!
```

#### Benefits for Kata Practice

- **Focus on Learning**: Clean imports let you focus on the kata, not the file structure
- **Professional Structure**: Learn industry-standard Python patterns
- **Tool Compatibility**: Everything works smoothly with modern tooling
- **Maintainability**: Control what's public vs internal implementation

**Bottom Line**: The `__init__.py` files are Python's "necessary evil" - accept them and move on to the fun stuff!

## Available Commands

### Makefile Commands

| Command | Description |
|---------|-------------|
| `make setup` | Install uv if not present and create virtual environment |
| `make install` | Install project dependencies |
| `make test` | Run tests once |
| `make watch` | Run tests in watch mode (auto-rerun on changes) |
| `make lint` | Check code with ruff linter |
| `make lint-fix` | Fix auto-fixable linting issues |
| `make pylint` | Run pylint for additional code quality checks |
| `make format` | Format code with ruff |
| `make demo` | Run the Clean Architecture demo application |
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
# No need to create __init__.py - using namespace packages!
touch src/mars_rover/mars_rover.py
touch tests/test_mars_rover.py
```

**Note:** Unlike traditional Python projects, we don't create empty `__init__.py` files. The project uses modern namespace packages. Only create `__init__.py` if you need to export a clean API:

```python
# src/mars_rover/__init__.py (optional - only if you want clean imports)
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

## Clean Architecture Example

In addition to kata practice, this project includes a **complete Clean Architecture implementation** demonstrating enterprise-level Python design patterns. This is especially valuable for .NET developers transitioning to Python.

### What's Included

```bash
make demo  # Interactive CLI demonstrating clean architecture
```

The clean architecture example (`src/clean_architecture_example/`) showcases:

**🏗️ Architecture Layers:**
- **Domain**: Business entities, value objects, and repository interfaces
- **Application**: Use cases, DTOs, and business orchestration
- **Infrastructure**: File/memory repositories, external services
- **Presentation**: CLI interface and API endpoints
- **Shared**: Dependency injection container, exceptions, utilities

**🔧 .NET Developer Friendly Features:**
- **Dependency Injection**: Custom DI container similar to .NET Core
- **Repository Pattern**: Abstract interfaces with multiple implementations
- **Use Case Pattern**: Similar to MediatR handlers in .NET
- **Value Objects**: Immutable objects with validation
- **Exception Hierarchy**: Structured error handling
- **DTOs**: Clean data transfer between layers

**📋 Key Design Patterns:**
- Dependency Inversion Principle
- Single Responsibility Principle  
- Repository Pattern
- Factory Pattern
- Strategy Pattern

### Architecture Benefits

```python
# Clean separation of concerns
from domain.entities.user import User                    # Business logic
from application.use_cases.create_user import CreateUser # Orchestration
from infrastructure.repositories import FileUserRepo     # Data access
from presentation.cli import UserCLI                     # Interface
```

**For .NET Developers:**
- Familiar patterns (DI, repositories, use cases)
- Async/await support throughout
- Strong typing with type hints
- Clean exception hierarchy
- Testable architecture with 73 comprehensive tests

### Documentation

See `CLEAN-ARCHITECTURE.md` for detailed implementation guidance, including:
- Layer responsibilities and dependencies
- Dependency injection setup
- Testing strategies for each layer
- Migration guide from .NET concepts

## Code Quality Tooling

This project includes comprehensive code quality tools:

### Linting Strategy

**Two-tier approach** for maximum coverage:

1. **Ruff** (Primary): Fast linting and formatting
   - Replaces flake8, black, isort, pylint for most checks
   - Extremely fast (written in Rust)
   - Auto-fixes most issues

2. **Pylint** (Deep Analysis): Additional code quality insights
   - Detects complex code smells
   - Enforces coding standards
   - Provides detailed quality scoring

```bash
make lint      # Fast ruff checks (primary workflow)
make lint-fix  # Auto-fix common issues
make pylint    # Deep analysis (when needed)
```

### Quality Configuration

The project includes sensible defaults via `.pylintrc`:
- Disables overly pedantic warnings
- Focuses on meaningful quality metrics
- Achieves 10.0/10 pylint score
- Maintains fast development workflow

**Result**: Professional code quality without workflow interruption.

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
# PythonCodeExercise

[TOC]

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

## Prerequisites

- Python 3.12 or higher
- macOS, Linux, or Windows with WSL

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
| | |
| **Setup Environment CLI** | |
| `make setup-env` | Run setup-environment CLI with ~/dev folder |
| `make setup-env-dry` | Run setup-environment CLI in dry-run mode |
| `make setup-env-help` | Show setup-environment CLI help and usage |
| `make setup-env-init` | Generate .env template file |
| `make setup-env-example` | Generate .env.example template file |
| | |
| **AWS Credentials** | |
| `make aws-creds-init` | Initialize AWS SSO configuration (.env template) |
| `make aws-credentials` | Get AWS SSO credentials interactively |
| `make aws-creds` | Alias for aws-credentials |
| `make aws-creds-help` | Show AWS credentials help and usage |
| | |
| **Software Installation** | |
| `make setup-brew-software` | Install configured development software interactively |
| `make setup-brew-all` | Install all configured software without prompts |
| `make install-setup-env-global` | Install setup-environment CLI tool globally |

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

### Use Watch Mode

```bash
make watch
```

This automatically reruns tests when you save files, providing instant feedback.

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

# Setup Environment CLI

This project includes a production-grade CLI tool for setting up development environments with Git repositories and npmrc configuration.

### Overview

The `setup-environment` CLI automates the process of:
1. **Installing development software** with specialised services for complex tools
2. **Automatic SSH configuration** for private Git repositories
3. **Loading repository definitions** from YAML configuration files
4. **Cloning repositories** to a specified development folder
5. **Setting up npmrc configuration** for GitHub Package Registry

### Architecture

Built following **Clean Architecture** principles with comprehensive test coverage:

```shell
src/setup_environment/
├── config/                # Configuration files
│   ├── repositories.yaml  # Repository definitions
│   └── software.yaml      # Software to install
├── domain/                # Business logic & entities
│   ├── entities/          # Repository, NPMRCConfiguration
│   └── value_objects/     # DevFolderPath, PersonalAccessToken
├── application/           # Use cases & business rules
│   ├── interfaces/        # Service abstractions
│   └── use_cases/         # SetupRepositories, ConfigureNPMRC
├── infrastructure/        # External dependencies
│   ├── git/               # Git operations via subprocess
│   ├── npm/               # File system operations
│   └── repository_config_service.py  # YAML config loader
└── presentation/          # User interface (CLI)

tests/setup_environment/   # 124 comprehensive tests
├── unit/                  # Unit tests (all layers)
└── integration/           # End-to-end workflow tests
```

#### Architecture Documentation

For detailed architecture documentation and visual diagrams, see:

- **[ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md)** - Comprehensive Clean Architecture documentation with layer breakdown, component responsibilities, and data flow examples
- **[CLEAN_ARCHITECTURE_VISUAL.md](docs/architecture/CLEAN_ARCHITECTURE_VISUAL.md)** - Visual ASCII diagrams and Mermaid charts showing the circular/onion architecture structure  
- **[makefile-workflow.puml](docs/architecture/makefile-workflow.puml)** - PlantUML diagram visualising Makefile command relationships and development workflow

### Key Features

- **🏗️ Clean Architecture**: Domain-driven design with dependency injection
- **🛠️ Software Installation**: Automated setup of development tools via Homebrew
- **🔐 Intelligent SSH Setup**: Automatic SSH key generation and GitHub configuration
- **🎯 Specialised Services**: Custom setup for Python+uv, Git+SSH, NVM+Node.js
- **✅ TDD Implementation**: 205 tests with 100% pass rate  
- **🔍 Dry-Run Mode**: Test setup without making changes (`--dry-run`)
- **📄 YAML Configuration**: Structured repository definitions in YAML format
- **⚙️ Configuration-Driven**: Configure repositories via repositories.yaml
- **🔐 Interactive npmrc Setup**: Guided GitHub Personal Access Token creation
- **📁 Smart Organisation**: Clones to `~/dev/{org}/{repo}` structure
- **🚫 Skip Existing**: Automatically skips repositories that already exist
- **🔧 Custom Config Files**: Support for multiple repository configurations
- **⚡ Error Handling**: Comprehensive validation and user feedback

### Quick Start

**Development Software Setup:**

```bash
# Install development tools interactively
make setup-brew-software

# Or install all tools automatically
make setup-brew-all
```

**Using Repository Configuration:**

```bash
# Repository definitions are in config/repositories.yaml
# Edit to add your repositories
vim src/setup_environment/config/repositories.yaml

# Run the setup
make setup-env

# Or use a custom config file
setup-environment setup --dev-folder ~/dev --repositories-config ~/my-repos.yaml
```

**Testing First:**

```bash
# Test without making changes (works with both methods)
make setup-env-dry
```

### CLI Usage

The `setup-environment` CLI can be used either locally within the project or installed globally for system-wide access.

#### Local Usage (Within Project)

```bash
# Using the Makefile commands
make setup-env              # Run with ~/test folder
make setup-env-dry          # Dry-run mode
make setup-env-help         # Show help

# Direct usage with uv
uv run setup-environment setup --dev-folder ~/dev
```

#### Global Installation

Install the CLI globally to use it from anywhere on your system:

```bash
# Install globally using the Makefile
make install-setup-env-global

# Or install manually with uv
uv tool install .
```

After global installation, the `setup-environment` command is available system-wide:

```bash
# Basic usage
setup-environment setup --dev-folder ~/dev

# Use custom repository config file
setup-environment setup --dev-folder ~/dev --repositories-config ~/repos-production.yaml

# Skip npmrc configuration
setup-environment setup --dev-folder ~/dev --skip-npmrc

# Dry run (validation only, no changes)
setup-environment setup --dev-folder ~/dev --dry-run

# All options together
setup-environment setup --dev-folder ~/dev --repositories-config custom-repos.yaml --skip-npmrc --dry-run
```

### Repository Configuration

Repositories are defined in a YAML configuration file located at `src/setup_environment/config/repositories.yaml`:

```yaml
repositories:
  - name: Frontend Application
    url: git@github.com:your-org/frontend.git
    description: "Main frontend application"
    
  - name: Backend Services
    url: git@github.com:your-org/backend.git
    description: "Backend API services"
```

**Benefits of YAML configuration:**
- 📝 **Structure**: Clear, readable repository definitions
- 🏗️ **Organisation**: Group related repositories with metadata
- 🔄 **Portability**: Easy to share and version control
- 📋 **Documentation**: Include descriptions for each repository

#### Migration from Environment Variables

If you're currently using environment variables, migrate to .env files:

1. **Generate template**: `make setup-env-init`
2. **Copy existing vars**: Move your `GIT_REPO_*` variables to `.env`
3. **Test migration**: Use `make setup-env-dry` to verify
4. **Remove old vars**: Clean up your shell profile files

### Repository Structure

Repositories are cloned to organised directories:

```shell
~/dev/
├── facebook/
│   └── react/
├── microsoft/
│   └── vscode/
└── webuild-ai/
    ├── frontend/
    ├── backend/
    └── dev-tools/
```

### npmrc Configuration

The CLI provides a comprehensive, guided npmrc configuration experience:

#### Automatic Browser Navigation
1. **Direct Token Creation**: Opens directly to GitHub's token creation page
2. **Interactive Setup**: Step-by-step guidance through the entire process
3. **Smart Detection**: Checks if `~/.npmrc` exists and has valid GitHub token

#### Required Token Permissions
The CLI clearly displays required permissions with checkboxes:
- ☐ **repo** - Full control of private repositories
- ☐ **write:packages** - Upload packages to GitHub Package Registry
- ☐ **read:packages** - Download packages from GitHub Package Registry  
- ☐ **delete:packages** - Delete packages from GitHub Package Registry

#### Security Features
- **Hidden Input**: Token input is masked for security
- **Token Validation**: Validates token format (ghp_* or github_pat_*)
- **One-Time Warning**: Reminds users that GitHub shows tokens only once
- **Secure Storage**: Token is immediately saved to `~/.npmrc`

#### Generated Configuration
```ini
package-lock=true
legacy-peer-deps=true
//npm.pkg.github.com/:_authToken=ghp_your_token_here
@webuild-ai:registry=https://npm.pkg.github.com
```

**Note**: Existing `.npmrc` settings are preserved and merged with new configuration.

### Dry-Run Mode

Test your setup without making any changes:

```bash
make setup-env-dry
```

**Dry-run shows:**
- ✅ Repository validation and parsing
- 📁 Target paths where repos would be cloned  
- 🔍 Git installation check
- 📋 npmrc configuration status
- 🚫 **No actual cloning or file modifications**

### Development Workflow Integration

#### Environment Consistency

Perfect for:
- **Team onboarding**: New developers can set up entire environment with one command
- **Environment standardisation**: Same repositories and structure across all machines
- **Documentation**: Self-documenting development environment with version-controlled templates

### Error Handling

The CLI provides clear feedback for common issues:
- Missing Git installation
- Invalid repository URLs  
- Permission denied (private repos)
- Network connectivity issues
- Invalid directory paths
- Malformed Personal Access Tokens

### Testing

Run the comprehensive test suite:

```bash
# All tests (124 tests)
uv run pytest tests/setup_environment/ -v

# Unit tests only  
uv run pytest tests/setup_environment/unit/ -v

# Integration tests
uv run pytest tests/setup_environment/integration/ -v

# With coverage
uv run pytest tests/setup_environment/ --cov=src/setup_environment
```

### Implementation Highlights

- **Value Objects**: `DevFolderPath`, `PersonalAccessToken` with validation
- **Domain Entities**: `Repository`, `NPMRCConfiguration` with business logic
- **Use Cases**: `SetupRepositoriesUseCase`, `ConfigureNPMRCUseCase`
- **Clean Interfaces**: `GitService`, `NPMRCService` for easy testing and mocking
- **Comprehensive Testing**: Unit tests, integration tests, mocking, parametrised tests
- **Error Safety**: Extensive validation and graceful error handling

### Software Installation

The CLI includes automated development software installation via Homebrew:

#### Supported Software

**Specialised Services (Advanced Setup):**
- **Python Environment** - Python + uv package manager with custom configuration
- **Git + SSH** - Git installation + user configuration + SSH key generation
- **Node.js Environment** - NVM + latest Node.js LTS with proper shell integration

**Essential Development Tools:**
- **GitHub CLI (gh)** - GitHub's official command line tool ✅ *required*
- **AWS CLI** - Amazon Web Services command line interface ✅ *required*
- **Azure CLI** - Microsoft Azure command line interface ✅ *required*
- **Terraform** - Infrastructure as Code tool ✅ *required*

**Development Environment:**
- **iTerm2** - Terminal emulator for macOS
- **Zsh** - Z shell
- **Oh My Zsh** - Zsh configuration framework
- **Slack** - Team communication and collaboration platform
- **Cursor** - AI-powered code editor built on VS Code
- **Claude Code** - Anthropic's official CLI for Claude
- **Visual Studio Code** - Open-source code editor from Microsoft
- **Rectangle** - Window management app for macOS
- **Docker Desktop** - Docker containerization platform
- **AltTab** - Windows-style alt-tab window switcher for macOS
- **Google Chrome** - Web browser from Google
- **Brave Browser** - Privacy-focused web browser with no adverts in youtube videos
- **Firefox** - Open-source web browser from Mozilla
- **Postman** - API development and testing platform
- **Xcode** - Apple's integrated development environment
- **Android Studio** - IDE for Android development
- **OpenJDK** - Open-source Java Development Kit to help drawing tools
- **PlantUML** - UML diagram generation tool
- **Mermaid CLI** - Diagram generation from text definitions
- **GIMP** - GNU Image Manipulation Program for graphics editing
- **ADR Tools** - Command-line tools for working with **Architecture Decision Records**
- **Raycast** - Productivity launcher and command palette for macOS

#### Installation Modes

**Interactive Installation:**
```bash
make setup-brew-software
```
- Prompts before each software installation
- Options: Yes / No / Yes to All / Skip All
- Shows software descriptions and installation commands

**Automatic Installation:**
```bash
make setup-brew-all
```
- Installs all configured software without prompts
- Useful for automated environment setup

#### Homebrew Auto-Installation

The CLI automatically detects if Homebrew is missing and offers to install it:
- Prompts user for permission before installation
- Handles the official Homebrew installation script
- Supports dry-run mode for testing

#### Configuration

Software packages are defined in `src/setup_environment/config/software.yaml`:
```yaml
software:
  - name: git
    description: "Distributed version control system"
    check_command: "git --version"
    install_command: "brew install git"
    required: true
```

Add custom software by extending this configuration file.

### SSH Configuration

The CLI provides intelligent SSH setup for Git repositories:

#### Automatic SSH Detection
- **Smart Detection**: Automatically detects SSH repository URLs (`git@github.com:...`)
- **Conditional Setup**: Only configures SSH when SSH repositories are present
- **Zero Assumptions**: Eliminates manual SSH configuration steps

#### SSH Setup Process
1. **Key Generation**: Creates Ed25519 SSH keys (GitHub recommended)
2. **Agent Configuration**: Adds keys to ssh-agent automatically
3. **Connection Testing**: Verifies GitHub SSH connectivity
4. **Manual Fallback**: Provides clear instructions if automated setup fails

#### SSH Features
- **Email Integration**: Uses Git user email for SSH key generation
- **Key Management**: Checks for existing keys before generating new ones
- **Security**: Ed25519 keys with no passphrase for automation
- **Instructions**: Step-by-step GitHub SSH key addition guidance

This CLI demonstrates production-ready Python development practices including clean architecture, comprehensive testing, user-focused design, and intelligent SSH automation.

## AWS Credentials Automation

The setup-environment CLI includes comprehensive AWS SSO credential management to eliminate the manual process of retrieving temporary credentials from the AWS SSO portal.

### Problem Solved

**Before**: Manual AWS SSO credential retrieval
1. Navigate to AWS SSO portal (multiple clicks)
2. Select account (WeBuild-AI, prod, dev, etc.)
3. Click "Access keys"  
4. Copy environment variables from "Option 1 (macOS/Linux)"
5. Paste and execute in terminal
6. Repeat every 12 hours when credentials expire

**After**: One command
```bash
make aws-credentials
# or
setup-environment aws-credentials --account production
```

### Quick Start

**1. Initialize Configuration:**
```bash
# Creates .env template with AWS SSO settings
make aws-creds-init
```

**2. Configure Your Environment:**
Edit the generated `.env` file:
```bash
# AWS SSO Configuration
AWS_SSO_START_URL=https://your-sso.awsapps.com/start/#
AWS_SSO_REGION=eu-west-2
AWS_DEFAULT_REGION=eu-west-2
```

**3. Get Credentials:**
```bash
# Interactive account selection
make aws-credentials

# Specific account
uv run setup-environment aws-credentials --account production

# Different shell formats
uv run setup-environment aws-credentials --export-format fish

# Save to file
uv run setup-environment aws-credentials --output-file ~/.aws/credentials
```

### Supported Features

#### Multiple AWS Accounts
Configure multiple accounts in `src/setup_environment/config/aws_accounts.yaml`:
```yaml
accounts:
  - name: production
    account_id: "123456789012"
    email: aws-admin@example.com
    role: Engineer
    default: true
    description: "Production environment"
    
  - name: development  
    account_id: "234567890123"
    email: aws-dev@example.com
    role: Engineer
    description: "Development environment"
```

#### Multiple Shell Formats
Export credentials for different shells:
- **Bash/Zsh**: `export AWS_ACCESS_KEY_ID="..."`
- **Fish**: `set -x AWS_ACCESS_KEY_ID "..."`
- **PowerShell**: `$env:AWS_ACCESS_KEY_ID="..."`

#### Authentication Methods
- **Primary**: AWS SDK (boto3) with SSO client
- **Fallback**: Browser automation (Selenium/Playwright)
- **Manual**: Clear instructions if automation fails

#### Usage Examples

```bash
# Interactive mode (prompts for account)
make aws-credentials

# Direct account selection
uv run setup-environment aws-credentials --account production

# Fish shell format
uv run setup-environment aws-credentials --export-format fish

# Save credentials to AWS config file
uv run setup-environment aws-credentials --output-file ~/.aws/credentials

# Use with existing environment
eval $(uv run setup-environment aws-credentials --account dev)
```

#### Security Features

- **Temporary Credentials**: All credentials expire (typically 12 hours)
- **No Persistent Storage**: Credentials only in memory unless explicitly saved
- **Secure Validation**: AWS access key format validation (ASIA*/AKIA*)
- **Masked Logging**: Sensitive data masked in logs and output
- **Environment Isolation**: Uses .env files, not system environment

#### Error Handling

Comprehensive error handling for common scenarios:
- **Expired SSO session**: Automatic re-authentication
- **Invalid account**: Clear error with available accounts
- **Network issues**: Graceful fallback to manual instructions  
- **Missing configuration**: Guided setup with clear instructions
- **Invalid credentials**: Format validation with helpful error messages

#### Architecture Integration

Built using Clean Architecture with:
- **Domain Entities**: `AWSAccount`, `AWSCredentials`
- **Value Objects**: `SSOConfig`, `AWSSession` 
- **Use Cases**: `SetupAWSCredentialsUseCase`
- **Services**: `AWSSSOService`, `AWSConfigService`
- **187+ Tests**: Comprehensive unit and integration test coverage

#### Command Reference

| Command | Description |
|---------|-------------|
| `make aws-creds-init` | Create .env template with AWS SSO configuration |
| `make aws-credentials` | Interactive credential retrieval |
| `make aws-creds` | Short alias for aws-credentials |
| `make aws-creds-help` | Show detailed usage instructions |
| `setup-environment aws-credentials --account ACCOUNT` | Direct account selection |
| `setup-environment aws-credentials --export-format FORMAT` | Shell format (bash/zsh/fish/powershell) |
| `setup-environment aws-credentials --output-file FILE` | Save to credentials file |

This automation eliminates manual credential management, reduces errors, and provides a consistent developer experience across different environments and team members.

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
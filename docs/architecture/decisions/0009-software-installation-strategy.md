# 9. Software Installation Strategy

Date: 2025-08-10

## Status

Accepted

## Context

The setup-environment CLI needed to install various development tools:

1. **Standard tools**: Git, AWS CLI, Terraform (via Homebrew)
2. **Complex environments**: Python+uv, Node.js+NVM (requiring special setup)
3. **GUI applications**: iTerm2, VS Code, Slack (via Homebrew Cask)
4. **Custom installations**: Oh My Zsh (via shell script)
5. **NPM globals**: Claude Code, Mermaid CLI (via npm)

We needed a flexible, maintainable approach that could:
- Handle different installation methods
- Support macOS primarily (with future Linux support)
- Provide interactive and batch installation modes
- Check for existing installations
- Handle special configuration requirements

## Decision

We adopted a strategy pattern with specialised services for complex installations:

```yaml
# software.yaml configuration
software:
  - name: GitHub CLI
    description: "GitHub's official command line tool"
    check_command: "gh --version"
    install_command: "brew install gh"
    required: true
    
  - name: Oh My Zsh
    description: "Zsh configuration framework"
    check_command: "test -d $HOME/.oh-my-zsh"
    install_command: 'sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"'
    custom_install: true
    required: false
```

### Architecture:
1. **Base SoftwareService**: Handles standard Homebrew installations
2. **Specialised Services**: PythonService, NVMService, GitInstallService for complex setups
3. **YAML Configuration**: Defines software with check/install commands
4. **InstallSoftwareUseCase**: Orchestrates the installation process

## Consequences

### Positive

- **Extensibility**: Easy to add new software via YAML
- **Flexibility**: Supports various installation methods
- **Maintainability**: Configuration separate from code
- **User control**: Interactive prompts or batch mode
- **Idempotency**: Checks before installing
- **Special handling**: Complex tools get proper setup

### Negative

- **Homebrew dependency**: Requires Homebrew on macOS
- **Platform specific**: Currently macOS focused
- **Complex abstractions**: Multiple service classes
- **YAML maintenance**: Configuration needs updates

## Alternatives Considered

### 1. Shell Script
```bash
#!/bin/bash
brew install git gh aws-cli terraform
brew install --cask iterm2 slack visual-studio-code
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
```
- **Pros**: Simple, direct, familiar
- **Cons**: No error handling, not testable, platform specific
- **Rejected because**: Lacks flexibility and error handling

### 2. Ansible Playbook
```yaml
- name: Install development tools
  hosts: localhost
  tasks:
    - name: Install Homebrew packages
      homebrew:
        name: "{{ item }}"
        state: present
      loop:
        - git
        - gh
        - aws-cli
```
- **Pros**: Declarative, idempotent, powerful
- **Cons**: Heavy dependency, learning curve, overkill
- **Rejected because**: Too complex for our needs

### 3. Package Manager Abstraction
```python
class PackageManager(ABC):
    @abstractmethod
    def install(self, package: str): ...

class HomebrewManager(PackageManager):
    def install(self, package: str):
        subprocess.run(["brew", "install", package])

class AptManager(PackageManager):
    def install(self, package: str):
        subprocess.run(["apt", "install", "-y", package])
```
- **Pros**: Cross-platform support, clean abstraction
- **Cons**: Complex implementation, many edge cases
- **Rejected because**: Premature abstraction for current needs

## Implementation Details

### Software Entity:
```python
@dataclass(frozen=True)
class Software:
    """Represents a software package to install."""
    name: str
    description: str
    check_command: str
    install_command: str
    required: bool = False
    custom_install: bool = False
```

### Specialised Service Example (PythonService):
```python
class PythonService:
    """Specialised service for Python and uv setup."""
    
    def setup_python_environment(self) -> bool:
        """Set up Python with uv package manager."""
        # Check Python version
        if not self._check_python_version():
            if not self._install_python():
                return False
        
        # Install uv
        if not self._check_uv_installed():
            if not self._install_uv():
                return False
        
        # Configure shell
        self._configure_shell_for_uv()
        return True
```

### Installation Flow:
```python
def execute(self, software_list: list[Software], install_all: bool = False):
    for software in software_list:
        # Check if installed
        if self._is_installed(software):
            click.echo(f"✓ {software.name} already installed")
            continue
        
        # Prompt user (unless batch mode)
        if not install_all:
            response = self._prompt_installation(software)
            if response == InstallResponse.SKIP:
                continue
            elif response == InstallResponse.ALL:
                install_all = True
        
        # Install
        if self._install_software(software):
            click.echo(f"✅ Successfully installed {software.name}")
        else:
            click.echo(f"❌ Failed to install {software.name}")
```

### Homebrew Auto-Installation:
```python
def _ensure_homebrew_installed(self) -> bool:
    """Ensure Homebrew is installed."""
    if self._is_homebrew_installed():
        return True
    
    if self.dry_run:
        click.echo("Would install Homebrew")
        return True
    
    if click.confirm("Homebrew not found. Install it?"):
        return self._install_homebrew()
    return False
```

## Configuration Examples

### Standard Homebrew Package:
```yaml
- name: Terraform
  description: "Infrastructure as Code tool"
  check_command: "terraform --version"
  install_command: "brew install terraform"
  required: true
```

### Homebrew Cask Application:
```yaml
- name: Docker Desktop
  description: "Docker containerization platform"
  check_command: "test -d /Applications/Docker.app"
  install_command: "brew install --cask docker"
  required: false
```

### NPM Global Package:
```yaml
- name: Claude Code
  description: "Anthropic's official CLI for Claude"
  check_command: "claude --version"
  install_command: "npm install -g @anthropic-ai/claude-code"
  required: false
```

### Custom Installation:
```yaml
- name: Oh My Zsh
  description: "Zsh configuration framework"
  check_command: "test -d $HOME/.oh-my-zsh"
  install_command: 'sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"'
  custom_install: true
  required: false
```

## Testing Strategy

```python
@patch("subprocess.run")
def test_install_software(mock_run):
    # Mock successful installation
    mock_run.return_value = Mock(returncode=0)
    
    service = BrewSoftwareService()
    software = Software(
        name="git",
        check_command="git --version",
        install_command="brew install git",
    )
    
    result = service.install(software)
    assert result == True
    mock_run.assert_called_with(
        ["brew", "install", "git"],
        capture_output=True,
        text=True,
    )
```

## Best Practices

1. **Check before installing**: Always verify if already installed
2. **Provide descriptions**: Help users understand what's being installed
3. **Support dry-run**: Show what would be installed
4. **Handle failures gracefully**: Continue with other software
5. **Log verbosely**: Help troubleshoot installation issues
6. **Respect user choice**: Don't install without permission

## Platform Considerations

### macOS:
- Primary platform with full support
- Homebrew as package manager
- Cask for GUI applications

### Linux (Future):
- Detect distribution
- Use apt/yum/dnf as appropriate
- Different check commands

### Windows (Future):
- Use Chocolatey or winget
- PowerShell for commands
- Different application paths

## Lessons Learnt

1. **YAML configuration works well**: Easy to extend and maintain
2. **Specialised services needed**: Complex tools need custom logic
3. **User control important**: Interactive vs batch modes
4. **Check commands crucial**: Reliable detection prevents reinstalls
5. **Error handling complex**: Many failure modes to consider

## Future Enhancements

- Version pinning support
- Dependency resolution
- Rollback capability
- Progress bars for long installations
- Parallel installation where possible
- Post-install configuration hooks
- Cross-platform package mappings

## References

- [Homebrew Documentation](https://brew.sh/)
- [Homebrew Cask](https://github.com/Homebrew/homebrew-cask)
- [Package Management Best Practices](https://12factor.net/dependencies)
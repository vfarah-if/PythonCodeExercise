# 12. Error Handling Approach

Date: 2025-08-10

## Status

Accepted

## Context

The setup-environment CLI interacts with many external systems that can fail:

1. **File system operations**: Directories might not exist or be read-only
2. **Network operations**: Repository cloning can fail or timeout
3. **External tools**: Git, Homebrew, NPM might not be installed
4. **Configuration errors**: YAML files might be invalid or missing
5. **User input errors**: Invalid paths, malformed URLs
6. **Permission issues**: SSH keys, directory access, sudo requirements

We needed an error handling strategy that would:
- Provide clear, actionable error messages
- Gracefully degrade when possible
- Not leave the system in an inconsistent state
- Give users enough information to resolve problems

## Decision

We adopted a layered error handling approach with graceful degradation:

```python
# Domain layer: Validate at boundaries
@dataclass(frozen=True)
class Repository:
    def from_url(cls, url: str) -> "Repository":
        if not url:
            raise ValueError("Repository URL cannot be empty")
        # Validation logic...

# Application layer: Handle business logic errors
def execute(self, repositories: list[Repository]) -> SetupResult:
    successful = []
    failed = []
    
    for repo in repositories:
        try:
            result = self._git_service.clone_repository(repo, target_path)
            if result.status == CloneStatus.SUCCESS:
                successful.append(result)
            else:
                failed.append(result)
        except Exception as e:
            # Convert to domain error
            error_result = CloneResult(
                repository=repo,
                status=CloneStatus.FAILED,
                message=str(e),
            )
            failed.append(error_result)
    
    return SetupResult(successful=successful, failed=failed)

# Presentation layer: User-friendly messages
def handle_setup_error(error: Exception) -> None:
    if isinstance(error, FileNotFoundError):
        click.echo("❌ Configuration file not found. Run with --help for options.")
    elif isinstance(error, ValueError):
        click.echo(f"❌ Invalid configuration: {error}")
    else:
        click.echo(f"❌ Unexpected error: {error}")
        logging.exception("Unexpected error in setup")
```

### Key Principles:
1. **Fail fast**: Validate inputs early
2. **Graceful degradation**: Continue with partial success
3. **Clear messages**: Explain what went wrong and how to fix it
4. **Preserve context**: Include relevant information in errors
5. **Don't silent fail**: Always inform user of problems

## Consequences

### Positive

- **Better user experience**: Clear, actionable error messages
- **Partial success handling**: Some repos can fail without stopping others
- **Debugging information**: Logs help troubleshoot issues
- **Graceful degradation**: System remains usable with partial failures
- **Consistent patterns**: Similar error handling throughout

### Negative

- **Complex error handling**: Multiple layers of error processing
- **Verbose code**: Error handling adds code volume
- **Testing complexity**: Need to test error paths
- **Message maintenance**: Error messages need updates

## Error Categories

### 1. Configuration Errors
```python
class ConfigurationError(Exception):
    """Configuration file problems."""
    pass

def load_repositories(self, config_path: str) -> list[Repository]:
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        raise ConfigurationError(
            f"Configuration file not found: {config_path}. "
            f"Create it or use --repositories-config to specify location."
        )
    except yaml.YAMLError as e:
        raise ConfigurationError(
            f"Invalid YAML in {config_path}: {e}. "
            f"Check syntax and structure."
        )
```

### 2. Validation Errors
```python
class ValidationError(Exception):
    """Input validation problems."""
    pass

def __post_init__(self):
    if not self.path.exists():
        raise ValidationError(
            f"Directory does not exist: {self.path}. "
            f"Create it with: mkdir -p {self.path}"
        )
    
    if not os.access(self.path, os.W_OK):
        raise ValidationError(
            f"Directory is not writable: {self.path}. "
            f"Check permissions with: ls -la {self.path.parent}"
        )
```

### 3. External Tool Errors
```python
class ToolError(Exception):
    """External tool execution problems."""
    pass

def clone_repository(self, repository: Repository, target_path: Path) -> CloneResult:
    try:
        result = subprocess.run(
            ["git", "clone", repository.url, str(target_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        
        if result.returncode != 0:
            # Parse git error for common issues
            if "Permission denied" in result.stderr:
                message = (
                    f"SSH permission denied for {repository}. "
                    f"Check SSH key setup: ssh -T git@github.com"
                )
            elif "Repository not found" in result.stderr:
                message = (
                    f"Repository not found: {repository}. "
                    f"Check URL and access permissions."
                )
            else:
                message = f"Git clone failed: {result.stderr.strip()}"
            
            return CloneResult(
                repository=repository,
                status=CloneStatus.FAILED,
                message=message,
            )
            
    except FileNotFoundError:
        raise ToolError(
            "Git is not installed. Install with: brew install git"
        )
```

### 4. Network Errors
```python
def _handle_network_error(self, error: Exception, repository: Repository) -> CloneResult:
    """Handle network-related clone failures."""
    if "timeout" in str(error).lower():
        message = (
            f"Network timeout cloning {repository}. "
            f"Check internet connection and try again."
        )
    elif "connection refused" in str(error).lower():
        message = (
            f"Connection refused for {repository}. "
            f"Check firewall and network settings."
        )
    else:
        message = f"Network error cloning {repository}: {error}"
    
    return CloneResult(
        repository=repository,
        status=CloneStatus.FAILED,
        message=message,
    )
```

## Graceful Degradation Patterns

### Continue on Partial Failure:
```python
def execute_all_installations(self, software_list: list[Software]) -> InstallResult:
    """Install all software, continuing on failures."""
    successful = []
    failed = []
    
    for software in software_list:
        try:
            if self._install_software(software):
                successful.append(software)
            else:
                failed.append(software)
        except Exception as e:
            logging.warning(f"Failed to install {software.name}: {e}")
            failed.append(software)
            # Continue with next software
    
    return InstallResult(successful=successful, failed=failed)
```

### Fallback Strategies:
```python
def load_repositories(self) -> list[Repository]:
    """Load repositories with fallback strategies."""
    try:
        # Try YAML configuration first
        return self._load_from_yaml()
    except ConfigurationError:
        try:
            # Fall back to environment variables
            return self._load_from_environment()
        except Exception:
            # Final fallback: empty list with warning
            click.echo("⚠️ No repository configuration found")
            return []
```

## User Communication

### Progress Indication:
```python
def setup_repositories(self, repositories: list[Repository]) -> SetupResult:
    """Setup with progress indication."""
    with click.progressbar(
        repositories,
        label="Cloning repositories",
        show_eta=False,
    ) as repos:
        for repo in repos:
            try:
                result = self._clone_repository(repo)
                if result.status == CloneStatus.FAILED:
                    click.echo(f"⚠️ Failed: {repo} - {result.message}")
            except Exception as e:
                click.echo(f"❌ Error: {repo} - {e}")
```

### Summary Reporting:
```python
def print_setup_summary(result: SetupResult):
    """Print comprehensive results summary."""
    click.echo("\n" + "="*50)
    click.echo("Setup Summary")
    click.echo("="*50)
    
    if result.success_count > 0:
        click.echo(f"✅ Successfully completed: {result.success_count}")
        for item in result.successful:
            click.echo(f"   • {item}")
    
    if result.failure_count > 0:
        click.echo(f"❌ Failed: {result.failure_count}")
        for item in result.failed:
            click.echo(f"   • {item.name}: {item.message}")
        
        click.echo("\n💡 Tips to resolve failures:")
        click.echo("   • Check internet connection")
        click.echo("   • Verify SSH keys: ssh -T git@github.com")
        click.echo("   • Run with --dry-run to test configuration")
```

## Logging Strategy

### Structured Logging:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('setup-environment.log'),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)

def clone_repository(self, repository: Repository) -> CloneResult:
    logger.info(f"Starting clone of {repository}")
    try:
        # Clone operation
        logger.info(f"Successfully cloned {repository}")
        return success_result
    except Exception as e:
        logger.error(f"Failed to clone {repository}: {e}", exc_info=True)
        return failure_result
```

## Testing Error Handling

```python
def test_repository_clone_failure():
    """Test handling of clone failures."""
    mock_service = Mock()
    mock_service.clone_repository.side_effect = subprocess.SubprocessError("Git failed")
    
    use_case = SetupRepositoriesUseCase(mock_service)
    result = use_case.execute([repo], dev_folder)
    
    assert result.failure_count == 1
    assert "Git failed" in result.failed[0].message

def test_invalid_configuration():
    """Test handling of configuration errors."""
    with pytest.raises(ConfigurationError, match="file not found"):
        service = RepositoryConfigService()
        service.load_repositories("/nonexistent/config.yaml")
```

## Best Practices

1. **Validate early**: Check inputs at system boundaries
2. **Use specific exceptions**: Create domain-specific error types
3. **Preserve error context**: Include relevant information
4. **Provide solutions**: Suggest how to fix problems
5. **Log appropriately**: Info for success, warning for recoverable errors, error for failures
6. **Test error paths**: Ensure error handling works correctly
7. **Don't mask errors**: Always inform user about problems

## Lessons Learnt

1. **Users appreciate clear messages**: Time invested in good error messages pays off
2. **Graceful degradation is valuable**: Partial success better than total failure
3. **Logging helps debugging**: Especially for CI/CD environments
4. **Error handling is complex**: Requires significant testing
5. **Context matters**: Include enough information to resolve issues

## Future Improvements

- Add error recovery suggestions
- Implement retry mechanisms for transient failures
- Create error reporting system
- Add more specific error types
- Improve error message localisation
- Add error analytics and monitoring

## References

- [Python Exception Handling](https://docs.python.org/3/tutorial/errors.html)
- [Click Error Handling](https://click.palletsprojects.com/en/8.1.x/exceptions/)
- [Error Handling Best Practices](https://www.python.org/dev/peps/pep-3134/)
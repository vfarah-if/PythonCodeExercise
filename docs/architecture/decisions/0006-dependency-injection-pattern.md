# 6. Dependency Injection Pattern

Date: 2025-08-10

## Status

Accepted

## Context

The setup-environment CLI needed to manage dependencies between components whilst maintaining:

1. **Testability**: Easy to mock external dependencies
2. **Flexibility**: Swap implementations without changing business logic
3. **Explicit dependencies**: Clear about what each component needs
4. **No hidden coupling**: Avoid global state and singletons
5. **Configuration simplicity**: Easy to wire components together

We needed to choose between various dependency injection approaches suitable for Python.

## Decision

We adopted constructor-based dependency injection with explicit interface definitions:

```python
# Interface definition (Protocol)
class GitService(Protocol):
    def clone_repository(self, repository: Repository, target_path: Path) -> CloneResult:
        ...

# Use case with injected dependency
class SetupRepositoriesUseCase:
    def __init__(self, git_service: GitService):
        self._git_service = git_service
    
    def execute(self, repositories: list[Repository], dev_folder: DevFolderPath) -> SetupResult:
        # Use the injected service
        result = self._git_service.clone_repository(repo, target_path)

# Wiring in CLI
git_service = GitPythonService()
use_case = SetupRepositoriesUseCase(git_service)
```

### Key Principles:

1. **Constructor injection**: Dependencies passed via `__init__`
2. **Interface segregation**: Small, focused interfaces
3. **No service locator**: No global registry or container
4. **Explicit wiring**: Dependencies wired in presentation layer
5. **Protocol-based interfaces**: Using Python's Protocol for interfaces

## Consequences

### Positive

- **Testability**: Easy to inject mocks and stubs
- **Explicit dependencies**: Constructor shows what a class needs
- **No magic**: Clear, traceable dependency flow
- **IDE support**: Type hints enable autocomplete and checking
- **Flexibility**: Easy to swap implementations
- **Simplicity**: No DI framework to learn or debug

### Negative

- **Manual wiring**: Must manually instantiate and connect components
- **Constructor bloat**: Many dependencies make long constructors
- **Boilerplate**: Repetitive dependency passing
- **No lifecycle management**: No automatic singleton/scope handling

## Alternatives Considered

### 1. Service Locator Pattern
```python
class ServiceLocator:
    _services = {}
    
    @classmethod
    def register(cls, interface, implementation):
        cls._services[interface] = implementation
    
    @classmethod
    def get(cls, interface):
        return cls._services[interface]

# Usage
ServiceLocator.register(GitService, GitPythonService())
git_service = ServiceLocator.get(GitService)
```
- **Pros**: Central configuration, less constructor parameters
- **Cons**: Hidden dependencies, global state, harder to test
- **Rejected because**: Creates hidden coupling and testing complexity

### 2. Dependency Injection Framework (e.g., injector)
```python
from injector import inject, Injector, Module

class AppModule(Module):
    def configure(self, binder):
        binder.bind(GitService, to=GitPythonService)

class SetupRepositoriesUseCase:
    @inject
    def __init__(self, git_service: GitService):
        self._git_service = git_service

injector = Injector([AppModule()])
use_case = injector.get(SetupRepositoriesUseCase)
```
- **Pros**: Automatic wiring, lifecycle management, less boilerplate
- **Cons**: Additional dependency, magic behaviour, learning curve
- **Rejected because**: Overkill for our needs, adds complexity

### 3. Factory Pattern
```python
class UseCaseFactory:
    @staticmethod
    def create_setup_repositories_use_case() -> SetupRepositoriesUseCase:
        git_service = GitPythonService()
        return SetupRepositoriesUseCase(git_service)
```
- **Pros**: Encapsulates creation logic, consistent creation
- **Cons**: Extra abstraction layer, can hide dependencies
- **Rejected because**: Doesn't solve the core dependency problem

### 4. Property Injection
```python
class SetupRepositoriesUseCase:
    git_service: GitService = None
    
    def execute(self):
        if not self.git_service:
            raise ValueError("git_service not set")
        # Use service

# Usage
use_case = SetupRepositoriesUseCase()
use_case.git_service = GitPythonService()
```
- **Pros**: Optional dependencies, less constructor parameters
- **Cons**: Mutable state, runtime errors, unclear requirements
- **Rejected because**: Makes dependencies optional and unclear

## Implementation Patterns

### Interface Definition Using Protocol:
```python
from typing import Protocol

class GitService(Protocol):
    """Interface for Git operations."""
    
    def clone_repository(self, repository: Repository, target_path: Path) -> CloneResult:
        """Clone a repository to target path."""
        ...
    
    def check_git_installed(self) -> bool:
        """Check if git is installed."""
        ...
```

### Testing with Mocks:
```python
def test_setup_repositories():
    # Create mock
    mock_git_service = Mock(spec=GitService)
    mock_git_service.clone_repository.return_value = CloneResult(
        status=CloneStatus.SUCCESS
    )
    
    # Inject mock
    use_case = SetupRepositoriesUseCase(mock_git_service)
    
    # Test behaviour
    result = use_case.execute(repositories, dev_folder)
    
    # Verify interactions
    mock_git_service.clone_repository.assert_called_once()
```

### Wiring in CLI:
```python
@click.command()
def setup_environment(dev_folder: str, dry_run: bool):
    # Create concrete implementations
    git_service = GitPythonService()
    software_service = BrewSoftwareService()
    npmrc_service = NPMRCFileService()
    
    # Wire use cases
    setup_repos = SetupRepositoriesUseCase(git_service)
    install_software = InstallSoftwareUseCase(software_service)
    configure_npmrc = ConfigureNPMRCUseCase(npmrc_service)
    
    # Execute use cases
    # ...
```

## Best Practices

1. **Keep interfaces small**: Single responsibility for each interface
2. **Use Protocols**: Define interfaces using typing.Protocol
3. **Inject abstractions**: Depend on interfaces, not concrete classes
4. **Wire at the edge**: Do dependency injection in presentation layer
5. **Avoid property injection**: Use constructor injection for clarity
6. **Document dependencies**: Type hints show what's needed

## Lessons Learnt

1. **Simplicity wins**: Manual DI is sufficient for most projects
2. **Type hints are crucial**: They document and validate dependencies
3. **Protocols work well**: Better than ABC for interfaces
4. **Testing is straightforward**: Mock injection is simple
5. **Framework not needed**: Python's simplicity makes DI frameworks unnecessary

## Future Enhancements

- Consider DI framework if wiring becomes complex
- Add factory methods for common configurations
- Create builder pattern for complex object graphs
- Document standard wiring patterns

## References

- [Dependency Injection Principles](https://martinfowler.com/articles/injection.html)
- [Python Protocols (PEP 544)](https://www.python.org/dev/peps/pep-0544/)
- [Clean Architecture in Python](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
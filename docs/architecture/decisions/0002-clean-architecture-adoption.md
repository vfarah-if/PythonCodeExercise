# 2. Clean Architecture Adoption

Date: 2025-08-10

## Status

Accepted

## Context

The setup-environment CLI needed a robust architectural pattern that would:
- Separate business logic from infrastructure concerns
- Enable comprehensive testing without external dependencies
- Support future extensions and modifications
- Provide clear boundaries between different responsibilities
- Allow for easy replacement of external tools and services

The codebase started as a simple script but quickly grew in complexity as features were added (repository cloning, software installation, SSH configuration, npmrc setup).

## Decision

We adopted Clean Architecture (also known as Hexagonal Architecture or Ports & Adapters) with the following layer structure:

```
src/setup_environment/
├── domain/               # Core business logic (no dependencies)
│   ├── entities/        # Business objects with identity
│   └── value_objects/   # Immutable objects with validation
├── application/         # Use cases and orchestration
│   ├── interfaces/      # Port definitions (abstractions)
│   └── use_cases/      # Application-specific business rules
├── infrastructure/      # External dependencies
│   ├── git/            # Git operations implementation
│   ├── npm/            # File system operations
│   └── software/       # Software installation services
└── presentation/       # User interface
    └── cli.py          # Click-based CLI
```

### Key Principles Applied:

1. **Dependency Rule**: Dependencies point inward only (Infrastructure → Application → Domain)
2. **Dependency Inversion**: High-level modules don't depend on low-level modules; both depend on abstractions
3. **Interface Segregation**: Clients depend only on interfaces they use
4. **Single Responsibility**: Each class has one reason to change

## Consequences

### Positive

- **Testability**: Each layer can be tested in isolation with mocked dependencies
- **Flexibility**: Infrastructure components (Git, Homebrew, etc.) can be swapped without affecting business logic
- **Maintainability**: Clear separation of concerns makes code easier to understand and modify
- **Framework Independence**: Business logic isn't coupled to Click, subprocess, or any external library
- **Documentation**: Architecture serves as living documentation of system design
- **Parallel Development**: Teams can work on different layers simultaneously

### Negative

- **Initial Complexity**: More files and abstractions than a simple script
- **Learning Curve**: Developers need to understand the architecture pattern
- **Indirection**: Following code flow requires navigating through multiple layers
- **Overhead**: Small features require changes across multiple layers

## Alternatives Considered

### 1. Monolithic Script
- **Pros**: Simple, direct, minimal files
- **Cons**: Hard to test, difficult to extend, mixing of concerns
- **Rejected because**: Would become unmaintainable as features grew

### 2. MVC Pattern
- **Pros**: Well-known, simpler than Clean Architecture
- **Cons**: Less separation between business logic and framework
- **Rejected because**: Doesn't provide sufficient isolation for testing

### 3. Service Layer Pattern
- **Pros**: Simpler than full Clean Architecture
- **Cons**: Less clear boundaries, tendency to create "god services"
- **Rejected because**: Insufficient structure for the complexity we anticipated

## Implementation Details

### Domain Layer
- Contains `Repository`, `Software`, `NPMRCConfiguration` entities
- Value objects like `DevFolderPath` and `PersonalAccessToken` with validation
- No external dependencies, pure Python

### Application Layer
- Use cases: `SetupRepositoriesUseCase`, `InstallSoftwareUseCase`, `ConfigureNPMRCUseCase`
- Interfaces: `GitService`, `SoftwareService`, `NPMRCService`
- Orchestrates domain objects and calls to infrastructure

### Infrastructure Layer
- `GitPythonService`: Implements GitService using subprocess
- `BrewSoftwareService`: Implements SoftwareService using Homebrew
- `RepositoryConfigService`: YAML configuration loading
- Specialised services: `PythonService`, `NVMService`, `GitInstallService`

### Presentation Layer
- Click CLI that instantiates use cases with concrete implementations
- Handles user input/output and progress reporting
- Maps CLI arguments to domain objects

## Lessons Learnt

1. Start with use cases to identify domain boundaries
2. Value objects prevent invalid states and centralise validation
3. Interfaces should be defined by consumers, not implementers
4. Test coverage naturally increases with proper separation
5. The architecture guides developers toward good practices

## References

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture by Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [Domain-Driven Design by Eric Evans](https://www.domainlanguage.com/ddd/)
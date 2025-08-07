1# Clean Architecture in Python

A comprehensive guide to implementing Clean Architecture principles in Python, especially for developers coming from .NET backgrounds.

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Directory Structure](#directory-structure)
4. [Layer Implementation](#layer-implementation)
5. [Key Patterns](#key-patterns)
6. [Avoiding Circular Dependencies](#avoiding-circular-dependencies)
7. [.NET Developer Guide](#net-developer-guide)
8. [Best Practices](#best-practices)
9. [Testing Strategy](#testing-strategy)
10. [Running the Example](#running-the-example)

## Introduction

Clean Architecture is a software design philosophy that emphasises separation of concerns and dependency inversion. This project demonstrates how to implement Clean Architecture in Python with patterns familiar to .NET developers.

### Key Benefits

- **Independence**: Business logic is independent of frameworks, databases, and external systems
- **Testability**: Easy to test with clear separation of concerns
- **Maintainability**: Changes to external systems don't affect business logic
- **Flexibility**: Can swap implementations without changing business logic

## Architecture Overview

Clean Architecture organises code into concentric layers, with dependencies flowing inward towards the business logic.

```
┌─────────────────────────────────────────┐
│           Presentation Layer            │ ← Controllers, CLI, Web APIs
├─────────────────────────────────────────┤
│           Application Layer             │ ← Use Cases, DTOs
├─────────────────────────────────────────┤
│           Infrastructure Layer          │ ← Repositories, External Services
├─────────────────────────────────────────┤
│              Domain Layer               │ ← Entities, Value Objects, Interfaces
└─────────────────────────────────────────┘
```

### Dependency Direction

- **Presentation** depends on **Application**
- **Application** depends on **Domain**
- **Infrastructure** depends on **Domain** (through interfaces)
- **Domain** depends on nothing

## Directory Structure

```
src/clean_architecture_example/
├── domain/                    # Core Business Logic
│   ├── entities/             # Business entities (User, Order, etc.)
│   ├── value_objects/        # Immutable value types (Email, Money, etc.)
│   └── interfaces/           # Abstract contracts (Repositories, Services)
├── application/              # Application Business Rules
│   ├── use_cases/           # Application services (CreateUser, GetOrder)
│   ├── dto/                 # Data Transfer Objects
│   └── interfaces/          # Application-specific contracts
├── infrastructure/           # External Concerns
│   ├── repositories/        # Data access implementations
│   ├── external_services/   # API clients, file systems
│   └── persistence/         # Database configurations
├── presentation/            # User Interface
│   ├── api/                # REST API controllers
│   ├── cli/                # Command line interfaces
│   └── web/                # Web framework routes
└── shared/                 # Cross-cutting concerns
    ├── di/                 # Dependency injection
    ├── exceptions/         # Custom exceptions
    └── utils/              # Helper functions
```

## Layer Implementation

### Domain Layer

The domain layer contains your core business logic and has no dependencies on external systems.

#### Entities
```python
@dataclass
class User:
    email: Email
    first_name: str
    last_name: str
    
    def update_name(self, first_name: str, last_name: str) -> None:
        # Business logic with validation
        self._validate_names()
        self.updated_at = datetime.utcnow()
```

#### Value Objects
```python
@dataclass(frozen=True)
class Email:
    value: str
    
    def __post_init__(self) -> None:
        if not self._is_valid_format():
            raise ValueError("Invalid email format")
```

#### Interfaces
```python
class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> User:
        pass
```

### Application Layer

The application layer orchestrates business operations without containing business logic.

#### Use Cases
```python
class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    async def execute(self, request: CreateUserRequest) -> UserResponse:
        # Coordinate domain operations
        email = Email(request.email)
        user = User(email, request.first_name, request.last_name)
        saved_user = await self._user_repository.save(user)
        return self._map_to_response(saved_user)
```

#### DTOs
```python
@dataclass(frozen=True)
class CreateUserRequest:
    email: str
    first_name: str
    last_name: str
```

### Infrastructure Layer

The infrastructure layer implements interfaces defined in the domain layer.

#### Repository Implementation
```python
class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._users: Dict[str, User] = {}
    
    async def save(self, user: User) -> User:
        self._users[user.id] = user
        return user
```

### Presentation Layer

The presentation layer handles user interaction and delegates to use cases.

#### CLI Implementation
```python
class UserCLI:
    def __init__(self, create_user_use_case: CreateUserUseCase):
        self._create_user = create_user_use_case
    
    async def handle_create_user(self):
        # Get user input, call use case, display result
        pass
```

## Key Patterns

### 1. Dependency Injection

Dependencies are injected rather than created internally.

```python
class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository):  # Injected
        self._user_repository = user_repository
```

### 2. Repository Pattern

Data access is abstracted behind interfaces.

```python
# Domain defines interface
class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> User: pass

# Infrastructure implements interface
class SqlUserRepository(UserRepository):
    async def save(self, user: User) -> User:
        # SQL implementation
```

### 3. Use Case Pattern

Each business operation is encapsulated in a use case.

```python
class CreateUserUseCase:
    async def execute(self, request: CreateUserRequest) -> UserResponse:
        # Single responsibility: create user
```

### 4. DTO Pattern

Data transfer between layers uses dedicated objects.

```python
@dataclass(frozen=True)
class UserResponse:  # For outbound data
    id: str
    email: str
    full_name: str
```

## Avoiding Circular Dependencies

### Problem
Python's import system can create circular dependencies when modules import each other.

```python
# ❌ Circular dependency
# module_a.py
from module_b import B

# module_b.py  
from module_a import A
```

### Solutions

#### 1. Proper Layer Dependencies
Follow the dependency rule - dependencies flow inward only.

```python
# ✅ Correct dependency direction
# application layer depends on domain
from ...domain.interfaces.user_repository import UserRepository

# infrastructure layer depends on domain  
from ...domain.interfaces.user_repository import UserRepository
```

#### 2. Interface Segregation
Define interfaces in the domain layer, implement in infrastructure.

```python
# Domain layer - defines interface
class UserRepository(ABC):
    pass

# Infrastructure layer - implements interface
class SqlUserRepository(UserRepository):
    pass
```

#### 3. Dependency Injection
Inject dependencies instead of importing them directly.

```python
class UseCase:
    def __init__(self, repository: UserRepository):  # Injected
        self._repository = repository
```

#### 4. Late Imports
Import at runtime when needed (sparingly).

```python
def get_service():
    from .infrastructure import Service  # Late import
    return Service()
```

## .NET Developer Guide

### Familiar Patterns

| .NET Concept | Python Equivalent | Example |
|--------------|-------------------|---------|
| Interface | Protocol/ABC | `class IRepository(Protocol)` |
| DTO | Dataclass | `@dataclass(frozen=True)` |
| DI Container | DIContainer | Custom implementation |
| Repository | Repository Pattern | Same concept |
| Entity | Entity Class | `@dataclass` with ID |
| Value Object | Frozen Dataclass | `@dataclass(frozen=True)` |

### Key Differences

#### 1. Type System
```python
# Python - gradual typing
from typing import Optional, List

def get_users() -> List[Optional[User]]:
    pass
```

#### 2. Interfaces
```python
# Python - Protocol (duck typing)
class UserRepository(Protocol):
    def save(self, user: User) -> User: ...

# Or ABC (explicit inheritance)
class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User: pass
```

#### 3. Dependency Injection
```python
# Python - constructor injection
class UseCase:
    def __init__(self, repo: UserRepository):
        self.repo = repo

# Registration
container.register_transient(UserRepository, SqlUserRepository)
```

#### 4. Async/Await
```python
# Python - async/await (similar to C#)
async def create_user(self, request: CreateUserRequest) -> UserResponse:
    user = await self.repository.save(user)
    return user
```

### Migration Tips

1. **Start with Domain Layer**: Define entities and value objects first
2. **Use Type Hints**: Leverage Python's type system for better IDE support
3. **Embrace Dataclasses**: Similar to C# records/POCOs
4. **Async by Default**: Use async/await for I/O operations
5. **Test Everything**: Python's dynamic nature requires comprehensive testing

## Best Practices

### 1. Domain Layer
- ✅ No external dependencies
- ✅ Rich domain models with behaviour
- ✅ Use value objects for primitive types
- ✅ Define clear interfaces
- ❌ Don't put infrastructure concerns here

### 2. Application Layer
- ✅ Orchestrate domain operations
- ✅ Handle cross-cutting concerns
- ✅ Use DTOs for data transfer
- ✅ Keep use cases focused (SRP)
- ❌ Don't put business logic here

### 3. Infrastructure Layer
- ✅ Implement domain interfaces
- ✅ Handle external system integration
- ✅ Manage data persistence
- ✅ Configure external dependencies
- ❌ Don't leak infrastructure details

### 4. Presentation Layer
- ✅ Handle user interaction
- ✅ Call appropriate use cases
- ✅ Format responses for display
- ✅ Validate input format
- ❌ Don't put business logic here

### 5. Testing
- ✅ Test each layer in isolation
- ✅ Use mocks for dependencies
- ✅ Test business rules thoroughly  
- ✅ Include integration tests
- ❌ Don't test implementation details

## Testing Strategy

### Test Pyramid

```
┌─────────────────┐
│ Integration     │ ← Few, test layer interactions
├─────────────────┤
│ Application     │ ← Use cases with mocked dependencies
├─────────────────┤
│ Domain          │ ← Many, test business logic
└─────────────────┘
```

### Domain Tests
Test business logic without external dependencies:

```python
def test_user_creation_with_valid_data():
    email = Email("test@example.com")
    user = User(email=email, first_name="Test", last_name="User")
    
    assert user.email == email
    assert user.full_name == "Test User"
```

### Application Tests
Test use cases with mocked dependencies:

```python
@pytest.mark.asyncio
async def test_create_user_success(mock_repository):
    use_case = CreateUserUseCase(mock_repository)
    request = CreateUserRequest("test@example.com", "Test", "User")
    
    result = await use_case.execute(request)
    
    assert result.email == "test@example.com"
    mock_repository.save.assert_called_once()
```

### Infrastructure Tests
Test implementations with real or fake external systems:

```python
@pytest.mark.asyncio
async def test_in_memory_repository_saves_user():
    repository = InMemoryUserRepository()
    user = User(Email("test@example.com"), "Test", "User")
    
    saved_user = await repository.save(user)
    
    assert saved_user.id == user.id
```

## Running the Example

### Prerequisites
- Python 3.12+
- uv package manager

### Installation
```bash
# Clone and setup
git clone <repository>
cd PythonCodeExercise
make install
```

### Running Tests
```bash
# Run all tests
make test

# Run specific test file
uv run pytest tests/test_clean_architecture_domain.py

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing
```

### Running the Application
```bash
# Run the CLI application
uv run python -m src.clean_architecture_example.main

# Or run directly
uv run python src/clean_architecture_example/main.py
```

### Example Usage
1. Choose storage type (in-memory or file-based)
2. Optionally create demo data
3. Use CLI commands:
   - `create` - Create new user
   - `list` - List all users  
   - `get` - Get user by ID or email
   - `update` - Update user information
   - `help` - Show available commands
   - `exit` - Exit application

## Conclusion

This implementation demonstrates how to build maintainable, testable Python applications using Clean Architecture principles. The patterns shown here scale from small projects to large enterprise applications.

Key takeaways:
- **Separation of Concerns**: Each layer has a single responsibility
- **Dependency Inversion**: Depend on abstractions, not concretions
- **Testability**: Easy to test with clear boundaries
- **Flexibility**: Can swap implementations without changing business logic
- **.NET Familiarity**: Uses patterns familiar to C# developers

The architecture provides a solid foundation for building robust Python applications that are easy to understand, test, and maintain over time.
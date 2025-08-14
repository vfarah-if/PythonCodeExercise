# 7. Value Objects for Validation

Date: 2025-08-10

## Status

Accepted

## Context

The setup-environment CLI handles several types of data that require validation:

1. **File paths**: Must exist, be directories, have write permissions
2. **Personal access tokens**: Must match GitHub's format
3. **Repository URLs**: Must be valid Git URLs
4. **Installation responses**: Limited set of valid responses

We needed to ensure data validity whilst avoiding:
- Primitive obsession (passing strings everywhere)
- Validation logic scattered across the codebase
- Invalid states being possible
- Defensive programming throughout

## Decision

We implemented value objects for critical data types, encapsulating validation and behaviour:

```python
@dataclass(frozen=True)
class DevFolderPath:
    """Value object representing a development folder path."""
    
    path: Path
    
    def __post_init__(self):
        """Validate the path after initialisation."""
        if not self.path.is_absolute():
            raise ValueError(f"Path must be absolute: {self.path}")
        
        if not self.path.exists():
            raise ValueError(f"Path does not exist: {self.path}")
        
        if not self.path.is_dir():
            raise ValueError(f"Path must be a directory: {self.path}")
        
        if not os.access(self.path, os.W_OK):
            raise ValueError(f"Path must be writable: {self.path}")

@dataclass(frozen=True)
class PersonalAccessToken:
    """Value object for GitHub personal access token."""
    
    value: str
    
    def __post_init__(self):
        """Validate token format."""
        if not self.value:
            raise ValueError("Token cannot be empty")
        
        # GitHub tokens start with ghp_ or github_pat_
        if not (self.value.startswith("ghp_") or self.value.startswith("github_pat_")):
            raise ValueError("Invalid GitHub token format")
    
    def masked(self) -> str:
        """Return masked version for display."""
        if len(self.value) <= 8:
            return "****"
        return f"{self.value[:4]}...{self.value[-4:]}"
```

## Consequences

### Positive

- **Impossible invalid states**: Validation happens at construction
- **Self-documenting**: Types express constraints and meaning
- **Centralised validation**: One place for validation logic
- **Type safety**: Can't accidentally pass wrong string
- **Immutability**: Frozen dataclasses prevent modification
- **Encapsulated behaviour**: Methods like `masked()` live with data
- **Fail fast**: Invalid data caught immediately

### Negative

- **More classes**: Each concept needs its own class
- **Conversion overhead**: Need to wrap/unwrap primitives
- **Learning curve**: Team needs to understand value objects
- **Serialisation complexity**: Need custom serialisation for storage

## Alternatives Considered

### 1. Validation Functions
```python
def validate_dev_folder(path: str) -> str:
    if not Path(path).exists():
        raise ValueError(f"Path does not exist: {path}")
    return path

# Usage
validated_path = validate_dev_folder(user_input)
```
- **Pros**: Simple functions, no new types
- **Cons**: Can forget to validate, validation scattered
- **Rejected because**: No type safety, easy to bypass

### 2. Pydantic Models
```python
from pydantic import BaseModel, validator

class DevFolderPath(BaseModel):
    path: Path
    
    @validator('path')
    def validate_path(cls, v):
        if not v.exists():
            raise ValueError(f"Path does not exist: {v}")
        return v
```
- **Pros**: Rich validation, serialisation support
- **Cons**: Heavy dependency, more complex than needed
- **Rejected because**: Overkill for our simple needs

### 3. Type Aliases with Runtime Checks
```python
from typing import NewType

DevFolderPath = NewType('DevFolderPath', Path)

def create_dev_folder_path(path: str) -> DevFolderPath:
    p = Path(path)
    if not p.exists():
        raise ValueError(f"Path does not exist: {p}")
    return DevFolderPath(p)
```
- **Pros**: Lightweight, type hints
- **Cons**: No behaviour encapsulation, can bypass factory
- **Rejected because**: Doesn't prevent invalid construction

### 4. Defensive Programming
```python
def clone_repository(self, repo_url: str, target_path: str):
    # Validate every time
    if not Path(target_path).exists():
        raise ValueError("Invalid path")
    # ... rest of method
```
- **Pros**: No abstraction needed
- **Cons**: Repetitive, error-prone, validation everywhere
- **Rejected because**: Violates DRY principle

## Implementation Patterns

### Enum for Constrained Choices:
```python
class InstallResponse(Enum):
    """Valid responses for installation prompts."""
    YES = "y"
    NO = "n"
    ALL = "a"
    SKIP = "s"
    
    @classmethod
    def from_input(cls, value: str) -> Optional["InstallResponse"]:
        """Parse user input to response."""
        normalised = value.lower().strip()
        for response in cls:
            if normalised == response.value:
                return response
        return None
```

### Factory Methods for Complex Creation:
```python
@classmethod
def from_string(cls, path_str: str) -> "DevFolderPath":
    """Create from string, expanding user directory."""
    expanded = Path(path_str).expanduser().resolve()
    return cls(expanded)
```

### Testing Value Objects:
```python
def test_dev_folder_path_validation():
    # Valid path
    temp_dir = Path(tempfile.mkdtemp())
    valid_path = DevFolderPath(temp_dir)
    assert valid_path.path == temp_dir
    
    # Invalid path
    with pytest.raises(ValueError, match="does not exist"):
        DevFolderPath(Path("/nonexistent"))
    
    # Not a directory
    temp_file = temp_dir / "file.txt"
    temp_file.touch()
    with pytest.raises(ValueError, match="must be a directory"):
        DevFolderPath(temp_file)
```

## Value Objects in the System

1. **DevFolderPath**: Validated directory for development
2. **PersonalAccessToken**: GitHub PAT with format validation
3. **Repository**: Parsed repository with org/name
4. **InstallResponse**: Enumerated installation choices
5. **CloneStatus**: Enumerated clone results

## Best Practices

1. **Make them immutable**: Use frozen=True on dataclasses
2. **Validate in __post_init__**: Ensure validity on construction
3. **Provide factory methods**: For complex creation logic
4. **Include behaviour**: Methods that operate on the data
5. **Use type hints**: Make them first-class types
6. **Test thoroughly**: Each value object needs tests

## Lessons Learnt

1. **Start with primitives**: Refactor to value objects when patterns emerge
2. **Not everything needs wrapping**: Balance abstraction with simplicity
3. **Validation at boundaries**: Create value objects at system entry points
4. **Rich behaviour emerges**: Value objects attract related methods
5. **Type safety is valuable**: Catches errors at development time

## Future Enhancements

- Add more sophisticated token validation
- Support for relative paths with resolution
- Serialisation support for configuration
- Builder pattern for complex value objects
- Custom exceptions for each value object

## References

- [Domain-Driven Design Value Objects](https://martinfowler.com/bliki/ValueObject.html)
- [Python Data Classes](https://docs.python.org/3/library/dataclasses.html)
- [Type-Driven Development](https://blog.ploeh.dk/2015/08/10/type-driven-development/)
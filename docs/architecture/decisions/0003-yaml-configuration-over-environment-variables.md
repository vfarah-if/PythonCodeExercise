# 3. YAML Configuration Over Environment Variables

Date: 2025-08-10

## Status

Accepted

## Context

Initially, the setup-environment CLI used environment variables (`GIT_REPO_*`) to define repositories for cloning. This approach had several limitations:

1. **No metadata support**: Couldn't store descriptions, tags, or other repository information
2. **Poor organisation**: Difficult to group related repositories
3. **Limited structure**: Flat key-value pairs with no hierarchy
4. **Environment pollution**: Many variables cluttering the shell environment
5. **No validation**: Environment variables are strings with no schema
6. **Version control challenges**: `.env` files often excluded from Git

The team needed a more structured, maintainable approach for defining repositories and software configurations.

## Decision

We migrated from environment variables to YAML configuration files:

```yaml
# repositories.yaml
repositories:
  - name: Frontend Application
    url: git@github.com:your-org/frontend.git
    description: "Main frontend application"
    
  - name: Backend Services
    url: git@github.com:your-org/backend.git
    description: "Backend API services"
```

```yaml
# software.yaml
software:
  - name: GitHub CLI
    description: "GitHub's official command line tool"
    check_command: "gh --version"
    install_command: "brew install gh"
    required: true
```

### Implementation Approach:

1. Created `RepositoryConfigService` to load and parse YAML files
2. Maintained backward compatibility with environment variables as fallback
3. Standardised configuration location: `src/setup_environment/config/`
4. Support for custom configuration paths via CLI arguments

## Consequences

### Positive

- **Rich metadata**: Can store descriptions, tags, priorities, and other attributes
- **Better organisation**: Logical grouping and categorisation of repositories
- **Schema validation**: YAML structure can be validated against expected format
- **Version control friendly**: Configuration files easily tracked in Git
- **Self-documenting**: YAML is human-readable with inline comments
- **Extensibility**: Easy to add new fields without breaking existing code
- **Portability**: Configuration files can be shared across teams
- **Multiple environments**: Different configs for dev/staging/production

### Negative

- **Additional dependency**: Requires PyYAML library
- **File management**: Need to handle file paths and missing files
- **Migration effort**: Existing users need to migrate from environment variables
- **Learning curve**: Users unfamiliar with YAML syntax

## Alternatives Considered

### 1. JSON Configuration
```json
{
  "repositories": [
    {"name": "Frontend", "url": "git@github.com:org/frontend.git"}
  ]
}
```
- **Pros**: Native Python support, widely understood
- **Cons**: No comments, verbose syntax, less human-friendly
- **Rejected because**: YAML is more readable and supports comments

### 2. TOML Configuration
```toml
[[repositories]]
name = "Frontend"
url = "git@github.com:org/frontend.git"
```
- **Pros**: Growing popularity, good for configuration
- **Cons**: Less familiar to most developers, limited tooling
- **Rejected because**: YAML has better ecosystem support

### 3. Python Configuration
```python
REPOSITORIES = [
    {"name": "Frontend", "url": "git@github.com:org/frontend.git"}
]
```
- **Pros**: Full Python power, no parsing needed
- **Cons**: Security risks, not language-agnostic, requires execution
- **Rejected because**: Configuration should be data, not code

### 4. INI Files
```ini
[frontend]
url = git@github.com:org/frontend.git
description = Frontend application
```
- **Pros**: Simple, familiar from many tools
- **Cons**: Limited structure, no arrays, string values only
- **Rejected because**: Insufficient for complex configurations

## Implementation Details

### Configuration Loading Strategy:
1. Check for custom config path from CLI argument
2. Fall back to default location in package
3. If no YAML found, check environment variables (backward compatibility)
4. Raise clear error if no configuration found

### Validation Approach:
```python
def _parse_repository_item(self, item: dict[str, Any]) -> Repository:
    required_fields = ["url"]
    for field in required_fields:
        if field not in item:
            raise ValueError(f"Missing required field '{field}'")
    return Repository.from_url(item["url"])
```

### Migration Path:
1. Generate YAML from existing environment variables
2. Validate generated configuration
3. Gradually deprecate environment variable support
4. Provide clear migration documentation

## Lessons Learnt

1. **Backward compatibility is crucial**: Keep old methods working during transition
2. **Clear error messages**: Help users understand configuration problems
3. **Provide examples**: Include sample configuration files in repository
4. **Document migration**: Clear instructions for moving from old to new format
5. **Validate early**: Catch configuration errors before attempting operations

## Future Enhancements

- Schema validation using JSON Schema or similar
- Configuration inheritance (base + overrides)
- Environment-specific configurations
- Encrypted values for sensitive data
- Configuration hot-reloading
- Web UI for configuration management

## References

- [YAML Specification](https://yaml.org/spec/1.2/spec.html)
- [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [Configuration File Best Practices](https://12factor.net/config)
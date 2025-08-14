# 4. Repository Organisation Strategy

Date: 2025-08-10

## Status

Accepted

## Context

When cloning multiple repositories, we needed a consistent, predictable organisation structure that would:

1. **Prevent naming conflicts**: Multiple repositories might have the same name
2. **Support multiple organisations**: Work with repos from different GitHub organisations
3. **Enable easy discovery**: Developers should quickly find repositories
4. **Mirror remote structure**: Local organisation should reflect GitHub structure
5. **Avoid deep nesting**: Keep paths reasonable for terminal navigation
6. **Support workspace tools**: Compatible with VS Code workspaces, IDEs

## Decision

We adopted a two-level directory structure: `~/dev/{organisation}/{repository}`

```
~/dev/
├── facebook/
│   └── react/              # from github.com/facebook/react
├── microsoft/
│   └── vscode/             # from github.com/microsoft/vscode
└── your-org/
    ├── frontend/           # from github.com/your-org/frontend
    ├── backend/            # from github.com/your-org/backend
    └── shared-lib/         # from github.com/your-org/shared-lib
```

### URL Parsing Implementation:

```python
def calculate_target_path(self, base_path: Path) -> Path:
    """Calculate the target path for cloning this repository."""
    return base_path / self.organisation / self.name
```

### Supported URL Formats:
- SSH: `git@github.com:organisation/repository.git`
- HTTPS: `https://github.com/organisation/repository.git`
- Both with and without `.git` suffix

## Consequences

### Positive

- **No conflicts**: Organisation namespace prevents repository name collisions
- **Intuitive navigation**: Mirrors GitHub's URL structure
- **Workspace friendly**: Easy to open entire organisation in IDE
- **Consistent paths**: Predictable location for any repository
- **Shallow structure**: Only two levels deep from base directory
- **Cross-reference friendly**: Easy to reference repos in scripts/documentation
- **Multi-account support**: Different organisations can represent different accounts

### Negative

- **Organisation changes**: If repo moves organisations, local path becomes outdated
- **Personal repos**: User's personal repos create many single-repo directories
- **Case sensitivity**: Different filesystems handle organisation case differently
- **Long organisation names**: Can create unwieldy paths

## Alternatives Considered

### 1. Flat Structure
```
~/dev/
├── react/
├── vscode/
├── frontend/
├── backend/
```
- **Pros**: Simplest structure, shortest paths
- **Cons**: Name conflicts, no organisation context
- **Rejected because**: Doesn't scale with multiple organisations

### 2. Domain-Based Structure
```
~/dev/
├── github.com/
│   ├── facebook/
│   │   └── react/
│   └── microsoft/
│       └── vscode/
├── gitlab.com/
│   └── company/
│       └── project/
```
- **Pros**: Supports multiple Git providers
- **Cons**: Deeper nesting, longer paths
- **Rejected because**: Currently only supporting GitHub

### 3. Category-Based Structure
```
~/dev/
├── frontend/
│   ├── react/
│   └── vue/
├── backend/
│   ├── api-gateway/
│   └── user-service/
```
- **Pros**: Logical grouping by purpose
- **Cons**: Requires categorisation, subjective organisation
- **Rejected because**: Doesn't match remote structure

### 4. Nested by Technology
```
~/dev/
├── javascript/
│   ├── react/
│   └── express/
├── python/
│   └── django/
```
- **Pros**: Groups by language/technology
- **Cons**: Polyglot repos don't fit, requires classification
- **Rejected because**: Too opinionated about technology

## Implementation Details

### Repository Entity Design:
```python
@dataclass(frozen=True)
class Repository:
    url: str
    organisation: str
    name: str
    
    @classmethod
    def from_url(cls, url: str) -> "Repository":
        # Parse both SSH and HTTPS URLs
        # Extract organisation and name
        return cls(url=url, organisation=organisation, name=name)
```

### Skip Detection:
```python
if target_path.exists():
    return CloneResult(
        repository=repository,
        path=target_path,
        status=CloneStatus.SKIPPED,
        message="Repository already exists"
    )
```

### Edge Cases Handled:

1. **Repository with .git suffix**: Stripped automatically
2. **URLs with trailing slashes**: Normalised
3. **Case preservation**: Organisation/repo names kept as-is
4. **Special characters**: Validated against GitHub's rules
5. **Existing directories**: Skipped rather than overwritten

## Migration Considerations

For existing repositories in different structures:

1. **Gradual migration**: Move repos as they're updated
2. **Symlinks**: Create links from old to new locations
3. **Script provision**: Automated migration script for bulk moves
4. **Documentation**: Clear communication about new structure

## Best Practices

1. **Use lowercase**: Recommend lowercase for organisation names
2. **Avoid special characters**: Stick to alphanumeric and hyphens
3. **Document structure**: Include structure in project README
4. **Backup before migration**: Always backup before reorganising
5. **Update tooling**: Ensure build scripts use new paths

## Future Enhancements

- Support for GitLab, Bitbucket, and other providers
- Configurable organisation strategies
- Automatic migration tools
- Integration with workspace managers
- Support for mono-repos with special handling

## References

- [GitHub Repository Naming](https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories)
- [Filesystem Hierarchy Standard](https://www.pathname.com/fhs/)
- [Workspace Organisation Best Practices](https://code.visualstudio.com/docs/editor/workspaces)
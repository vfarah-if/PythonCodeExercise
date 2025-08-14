# 5. Subprocess Over GitPython

Date: 2025-08-10

## Status

Accepted

## Context

For Git operations (clone, config, SSH setup), we needed to choose between:

1. **GitPython**: A pure Python Git library
2. **pygit2**: Python bindings for libgit2
3. **Direct subprocess calls**: Executing git commands directly

The choice would impact:
- Dependency management
- Error handling complexity
- SSH authentication support
- Performance characteristics
- Debugging and troubleshooting

## Decision

We chose to use direct subprocess calls to the git CLI rather than GitPython or other libraries:

```python
def clone_repository(self, repository: Repository, target_path: Path) -> CloneResult:
    try:
        result = subprocess.run(
            ["git", "clone", repository.url, str(target_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        # Handle result...
    except subprocess.SubprocessError as e:
        # Handle error...
```

## Consequences

### Positive

- **No additional dependencies**: Uses system's git installation
- **SSH compatibility**: Works with existing SSH configurations and keys
- **Familiar output**: Error messages match what developers see in terminal
- **Debugging simplicity**: Can reproduce issues with exact same commands
- **Feature completeness**: Access to all git features and flags
- **Version flexibility**: Works with any git version installed
- **Standard behaviour**: Matches user's git configuration exactly

### Negative

- **Git requirement**: System must have git installed
- **Platform differences**: Commands might behave differently across OS
- **String parsing**: Need to parse text output rather than structured data
- **Process overhead**: Spawning processes has more overhead than library calls
- **Error handling**: Need to handle process errors and git errors separately

## Alternatives Considered

### 1. GitPython
```python
import git
repo = git.Repo.clone_from(url, target_path)
```
- **Pros**: Pythonic API, structured data, no subprocess overhead
- **Cons**: Large dependency, SSH issues, version mismatches
- **Rejected because**: SSH authentication complications and dependency weight

### 2. pygit2
```python
import pygit2
pygit2.clone_repository(url, target_path)
```
- **Pros**: Fast C bindings, good performance
- **Cons**: Complex installation, C dependencies, SSH configuration issues
- **Rejected because**: Installation complexity and SSH handling

### 3. Dulwich
```python
from dulwich import porcelain
porcelain.clone(url, target_path)
```
- **Pros**: Pure Python, no C dependencies
- **Cons**: Limited features, less mature, smaller community
- **Rejected because**: Insufficient feature coverage

## Implementation Details

### Command Execution Pattern:
```python
def _run_git_command(self, args: list[str], cwd: Path = None) -> tuple[bool, str, str]:
    """Run a git command and return success, stdout, stderr."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd,
        )
        return result.returncode == 0, result.stdout, result.stderr
    except FileNotFoundError:
        return False, "", "Git is not installed"
```

### SSH Detection and Handling:
```python
def _has_ssh_repositories(self, repositories: list[Repository]) -> bool:
    """Check if any repository uses SSH URLs."""
    return any(repo.url.startswith("git@") for repo in repositories)
```

### Error Message Preservation:
- Capture both stdout and stderr
- Return git's error messages unchanged
- Add context about which operation failed

## SSH Authentication Benefits

Using subprocess with system git means:

1. **Existing SSH keys work**: No need to configure library-specific auth
2. **SSH agent integration**: Automatically uses ssh-agent
3. **Config file support**: Respects ~/.ssh/config settings
4. **Key formats**: Supports all key types git supports
5. **Passphrase handling**: Uses system's askpass if configured

## Testing Strategy

```python
@patch("subprocess.run")
def test_clone_repository(mock_run):
    mock_run.return_value = Mock(
        returncode=0,
        stdout="Cloning into 'repo'...",
        stderr=""
    )
    # Test implementation
```

## Performance Considerations

- **Process spawn overhead**: ~10-50ms per command
- **Acceptable for our use case**: One-time setup operations
- **Not suitable for**: High-frequency operations or performance-critical paths

## Platform Compatibility

Tested on:
- macOS: Full compatibility
- Linux: Full compatibility
- Windows: Requires Git Bash or WSL
- Docker: Works with git installed in container

## Lessons Learnt

1. **Simplicity wins**: Direct subprocess calls were easier to debug
2. **SSH is complex**: Libraries struggle with SSH authentication
3. **User expectations**: Developers expect git to work like their terminal
4. **Error messages matter**: Preserving git's messages helps users
5. **Testing is straightforward**: Easy to mock subprocess calls

## Future Considerations

- Could add GitPython as optional accelerator for read operations
- Might revisit if SSH handling in libraries improves
- Consider abstraction layer for cross-platform compatibility
- Monitor for security issues with subprocess usage

## References

- [GitPython Documentation](https://gitpython.readthedocs.io/)
- [Subprocess Security Considerations](https://docs.python.org/3/library/subprocess.html#security-considerations)
- [Git SSH Authentication](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
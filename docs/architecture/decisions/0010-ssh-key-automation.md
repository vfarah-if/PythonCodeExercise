# 10. SSH Key Automation

Date: 2025-08-10

## Status

Accepted

## Context

Many repositories use SSH URLs (git@github.com:org/repo.git) for authentication. Setting up SSH keys manually is:

1. **Error-prone**: Users often misconfigure SSH
2. **Time-consuming**: Multiple steps across different tools
3. **Inconsistent**: Different users follow different practices
4. **Undocumented**: Knowledge often not shared
5. **Security-sensitive**: Keys need proper generation and management

We needed to automate SSH setup whilst maintaining security and giving users control.

## Decision

We implemented automatic SSH key generation and configuration with Ed25519 keys:

```python
def setup_ssh_if_needed(self, repositories: list[Repository]) -> bool:
    """Set up SSH keys if needed for repository access."""
    
    # Only setup if SSH URLs present
    if not self._has_ssh_repositories(repositories):
        return True
    
    # Check existing SSH setup
    if self._check_ssh_configured():
        return True
    
    # Prompt user
    if not click.confirm("SSH key setup needed. Configure now?"):
        return False
    
    # Generate Ed25519 key
    email = self._get_git_email()
    if not self._generate_ssh_key(email):
        return False
    
    # Add to SSH agent
    if not self._add_key_to_agent():
        return False
    
    # Test GitHub connection
    if not self._test_github_ssh():
        self._show_manual_instructions()
        return False
    
    return True
```

### Key Decisions:
1. **Ed25519 algorithm**: Modern, secure, GitHub-recommended
2. **No passphrase**: Automation-friendly (user can add later)
3. **Automatic agent addition**: Keys immediately available
4. **GitHub verification**: Test connection before proceeding
5. **Manual fallback**: Clear instructions if automation fails

## Consequences

### Positive

- **Simplified onboarding**: New developers get SSH working immediately
- **Consistent setup**: Everyone uses same key type and configuration
- **Secure defaults**: Ed25519 is current best practice
- **Time-saving**: Minutes instead of manual setup time
- **Educational**: Shows users proper SSH setup
- **Conditional**: Only runs when SSH repos detected

### Negative

- **No passphrase default**: Less secure (but user can add)
- **Overwrites existing**: Could replace existing id_ed25519
- **GitHub-specific**: Test only verifies GitHub access
- **Platform assumptions**: Assumes standard SSH locations

## Alternatives Considered

### 1. Manual Process Documentation
```markdown
# SSH Setup Guide
1. Run: ssh-keygen -t ed25519 -C "your_email@example.com"
2. Press Enter for default location
3. Enter passphrase (optional)
4. Run: ssh-add ~/.ssh/id_ed25519
5. Copy public key: cat ~/.ssh/id_ed25519.pub
6. Add to GitHub settings
```
- **Pros**: User has full control, educational
- **Cons**: Error-prone, time-consuming, often skipped
- **Rejected because**: Defeats automation purpose

### 2. Require Existing SSH
```python
def check_ssh_required(self):
    if not self._check_ssh_configured():
        raise click.ClickException(
            "SSH not configured. Please set up SSH keys first."
        )
```
- **Pros**: Simple, no key management responsibility
- **Cons**: Poor user experience, blocks progress
- **Rejected because**: Creates friction for new users

### 3. Use HTTPS with Token
```python
def convert_to_https(self, ssh_url: str) -> str:
    """Convert SSH URL to HTTPS with token auth."""
    # git@github.com:org/repo.git -> https://token@github.com/org/repo.git
    return ssh_url.replace("git@github.com:", "https://github.com/")
```
- **Pros**: No SSH needed, works everywhere
- **Cons**: Token management, less secure, URL rewriting
- **Rejected because**: SSH is standard for development

### 4. Deploy Keys
```python
def create_deploy_key(self, repository: Repository):
    """Create repository-specific deploy key."""
    key_path = f"~/.ssh/{repository.name}_deploy"
    subprocess.run(["ssh-keygen", "-f", key_path])
```
- **Pros**: Per-repo isolation, limited access
- **Cons**: Many keys to manage, complex configuration
- **Rejected because**: Overly complex for development setup

## Implementation Details

### Ed25519 Key Generation:
```python
def _generate_ssh_key(self, email: str) -> bool:
    """Generate Ed25519 SSH key."""
    key_path = Path.home() / ".ssh" / "id_ed25519"
    
    if key_path.exists():
        if not click.confirm(f"SSH key exists at {key_path}. Overwrite?"):
            return False
    
    cmd = [
        "ssh-keygen",
        "-t", "ed25519",
        "-C", email,
        "-f", str(key_path),
        "-N", "",  # No passphrase
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0
```

### SSH Agent Configuration:
```python
def _add_key_to_agent(self) -> bool:
    """Add SSH key to agent."""
    # Start agent if needed
    subprocess.run(["ssh-agent", "-s"], capture_output=True)
    
    # Add key
    key_path = Path.home() / ".ssh" / "id_ed25519"
    result = subprocess.run(
        ["ssh-add", str(key_path)],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0
```

### GitHub Connection Test:
```python
def _test_github_ssh(self) -> bool:
    """Test SSH connection to GitHub."""
    result = subprocess.run(
        ["ssh", "-T", "git@github.com"],
        capture_output=True,
        text=True,
    )
    # GitHub returns 1 but with success message
    return "successfully authenticated" in result.stderr.lower()
```

### Manual Instructions Display:
```python
def _show_manual_instructions(self):
    """Show manual SSH setup instructions."""
    key_path = Path.home() / ".ssh" / "id_ed25519.pub"
    
    click.echo("\n" + "="*50)
    click.echo("Manual SSH Setup Required")
    click.echo("="*50)
    click.echo("\n1. Copy your public key:")
    click.echo(f"   cat {key_path}")
    click.echo("\n2. Add to GitHub:")
    click.echo("   https://github.com/settings/keys")
    click.echo("\n3. Click 'New SSH key'")
    click.echo("\n4. Paste the key and save")
    click.echo("\n5. Test connection:")
    click.echo("   ssh -T git@github.com")
```

## Security Considerations

1. **Key Algorithm**: Ed25519 is currently recommended by GitHub
2. **Key Location**: Standard ~/.ssh/ directory with proper permissions
3. **No Passphrase**: Trade-off for automation (users can add later)
4. **Agent Usage**: Keys not written to disk in commands
5. **Overwrite Protection**: Prompts before replacing existing keys

## Platform Support

### macOS:
- Full support with native SSH tools
- Keychain integration available

### Linux:
- Full support with OpenSSH
- ssh-agent works as expected

### Windows:
- Requires OpenSSH or Git Bash
- May need additional configuration

## Testing Approach

```python
@patch("subprocess.run")
@patch("click.confirm")
def test_ssh_setup(mock_confirm, mock_run):
    mock_confirm.return_value = True
    mock_run.return_value = Mock(returncode=0)
    
    service = GitInstallService()
    result = service.setup_ssh_if_needed([ssh_repo])
    
    assert result == True
    # Verify ssh-keygen was called
    assert any("ssh-keygen" in str(call) for call in mock_run.call_args_list)
```

## Best Practices

1. **Check before generating**: Don't overwrite without permission
2. **Use modern algorithms**: Ed25519 over RSA
3. **Test connectivity**: Verify setup works
4. **Provide fallback**: Manual instructions if automation fails
5. **Document thoroughly**: Users should understand what happened
6. **Make it optional**: User can skip if preferred

## Lessons Learnt

1. **SSH is complex**: Many edge cases and platform differences
2. **Automation valued**: Users appreciate automatic setup
3. **Ed25519 preferred**: Modern and well-supported
4. **Testing important**: Mock subprocess calls thoroughly
5. **Clear instructions help**: Good fallback documentation essential

## Future Enhancements

- Support for multiple keys
- Passphrase addition wizard
- SSH config file management
- Support for other Git providers
- Key rotation reminders
- Integration with password managers

## References

- [GitHub SSH Documentation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [Ed25519 Keys](https://ed25519.cr.yp.to/)
- [OpenSSH Documentation](https://www.openssh.com/manual.html)
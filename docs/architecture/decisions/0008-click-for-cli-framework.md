# 8. Click for CLI Framework

Date: 2025-08-10

## Status

Accepted

## Context

The setup-environment tool needed a robust CLI framework to handle:

1. **Command-line argument parsing**: Paths, flags, options
2. **User interaction**: Prompts, confirmations, progress display
3. **Help generation**: Automatic help text from code
4. **Error handling**: User-friendly error messages
5. **Extensibility**: Easy to add new commands and options
6. **Testing**: CLI components should be testable

Python offers several CLI frameworks: argparse (built-in), Click, Typer, Fire, and Docopt.

## Decision

We chose Click as the CLI framework:

```python
import click

@click.command()
@click.option(
    "--dev-folder",
    required=True,
    help="Base folder for development repositories",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
@click.option(
    "--skip-npmrc",
    is_flag=True,
    help="Skip npmrc configuration",
)
def setup_environment(dev_folder: str, dry_run: bool, skip_npmrc: bool):
    """Set up development environment with repositories and tools."""
    # Implementation
```

## Consequences

### Positive

- **Declarative syntax**: Decorators make CLI definition clear
- **Built-in validation**: Path validation, type conversion
- **Automatic help**: Generates help from docstrings and decorators
- **User interaction**: Built-in prompts, confirmations, progress bars
- **Testing utilities**: CliRunner for testing commands
- **Composability**: Commands can be grouped and nested
- **Extensive ecosystem**: Many plugins and extensions available
- **Excellent documentation**: Well-documented with examples

### Negative

- **Additional dependency**: Not part of standard library
- **Decorator magic**: Some find decorator syntax confusing
- **Learning curve**: Need to learn Click's patterns
- **Overkill for simple scripts**: More complex than argparse for basics

## Alternatives Considered

### 1. argparse (Built-in)
```python
import argparse

parser = argparse.ArgumentParser(description='Setup environment')
parser.add_argument('--dev-folder', required=True, help='Dev folder')
parser.add_argument('--dry-run', action='store_true', help='Dry run')
args = parser.parse_args()
```
- **Pros**: No dependencies, part of standard library, familiar
- **Cons**: Verbose, no built-in prompts, manual validation
- **Rejected because**: Too verbose for complex CLI, lacks user interaction

### 2. Typer
```python
import typer

app = typer.Typer()

@app.command()
def setup_environment(
    dev_folder: Path = typer.Option(..., help="Dev folder"),
    dry_run: bool = typer.Option(False, help="Dry run")
):
    """Setup environment."""
    # Implementation
```
- **Pros**: Modern, type hints based, built on Click
- **Cons**: Newer with smaller community, additional abstraction layer
- **Rejected because**: Less mature, adds complexity over Click

### 3. Fire
```python
import fire

def setup_environment(dev_folder, dry_run=False):
    """Setup environment."""
    # Implementation

if __name__ == '__main__':
    fire.Fire(setup_environment)
```
- **Pros**: Minimal syntax, automatic CLI from functions
- **Cons**: Less control, no built-in validation, magic behaviour
- **Rejected because**: Too much magic, insufficient control

### 4. Docopt
```python
"""Setup Environment.

Usage:
  setup-environment --dev-folder=<path> [--dry-run]
  setup-environment (-h | --help)

Options:
  -h --help          Show this screen.
  --dev-folder=<path>  Dev folder path.
  --dry-run          Dry run mode.
"""
from docopt import docopt

arguments = docopt(__doc__)
```
- **Pros**: Document-driven, clear usage patterns
- **Cons**: String parsing, no type safety, limited features
- **Rejected because**: Lacks features we need (prompts, validation)

## Implementation Patterns

### Path Validation:
```python
@click.option(
    "--dev-folder",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        writable=True,
        resolve_path=True,
    ),
    help="Development folder path",
)
```

### User Prompts:
```python
def prompt_for_token() -> str:
    """Prompt user for GitHub token."""
    return click.prompt(
        "Please enter your GitHub Personal Access Token",
        hide_input=True,  # Hide for security
        confirmation_prompt=False,
    )
```

### Progress Display:
```python
with click.progressbar(repositories, label="Cloning repositories") as repos:
    for repo in repos:
        clone_result = git_service.clone_repository(repo, target_path)
```

### Styled Output:
```python
click.echo(click.style("✓ Success", fg="green", bold=True))
click.echo(click.style("✗ Failed", fg="red", bold=True))
click.echo(click.style("→ Skipped", fg="yellow"))
```

### Testing with CliRunner:
```python
from click.testing import CliRunner

def test_setup_environment():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            setup_environment,
            ["--dev-folder", ".", "--dry-run"],
        )
        assert result.exit_code == 0
        assert "Dry run mode" in result.output
```

## User Interaction Features

### Confirmations:
```python
if not dry_run and not click.confirm("Continue with installation?"):
    click.echo("Installation cancelled.")
    return
```

### Choice Prompts:
```python
response = click.prompt(
    "Install software?",
    type=click.Choice(["y", "n", "a", "s"]),
    default="y",
)
```

### Error Handling:
```python
try:
    # Operation
except ValueError as e:
    click.echo(click.style(f"Error: {e}", fg="red"), err=True)
    raise click.ClickException(str(e))
```

## Best Practices

1. **Use Click's types**: Path, Choice, IntRange for validation
2. **Provide defaults**: Make common cases easy
3. **Add help text**: Document every option and command
4. **Use echo for output**: Better than print for CLI
5. **Handle errors gracefully**: Use ClickException for user errors
6. **Test with CliRunner**: Don't test via subprocess
7. **Use contexts**: For sharing state between commands

## Integration Benefits

- **Works with setuptools**: Easy to create installable commands
- **Shell completion**: Can generate bash/zsh completions
- **Plugin system**: Extensible with plugins
- **Colour support**: Automatic terminal colour detection
- **Unicode handling**: Proper handling across platforms

## Lessons Learnt

1. **Click's verbosity is worth it**: Explicit is better than implicit
2. **Built-in features save time**: Prompts, progress bars, styling
3. **Testing is straightforward**: CliRunner makes testing easy
4. **Documentation is excellent**: Good examples and patterns
5. **Community is helpful**: Many examples and solutions available

## Future Enhancements

- Add command groups for different functions
- Implement shell completion
- Add configuration file support via Click
- Create custom parameter types for common patterns
- Add interactive mode for guided setup

## References

- [Click Documentation](https://click.palletsprojects.com/)
- [Click Best Practices](https://click.palletsprojects.com/en/8.1.x/quickstart/#basic-concepts)
- [Building CLIs with Click](https://realpython.com/python-click/)
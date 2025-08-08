"""Command-line interface for setup-environment."""

import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

from src.setup_environment.application.use_cases import (
    ConfigureNPMUseCase,
    SetupRepositoriesUseCase,
)
from src.setup_environment.application.use_cases.configure_npm import (
    ConfigurationStatus,
)
from src.setup_environment.application.use_cases.install_software import (
    InstallSoftwareUseCase,
)
from src.setup_environment.domain.entities import Repository
from src.setup_environment.domain.value_objects import DevFolderPath
from src.setup_environment.infrastructure import GitPythonService, NPMFileService
from src.setup_environment.infrastructure.software import BrewSoftwareService
from src.setup_environment.infrastructure.software.git_service import (
    GitService as GitInstallService,
)
from src.setup_environment.infrastructure.software.nvm_service import NVMService
from src.setup_environment.infrastructure.software.python_service import PythonService


def load_environment_config(env_file: Path | None = None) -> None:
    """Load configuration from .env file if it exists."""
    if env_file and env_file.exists():
        click.echo(f"📄 Loading configuration from {env_file}")
        load_dotenv(env_file)
    else:
        # Try default .env file
        default_env = Path(".env")
        if default_env.exists():
            click.echo(f"📄 Loading configuration from {default_env}")
            load_dotenv(default_env)


def get_repositories_from_environment() -> list[Repository]:
    """Get repository URLs from environment variables."""
    repositories = []

    # Look for GIT_REPO_* environment variables
    for key, value in os.environ.items():
        if key.startswith("GIT_REPO_") and value.strip():
            try:
                repo = Repository.from_url(value.strip())
                repositories.append(repo)
            except ValueError as e:
                click.echo(
                    f"Warning: Invalid repository URL in {key}: {value} - {e}",
                    err=True,
                )

    return repositories


def generate_env_template(env_file: Path, example: bool = False) -> None:
    """Generate a template .env file."""
    suffix = ".example" if example else ""
    template_path = env_file.parent / f"{env_file.name}{suffix}"

    template_content = """# Setup Environment Configuration
# Add your Git repository URLs below using the GIT_REPO_* pattern
# Supports both HTTPS and SSH URLs

# Example repositories (replace with your own)
GIT_REPO_1=https://github.com/facebook/react.git
GIT_REPO_2=https://github.com/microsoft/vscode.git
GIT_REPO_FRONTEND=https://github.com/your-org/frontend.git
GIT_REPO_BACKEND=https://github.com/your-org/backend.git

# For private repositories, use SSH URLs:
# GIT_REPO_PRIVATE=git@github.com:your-org/private-repo.git

# You can use any GIT_REPO_* pattern:
# GIT_REPO_TOOLS=https://github.com/your-org/dev-tools.git
# GIT_REPO_DOCS=https://github.com/your-org/documentation.git
"""

    template_path.write_text(template_content)
    click.echo(f"✅ Generated template: {template_path}")

    if not example:
        click.echo("💡 Edit the file to add your repository URLs, then run:")
        click.echo(f"   setup-environment --dev-folder ~/dev --env-file {env_file}")
    else:
        click.echo("💡 Copy .env.example to .env and customize with your repositories")


def print_setup_summary(result):
    """Print a summary of the repository setup results."""
    click.echo("\n" + "=" * 50)
    click.echo("Repository Setup Summary")
    click.echo("=" * 50)

    if result.success_count > 0:
        click.echo(f"✓ Successfully cloned: {result.success_count} repositories")
        for clone_result in result.successful:
            click.echo(f"  - {clone_result.repository} → {clone_result.path}")

    if result.skip_count > 0:
        click.echo(f"→ Skipped (already exist): {result.skip_count} repositories")
        for clone_result in result.skipped:
            click.echo(f"  - {clone_result.repository}")

    if result.failure_count > 0:
        click.echo(f"✗ Failed to clone: {result.failure_count} repositories", err=True)
        for clone_result in result.failed:
            click.echo(
                f"  - {clone_result.repository}: {clone_result.error_message}",
                err=True,
            )

    click.echo("\n" + "=" * 50)


def print_npm_summary(result):
    """Print a summary of the NPM configuration results."""
    click.echo("\n" + "=" * 50)
    click.echo("NPM Configuration Summary")
    click.echo("=" * 50)

    if result.status == ConfigurationStatus.ALREADY_EXISTS:
        click.echo("→ NPM configuration already exists with GitHub token")
    elif result.status == ConfigurationStatus.CREATED:
        click.echo("✓ Created new NPM configuration")
        click.echo(f"  Location: {result.message.split('at ')[-1]}")
    elif result.status == ConfigurationStatus.UPDATED:
        click.echo("✓ Updated existing NPM configuration")
        click.echo(f"  Location: {result.message.split('at ')[-1]}")

    if result.config:
        click.echo(f"  Token: {result.config.token}")
        click.echo(f"  Organisation: {result.config.organisation}")
        click.echo(f"  Registry: {result.config.registry_url}")

    click.echo("\n" + "=" * 50)


def print_software_summary(result):
    """Print a summary of the software installation results."""
    click.echo("\n" + "=" * 60)
    click.echo("Software Installation Summary")
    click.echo("=" * 60)

    if result.already_installed:
        click.echo(f"→ Already installed: {len(result.already_installed)} packages")
        for install_result in result.already_installed:
            click.echo(f"  - {install_result.software.name}")

    if result.installed:
        click.echo(f"✓ Newly installed: {len(result.installed)} packages")
        for install_result in result.installed:
            click.echo(f"  - {install_result.software.name}")

    if result.skipped:
        click.echo(f"→ Skipped: {len(result.skipped)} packages")
        for install_result in result.skipped:
            click.echo(f"  - {install_result.software.name}")

    if result.failed:
        click.echo(f"✗ Failed: {len(result.failed)} packages", err=True)
        for install_result in result.failed:
            click.echo(
                f"  - {install_result.software.name}: {install_result.message}",
                err=True,
            )

    click.echo("\n" + "=" * 60)


@click.command()
@click.option(
    "--dev-folder",
    required=False,  # Make optional for template generation
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Development folder where repositories will be cloned",
)
@click.option(
    "--skip-npm",
    is_flag=True,
    default=False,
    help="Skip NPM configuration setup",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be done without actually doing it (validation and logging only)",
)
@click.option(
    "--env-file",
    type=click.Path(exists=False, path_type=Path),
    help="Environment file to load (default: .env if exists)",
)
@click.option(
    "--generate-env",
    is_flag=True,
    default=False,
    help="Generate a template .env file and exit",
)
@click.option(
    "--generate-env-example",
    is_flag=True,
    default=False,
    help="Generate a .env.example template file and exit",
)
@click.option(
    "--skip-software",
    is_flag=True,
    default=False,
    help="Skip development software installation",
)
@click.option(
    "--software-config",
    type=click.Path(exists=True, path_type=Path),
    help="Custom software configuration file",
)
@click.option(
    "--install-all-software",
    is_flag=True,
    default=False,
    help="Install all software without prompting",
)
def setup_environment(
    dev_folder: Path | None,
    skip_npm: bool,
    dry_run: bool,
    env_file: Path | None,
    generate_env: bool,
    generate_env_example: bool,
    skip_software: bool,
    software_config: Path | None,
    install_all_software: bool,
):
    """Configure development environment: software, Git repositories, and NPM.

    Installs development software via Homebrew, clones Git repositories from
    environment variables or .env files, and configures NPM for GitHub packages.

    \b
    QUICK START:
      setup-environment --generate-env     # Create template
      setup-environment --dev-folder ~/dev # Run full setup

    \b
    TESTING:
      setup-environment --dev-folder ~/dev --dry-run

    \b
    SOFTWARE OPTIONS:
      setup-environment --dev-folder ~/dev --skip-software
      setup-environment --dev-folder ~/dev --install-all-software
    """
    # Handle template generation options first
    if generate_env or generate_env_example:
        env_target = env_file or Path(".env")
        generate_env_template(env_target, example=generate_env_example)
        return

    # Load environment configuration
    load_environment_config(env_file)

    if dry_run:
        click.echo("Setup Environment CLI (DRY RUN - No changes will be made)")
    else:
        click.echo("Setup Environment CLI")
    click.echo("=" * 50)

    try:
        # Validate development folder is provided for non-generation operations
        if not dev_folder:
            click.echo("Error: --dev-folder is required for setup operations", err=True)
            click.echo("Use --generate-env to create template files", err=True)
            sys.exit(1)

        # Validate development folder
        dev_folder_path = DevFolderPath(dev_folder)
        click.echo(f"Development folder: {dev_folder_path}")

        # Get repositories early to check for SSH URLs
        repositories = get_repositories_from_environment()

        # Check if any repositories use SSH
        ssh_needed = any(repo.url.startswith("git@") for repo in repositories)

        # Install development software first (before repositories)
        if not skip_software:
            click.echo("\nChecking development software...")
            if ssh_needed:
                click.echo(
                    "🔐 SSH repositories detected - Git will be configured with SSH keys"
                )

            software_service = BrewSoftwareService()
            python_service = PythonService()
            git_install_service = GitInstallService()
            nvm_service = NVMService()

            software_use_case = InstallSoftwareUseCase(
                software_service,
                python_service=python_service,
                git_service=git_install_service,
                nvm_service=nvm_service,
            )

            software_result = software_use_case.execute(
                config_path=str(software_config) if software_config else None,
                dry_run=dry_run,
                install_all=install_all_software,
                skip_all=False,
                setup_ssh=ssh_needed,
            )
            print_software_summary(software_result)

            # Check if any critical installations failed (only in non-dry-run mode)
            if not dry_run and software_result.has_failures:
                critical_failed = [
                    r for r in software_result.failed if r.software.required
                ]
                if critical_failed:
                    click.echo(
                        f"\n⚠️  {len(critical_failed)} required software packages failed to install.",
                        err=True,
                    )
                    for result in critical_failed:
                        click.echo(
                            f"   - {result.software.name}: {result.message}", err=True
                        )
                    click.echo(
                        "\nPlease resolve these issues before continuing.", err=True
                    )
                    sys.exit(1)
        else:
            click.echo("\n→ Skipped software installation (--skip-software flag)")

        if not repositories:
            click.echo(
                "\nNo repositories found in environment variables.",
                err=True,
            )
            click.echo(
                "Please set GIT_REPO_* environment variables with repository URLs.",
                err=True,
            )
            click.echo(
                "Example: export GIT_REPO_1='https://github.com/org/repo.git'",
                err=True,
            )
            sys.exit(1)

        click.echo(f"\nFound {len(repositories)} repositories to setup:")
        for repo in repositories:
            target_path = repo.calculate_target_path(dev_folder_path.value)
            if dry_run:
                click.echo(f"  - {repo} → {target_path}")
            else:
                click.echo(f"  - {repo}")

        # Setup repositories
        git_service = GitPythonService()

        if dry_run:
            # In dry-run mode, just validate and show what would happen
            click.echo("\n--- DRY RUN: Repository Setup ---")

            if not git_service.is_git_installed():
                click.echo("✗ Git is not installed or not available in PATH", err=True)
            else:
                click.echo("✓ Git is available")

            for repo in repositories:
                target_path = repo.calculate_target_path(dev_folder_path.value)
                if git_service.repository_exists(target_path):
                    click.echo(f"→ Would skip {repo} (already exists)")
                else:
                    click.echo(f"✓ Would clone {repo} to {target_path}")
        else:
            # Normal execution
            click.echo("\nSetting up repositories...")
            setup_use_case = SetupRepositoriesUseCase(git_service)

            setup_result = setup_use_case.execute(repositories, dev_folder_path)
            print_setup_summary(setup_result)

        # Configure NPM if not skipped
        if not skip_npm:
            if dry_run:
                click.echo("\n--- DRY RUN: NPM Configuration ---")
                npm_service = NPMFileService()
                config_path = npm_service.get_config_path()

                if npm_service.config_exists():
                    if npm_service.has_github_token():
                        click.echo(
                            "→ Would skip NPM configuration (already exists with GitHub token)"
                        )
                    else:
                        click.echo(
                            f"→ Would update existing NPM configuration at {config_path}"
                        )
                else:
                    click.echo(f"→ Would create new NPM configuration at {config_path}")

                click.echo("→ Would prompt for GitHub Personal Access Token")
            else:
                click.echo("\nConfiguring NPM settings...")
                npm_service = NPMFileService()
                npm_use_case = ConfigureNPMUseCase(npm_service)

                npm_result = npm_use_case.execute()
                print_npm_summary(npm_result)
        else:
            click.echo("\n→ Skipped NPM configuration (--skip-npm flag)")

        if dry_run:
            click.echo("\n✓ Dry run completed successfully! No changes were made.")
        else:
            # Exit with error code if any repositories failed
            if "setup_result" in locals() and setup_result.has_failures:
                click.echo(
                    f"\nSetup completed with {setup_result.failure_count} failures.",
                    err=True,
                )
                sys.exit(1)
            else:
                click.echo("\n✓ Setup completed successfully!")

    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


def main():
    """Entry point for the CLI application."""
    setup_environment()


if __name__ == "__main__":
    main()

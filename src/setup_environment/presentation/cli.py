"""Command-line interface for setup-environment."""

import os
import sys
from pathlib import Path

import click

from src.setup_environment.application.use_cases import (
    ConfigureNPMRCUseCase,
    SetupRepositoriesUseCase,
)
from src.setup_environment.application.use_cases.configure_npmrc import (
    ConfigurationStatus,
)
from src.setup_environment.application.use_cases.install_software import (
    InstallSoftwareUseCase,
)
from src.setup_environment.domain.entities import Repository
from src.setup_environment.domain.value_objects import DevFolderPath
from src.setup_environment.infrastructure import GitPythonService, NPMRCFileService
from src.setup_environment.infrastructure.repository_config_service import (
    YamlRepositoryConfigService,
)
from src.setup_environment.infrastructure.software import BrewSoftwareService
from src.setup_environment.infrastructure.software.git_service import (
    GitService as GitInstallService,
)
from src.setup_environment.infrastructure.software.nvm_service import (
    NodeEnvironmentService,
)
from src.setup_environment.infrastructure.software.python_service import (
    BrewPythonService,
)


def load_repositories_from_config(
    config_path: Path | None = None,
) -> list[Repository]:
    """Load repository configurations from YAML file.

    Args:
        config_path: Optional path to custom repositories.yaml file.

    Returns:
        List of Repository entities.
    """
    config_service = YamlRepositoryConfigService()

    try:
        repositories = config_service.load_repositories(
            str(config_path) if config_path else None
        )
        return repositories
    except FileNotFoundError as e:
        # Fall back to environment variables for backward compatibility
        click.echo(
            f"⚠️  Repository config not found: {e}. Checking environment variables...",
            err=True,
        )
        return get_repositories_from_environment()
    except ValueError as e:
        click.echo(f"Error loading repository configuration: {e}", err=True)
        return []


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


def print_npmrc_summary(result):
    """Print a summary of the npmrc configuration results."""
    click.echo("\n" + "=" * 50)
    click.echo("npmrc Configuration Summary")
    click.echo("=" * 50)

    if result.status == ConfigurationStatus.ALREADY_EXISTS:
        click.echo("→ npmrc configuration already exists with GitHub token")
    elif result.status == ConfigurationStatus.CREATED:
        click.echo("✓ Created new npmrc configuration")
        click.echo(f"  Location: {result.message.split('at ')[-1]}")
    elif result.status == ConfigurationStatus.UPDATED:
        click.echo("✓ Updated existing npmrc configuration")
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
    "--skip-npmrc",
    is_flag=True,
    default=False,
    help="Skip npmrc configuration setup",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be done without actually doing it (validation and logging only)",
)
@click.option(
    "--repositories-config",
    type=click.Path(exists=False, path_type=Path),
    help="Repository configuration YAML file (default: config/repositories.yaml)",
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
    skip_npmrc: bool,
    dry_run: bool,
    repositories_config: Path | None,
    skip_software: bool,
    software_config: Path | None,
    install_all_software: bool,
):
    """Configure development environment: software, Git repositories, and npmrc.

    Installs development software via Homebrew, clones Git repositories from
    YAML configuration files, and configures npmrc for GitHub packages.

    \b
    QUICK START:
      setup-environment --dev-folder ~/dev  # Run full setup

    \b
    TESTING:
      setup-environment --dev-folder ~/dev --dry-run

    \b
    SOFTWARE OPTIONS:
      setup-environment --dev-folder ~/dev --skip-software
      setup-environment --dev-folder ~/dev --install-all-software

    \b
    REPOSITORY CONFIGURATION:
      Repositories are defined in config/repositories.yaml by default.
      Use --repositories-config to specify a custom location.
    """
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

        # Load repositories from configuration
        repositories = load_repositories_from_config(repositories_config)

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
            python_service = BrewPythonService()
            git_install_service = GitInstallService()
            nvm_service = NodeEnvironmentService()

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
                "\nNo repositories found in configuration.",
                err=True,
            )
            click.echo(
                "Please create a repositories.yaml file with repository definitions.",
                err=True,
            )
            click.echo(
                "Run with --generate-repo-template to create an example configuration.",
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

        # Configure npmrc if not skipped
        if not skip_npmrc:
            if dry_run:
                click.echo("\n--- DRY RUN: npmrc Configuration ---")
                npmrc_service = NPMRCFileService()
                config_path = npmrc_service.get_config_path()

                if npmrc_service.config_exists():
                    if npmrc_service.has_github_token():
                        click.echo(
                            "→ Would skip npmrc configuration (already exists with GitHub token)"
                        )
                    else:
                        click.echo(
                            f"→ Would update existing npmrc configuration at {config_path}"
                        )
                else:
                    click.echo(
                        f"→ Would create new npmrc configuration at {config_path}"
                    )

                click.echo("→ Would prompt for GitHub Personal Access Token")
            else:
                click.echo("\nConfiguring npmrc settings...")
                npmrc_service = NPMRCFileService()
                npmrc_use_case = ConfigureNPMRCUseCase(npmrc_service)

                npmrc_result = npmrc_use_case.execute()
                print_npmrc_summary(npmrc_result)
        else:
            click.echo("\n→ Skipped npmrc configuration (--skip-npmrc flag)")

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

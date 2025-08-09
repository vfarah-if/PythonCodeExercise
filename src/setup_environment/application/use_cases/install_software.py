"""Use case for installing development software."""

from dataclasses import dataclass
from enum import Enum

import click

from src.setup_environment.application.interfaces.software_service import (
    SoftwareService,
)
from src.setup_environment.domain.entities.software import Software
from src.setup_environment.domain.value_objects.install_response import InstallResponse


class InstallationStatus(Enum):
    """Status of software installation process."""

    ALREADY_INSTALLED = "already_installed"
    INSTALLED = "installed"
    SKIPPED = "skipped"
    FAILED = "failed"
    NO_PACKAGE_MANAGER = "no_package_manager"


@dataclass
class InstallationResult:
    """Result of a single software installation."""

    software: Software
    status: InstallationStatus
    message: str = ""


@dataclass
class InstallSoftwareResult:
    """Overall result of software installation process."""

    results: list[InstallationResult]

    @property
    def already_installed(self) -> list[InstallationResult]:
        """Get already installed software."""
        return [
            r for r in self.results if r.status == InstallationStatus.ALREADY_INSTALLED
        ]

    @property
    def installed(self) -> list[InstallationResult]:
        """Get newly installed software."""
        return [r for r in self.results if r.status == InstallationStatus.INSTALLED]

    @property
    def skipped(self) -> list[InstallationResult]:
        """Get skipped software."""
        return [r for r in self.results if r.status == InstallationStatus.SKIPPED]

    @property
    def failed(self) -> list[InstallationResult]:
        """Get failed installations."""
        return [r for r in self.results if r.status == InstallationStatus.FAILED]

    @property
    def has_failures(self) -> bool:
        """Check if any installations failed."""
        return len(self.failed) > 0


class InstallSoftwareUseCase:
    """Use case for handling software installation with user prompts."""

    def __init__(
        self,
        software_service: SoftwareService,
        python_service=None,
        git_service=None,
        nvm_service=None,
    ):
        """Initialize with software service and specialised services."""
        self._software_service = software_service
        self._python_service = python_service
        self._git_service = git_service
        self._nvm_service = nvm_service

    def execute(
        self,
        config_path: str | None = None,
        dry_run: bool = False,
        install_all: bool = False,
        skip_all: bool = False,
        setup_ssh: bool = False,
    ) -> InstallSoftwareResult:
        """Execute software installation process.

        Args:
            config_path: Path to software configuration file
            dry_run: If True, only simulate installations
            install_all: If True, install all without prompting
            skip_all: If True, skip all installations
            setup_ssh: If True, configure SSH for Git

        Returns:
            InstallSoftwareResult with installation outcomes
        """
        # Check if package manager is available
        if not self._software_service.is_package_manager_installed():
            if dry_run:
                click.echo(
                    click.style("⚠️  Homebrew not found - would install", fg="yellow")
                )
                return InstallSoftwareResult(
                    [
                        InstallationResult(
                            Software(
                                "homebrew",
                                "Package manager",
                                "brew --version",
                                "specialised",
                            ),
                            InstallationStatus.SKIPPED,
                            "Would install Homebrew",
                        )
                    ]
                )
            else:
                click.echo(
                    click.style("⚠️  Homebrew is not installed.", fg="yellow", bold=True)
                )

                # Prompt user to install Homebrew
                if install_all:
                    install_brew = True
                elif skip_all:
                    install_brew = False
                else:
                    install_brew = click.confirm(
                        click.style(
                            "Would you like to install Homebrew now?", fg="cyan"
                        ),
                        default=True,
                    )

                if install_brew:
                    success, message = self._software_service.install_package_manager(
                        dry_run
                    )
                    if success:
                        click.echo(click.style(f"✓ {message}", fg="green"))
                    else:
                        click.echo(click.style(f"✗ {message}", fg="red"))
                        return InstallSoftwareResult(
                            [
                                InstallationResult(
                                    Software(
                                        "homebrew",
                                        "Package manager",
                                        "brew --version",
                                        "specialised",
                                    ),
                                    InstallationStatus.FAILED,
                                    message,
                                )
                            ]
                        )
                else:
                    click.echo(
                        "Skipping Homebrew installation. Software installation will be limited."
                    )
                    return InstallSoftwareResult(
                        [
                            InstallationResult(
                                Software(
                                    "homebrew",
                                    "Package manager",
                                    "brew --version",
                                    "specialised",
                                ),
                                InstallationStatus.SKIPPED,
                                "User declined Homebrew installation",
                            )
                        ]
                    )

        # Display header
        click.echo("\n" + "=" * 60)
        click.echo(
            click.style("🛠️  Development Software Installation", bold=True, fg="cyan")
        )
        click.echo("=" * 60)

        if dry_run:
            click.echo(
                click.style(
                    "DRY RUN - No software will actually be installed", fg="yellow"
                )
            )

        # Install specialised services first
        results = []
        user_choice = None  # Track "all" responses

        # Handle specialised services
        specialised_results = self._handle_specialised_services(
            dry_run, install_all, skip_all, user_choice, setup_ssh
        )
        results.extend(specialised_results)

        # Load software configuration
        try:
            from pathlib import Path

            config_file_path = Path(config_path) if config_path else None
            software_list = self._software_service.load_software_config(
                config_file_path
            )
        except (FileNotFoundError, ValueError) as e:
            click.echo(
                click.style(f"Error loading software configuration: {e}", fg="red")
            )
            # Return specialised results even if config loading fails
            return InstallSoftwareResult(results)

        if not software_list:
            click.echo(
                click.style("No software configured for installation", fg="yellow")
            )
            # Return specialised results even if no regular software configured
            return InstallSoftwareResult(results)

        # Check current installation status for regular software
        click.echo("\nChecking remaining software...")
        user_choice = None  # Reset user choice for regular software

        for software in software_list:
            if self._software_service.is_installed(software):
                click.echo(
                    click.style(
                        f"✓ {software.display_name} (already installed)", fg="green"
                    )
                )
                results.append(
                    InstallationResult(
                        software,
                        InstallationStatus.ALREADY_INSTALLED,
                        "Already installed",
                    )
                )
            else:
                click.echo(
                    click.style(f"✗ {software.display_name} not found", fg="red")
                )

                # Handle installation decision
                if skip_all or (user_choice == InstallResponse.NO_TO_ALL):
                    results.append(
                        InstallationResult(
                            software,
                            InstallationStatus.SKIPPED,
                            "Skipped by user choice",
                        )
                    )
                elif install_all or (user_choice == InstallResponse.YES_TO_ALL):
                    # Install without prompting
                    result = self._install_software(software, dry_run)
                    results.append(result)
                elif dry_run:
                    # In dry-run mode, just show what would happen
                    click.echo(f"→ Would prompt to install {software.display_name}")
                    results.append(
                        InstallationResult(
                            software, InstallationStatus.SKIPPED, "Would prompt user"
                        )
                    )
                else:
                    # Prompt user for this specific software
                    response = self._prompt_for_installation(software)

                    if response.is_all_response():
                        user_choice = response

                    if response.should_install():
                        result = self._install_software(software, dry_run)
                        results.append(result)
                    else:
                        results.append(
                            InstallationResult(
                                software, InstallationStatus.SKIPPED, "Skipped by user"
                            )
                        )

        return InstallSoftwareResult(results)

    def _handle_specialised_services(
        self,
        dry_run: bool,
        install_all: bool,
        skip_all: bool,
        user_choice,
        setup_ssh: bool = False,
    ) -> list[InstallationResult]:
        """Handle installation of specialised services (Python, Git, NVM)."""
        results = []

        # Python environment (Python + uv)
        if self._python_service:
            results.extend(
                self._handle_python_service(dry_run, install_all, skip_all, user_choice)
            )

        # Git (install + configure + SSH)
        if self._git_service:
            results.extend(
                self._handle_git_service(
                    dry_run, install_all, skip_all, user_choice, setup_ssh
                )
            )

        # NVM (install + latest Node)
        if self._nvm_service:
            results.extend(
                self._handle_nvm_service(dry_run, install_all, skip_all, user_choice)
            )

        return results

    def _handle_python_service(
        self, dry_run: bool, install_all: bool, skip_all: bool, user_choice
    ) -> list[InstallationResult]:
        """Handle Python environment setup."""
        if skip_all:
            return [
                InstallationResult(
                    Software(
                        "python-env",
                        "Python Environment",
                        "python3 --version && uv --version",
                        "specialised",
                    ),
                    InstallationStatus.SKIPPED,
                    "Skipped by user choice",
                )
            ]

        if install_all or dry_run:
            success, message = self._python_service.setup_python_environment(dry_run)
            # Check if everything was already installed
            if success and "already installed" in message.lower():
                status = InstallationStatus.ALREADY_INSTALLED
            elif success:
                status = InstallationStatus.INSTALLED
            else:
                status = InstallationStatus.FAILED
            return [
                InstallationResult(
                    Software(
                        "python-env",
                        "Python Environment",
                        "python3 --version && uv --version",
                        "specialised",
                    ),
                    status,
                    message,
                )
            ]

        # Interactive prompt
        click.echo(click.style("\n🐍 Python Environment Setup", fg="cyan", bold=True))
        click.echo("This will install Python and uv package manager")

        if click.confirm(
            click.style("Set up Python environment?", fg="cyan"), default=True
        ):
            success, message = self._python_service.setup_python_environment(dry_run)
            # Check if everything was already installed
            if success and "already installed" in message.lower():
                status = InstallationStatus.ALREADY_INSTALLED
            elif success:
                status = InstallationStatus.INSTALLED
            else:
                status = InstallationStatus.FAILED
            return [
                InstallationResult(
                    Software(
                        "python-env",
                        "Python Environment",
                        "python3 --version && uv --version",
                        "specialised",
                    ),
                    status,
                    message,
                )
            ]
        else:
            return [
                InstallationResult(
                    Software(
                        "python-env",
                        "Python Environment",
                        "python3 --version && uv --version",
                        "specialised",
                    ),
                    InstallationStatus.SKIPPED,
                    "Skipped by user",
                )
            ]

    def _handle_git_service(
        self,
        dry_run: bool,
        install_all: bool,
        skip_all: bool,
        user_choice,
        setup_ssh: bool = False,
    ) -> list[InstallationResult]:
        """Handle Git setup with optional SSH configuration."""
        service_name = "Git + Configuration"
        if setup_ssh:
            service_name = "Git + Configuration + SSH"

        if skip_all:
            return [
                InstallationResult(
                    Software("git", service_name, "git --version", "specialised"),
                    InstallationStatus.SKIPPED,
                    "Skipped by user choice",
                )
            ]

        if install_all or dry_run:
            success, message = self._git_service.setup_git(dry_run, setup_ssh=setup_ssh)
            # Check if everything was already installed/configured
            if (
                success
                and "already" in message.lower()
                and "already installed" in message.lower()
            ):
                status = InstallationStatus.ALREADY_INSTALLED
            elif success:
                status = InstallationStatus.INSTALLED
            else:
                status = InstallationStatus.FAILED
            return [
                InstallationResult(
                    Software("git", service_name, "git --version", "specialised"),
                    status,
                    message,
                )
            ]

        # Interactive prompt
        click.echo(click.style("\n🔧 Git Setup", fg="cyan", bold=True))
        if setup_ssh:
            click.echo(
                "This will install Git, configure user settings, and set up SSH keys"
            )
        else:
            click.echo("This will install Git and configure your user settings")

        if click.confirm(click.style("Set up Git?", fg="cyan"), default=True):
            success, message = self._git_service.setup_git(dry_run, setup_ssh=setup_ssh)
            # Check if everything was already installed/configured
            if (
                success
                and "already" in message.lower()
                and "already installed" in message.lower()
            ):
                status = InstallationStatus.ALREADY_INSTALLED
            elif success:
                status = InstallationStatus.INSTALLED
            else:
                status = InstallationStatus.FAILED
            return [
                InstallationResult(
                    Software("git", service_name, "git --version", "specialised"),
                    status,
                    message,
                )
            ]
        else:
            return [
                InstallationResult(
                    Software("git", service_name, "git --version", "specialised"),
                    InstallationStatus.SKIPPED,
                    "Skipped by user",
                )
            ]

    def _handle_nvm_service(
        self, dry_run: bool, install_all: bool, skip_all: bool, user_choice
    ) -> list[InstallationResult]:
        """Handle NVM and Node.js setup."""
        if skip_all:
            return [
                InstallationResult(
                    Software(
                        "node-env",
                        "Node.js Environment",
                        "nvm --version",
                        "specialised",
                    ),
                    InstallationStatus.SKIPPED,
                    "Skipped by user choice",
                )
            ]

        if install_all or dry_run:
            success, message = self._nvm_service.setup_node_environment(dry_run)
            # Check if everything was already installed
            if success and "already installed" in message.lower():
                status = InstallationStatus.ALREADY_INSTALLED
            elif success:
                status = InstallationStatus.INSTALLED
            else:
                status = InstallationStatus.FAILED
            return [
                InstallationResult(
                    Software(
                        "node-env",
                        "Node.js Environment",
                        "nvm --version",
                        "specialised",
                    ),
                    status,
                    message,
                )
            ]

        # Interactive prompt
        click.echo(click.style("\n📦 Node.js Environment Setup", fg="cyan", bold=True))
        click.echo("This will install NVM and the latest Node.js LTS version")

        if click.confirm(
            click.style("Set up Node.js environment?", fg="cyan"), default=True
        ):
            success, message = self._nvm_service.setup_node_environment(dry_run)
            # Check if everything was already installed
            if success and "already installed" in message.lower():
                status = InstallationStatus.ALREADY_INSTALLED
            elif success:
                status = InstallationStatus.INSTALLED
            else:
                status = InstallationStatus.FAILED
            return [
                InstallationResult(
                    Software(
                        "node-env",
                        "Node.js Environment",
                        "nvm --version",
                        "specialised",
                    ),
                    status,
                    message,
                )
            ]
        else:
            return [
                InstallationResult(
                    Software(
                        "node-env",
                        "Node.js Environment",
                        "nvm --version",
                        "specialised",
                    ),
                    InstallationStatus.SKIPPED,
                    "Skipped by user",
                )
            ]

    def _prompt_for_installation(self, software: Software) -> InstallResponse:
        """Prompt user whether to install software."""
        click.echo(f"\n{software.description}")

        if software.custom_install:
            click.echo(click.style("⚠️  Custom installation required", fg="yellow"))

        while True:
            try:
                user_input = click.prompt(
                    click.style(
                        f"Install {software.display_name}? [Y]es / [N]o / [A]ll / [S]kip all",
                        fg="cyan",
                    ),
                    type=str,
                    show_default=False,
                )
                return InstallResponse.from_input(user_input)
            except ValueError as e:
                click.echo(click.style(str(e), fg="red"))

    def _install_software(
        self, software: Software, dry_run: bool
    ) -> InstallationResult:
        """Install a single software package."""
        if dry_run:
            success, message = self._software_service.install(software, dry_run=True)
            return InstallationResult(software, InstallationStatus.INSTALLED, message)

        click.echo(f"Installing {software.name}...")
        success, message = self._software_service.install(software, dry_run=False)

        if success:
            click.echo(click.style(f"✓ {message}", fg="green"))
            return InstallationResult(software, InstallationStatus.INSTALLED, message)
        else:
            click.echo(click.style(f"✗ {message}", fg="red"))
            return InstallationResult(software, InstallationStatus.FAILED, message)

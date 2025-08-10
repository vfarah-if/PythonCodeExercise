"""Homebrew-based software installation service."""

import shlex
import subprocess
from pathlib import Path
from typing import Any

import yaml

from src.setup_environment.application.interfaces.software.software_service import (
    SoftwareService,
)
from src.setup_environment.domain.entities.software import Software


class BrewSoftwareService(SoftwareService):
    """Homebrew implementation of software installation service."""

    def __init__(self, config_dir: Path | None = None):
        """Initialize with optional config directory override."""
        if config_dir is None:
            # Default to the package config directory - go up two levels from infrastructure/software
            self._config_dir = Path(__file__).parent.parent.parent / "config"
        else:
            self._config_dir = config_dir

    def is_package_manager_installed(self) -> bool:
        """Check if Homebrew is installed."""
        try:
            result = subprocess.run(
                ["brew", "--version"], capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def install_package_manager(self, dry_run: bool = False) -> tuple[bool, str]:
        """Install Homebrew if not present.

        Args:
            dry_run: If True, only simulate installation

        Returns:
            Tuple of (success, message)
        """
        import click

        if dry_run:
            return True, "Would install Homebrew"

        click.echo(click.style("\n🍺 Installing Homebrew...", fg="cyan", bold=True))
        click.echo("This may take several minutes and requires sudo access.")

        try:
            # Official Homebrew installation command
            install_cmd = [
                "/bin/bash",
                "-c",
                "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)",
            ]

            result = subprocess.run(
                install_cmd,
                timeout=600,  # 10 minute timeout for Homebrew installation
                text=True,
            )

            if result.returncode == 0:
                click.echo(click.style("✓ Homebrew installed successfully", fg="green"))
                return True, "Homebrew installed successfully"
            else:
                return False, "Homebrew installation failed"

        except subprocess.TimeoutExpired:
            return False, "Homebrew installation timed out"
        except Exception as e:
            return False, f"Error installing Homebrew: {e!s}"

    def is_installed(self, software: Software) -> bool:
        """Check if software is installed by running its check command."""
        import os

        try:
            # Parse command safely using shlex
            cmd_parts = shlex.split(software.check_command)

            # Expand environment variables in command parts
            expanded_cmd = [os.path.expandvars(part) for part in cmd_parts]

            result = subprocess.run(
                expanded_cmd, capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def install(self, software: Software, dry_run: bool = False) -> tuple[bool, str]:
        """Install software using the configured command."""
        if dry_run:
            return True, f"Would execute: {software.install_command}"

        try:
            # Parse command safely using shlex
            cmd_parts = shlex.split(software.install_command)

            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout for installations
            )

            if result.returncode == 0:
                return True, f"Successfully installed {software.name}"
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                return False, f"Failed to install {software.name}: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, f"Installation of {software.name} timed out"
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            return False, f"Error installing {software.name}: {e!s}"

    def load_software_config(self, config_path: Path | None = None) -> list[Software]:
        """Load software configuration from YAML file."""
        if config_path is None:
            config_path = self._config_dir / "software.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"Software configuration not found: {config_path}")

        try:
            with config_path.open("r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            if not isinstance(config_data, dict) or "software" not in config_data:
                raise ValueError(
                    "Invalid software configuration: missing 'software' key"
                )

            software_list = []
            for item in config_data["software"]:
                software_list.append(self._parse_software_item(item))

            return software_list

        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing software configuration: {e}") from e

    def _parse_software_item(self, item: dict[str, Any]) -> Software:
        """Parse a single software item from configuration."""
        required_fields = ["name", "description", "check_command", "install_command"]

        for field in required_fields:
            if field not in item:
                raise ValueError(
                    f"Missing required field '{field}' in software configuration"
                )

        return Software(
            name=item["name"],
            description=item["description"],
            check_command=item["check_command"],
            install_command=item["install_command"],
            required=item.get("required", False),
            custom_install=item.get("custom_install", False),
        )

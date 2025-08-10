"""Python and uv installation service."""

import subprocess

import click

from src.setup_environment.application.interfaces.python_service import (
    PythonEnvironmentService,
)


class BrewPythonService(PythonEnvironmentService):
    """Service for installing Python and uv package manager."""

    def is_python_installed(self) -> bool:
        """Check if Python is installed."""
        try:
            result = subprocess.run(
                ["python3", "--version"], capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def is_uv_installed(self) -> bool:
        """Check if uv is installed."""
        try:
            result = subprocess.run(
                ["uv", "--version"], capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def install_python(self, dry_run: bool = False) -> tuple[bool, str]:
        """Install Python using Homebrew."""
        if dry_run:
            return True, "Would install Python via Homebrew"

        click.echo("🐍 Installing Python...")

        try:
            result = subprocess.run(
                ["brew", "install", "python"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                return True, "Python installed successfully"
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                return False, f"Failed to install Python: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "Python installation timed out"
        except Exception as e:
            return False, f"Error installing Python: {e!s}"

    def install_uv(self, dry_run: bool = False) -> tuple[bool, str]:
        """Install uv package manager."""
        if dry_run:
            return True, "Would install uv via Homebrew"

        click.echo("⚡ Installing uv...")

        try:
            result = subprocess.run(
                ["brew", "install", "uv"], capture_output=True, text=True, timeout=300
            )

            if result.returncode == 0:
                return True, "uv installed successfully"
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                return False, f"Failed to install uv: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "uv installation timed out"
        except Exception as e:
            return False, f"Error installing uv: {e!s}"

    def setup_python_environment(self, dry_run: bool = False) -> tuple[bool, str]:
        """Set up complete Python environment (Python + uv)."""
        results = []

        # Check and install Python
        if not self.is_python_installed():
            success, message = self.install_python(dry_run)
            results.append(f"Python: {message}")
            if not success:
                return False, "; ".join(results)
        else:
            results.append("Python: already installed")

        # Check and install uv
        if not self.is_uv_installed():
            success, message = self.install_uv(dry_run)
            results.append(f"uv: {message}")
            if not success:
                return False, "; ".join(results)
        else:
            results.append("uv: already installed")

        return True, "; ".join(results)

"""NVM and Node.js installation service."""

import os
import subprocess

import click

from src.setup_environment.application.interfaces.software.node_service import (
    NodeService,
)


class NodeEnvironmentService(NodeService):
    """Service for installing NVM and Node.js."""

    def is_nvm_installed(self) -> bool:
        """Check if NVM is installed."""
        # NVM is a shell function, so we need to source it and check version
        try:
            nvm_script = os.path.expanduser("~/.nvm/nvm.sh")
            # Try to run nvm --version through bash
            result = subprocess.run(
                ["/bin/bash", "-c", f"source {nvm_script} 2>/dev/null && nvm --version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            # If the command succeeds and returns a version, NVM is installed
            return result.returncode == 0 and result.stdout.strip() != ""
        except (subprocess.TimeoutExpired, Exception):
            return False

    def install_nvm(self, dry_run: bool = False) -> tuple[bool, str]:
        """Install NVM using the official installation script."""
        if dry_run:
            return True, "Would install NVM via official script"

        click.echo("📦 Installing NVM...")

        try:
            # Use latest stable version - v0.40.1 as of 2025
            # Official NVM installation command
            install_cmd = [
                "/bin/bash",
                "-c",
                "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash",
            ]

            result = subprocess.run(
                install_cmd,
                timeout=300,  # 5 minute timeout
                text=True,
            )

            if result.returncode == 0:
                # Verify installation by checking if nvm is available
                if self.is_nvm_installed():
                    return True, "NVM installed successfully"
                else:
                    return False, "NVM installation completed but verification failed"
            else:
                return False, "NVM installation failed"

        except subprocess.TimeoutExpired:
            return False, "NVM installation timed out"
        except Exception as e:
            return False, f"Error installing NVM: {e!s}"

    def install_latest_node(self, dry_run: bool = False) -> tuple[bool, str]:
        """Install the latest LTS version of Node.js using NVM."""
        if dry_run:
            return True, "Would install latest Node.js LTS via NVM"

        click.echo("🌟 Installing latest Node.js LTS...")

        try:
            # Source NVM and install latest LTS Node
            nvm_script = os.path.expanduser("~/.nvm/nvm.sh")
            install_cmd = [
                "/bin/bash",
                "-c",
                f"source {nvm_script} && nvm install --lts && nvm use --lts && nvm alias default lts/*",
            ]

            result = subprocess.run(
                install_cmd,
                capture_output=True,
                timeout=600,  # 10 minute timeout for Node.js download
                text=True,
            )

            if result.returncode == 0:
                # Get the installed version for confirmation
                version = self.get_node_version()
                if version != "unknown":
                    return True, f"Node.js LTS {version} installed and set as default"
                else:
                    return True, "Latest Node.js LTS installed and set as default"
            else:
                error_msg = result.stderr.strip() if result.stderr else "Failed to install Node.js"
                return False, error_msg

        except subprocess.TimeoutExpired:
            return False, "Node.js installation timed out"
        except Exception as e:
            return False, f"Error installing Node.js: {e!s}"

    def install_node_version(self, version: str = "lts", dry_run: bool = False) -> tuple[bool, str]:
        """Install a specific version of Node.js using NVM.

        Args:
            version: Version to install ('lts', 'latest', or specific version like '18.17.0')
            dry_run: If True, only simulate installation

        Returns:
            Tuple of (success, message)
        """
        if dry_run:
            return True, f"Would install Node.js {version} via NVM"

        # Map version aliases
        nvm_version = version
        if version.lower() == "lts":
            nvm_version = "--lts"
            display_version = "LTS"
        elif version.lower() in ["latest", "node"]:
            nvm_version = "node"  # 'node' is NVM's alias for latest
            display_version = "latest"
        else:
            display_version = version

        click.echo(f"📦 Installing Node.js {display_version}...")

        try:
            nvm_script = os.path.expanduser("~/.nvm/nvm.sh")
            install_cmd = [
                "/bin/bash",
                "-c",
                f"source {nvm_script} && nvm install {nvm_version} && nvm use {nvm_version}",
            ]

            result = subprocess.run(
                install_cmd,
                capture_output=True,
                timeout=600,
                text=True,
            )

            if result.returncode == 0:
                installed_version = self.get_node_version()
                if installed_version != "unknown":
                    return True, f"Node.js {installed_version} installed successfully"
                else:
                    return True, f"Node.js {display_version} installed successfully"
            else:
                error_msg = result.stderr.strip() if result.stderr else f"Failed to install Node.js {display_version}"
                return False, error_msg

        except subprocess.TimeoutExpired:
            return False, f"Node.js {display_version} installation timed out"
        except Exception as e:
            return False, f"Error installing Node.js {display_version}: {e!s}"

    def get_node_version(self) -> str:
        """Get currently active Node.js version."""
        try:
            nvm_script = os.path.expanduser("~/.nvm/nvm.sh")
            result = subprocess.run(
                ["/bin/bash", "-c", f"source {nvm_script} && node --version"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "unknown"
        except Exception:
            return "unknown"

    def setup_node_environment(self, dry_run: bool = False) -> tuple[bool, str]:
        """Set up complete Node.js environment (NVM + latest Node)."""
        results = []

        # Check and install NVM
        if not self.is_nvm_installed():
            success, message = self.install_nvm(dry_run)
            results.append(f"NVM: {message}")
            if not success:
                return False, "; ".join(results)
        else:
            results.append("NVM: already installed")

        # Install latest Node.js
        if not dry_run and self.is_nvm_installed():
            success, message = self.install_latest_node(dry_run)
            results.append(f"Node.js: {message}")
            if not success:
                return False, "; ".join(results)
        elif dry_run:
            results.append("Node.js: would install latest LTS")

        return True, "; ".join(results)

"""NVM and Node.js installation service."""

import os
import subprocess

import click


class NVMService:
    """Service for installing NVM and Node.js."""

    def is_nvm_installed(self) -> bool:
        """Check if NVM is installed."""
        # NVM is a shell function, not a binary, so check for the directory
        nvm_dir = os.path.expanduser("~/.nvm")
        return os.path.exists(nvm_dir) and os.path.exists(f"{nvm_dir}/nvm.sh")

    def install_nvm(self, dry_run: bool = False) -> tuple[bool, str]:
        """Install NVM using the official installation script."""
        if dry_run:
            return True, "Would install NVM via official script"

        click.echo("📦 Installing NVM...")

        try:
            # Official NVM installation command
            install_cmd = [
                "/bin/bash",
                "-c",
                "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash",
            ]

            result = subprocess.run(
                install_cmd,
                timeout=300,  # 5 minute timeout
                text=True,
            )

            if result.returncode == 0:
                return True, "NVM installed successfully"
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
                timeout=600,  # 10 minute timeout for Node.js download
                text=True,
            )

            if result.returncode == 0:
                return True, "Latest Node.js LTS installed and set as default"
            else:
                return False, "Failed to install Node.js"

        except subprocess.TimeoutExpired:
            return False, "Node.js installation timed out"
        except Exception as e:
            return False, f"Error installing Node.js: {e!s}"

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

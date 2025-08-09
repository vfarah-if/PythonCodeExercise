"""Git installation and configuration service."""

import subprocess
from pathlib import Path

import click


class GitService:
    """Service for installing and configuring Git."""

    def is_git_installed(self) -> bool:
        """Check if Git is installed."""
        try:
            result = subprocess.run(
                ["git", "--version"], capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def is_git_configured(self) -> bool:
        """Check if Git has user.name and user.email configured."""
        try:
            # Check user.name
            name_result = subprocess.run(
                ["git", "config", "--global", "user.name"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Check user.email
            email_result = subprocess.run(
                ["git", "config", "--global", "user.email"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            return (
                name_result.returncode == 0
                and bool(name_result.stdout.strip())
                and email_result.returncode == 0
                and bool(email_result.stdout.strip())
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def install_git(self, dry_run: bool = False) -> tuple[bool, str]:
        """Install Git using Homebrew."""
        if dry_run:
            return True, "Would install Git via Homebrew"

        click.echo("🔧 Installing Git...")

        try:
            result = subprocess.run(
                ["brew", "install", "git"], capture_output=True, text=True, timeout=300
            )

            if result.returncode == 0:
                return True, "Git installed successfully"
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                return False, f"Failed to install Git: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "Git installation timed out"
        except Exception as e:
            return False, f"Error installing Git: {e!s}"

    def configure_git(
        self, username: str, email: str, dry_run: bool = False
    ) -> tuple[bool, str]:
        """Configure Git with user name and email."""
        if dry_run:
            return (
                True,
                f"Would configure Git: user.name='{username}', user.email='{email}'",
            )

        click.echo("⚙️  Configuring Git...")

        try:
            # Set user.name
            name_result = subprocess.run(
                ["git", "config", "--global", "user.name", username],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Set user.email
            email_result = subprocess.run(
                ["git", "config", "--global", "user.email", email],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if name_result.returncode == 0 and email_result.returncode == 0:
                return True, f"Git configured: {username} <{email}>"
            else:
                return False, "Failed to configure Git user settings"

        except Exception as e:
            return False, f"Error configuring Git: {e!s}"

    def prompt_for_git_config(self) -> tuple[str, str]:
        """Prompt user for Git configuration details."""
        click.echo(click.style("\n🔧 Git Configuration Required", fg="cyan", bold=True))
        click.echo("Please provide your Git user information for commits:")

        username = click.prompt(click.style("Full Name", fg="cyan"), type=str)

        email = click.prompt(click.style("Email Address", fg="cyan"), type=str)

        return username, email

    def has_ssh_key(self) -> bool:
        """Check if SSH keys exist."""
        ssh_dir = Path.home() / ".ssh"

        # Check for common SSH key types
        key_files = ["id_rsa", "id_ed25519", "id_ecdsa"]

        return any((ssh_dir / key_file).exists() for key_file in key_files)

    def generate_ssh_key(self, email: str, dry_run: bool = False) -> tuple[bool, str]:
        """Generate SSH key for Git operations."""
        if dry_run:
            return True, f"Would generate SSH key for {email}"

        click.echo("🔐 Generating SSH key...")

        try:
            # Generate Ed25519 key (recommended by GitHub)
            ssh_dir = Path.home() / ".ssh"
            ssh_dir.mkdir(exist_ok=True)

            key_path = ssh_dir / "id_ed25519"

            result = subprocess.run(
                [
                    "ssh-keygen",
                    "-t",
                    "ed25519",
                    "-C",
                    email,
                    "-f",
                    str(key_path),
                    "-N",
                    "",  # No passphrase for automation
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return True, f"SSH key generated at {key_path}"
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                return False, f"Failed to generate SSH key: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "SSH key generation timed out"
        except Exception as e:
            return False, f"Error generating SSH key: {e!s}"

    def add_ssh_key_to_agent(self, dry_run: bool = False) -> tuple[bool, str]:
        """Add SSH key to ssh-agent."""
        if dry_run:
            return True, "Would add SSH key to ssh-agent"

        click.echo("🔑 Adding SSH key to ssh-agent...")

        try:
            # Start ssh-agent if not running
            subprocess.run(["ssh-add", "-l"], capture_output=True, timeout=10)

            # Add SSH key
            ssh_dir = Path.home() / ".ssh"

            # Try common key files
            for key_file in ["id_ed25519", "id_rsa", "id_ecdsa"]:
                key_path = ssh_dir / key_file
                if key_path.exists():
                    result = subprocess.run(
                        ["ssh-add", str(key_path)],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )

                    if result.returncode == 0:
                        return True, f"SSH key {key_file} added to ssh-agent"

            return False, "No SSH keys found to add to ssh-agent"

        except Exception as e:
            return False, f"Error adding SSH key to agent: {e!s}"

    def test_ssh_connection(self, dry_run: bool = False) -> tuple[bool, str]:
        """Test SSH connection to GitHub."""
        if dry_run:
            return True, "Would test SSH connection to GitHub"

        click.echo("🔗 Testing SSH connection to GitHub...")

        try:
            result = subprocess.run(
                [
                    "ssh",
                    "-T",
                    "git@github.com",
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-o",
                    "UserKnownHostsFile=/dev/null",
                    "-o",
                    "LogLevel=ERROR",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # GitHub SSH test returns exit code 1 but with success message
            if "successfully authenticated" in result.stderr.lower():
                return True, "SSH connection to GitHub successful"
            elif result.returncode == 255:
                return False, "SSH connection failed - key may not be added to GitHub"
            else:
                return False, f"SSH connection test failed: {result.stderr.strip()}"

        except subprocess.TimeoutExpired:
            return False, "SSH connection test timed out"
        except Exception as e:
            return False, f"Error testing SSH connection: {e!s}"

    def display_github_ssh_instructions(self, email: str) -> None:
        """Display instructions for adding SSH key to GitHub."""
        ssh_dir = Path.home() / ".ssh"
        pub_key_path = None

        # Find public key file
        for key_file in ["id_ed25519.pub", "id_rsa.pub", "id_ecdsa.pub"]:
            potential_path = ssh_dir / key_file
            if potential_path.exists():
                pub_key_path = potential_path
                break

        if not pub_key_path:
            click.echo(click.style("⚠️  No public key found", fg="yellow"))
            return

        click.echo(click.style("\n🔑 GitHub SSH Key Setup", fg="cyan", bold=True))
        click.echo("To complete SSH setup, add your public key to GitHub:")
        click.echo("")
        click.echo(click.style("1. Copy your public key:", fg="cyan"))
        click.echo(f"   cat {pub_key_path}")
        click.echo("")
        click.echo(click.style("2. Add it to GitHub:", fg="cyan"))
        click.echo("   https://github.com/settings/ssh/new")
        click.echo("")
        click.echo(click.style("3. Test the connection:", fg="cyan"))
        click.echo("   ssh -T git@github.com")

    def setup_ssh_configuration(
        self, email: str, dry_run: bool = False
    ) -> tuple[bool, str]:
        """Set up complete SSH configuration for Git."""
        results = []

        # Check if SSH key exists
        if not self.has_ssh_key():
            if dry_run:
                results.append("SSH Key: would generate")
            else:
                success, message = self.generate_ssh_key(email, dry_run)
                results.append(f"SSH Key: {message}")
                if not success:
                    return False, "; ".join(results)
        else:
            results.append("SSH Key: already exists")

        # Add to ssh-agent
        if not dry_run and self.has_ssh_key():
            success, message = self.add_ssh_key_to_agent(dry_run)
            results.append(f"SSH Agent: {message}")
            if not success:
                return False, "; ".join(results)
        elif dry_run:
            results.append("SSH Agent: would add key")

        # Test SSH connection
        if not dry_run and self.has_ssh_key():
            success, message = self.test_ssh_connection(dry_run)
            results.append(f"SSH Test: {message}")
            if not success:
                # Don't fail on SSH test - just show instructions
                results.append("SSH Setup: manual GitHub configuration needed")
                self.display_github_ssh_instructions(email)
        elif dry_run:
            results.append("SSH Test: would test connection")

        return True, "; ".join(results)

    def setup_git(
        self, dry_run: bool = False, setup_ssh: bool = False
    ) -> tuple[bool, str]:
        """Set up complete Git environment (install + configure + SSH)."""
        results = []
        newly_installed = False
        user_email = None

        # Check and install Git
        if not self.is_git_installed():
            success, message = self.install_git(dry_run)
            results.append(f"Installation: {message}")
            if not success:
                return False, "; ".join(results)
            newly_installed = True
        else:
            results.append("Installation: already installed")

        # Configure Git only if newly installed or not configured
        if newly_installed or not self.is_git_configured():
            if dry_run:
                results.append("Configuration: would prompt for user details")
            else:
                username, email = self.prompt_for_git_config()
                user_email = email  # Store for SSH setup
                success, message = self.configure_git(username, email, dry_run)
                results.append(f"Configuration: {message}")
                if not success:
                    return False, "; ".join(results)
        else:
            results.append("Configuration: already configured")

        # Set up SSH if requested
        if setup_ssh:
            if not user_email:
                # If we didn't configure Git above, we need to get the email for SSH
                if dry_run:
                    user_email = "user@example.com"  # Placeholder for dry run
                else:
                    try:
                        email_result = subprocess.run(
                            ["git", "config", "--global", "user.email"],
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        if email_result.returncode == 0 and email_result.stdout.strip():
                            user_email = email_result.stdout.strip()
                        else:
                            # Fall back to prompting
                            user_email = click.prompt(
                                click.style("Email for SSH key", fg="cyan"), type=str
                            )
                    except Exception:
                        user_email = click.prompt(
                            click.style("Email for SSH key", fg="cyan"), type=str
                        )

            success, ssh_message = self.setup_ssh_configuration(user_email, dry_run)
            results.append(f"SSH: {ssh_message}")
            if not success:
                return False, "; ".join(results)

        return True, "; ".join(results)

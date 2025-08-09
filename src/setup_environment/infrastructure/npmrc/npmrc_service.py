"""npmrc service implementation for file system operations."""

import webbrowser
from pathlib import Path

from src.setup_environment.application.interfaces import NPMRCService
from src.setup_environment.domain.entities import NPMRCConfiguration
from src.setup_environment.domain.value_objects import PersonalAccessToken


class NPMRCFileService(NPMRCService):
    """npmrc service implementation using file system operations."""

    def __init__(self, home_dir: Path | None = None):
        """Initialise with optional home directory override."""
        self._home_dir = home_dir or Path.home()

    def config_exists(self) -> bool:
        """Check if npmrc configuration exists in the user's home directory."""
        return self.get_config_path().exists()

    def has_github_token(self) -> bool:
        """Check if the npmrc configuration has a GitHub token configured."""
        config_path = self.get_config_path()
        if not config_path.exists():
            return False

        try:
            content = config_path.read_text()
            return "_authToken" in content and "npm.pkg.github.com" in content
        except Exception:
            return False

    def write_config(self, config: NPMRCConfiguration) -> None:
        """Write npmrc configuration to the user's home directory."""
        config_path = self.get_config_path()

        # If config exists, we might want to preserve some existing content
        existing_content = ""
        if config_path.exists():
            try:
                existing_content = config_path.read_text()
                # Remove any existing GitHub registry configuration
                lines = existing_content.split("\n")
                filtered_lines = [
                    line
                    for line in lines
                    if not any(
                        keyword in line
                        for keyword in [
                            "_authToken",
                            "npm.pkg.github.com",
                            "@webuild-ai:registry",
                            "package-lock",
                            "legacy-peer-deps",
                        ]
                    )
                ]
                existing_content = "\n".join(filtered_lines).strip()
            except Exception:
                existing_content = ""

        # Generate new content
        new_content = config.generate_config_content()

        # Combine existing and new content
        if existing_content:
            final_content = f"{existing_content}\n\n{new_content}"
        else:
            final_content = new_content

        # Write combined content to file
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(final_content)

    def get_config_path(self) -> Path:
        """Get the path to the npmrc configuration file."""
        return self._home_dir / ".npmrc"

    def prompt_for_token(self) -> PersonalAccessToken:
        """Prompt the user to create and enter a GitHub Personal Access Token."""
        import click

        click.echo("\n" + "=" * 70)
        click.echo(
            click.style("🔐 GitHub Personal Access Token Setup", bold=True, fg="cyan")
        )
        click.echo("=" * 70)

        if not self.config_exists():
            click.echo(click.style("\n⚠️  No ~/.npmrc file found", fg="yellow"))
            click.echo(
                "We'll create one for you with the necessary GitHub Package Registry settings."
            )
        elif not self.has_github_token():
            click.echo(
                click.style("\n⚠️  No GitHub token found in ~/.npmrc", fg="yellow")
            )

        click.echo("\n" + click.style("📋 Required Steps:", bold=True))
        click.echo("\n1. I'll open GitHub's token creation page in your browser")
        click.echo("2. Configure your Personal Access Token with these settings:")
        click.echo(
            click.style("\n   Token Name:", bold=True)
            + " npm-packages (or any descriptive name)"
        )
        click.echo(
            click.style("   Expiration:", bold=True)
            + " 90 days (recommended) or custom"
        )
        click.echo(click.style("\n   Required Permissions:", bold=True, fg="green"))
        click.echo(
            "   ☐ "
            + click.style("repo", bold=True)
            + " - Full control of private repositories"
        )
        click.echo(
            "   ☐ "
            + click.style("write:packages", bold=True)
            + " - Upload packages to GitHub Package Registry"
        )
        click.echo(
            "   ☐ "
            + click.style("read:packages", bold=True)
            + " - Download packages from GitHub Package Registry"
        )
        click.echo(
            "   ☐ "
            + click.style("delete:packages", bold=True)
            + " - Delete packages from GitHub Package Registry"
        )

        click.echo(click.style("\n⚠️  IMPORTANT:", bold=True, fg="yellow"))
        click.echo(
            click.style("   GitHub will only show your token ONCE!", fg="yellow")
        )
        click.echo(click.style("   Copy it immediately after creation!", fg="yellow"))

        click.echo("\n" + "=" * 70)

        # Wait for user confirmation
        click.echo("\n" + click.style("Ready to create your token?", bold=True))
        input("Press Enter to open GitHub in your browser...")

        # Open GitHub token creation page directly
        token_url = "https://github.com/settings/tokens/new"
        click.echo(f"\n🌐 Opening browser to: {token_url}")

        try:
            webbrowser.open(token_url)
            click.echo(click.style("✓ Browser opened successfully", fg="green"))
        except Exception as e:
            click.echo(
                click.style(
                    f"⚠️  Could not open browser automatically: {e}", fg="yellow"
                )
            )
            click.echo(f"Please manually open: {token_url}")

        click.echo("\n" + "=" * 70)
        click.echo(
            click.style("Waiting for you to create and copy your token...", fg="cyan")
        )
        click.echo("=" * 70)

        click.echo(click.style("\n📝 Token Format Examples:", bold=True))
        click.echo("  Classic Token: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        click.echo("  Fine-grained:  github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

        while True:
            token_input = click.prompt(
                click.style(
                    "\n🔑 Paste your GitHub Personal Access Token here", fg="cyan"
                ),
                hide_input=True,  # Hide token input for security
                show_default=False,
            ).strip()

            if not token_input:
                click.echo(
                    click.style("✗ Token cannot be empty. Please try again.", fg="red")
                )
                continue

            try:
                token = PersonalAccessToken(token_input)
                click.echo(
                    click.style(
                        f"\n✓ Token validated successfully: {token}",
                        fg="green",
                        bold=True,
                    )
                )
                click.echo(
                    click.style("Your token has been securely stored.", fg="green")
                )
                return token
            except ValueError as e:
                click.echo(click.style(f"\n✗ Invalid token format: {e}", fg="red"))
                click.echo(
                    "GitHub tokens should start with 'ghp_' (classic) or 'github_pat_' (fine-grained)"
                )
                retry = click.confirm("Would you like to try again?", default=True)
                if not retry:
                    raise ValueError("Token creation cancelled by user") from None

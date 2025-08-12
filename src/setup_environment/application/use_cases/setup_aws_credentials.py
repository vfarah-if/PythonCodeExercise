"""Use case for setting up AWS credentials."""

from dataclasses import dataclass
from pathlib import Path

import click

from src.setup_environment.application.interfaces.aws import (
    AWSConfigService,
    AWSSSOService,
)
from src.setup_environment.domain.entities import AWSAccount, AWSCredentials


@dataclass
class AWSCredentialsResult:
    """Result of AWS credentials setup operation."""

    success: bool
    credentials: AWSCredentials | None = None
    account: AWSAccount | None = None
    env_vars: str | None = None
    error_message: str | None = None

    def is_successful(self) -> bool:
        """Check if the operation was successful."""
        return self.success and self.credentials is not None


class SetupAWSCredentialsUseCase:
    """Orchestrates AWS credential retrieval and configuration.

    This use case coordinates the interaction between various services
    to authenticate with AWS SSO and obtain temporary credentials.
    """

    def __init__(
        self,
        sso_service: AWSSSOService,
        config_service: AWSConfigService,
    ):
        """Initialise the use case with required services.

        Args:
            sso_service: Service for AWS SSO operations
            config_service: Service for configuration management
        """
        self.sso_service = sso_service
        self.config_service = config_service

    def execute(
        self,
        account_name: str | None = None,
        export_format: str = "bash",
        output_file: Path | None = None,
        env_file: Path | None = None,
        config_file: Path | None = None,
    ) -> AWSCredentialsResult:
        """Setup AWS credentials for specified account.

        Args:
            account_name: Name of AWS account (optional, prompts if not provided)
            export_format: Shell format for environment variables
            output_file: Optional file to save credentials to
            env_file: Optional .env file for SSO configuration
            config_file: Optional YAML file for account definitions

        Returns:
            Result containing credentials and export information
        """
        try:
            # Load SSO configuration
            click.echo("📋 Loading SSO configuration...")
            sso_config = self.config_service.load_sso_config(env_file)

            # Load account definitions
            click.echo("📋 Loading AWS account definitions...")
            accounts = self.config_service.load_accounts(config_file)

            if not accounts:
                return AWSCredentialsResult(
                    success=False,
                    error_message="No AWS accounts configured",
                )

            # Select account
            if account_name:
                account = self._find_account(accounts, account_name)
                if not account:
                    return AWSCredentialsResult(
                        success=False,
                        error_message=f"Account '{account_name}' not found",
                    )
            else:
                account = self._prompt_account_selection(accounts)
                if not account:
                    return AWSCredentialsResult(
                        success=False,
                        error_message="No account selected",
                    )

            click.echo("\n🔐 Authenticating with AWS SSO...")

            # Authenticate with SSO
            session = self.sso_service.authenticate(sso_config)

            if session.is_expired():
                click.echo("⚠️  Session expired, refreshing...")
                session = self.sso_service.refresh_session(sso_config)

            # Get credentials for selected account
            click.echo(f"🔑 Getting credentials for {account}...")
            credentials = self.sso_service.get_credentials(session, account)

            # Validate credentials
            if self.sso_service.validate_credentials(credentials):
                click.echo("✅ Credentials validated successfully")
            else:
                click.echo("⚠️  Warning: Could not validate credentials")

            # Format output
            env_vars = credentials.to_env_vars(export_format)

            # Save to file if requested
            if output_file:
                self.config_service.save_credentials_to_file(env_vars, output_file)
                click.echo(f"💾 Credentials saved to {output_file}")

            # Display expiration info
            click.echo(
                f"\n✓ Retrieved credentials for {account.name}\n"
                f"✓ Credentials valid for: {credentials.time_until_expiry()}"
            )

            return AWSCredentialsResult(
                success=True,
                credentials=credentials,
                account=account,
                env_vars=env_vars,
            )

        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            return AWSCredentialsResult(
                success=False,
                error_message=str(e),
            )

    def _find_account(
        self,
        accounts: list[AWSAccount],
        name: str,
    ) -> AWSAccount | None:
        """Find an account by name.

        Args:
            accounts: List of available accounts
            name: Account name to find

        Returns:
            Matching account or None
        """
        for account in accounts:
            if account.name.lower() == name.lower():
                return account
        return None

    def _prompt_account_selection(
        self,
        accounts: list[AWSAccount],
    ) -> AWSAccount | None:
        """Prompt user to select an account.

        Args:
            accounts: List of available accounts

        Returns:
            Selected account or None
        """
        # Check for default account
        default_account = self.config_service.get_default_account(accounts)

        click.echo("\nAvailable AWS Accounts:")
        for i, account in enumerate(accounts, 1):
            default_marker = " [default]" if account.is_default else ""
            click.echo(f"{i}. {account.name} ({account.account_id}){default_marker}")

        # Prompt for selection
        default_choice = None
        if default_account:
            default_choice = accounts.index(default_account) + 1
            prompt = f"Select account [1-{len(accounts)}] (default: {default_choice}): "
        else:
            prompt = f"Select account [1-{len(accounts)}]: "

        choice = click.prompt(
            prompt,
            type=int,
            default=default_choice,
            show_default=False,
        )

        if 1 <= choice <= len(accounts):
            return accounts[choice - 1]

        click.echo("Invalid selection", err=True)
        return None

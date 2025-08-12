"""AWS configuration service implementation."""

import os
from pathlib import Path

import yaml

from src.setup_environment.application.interfaces.aws import AWSConfigService
from src.setup_environment.domain.entities import AWSAccount
from src.setup_environment.domain.value_objects import SSOConfig


class YamlAWSConfigService(AWSConfigService):
    """AWS configuration service using YAML files and environment variables.

    This service loads AWS configuration from YAML files and environment
    variables, following the existing pattern in the codebase.
    """

    def __init__(self):
        """Initialise the service."""
        self._default_config_dir = Path(__file__).parent.parent.parent / "config"

    def load_sso_config(self, env_file: Path | None = None) -> SSOConfig:
        """Load SSO configuration from environment or .env file."""
        env_vars = {}

        # Load from .env file if provided
        if env_file and env_file.exists():
            env_vars.update(self._load_env_file(env_file))

        # Override with actual environment variables
        env_vars.update(os.environ)

        # Check for required variables
        if "AWS_SSO_START_URL" not in env_vars:
            # Try to load from .env in project root
            project_env = Path.cwd() / ".env"
            if project_env.exists():
                env_vars.update(self._load_env_file(project_env))

        # Validate required configuration
        if "AWS_SSO_START_URL" not in env_vars:
            raise ValueError(
                "AWS_SSO_START_URL not found in environment. "
                "Please set it in .env file or environment variables"
            )

        return SSOConfig.from_env(env_vars)

    def load_accounts(self, config_file: Path | None = None) -> list[AWSAccount]:
        """Load AWS account definitions from configuration file."""
        # Determine config file path
        config_path = config_file or self._default_config_dir / "aws_accounts.yaml"

        if not config_path.exists():
            # Try alternate location
            alt_path = Path.cwd() / "config" / "aws_accounts.yaml"
            if alt_path.exists():
                config_path = alt_path
            else:
                raise FileNotFoundError(
                    f"AWS accounts configuration not found at {config_path}"
                )

        # Load YAML file
        try:
            with open(config_path) as f:
                data = yaml.safe_load(f)

            if not data or "accounts" not in data:
                raise ValueError(
                    "Invalid AWS accounts configuration: missing 'accounts' key"
                )

            accounts = []
            for account_data in data["accounts"]:
                try:
                    account = AWSAccount.from_dict(account_data)
                    accounts.append(account)
                except (ValueError, TypeError) as e:
                    # Log warning and skip invalid account
                    print(f"Warning: Skipping invalid account: {e}")

            return accounts

        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML configuration: {e}") from e

    def save_credentials_to_file(
        self,
        credentials: str,
        file_path: Path,
    ) -> None:
        """Save credentials to a file."""
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write credentials
            with open(file_path, "w") as f:
                f.write(credentials)

            # Set restrictive permissions (readable by owner only)
            file_path.chmod(0o600)

        except OSError as e:
            raise OSError(f"Failed to save credentials to {file_path}: {e}") from e

    def get_default_account(self, accounts: list[AWSAccount]) -> AWSAccount | None:
        """Get the default account from a list of accounts."""
        for account in accounts:
            if account.is_default:
                return account

        # If no default is set, return the first account
        return accounts[0] if accounts else None

    def _load_env_file(self, env_file: Path) -> dict:
        """Load environment variables from a .env file.

        Args:
            env_file: Path to .env file

        Returns:
            Dictionary of environment variables
        """
        env_vars = {}

        try:
            with open(env_file) as f:
                for line in f:
                    line = line.strip()

                    # Skip comments and empty lines
                    if not line or line.startswith("#"):
                        continue

                    # Parse key=value pairs
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()

                        # Remove quotes if present
                        if (value.startswith('"') and value.endswith('"')) or (
                            value.startswith("'") and value.endswith("'")
                        ):
                            value = value[1:-1]

                        env_vars[key] = value

            return env_vars

        except OSError as e:
            raise ValueError(f"Failed to load .env file {env_file}: {e}") from e

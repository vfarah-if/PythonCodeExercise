"""AWS SSO service implementation using boto3."""

import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import click

from src.setup_environment.application.interfaces.aws import AWSSSOService
from src.setup_environment.domain.entities import AWSAccount, AWSCredentials
from src.setup_environment.domain.value_objects import AWSSession, SSOConfig


class Boto3SSOService(AWSSSOService):
    """AWS SSO service implementation using boto3 SDK.

    This implementation uses the boto3 SDK to interact with AWS SSO
    for authentication and credential retrieval.
    """

    def __init__(self):
        """Initialise the service."""
        self._cache_dir = Path.home() / ".aws" / "sso" / "cache"
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def authenticate(self, config: SSOConfig) -> AWSSession:
        """Authenticate with AWS SSO and obtain a session token.

        This implementation uses AWS CLI's SSO login flow for simplicity,
        as it handles the browser-based authentication automatically.
        """
        try:
            # Check for cached token first
            cached_token = self._get_cached_token(config)
            if cached_token:
                return cached_token

            # Perform SSO login using AWS CLI
            click.echo("🌐 Opening browser for SSO authentication...")
            self._perform_sso_login(config)

            # Get the token from cache after login
            cached_token = self._get_cached_token(config)
            if cached_token:
                return cached_token

            raise RuntimeError("Failed to obtain SSO token after authentication")

        except Exception as e:
            raise RuntimeError(f"SSO authentication failed: {e}") from e

    def get_credentials(
        self,
        session: AWSSession,
        account: AWSAccount,
    ) -> AWSCredentials:
        """Get temporary AWS credentials for a specific account.

        Uses boto3 to get role credentials from SSO.
        """
        if session.is_expired():
            raise ValueError("SSO session has expired")

        try:
            import boto3
            from botocore.exceptions import ClientError

            # Create SSO client
            sso_client = boto3.client("sso", region_name=session.region)

            # Get role credentials
            response = sso_client.get_role_credentials(
                roleName=account.role,
                accountId=account.account_id,
                accessToken=session.access_token,
            )

            # Extract credentials
            role_creds = response["roleCredentials"]

            # Convert expiration timestamp to datetime
            expiration = datetime.fromtimestamp(
                role_creds["expiration"] / 1000,
                tz=UTC,
            )

            return AWSCredentials(
                access_key_id=role_creds["accessKeyId"],
                secret_access_key=role_creds["secretAccessKey"],
                session_token=role_creds["sessionToken"],
                expiration=expiration.replace(tzinfo=None),
                region=session.region,
            )

        except ImportError:
            # Fall back to AWS CLI if boto3 not available
            return self._get_credentials_via_cli(session, account)
        except ClientError as e:
            raise RuntimeError(f"Failed to get credentials: {e}") from e

    def list_accounts(self, session: AWSSession) -> list[AWSAccount]:
        """List all available AWS accounts for the authenticated user."""
        if session.is_expired():
            raise ValueError("SSO session has expired")

        try:
            import boto3

            sso_client = boto3.client("sso", region_name=session.region)

            accounts = []
            paginator = sso_client.get_paginator("list_accounts")

            for page in paginator.paginate(accessToken=session.access_token):
                for account_info in page.get("accountList", []):
                    # Get roles for this account
                    roles_response = sso_client.list_account_roles(
                        accessToken=session.access_token,
                        accountId=account_info["accountId"],
                    )

                    # Use the first available role
                    roles = roles_response.get("roleList", [])
                    role_name = roles[0]["roleName"] if roles else "Engineer"

                    account = AWSAccount(
                        name=account_info.get("accountName", "Unknown"),
                        account_id=account_info["accountId"],
                        email=account_info.get("emailAddress", ""),
                        role=role_name,
                        is_default=False,
                    )
                    accounts.append(account)

            return accounts

        except Exception as e:
            raise RuntimeError(f"Failed to list accounts: {e}") from e

    def refresh_session(self, config: SSOConfig) -> AWSSession:
        """Refresh an SSO session to get a new access token."""
        # For SSO, refreshing means re-authenticating
        return self.authenticate(config)

    def validate_credentials(self, credentials: AWSCredentials) -> bool:
        """Validate that AWS credentials are working."""
        try:
            import boto3

            # Create STS client with the credentials
            sts_client = boto3.client(
                "sts",
                aws_access_key_id=credentials.access_key_id,
                aws_secret_access_key=credentials.secret_access_key,
                aws_session_token=credentials.session_token,
                region_name=credentials.region,
            )

            # Try to get caller identity
            response = sts_client.get_caller_identity()
            return "Account" in response

        except Exception:
            # Try AWS CLI as fallback
            return self._validate_credentials_via_cli(credentials)

    def _perform_sso_login(self, config: SSOConfig) -> None:
        """Perform SSO login using AWS CLI."""
        # Configure AWS SSO if not already configured
        self._configure_sso_profile(config)

        # Run AWS SSO login
        cmd = ["aws", "sso", "login", "--profile", "sso-session"]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            if result.returncode != 0:
                raise RuntimeError(f"AWS SSO login failed: {result.stderr}")

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"AWS SSO login failed: {e.stderr}") from e
        except FileNotFoundError as e:
            raise RuntimeError(
                "AWS CLI not found. Please install AWS CLI or add boto3 to dependencies"
            ) from e

    def _configure_sso_profile(self, config: SSOConfig) -> None:
        """Configure AWS SSO profile if not exists."""
        aws_config_dir = Path.home() / ".aws"
        aws_config_dir.mkdir(exist_ok=True)

        config_file = aws_config_dir / "config"

        # Check if SSO profile already exists
        profile_exists = False
        if config_file.exists():
            with open(config_file) as f:
                content = f.read()
                profile_exists = "[profile sso-session]" in content

        if not profile_exists:
            # Add SSO profile configuration
            sso_profile = f"""
[profile sso-session]
sso_start_url = {config.sso_start_url}
sso_region = {config.sso_region}
sso_registration_scopes = sso:account:access
"""

            with open(config_file, "a") as f:
                f.write(sso_profile)

    def _get_cached_token(self, config: SSOConfig) -> AWSSession | None:
        """Get cached SSO token if available."""
        # Look for cached tokens in AWS SSO cache directory
        for cache_file in self._cache_dir.glob("*.json"):
            try:
                with open(cache_file) as f:
                    cache_data = json.load(f)

                # Check if this is for our SSO start URL
                if cache_data.get("startUrl") != config.sso_start_url:
                    continue

                # Check if token is expired
                expires_at_str = cache_data.get("expiresAt")
                if not expires_at_str:
                    continue

                # Parse expiration time
                expires_at = datetime.fromisoformat(
                    expires_at_str.replace("Z", "+00:00")
                ).replace(tzinfo=None)

                if expires_at <= datetime.now():
                    continue

                # Token is valid
                return AWSSession(
                    access_token=cache_data["accessToken"],
                    expires_at=expires_at,
                    region=cache_data.get("region", config.sso_region),
                )

            except (json.JSONDecodeError, KeyError):
                continue

        return None

    def _get_credentials_via_cli(
        self,
        session: AWSSession,
        account: AWSAccount,
    ) -> AWSCredentials:
        """Get credentials using AWS CLI as fallback."""
        # This would require configuring a profile and using aws configure
        # For now, we'll raise an error suggesting boto3 installation
        raise RuntimeError(
            "boto3 is required for credential retrieval. "
            "Please run: uv add boto3 botocore"
        )

    def _validate_credentials_via_cli(self, credentials: AWSCredentials) -> bool:
        """Validate credentials using AWS CLI."""
        env = os.environ.copy()
        env.update(
            {
                "AWS_ACCESS_KEY_ID": credentials.access_key_id,
                "AWS_SECRET_ACCESS_KEY": credentials.secret_access_key,
                "AWS_SESSION_TOKEN": credentials.session_token,
                "AWS_DEFAULT_REGION": credentials.region,
            }
        )

        try:
            result = subprocess.run(
                ["aws", "sts", "get-caller-identity"],
                capture_output=True,
                text=True,
                env=env,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

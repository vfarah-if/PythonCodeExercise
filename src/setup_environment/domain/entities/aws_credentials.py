"""AWS Credentials entity for temporary SSO credentials."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class AWSCredentials:
    """Temporary AWS credentials from SSO.

    This entity represents temporary AWS credentials obtained through
    SSO authentication. These credentials have a limited lifespan and
    need to be refreshed periodically.

    Attributes:
        access_key_id: AWS access key ID
        secret_access_key: AWS secret access key
        session_token: Temporary session token
        expiration: When the credentials expire
        region: AWS region (default: eu-west-2)
    """

    access_key_id: str
    secret_access_key: str
    session_token: str
    expiration: datetime
    region: str = "eu-west-2"

    def __post_init__(self):
        """Validate credentials after initialisation."""
        if not self.access_key_id or not self.access_key_id.strip():
            raise ValueError("Access key ID cannot be empty")

        if not self.secret_access_key or not self.secret_access_key.strip():
            raise ValueError("Secret access key cannot be empty")

        if not self.session_token or not self.session_token.strip():
            raise ValueError("Session token cannot be empty")

        if not isinstance(self.expiration, datetime):
            raise TypeError("Expiration must be a datetime object")

        if not self.region or not self.region.strip():
            raise ValueError("Region cannot be empty")

        # Validate AWS key format
        if not self.access_key_id.startswith(("ASIA", "AKIA")):
            raise ValueError(
                f"Invalid access key ID format: {self.access_key_id}. "
                "AWS access keys should start with ASIA or AKIA"
            )

    def is_expired(self) -> bool:
        """Check if the credentials have expired.

        Returns:
            True if credentials are expired, False otherwise
        """
        return datetime.now() >= self.expiration

    def time_until_expiry(self) -> str:
        """Get human-readable time until expiry.

        Returns:
            String describing time until expiry
        """
        if self.is_expired():
            return "Expired"

        delta = self.expiration - datetime.now()
        hours = delta.total_seconds() / 3600

        if hours < 1:
            minutes = delta.total_seconds() / 60
            return f"{int(minutes)} minutes"
        elif hours < 24:
            return f"{int(hours)} hours"
        else:
            days = hours / 24
            return f"{int(days)} days"

    def to_env_vars(self, format: str = "bash") -> str:
        """Export credentials as environment variables.

        Args:
            format: Shell format ('bash', 'zsh', 'fish', 'powershell')

        Returns:
            String containing export commands for the specified shell
        """
        if format in ("bash", "zsh"):
            return f"""export AWS_ACCESS_KEY_ID="{self.access_key_id}"
export AWS_SECRET_ACCESS_KEY="{self.secret_access_key}"
export AWS_SESSION_TOKEN="{self.session_token}"
export AWS_DEFAULT_REGION="{self.region}"
"""
        elif format == "fish":
            return f"""set -x AWS_ACCESS_KEY_ID "{self.access_key_id}"
set -x AWS_SECRET_ACCESS_KEY "{self.secret_access_key}"
set -x AWS_SESSION_TOKEN "{self.session_token}"
set -x AWS_DEFAULT_REGION "{self.region}"
"""
        elif format == "powershell":
            return f"""$env:AWS_ACCESS_KEY_ID="{self.access_key_id}"
$env:AWS_SECRET_ACCESS_KEY="{self.secret_access_key}"
$env:AWS_SESSION_TOKEN="{self.session_token}"
$env:AWS_DEFAULT_REGION="{self.region}"
"""
        else:
            raise ValueError(f"Unsupported shell format: {format}")

    def to_aws_config_format(self, profile_name: str = "default") -> str:
        """Export credentials in AWS config file format.

        Args:
            profile_name: Name of the AWS profile

        Returns:
            String in AWS credentials file format
        """
        return f"""[{profile_name}]
aws_access_key_id = {self.access_key_id}
aws_secret_access_key = {self.secret_access_key}
aws_session_token = {self.session_token}
region = {self.region}
"""

    def mask_sensitive_data(self) -> dict:
        """Return credentials with masked sensitive data for logging.

        Returns:
            Dictionary with masked credentials
        """
        return {
            "access_key_id": f"{self.access_key_id[:8]}...{self.access_key_id[-4:]}",
            "secret_access_key": "***MASKED***",
            "session_token": f"{self.session_token[:20]}...{self.session_token[-10:]}",
            "expiration": self.expiration.isoformat(),
            "region": self.region,
        }

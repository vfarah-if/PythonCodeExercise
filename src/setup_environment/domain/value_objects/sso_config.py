"""SSO Configuration value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SSOConfig:
    """Immutable SSO configuration value object.

    This value object encapsulates SSO configuration settings
    required for AWS SSO authentication.

    Attributes:
        sso_start_url: The SSO portal URL
        sso_region: AWS region for SSO (default: eu-west-2)
        sso_account_id: Default AWS account ID (optional)
    """

    sso_start_url: str
    sso_region: str = "eu-west-2"
    sso_account_id: str | None = None

    def __post_init__(self):
        """Validate SSO configuration."""
        if not self.sso_start_url or not self.sso_start_url.strip():
            raise ValueError("SSO start URL cannot be empty")

        if not self.sso_start_url.startswith(("https://", "http://")):
            raise ValueError(
                f"Invalid SSO URL: {self.sso_start_url}. "
                "Must start with https:// or http://"
            )

        if not self.sso_region or not self.sso_region.strip():
            raise ValueError("SSO region cannot be empty")

        # Validate region format (basic check)
        if not self._is_valid_region(self.sso_region):
            raise ValueError(f"Invalid AWS region: {self.sso_region}")

        # Validate account ID if provided
        if self.sso_account_id and (
            not self.sso_account_id.isdigit() or len(self.sso_account_id) != 12
        ):
            raise ValueError(
                f"Invalid AWS account ID: {self.sso_account_id}. "
                "Must be a 12-digit number"
            )

    def _is_valid_region(self, region: str) -> bool:
        """Check if the region follows AWS region naming convention.

        Args:
            region: AWS region name

        Returns:
            True if region appears valid
        """
        # AWS regions typically follow the pattern: xx-xxxx-#
        # e.g., eu-west-2, us-east-1, ap-southeast-1
        parts = region.split("-")
        return (
            len(parts) >= 3
            and all(part.strip() for part in parts)
            and parts[-1].isdigit()
        )

    def to_dict(self) -> dict:
        """Convert to dictionary representation.

        Returns:
            Dictionary with SSO configuration
        """
        config = {
            "sso_start_url": self.sso_start_url,
            "sso_region": self.sso_region,
        }
        if self.sso_account_id:
            config["sso_account_id"] = self.sso_account_id
        return config

    @classmethod
    def from_env(cls, env_vars: dict) -> "SSOConfig":
        """Create SSOConfig from environment variables.

        Args:
            env_vars: Dictionary of environment variables

        Returns:
            SSOConfig instance
        """
        return cls(
            sso_start_url=env_vars.get("AWS_SSO_START_URL", ""),
            sso_region=env_vars.get("AWS_SSO_REGION", "eu-west-2"),
            sso_account_id=env_vars.get("AWS_SSO_ACCOUNT_ID"),
        )

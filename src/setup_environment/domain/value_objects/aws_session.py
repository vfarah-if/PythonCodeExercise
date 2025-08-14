"""AWS Session value object for SSO authentication tokens."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AWSSession:
    """Immutable AWS SSO session value object.

    This value object represents an authenticated SSO session
    with access tokens required for obtaining temporary credentials.

    Attributes:
        access_token: SSO access token
        expires_at: When the token expires
        region: AWS region for the session
    """

    access_token: str
    expires_at: datetime
    region: str = "eu-west-2"

    def __post_init__(self):
        """Validate session data."""
        if not self.access_token or not self.access_token.strip():
            raise ValueError("Access token cannot be empty")

        if not isinstance(self.expires_at, datetime):
            raise TypeError("expires_at must be a datetime object")

        if not self.region or not self.region.strip():
            raise ValueError("Region cannot be empty")

    def is_expired(self) -> bool:
        """Check if the session token has expired.

        Returns:
            True if session is expired, False otherwise
        """
        return datetime.now() >= self.expires_at

    def is_valid(self) -> bool:
        """Check if the session is valid (not expired).

        Returns:
            True if session is valid, False otherwise
        """
        return not self.is_expired()

    def time_remaining(self) -> str:
        """Get human-readable time remaining for the session.

        Returns:
            String describing time remaining
        """
        if self.is_expired():
            return "Expired"

        delta = self.expires_at - datetime.now()
        minutes = delta.total_seconds() / 60

        if minutes < 60:
            return f"{int(minutes)} minutes"
        else:
            hours = minutes / 60
            return f"{int(hours)} hours"

    def masked_token(self) -> str:
        """Get masked version of the access token for logging.

        Returns:
            Masked token string
        """
        if len(self.access_token) <= 20:
            return "***MASKED***"
        return f"{self.access_token[:10]}...{self.access_token[-10:]}"

    def to_dict(self) -> dict:
        """Convert to dictionary representation.

        Returns:
            Dictionary with session data (token masked)
        """
        return {
            "access_token": self.masked_token(),
            "expires_at": self.expires_at.isoformat(),
            "region": self.region,
            "is_valid": self.is_valid(),
        }

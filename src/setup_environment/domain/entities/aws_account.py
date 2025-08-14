"""AWS Account entity for SSO authentication."""

from dataclasses import dataclass


@dataclass
class AWSAccount:
    """Represents an AWS account accessible via SSO.

    This entity encapsulates the core business logic for AWS accounts
    that can be accessed through Single Sign-On (SSO).

    Attributes:
        name: Human-readable name for the account (e.g., 'dev', 'prod')
        account_id: AWS account ID (12-digit number as string)
        email: Email address associated with the account
        role: IAM role to assume in the account (default: 'Engineer')
        is_default: Whether this is the default account for selection
    """

    name: str
    account_id: str
    email: str
    role: str = "Engineer"
    is_default: bool = False

    def __post_init__(self):
        """Validate account data after initialisation."""
        if not self.name or not self.name.strip():
            raise ValueError("Account name cannot be empty")

        if not self.account_id or not self.account_id.strip():
            raise ValueError("Account ID cannot be empty")

        # Validate account ID format (should be 12 digits)
        if not self.account_id.isdigit() or len(self.account_id) != 12:
            raise ValueError(
                f"Invalid AWS account ID: {self.account_id}. Must be a 12-digit number"
            )

        if not self.email or not self.email.strip():
            raise ValueError("Email cannot be empty")

        if "@" not in self.email:
            raise ValueError(f"Invalid email format: {self.email}")

        if not self.role or not self.role.strip():
            raise ValueError("Role cannot be empty")

    def __str__(self) -> str:
        """String representation of the account."""
        default_marker = " [default]" if self.is_default else ""
        return f"{self.name} ({self.account_id}){default_marker}"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"AWSAccount(name='{self.name}', account_id='{self.account_id}', "
            f"email='{self.email}', role='{self.role}', is_default={self.is_default})"
        )

    def to_dict(self) -> dict:
        """Convert account to dictionary representation."""
        return {
            "name": self.name,
            "account_id": self.account_id,
            "email": self.email,
            "role": self.role,
            "is_default": self.is_default,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AWSAccount":
        """Create an AWSAccount from a dictionary.

        Args:
            data: Dictionary containing account data

        Returns:
            AWSAccount instance
        """
        return cls(
            name=data.get("name", ""),
            account_id=data.get("account_id", ""),
            email=data.get("email", ""),
            role=data.get("role", "Engineer"),
            is_default=data.get("is_default", False) or data.get("default", False),
        )

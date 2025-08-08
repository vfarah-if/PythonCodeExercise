"""Personal Access Token value object."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PersonalAccessToken:
    """Represents a validated GitHub Personal Access Token."""

    value: str

    def __post_init__(self) -> None:
        """Validate the token format after initialisation."""
        if not self.value:
            raise ValueError("Personal access token cannot be empty")
        
        if not self._is_valid_format():
            raise ValueError(
                "Invalid token format. Expected format: ghp_* or github_pat_*"
            )

    def _is_valid_format(self) -> bool:
        """Check if token has valid GitHub PAT format."""
        classic_pattern = r"^ghp_[a-zA-Z0-9]{36}$"
        fine_grained_pattern = r"^github_pat_[a-zA-Z0-9_]{82}$"
        
        return (
            re.match(classic_pattern, self.value) is not None or
            re.match(fine_grained_pattern, self.value) is not None
        )

    def __str__(self) -> str:
        """Return masked representation for security."""
        if len(self.value) <= 8:
            return "***"
        return f"{self.value[:4]}...{self.value[-4:]}"

    def __repr__(self) -> str:
        """Return masked representation for security."""
        return f"PersonalAccessToken({str(self)})"
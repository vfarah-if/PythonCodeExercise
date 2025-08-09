"""Software entity for managing development tools."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Software:
    """Represents a software package to be installed."""

    name: str
    description: str
    check_command: str
    install_command: str
    required: bool = False
    custom_install: bool = False

    def __post_init__(self):
        """Validate software configuration."""
        if not self.name:
            raise ValueError("Software name cannot be empty")
        if not self.check_command:
            raise ValueError(f"Check command required for {self.name}")
        if not self.install_command:
            raise ValueError(f"Install command required for {self.name}")

    def __str__(self) -> str:
        """String representation of software."""
        return self.name

    @property
    def display_name(self) -> str:
        """Get display name with required indicator."""
        if self.required:
            return f"{self.name} (required)"
        return self.name

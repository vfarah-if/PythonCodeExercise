"""Development folder path value object."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DevFolderPath:
    """Represents a validated development folder path."""

    value: Path

    def __post_init__(self) -> None:
        """Validate the path after initialisation."""
        if not isinstance(self.value, Path):
            object.__setattr__(self, "value", Path(self.value))

        # Check for empty path
        if str(self.value) == ".":
            # Path("") or Path(".") both resolve to "."
            raise ValueError("Development folder path cannot be empty")

        if not self.value.exists():
            raise ValueError(f"Development folder does not exist: {self.value}")

        if not self.value.is_dir():
            raise ValueError(f"Path is not a directory: {self.value}")

        if not self.value.is_absolute():
            object.__setattr__(self, "value", self.value.resolve())

    def __str__(self) -> str:
        """Return string representation of the path."""
        return str(self.value)

    def create_subdirectory(self, *parts: str) -> Path:
        """Create a subdirectory under the development folder."""
        subdirectory = self.value.joinpath(*parts)
        subdirectory.mkdir(parents=True, exist_ok=True)
        return subdirectory

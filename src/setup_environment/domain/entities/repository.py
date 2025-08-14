"""Repository entity."""

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class Repository:
    """Represents a Git repository."""

    url: str
    organisation: str
    name: str

    @classmethod
    def from_url(cls, url: str) -> "Repository":
        """Create a Repository from a Git URL."""
        if not url:
            raise ValueError("Repository URL cannot be empty")

        # Support both HTTPS and SSH URLs
        if url.startswith("git@"):
            # SSH format: git@github.com:org/repo.git
            match = re.match(r"git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$", url)
            if not match:
                raise ValueError(f"Invalid SSH repository URL: {url}")
            organisation, name = match.groups()
        else:
            # HTTPS format: https://github.com/org/repo.git
            parsed = urlparse(url)
            if parsed.hostname != "github.com":
                raise ValueError(f"Only GitHub repositories are supported: {url}")

            path_parts = parsed.path.strip("/").split("/")
            if len(path_parts) < 2:
                raise ValueError(f"Invalid repository URL format: {url}")

            organisation = path_parts[0]
            name = path_parts[1].removesuffix(".git")

        if not organisation or not name:
            raise ValueError(f"Could not extract organisation and name from URL: {url}")

        return cls(url=url, organisation=organisation, name=name)

    def calculate_target_path(self, base_path: Path) -> Path:
        """Calculate the target path for cloning this repository."""
        return base_path / self.organisation / self.name

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.organisation}/{self.name}"

    def __eq__(self, other: object) -> bool:
        """Check equality based on organisation and name."""
        if not isinstance(other, Repository):
            return False
        return self.organisation == other.organisation and self.name == other.name

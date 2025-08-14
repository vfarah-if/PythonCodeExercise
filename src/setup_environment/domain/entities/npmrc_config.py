"""npmrc Configuration entity."""

from dataclasses import dataclass
from pathlib import Path

from src.setup_environment.domain.value_objects import PersonalAccessToken


@dataclass(frozen=True)
class NPMRCConfiguration:
    """Represents npmrc configuration settings."""

    token: PersonalAccessToken
    registry_url: str = "https://npm.pkg.github.com"
    organisation: str = "@webuild-ai"
    package_lock: bool = True
    legacy_peer_deps: bool = True

    def generate_config_content(self) -> str:
        """Generate the .npmrc file content."""
        lines = []

        if self.package_lock:
            lines.append("package-lock=true")

        if self.legacy_peer_deps:
            lines.append("legacy-peer-deps=true")

        # Add authentication token
        registry_host = self.registry_url.replace("https://", "").replace("http://", "")
        lines.append(f"//{registry_host}/:_authToken={self.token.value}")

        # Add organisation registry
        lines.append(f"{self.organisation}:registry={self.registry_url}")

        return "\n".join(lines)

    def write_to_file(self, path: Path) -> None:
        """Write configuration to a file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.generate_config_content())

    @classmethod
    def exists_at_path(cls, path: Path) -> bool:
        """Check if npmrc configuration exists at the given path."""
        if not path.exists():
            return False

        content = path.read_text()
        return "_authToken" in content and "npm.pkg.github.com" in content

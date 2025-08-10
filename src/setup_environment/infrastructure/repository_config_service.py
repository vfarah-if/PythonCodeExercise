"""Repository configuration service for loading repository definitions from YAML."""

from pathlib import Path
from typing import Any

import yaml

from src.setup_environment.application.interfaces.repository_config_service import (
    RepositoryConfigurationService,
)
from src.setup_environment.domain.entities import Repository


class YamlRepositoryConfigService(RepositoryConfigurationService):
    """Service for loading and managing repository configurations from YAML files."""

    def __init__(self, config_dir: Path | None = None):
        """Initialize with optional config directory override.

        Args:
            config_dir: Optional directory containing repositories.yaml.
                       Defaults to the package config directory.
        """
        if config_dir is None:
            # Default to the package config directory
            self._config_dir = Path(__file__).parent.parent / "config"
        else:
            self._config_dir = config_dir

    def load_repositories(self, config_path: str | None = None) -> list[Repository]:
        """Load repository configurations from YAML file.

        Args:
            config_path: Optional path to custom repositories.yaml file.
                        If not provided, uses default location.

        Returns:
            List of Repository entities.

        Raises:
            FileNotFoundError: If configuration file doesn't exist.
            ValueError: If configuration is invalid.
        """
        if config_path:
            config_file = Path(config_path)
        else:
            config_file = self._config_dir / "repositories.yaml"

        if not config_file.exists():
            raise FileNotFoundError(
                f"Repository configuration not found: {config_file}"
            )

        try:
            with open(config_file) as f:
                config_data = yaml.safe_load(f)

            if not config_data or "repositories" not in config_data:
                raise ValueError(
                    "Invalid repository configuration: missing 'repositories' key"
                )

            repositories = []
            for item in config_data["repositories"]:
                repo = self._parse_repository_item(item)
                repositories.append(repo)

            return repositories

        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing repository configuration: {e}") from e

    def _parse_repository_item(self, item: dict[str, Any]) -> Repository:
        """Parse a single repository item from configuration.

        Args:
            item: Dictionary containing repository configuration.

        Returns:
            Repository entity.

        Raises:
            ValueError: If required fields are missing.
        """
        required_fields = ["url"]

        for field in required_fields:
            if field not in item:
                raise ValueError(
                    f"Missing required field '{field}' in repository configuration"
                )

        # Create Repository from URL
        repo = Repository.from_url(item["url"])

        # Note: Repository metadata (name, description) from YAML is currently
        # not used but could be extended in the future

        return repo

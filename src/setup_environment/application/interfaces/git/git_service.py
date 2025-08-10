"""Git service interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from src.setup_environment.domain.entities import Repository


class CloneStatus(Enum):
    """Status of a clone operation."""

    SUCCESS = "success"
    ALREADY_EXISTS = "already_exists"
    FAILED = "failed"


@dataclass
class CloneResult:
    """Result of a repository clone operation."""

    repository: Repository
    status: CloneStatus
    path: Path | None = None
    error_message: str | None = None

    @property
    def is_success(self) -> bool:
        """Check if the clone was successful or already existed."""
        return self.status in (CloneStatus.SUCCESS, CloneStatus.ALREADY_EXISTS)


class GitService(ABC):
    """Interface for Git operations."""

    @abstractmethod
    def clone_repository(
        self, repository: Repository, target_path: Path
    ) -> CloneResult:
        """Clone a repository to the specified path."""
        pass

    @abstractmethod
    def repository_exists(self, path: Path) -> bool:
        """Check if a valid Git repository exists at the given path."""
        pass

    @abstractmethod
    def is_git_installed(self) -> bool:
        """Check if Git is installed and available."""
        pass

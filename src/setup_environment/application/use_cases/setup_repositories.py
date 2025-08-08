"""Use case for setting up Git repositories."""

from dataclasses import dataclass

from src.setup_environment.application.interfaces import CloneResult, GitService
from src.setup_environment.application.interfaces.git_service import CloneStatus
from src.setup_environment.domain.entities import Repository
from src.setup_environment.domain.value_objects import DevFolderPath


@dataclass
class SetupResult:
    """Result of the repository setup process."""

    successful: list[CloneResult]
    skipped: list[CloneResult]
    failed: list[CloneResult]

    @property
    def total_count(self) -> int:
        """Get total number of repositories processed."""
        return len(self.successful) + len(self.skipped) + len(self.failed)

    @property
    def success_count(self) -> int:
        """Get number of successfully cloned repositories."""
        return len(self.successful)

    @property
    def skip_count(self) -> int:
        """Get number of skipped repositories."""
        return len(self.skipped)

    @property
    def failure_count(self) -> int:
        """Get number of failed repositories."""
        return len(self.failed)

    @property
    def has_failures(self) -> bool:
        """Check if any repositories failed to clone."""
        return len(self.failed) > 0


class SetupRepositoriesUseCase:
    """Use case for setting up multiple Git repositories."""

    def __init__(self, git_service: GitService):
        """Initialise with a Git service."""
        self._git_service = git_service

    def execute(
        self, repositories: list[Repository], dev_folder: DevFolderPath
    ) -> SetupResult:
        """Set up the specified repositories in the development folder."""
        if not self._git_service.is_git_installed():
            raise RuntimeError("Git is not installed or not available in PATH")

        successful = []
        skipped = []
        failed = []

        for repository in repositories:
            target_path = repository.calculate_target_path(dev_folder.value)

            # Check if repository already exists
            if self._git_service.repository_exists(target_path):
                result = CloneResult(
                    repository=repository,
                    status=CloneStatus.ALREADY_EXISTS,
                    path=target_path,
                )
                skipped.append(result)
                continue

            # Clone the repository
            result = self._git_service.clone_repository(repository, target_path)

            if result.is_success:
                if result.status == CloneStatus.SUCCESS:
                    successful.append(result)
                else:
                    skipped.append(result)
            else:
                failed.append(result)

        return SetupResult(
            successful=successful,
            skipped=skipped,
            failed=failed,
        )

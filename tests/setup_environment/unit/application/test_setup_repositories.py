"""Unit tests for SetupRepositoriesUseCase."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from src.setup_environment.application.interfaces import CloneResult, GitService
from src.setup_environment.application.interfaces.git.git_service import CloneStatus
from src.setup_environment.application.use_cases import SetupRepositoriesUseCase
from src.setup_environment.domain.entities import Repository
from src.setup_environment.domain.value_objects import DevFolderPath


class TestSetupResult:
    """Test suite for SetupResult class."""

    def test_setup_result_counts(self):
        """Test that SetupResult correctly counts results."""
        from src.setup_environment.application.use_cases.setup_repositories import (
            SetupResult,
        )

        repo1 = Repository.from_url("https://github.com/org/repo1.git")
        repo2 = Repository.from_url("https://github.com/org/repo2.git")
        repo3 = Repository.from_url("https://github.com/org/repo3.git")

        successful = [CloneResult(repo1, CloneStatus.SUCCESS, Path("/dev/repo1"))]
        skipped = [CloneResult(repo2, CloneStatus.ALREADY_EXISTS, Path("/dev/repo2"))]
        failed = [CloneResult(repo3, CloneStatus.FAILED, error_message="Access denied")]

        result = SetupResult(successful=successful, skipped=skipped, failed=failed)

        assert result.total_count == 3
        assert result.success_count == 1
        assert result.skip_count == 1
        assert result.failure_count == 1
        assert result.has_failures is True

    def test_setup_result_no_failures(self):
        """Test SetupResult with no failures."""
        from src.setup_environment.application.use_cases.setup_repositories import (
            SetupResult,
        )

        result = SetupResult(successful=[], skipped=[], failed=[])
        assert result.has_failures is False


class TestSetupRepositoriesUseCase:
    """Test suite for SetupRepositoriesUseCase."""

    @pytest.fixture
    def mock_git_service(self):
        """Create a mock Git service."""
        return Mock(spec=GitService)

    @pytest.fixture
    def temp_dev_folder(self):
        """Create a temporary development folder."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield DevFolderPath(temp_dir)

    @pytest.fixture
    def sample_repositories(self):
        """Create sample repositories for testing."""
        return [
            Repository.from_url("https://github.com/webuild-ai/repo1.git"),
            Repository.from_url("https://github.com/webuild-ai/repo2.git"),
            Repository.from_url("https://github.com/other-org/repo3.git"),
        ]

    def test_execute_with_git_not_installed(self, mock_git_service, temp_dev_folder):
        """Test that RuntimeError is raised when Git is not installed."""
        mock_git_service.is_git_installed.return_value = False

        use_case = SetupRepositoriesUseCase(mock_git_service)

        with pytest.raises(RuntimeError, match="Git is not installed"):
            use_case.execute([], temp_dev_folder)

    def test_execute_all_successful(
        self, mock_git_service, temp_dev_folder, sample_repositories
    ):
        """Test successful cloning of all repositories."""
        mock_git_service.is_git_installed.return_value = True
        mock_git_service.repository_exists.return_value = False

        def mock_clone(repo, path):
            return CloneResult(
                repository=repo,
                status=CloneStatus.SUCCESS,
                path=path,
            )

        mock_git_service.clone_repository.side_effect = mock_clone

        use_case = SetupRepositoriesUseCase(mock_git_service)
        result = use_case.execute(sample_repositories, temp_dev_folder)

        assert result.success_count == 3
        assert result.skip_count == 0
        assert result.failure_count == 0
        assert not result.has_failures
        assert mock_git_service.clone_repository.call_count == 3

    def test_execute_skip_existing_repositories(
        self, mock_git_service, temp_dev_folder, sample_repositories
    ):
        """Test skipping repositories that already exist."""
        mock_git_service.is_git_installed.return_value = True

        # First two repos exist, third doesn't
        mock_git_service.repository_exists.side_effect = [True, True, False]

        mock_git_service.clone_repository.return_value = CloneResult(
            repository=sample_repositories[2],
            status=CloneStatus.SUCCESS,
            path=Path("/dev/repo3"),
        )

        use_case = SetupRepositoriesUseCase(mock_git_service)
        result = use_case.execute(sample_repositories, temp_dev_folder)

        assert result.success_count == 1
        assert result.skip_count == 2
        assert result.failure_count == 0
        assert not result.has_failures
        # Only called once for the non-existing repo
        assert mock_git_service.clone_repository.call_count == 1

    def test_execute_with_clone_failures(
        self, mock_git_service, temp_dev_folder, sample_repositories
    ):
        """Test handling of clone failures."""
        mock_git_service.is_git_installed.return_value = True
        mock_git_service.repository_exists.return_value = False

        # First succeeds, second fails, third succeeds
        mock_git_service.clone_repository.side_effect = [
            CloneResult(
                repository=sample_repositories[0],
                status=CloneStatus.SUCCESS,
                path=Path("/dev/repo1"),
            ),
            CloneResult(
                repository=sample_repositories[1],
                status=CloneStatus.FAILED,
                error_message="Authentication failed",
            ),
            CloneResult(
                repository=sample_repositories[2],
                status=CloneStatus.SUCCESS,
                path=Path("/dev/repo3"),
            ),
        ]

        use_case = SetupRepositoriesUseCase(mock_git_service)
        result = use_case.execute(sample_repositories, temp_dev_folder)

        assert result.success_count == 2
        assert result.skip_count == 0
        assert result.failure_count == 1
        assert result.has_failures
        assert result.failed[0].error_message == "Authentication failed"

    def test_execute_mixed_results(
        self, mock_git_service, temp_dev_folder, sample_repositories
    ):
        """Test with a mix of successful, skipped, and failed repositories."""
        mock_git_service.is_git_installed.return_value = True

        # First exists, others don't
        mock_git_service.repository_exists.side_effect = [True, False, False]

        # Second succeeds, third fails
        mock_git_service.clone_repository.side_effect = [
            CloneResult(
                repository=sample_repositories[1],
                status=CloneStatus.SUCCESS,
                path=Path("/dev/repo2"),
            ),
            CloneResult(
                repository=sample_repositories[2],
                status=CloneStatus.FAILED,
                error_message="Network error",
            ),
        ]

        use_case = SetupRepositoriesUseCase(mock_git_service)
        result = use_case.execute(sample_repositories, temp_dev_folder)

        assert result.success_count == 1
        assert result.skip_count == 1
        assert result.failure_count == 1
        assert result.total_count == 3
        assert result.has_failures

    def test_execute_empty_repository_list(self, mock_git_service, temp_dev_folder):
        """Test with empty repository list."""
        mock_git_service.is_git_installed.return_value = True

        use_case = SetupRepositoriesUseCase(mock_git_service)
        result = use_case.execute([], temp_dev_folder)

        assert result.total_count == 0
        assert result.success_count == 0
        assert result.skip_count == 0
        assert result.failure_count == 0
        assert not result.has_failures
        mock_git_service.clone_repository.assert_not_called()

    def test_execute_calls_correct_target_paths(
        self, mock_git_service, temp_dev_folder, sample_repositories
    ):
        """Test that repositories are cloned to correct target paths."""
        mock_git_service.is_git_installed.return_value = True
        mock_git_service.repository_exists.return_value = False

        called_paths = []

        def mock_clone(repo, path):
            called_paths.append((repo.organisation, repo.name, path))
            return CloneResult(repository=repo, status=CloneStatus.SUCCESS, path=path)

        mock_git_service.clone_repository.side_effect = mock_clone

        use_case = SetupRepositoriesUseCase(mock_git_service)
        use_case.execute(sample_repositories, temp_dev_folder)

        # Verify correct paths were used
        expected_base = Path(temp_dev_folder.value)
        assert called_paths[0][2] == expected_base / "webuild-ai" / "repo1"
        assert called_paths[1][2] == expected_base / "webuild-ai" / "repo2"
        assert called_paths[2][2] == expected_base / "other-org" / "repo3"

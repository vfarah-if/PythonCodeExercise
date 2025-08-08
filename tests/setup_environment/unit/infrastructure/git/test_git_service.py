"""Unit tests for GitPythonService."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.setup_environment.application.interfaces.git_service import CloneStatus
from src.setup_environment.domain.entities import Repository
from src.setup_environment.infrastructure.git import GitPythonService


class TestGitPythonService:
    """Test suite for GitPythonService."""

    @pytest.fixture
    def git_service(self):
        """Create a GitPythonService instance."""
        return GitPythonService()

    @pytest.fixture
    def sample_repository(self):
        """Create a sample repository."""
        return Repository.from_url("https://github.com/webuild-ai/test-repo.git")

    def test_is_git_installed_returns_true_when_git_present(self, git_service):
        """Test that is_git_installed returns True when Git is available."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            result = git_service.is_git_installed()

            assert result is True
            mock_run.assert_called_once_with(
                ["git", "--version"],
                capture_output=True,
                check=False,
            )

    def test_is_git_installed_returns_false_when_git_missing(self, git_service):
        """Test that is_git_installed returns False when Git is not available."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()

            result = git_service.is_git_installed()

            assert result is False

    def test_is_git_installed_returns_false_on_error(self, git_service):
        """Test that is_git_installed returns False on command error."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=1)

            result = git_service.is_git_installed()

            assert result is False

    def test_repository_exists_returns_true_for_valid_repo(self, git_service):
        """Test that repository_exists returns True for valid Git repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            git_dir = repo_path / ".git"
            git_dir.mkdir()

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=0)

                result = git_service.repository_exists(repo_path)

                assert result is True
                mock_run.assert_called_once_with(
                    ["git", "rev-parse", "--git-dir"],
                    cwd=str(repo_path),
                    capture_output=True,
                    check=False,
                )

    def test_repository_exists_returns_false_for_non_existent_path(self, git_service):
        """Test that repository_exists returns False for non-existent path."""
        non_existent = Path("/does/not/exist")

        result = git_service.repository_exists(non_existent)

        assert result is False

    def test_repository_exists_returns_false_for_non_git_directory(self, git_service):
        """Test that repository_exists returns False for directory without .git."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            result = git_service.repository_exists(repo_path)

            assert result is False

    def test_repository_exists_returns_false_when_git_command_fails(self, git_service):
        """Test that repository_exists returns False when git command fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            git_dir = repo_path / ".git"
            git_dir.mkdir()

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=1)

                result = git_service.repository_exists(repo_path)

                assert result is False

    def test_clone_repository_success(self, git_service, sample_repository):
        """Test successful repository cloning."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "test-repo"

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr="", stdout="")

                result = git_service.clone_repository(sample_repository, target_path)

                assert result.status == CloneStatus.SUCCESS
                assert result.repository == sample_repository
                assert result.path == target_path
                assert result.error_message is None

                mock_run.assert_called_once_with(
                    ["git", "clone", sample_repository.url, str(target_path)],
                    capture_output=True,
                    text=True,
                    check=False,
                )

    def test_clone_repository_creates_parent_directory(
        self, git_service, sample_repository
    ):
        """Test that clone_repository creates parent directory if needed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "org" / "repo"

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr="", stdout="")

                result = git_service.clone_repository(sample_repository, target_path)

                assert result.status == CloneStatus.SUCCESS
                # Parent directory should be created
                assert target_path.parent.exists()

    def test_clone_repository_failure_with_error_message(
        self, git_service, sample_repository
    ):
        """Test repository cloning failure with error message."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "test-repo"

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(
                    returncode=128,
                    stderr="fatal: repository not found",
                    stdout="",
                )

                result = git_service.clone_repository(sample_repository, target_path)

                assert result.status == CloneStatus.FAILED
                assert result.repository == sample_repository
                assert result.path is None
                assert "repository not found" in result.error_message

    def test_clone_repository_git_not_found(self, git_service, sample_repository):
        """Test clone_repository when Git is not installed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "test-repo"

            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = FileNotFoundError()

                result = git_service.clone_repository(sample_repository, target_path)

                assert result.status == CloneStatus.FAILED
                assert "Git command not found" in result.error_message

    def test_clone_repository_unexpected_error(self, git_service, sample_repository):
        """Test clone_repository with unexpected error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "test-repo"

            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = Exception("Unexpected error")

                result = git_service.clone_repository(sample_repository, target_path)

                assert result.status == CloneStatus.FAILED
                assert "Unexpected error" in result.error_message

    def test_clone_repository_uses_stdout_if_stderr_empty(
        self, git_service, sample_repository
    ):
        """Test that stdout is used for error message if stderr is empty."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "test-repo"

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(
                    returncode=1,
                    stderr="",
                    stdout="Error: Permission denied",
                )

                result = git_service.clone_repository(sample_repository, target_path)

                assert result.status == CloneStatus.FAILED
                assert "Permission denied" in result.error_message

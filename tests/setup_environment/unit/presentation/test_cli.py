"""Unit tests for CLI."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from src.setup_environment.application.interfaces.git_service import CloneStatus
from src.setup_environment.application.use_cases.configure_npmrc import (
    ConfigurationStatus,
)
from src.setup_environment.presentation.cli import (
    get_repositories_from_environment,
    setup_environment,
)


class TestGetRepositoriesFromEnvironment:
    """Test suite for get_repositories_from_environment function."""

    def test_get_repositories_from_environment_success(self):
        """Test getting repositories from environment variables."""
        env_vars = {
            "GIT_REPO_1": "https://github.com/webuild-ai/repo1.git",
            "GIT_REPO_2": "https://github.com/webuild-ai/repo2.git",
            "GIT_REPO_TEST": "git@github.com:org/test.git",
            "OTHER_VAR": "not a repo",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            repositories = get_repositories_from_environment()

        assert len(repositories) == 3
        assert repositories[0].organisation == "webuild-ai"
        assert repositories[0].name == "repo1"
        assert repositories[1].organisation == "webuild-ai"
        assert repositories[1].name == "repo2"
        assert repositories[2].organisation == "org"
        assert repositories[2].name == "test"

    def test_get_repositories_empty_environment(self):
        """Test with no GIT_REPO_* environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            repositories = get_repositories_from_environment()

        assert repositories == []

    def test_get_repositories_invalid_urls_skipped(self):
        """Test that invalid repository URLs are skipped."""
        env_vars = {
            "GIT_REPO_1": "https://github.com/valid/repo.git",
            "GIT_REPO_2": "invalid-url",
            "GIT_REPO_3": "https://gitlab.com/not/supported.git",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            repositories = get_repositories_from_environment()

        # Only the valid GitHub repo should be included
        assert len(repositories) == 1
        assert repositories[0].name == "repo"

    def test_get_repositories_empty_values_skipped(self):
        """Test that empty environment variable values are skipped."""
        env_vars = {
            "GIT_REPO_1": "https://github.com/valid/repo.git",
            "GIT_REPO_2": "",
            "GIT_REPO_3": "   ",  # Whitespace only
        }

        with patch.dict(os.environ, env_vars, clear=True):
            repositories = get_repositories_from_environment()

        assert len(repositories) == 1
        assert repositories[0].name == "repo"


class TestSetupEnvironmentCLI:
    """Test suite for setup_environment CLI command."""

    @pytest.fixture
    def runner(self):
        """Create a Click CLI runner."""
        return CliRunner()

    @pytest.fixture
    def temp_dev_folder(self):
        """Create a temporary development folder."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def mock_environment(self):
        """Mock environment with test repositories."""
        return {
            "GIT_REPO_1": "https://github.com/webuild-ai/repo1.git",
            "GIT_REPO_2": "https://github.com/webuild-ai/repo2.git",
        }

    def test_cli_requires_dev_folder_argument(self, runner):
        """Test that CLI requires --dev-folder argument."""
        result = runner.invoke(setup_environment, [])

        assert result.exit_code != 0
        assert "--dev-folder" in result.output

    def test_cli_validates_dev_folder_exists(self, runner):
        """Test that CLI validates dev folder exists."""
        result = runner.invoke(setup_environment, ["--dev-folder", "/does/not/exist"])

        assert result.exit_code != 0
        assert "does not exist" in result.output.lower()

    @patch("src.setup_environment.presentation.cli.SetupRepositoriesUseCase")
    @patch("src.setup_environment.presentation.cli.ConfigureNPMRCUseCase")
    @patch("src.setup_environment.presentation.cli.GitPythonService")
    @patch("src.setup_environment.presentation.cli.NPMRCFileService")
    def test_cli_successful_execution(
        self,
        mock_npm_service,
        mock_git_service,
        mock_npm_use_case,
        mock_setup_use_case,
        runner,
        temp_dev_folder,
        mock_environment,
    ):
        """Test successful CLI execution."""
        # Mock setup results
        from src.setup_environment.application.use_cases.configure_npmrc import (
            ConfigureResult,
        )
        from src.setup_environment.application.use_cases.setup_repositories import (
            SetupResult,
        )

        mock_setup_result = SetupResult(successful=[], skipped=[], failed=[])
        mock_setup_use_case.return_value.execute.return_value = mock_setup_result

        mock_npm_result = ConfigureResult(
            status=ConfigurationStatus.CREATED,
            message="Configuration created at ~/.npmrc",
        )
        mock_npm_use_case.return_value.execute.return_value = mock_npm_result

        with patch.dict(os.environ, mock_environment):
            result = runner.invoke(
                setup_environment, ["--dev-folder", temp_dev_folder, "--skip-software"]
            )

        assert result.exit_code == 0
        assert "Setup completed successfully" in result.output
        mock_setup_use_case.return_value.execute.assert_called_once()
        mock_npm_use_case.return_value.execute.assert_called_once()

    @patch("src.setup_environment.presentation.cli.SetupRepositoriesUseCase")
    def test_cli_exits_with_error_on_setup_failures(
        self, mock_setup_use_case, runner, temp_dev_folder, mock_environment
    ):
        """Test CLI exits with error when repositories fail to clone."""
        from src.setup_environment.application.interfaces import CloneResult
        from src.setup_environment.application.use_cases.setup_repositories import (
            SetupResult,
        )
        from src.setup_environment.domain.entities import Repository

        failed_repo = Repository.from_url("https://github.com/org/failed.git")
        failed_result = CloneResult(
            repository=failed_repo,
            status=CloneStatus.FAILED,
            error_message="Access denied",
        )

        mock_setup_result = SetupResult(
            successful=[], skipped=[], failed=[failed_result]
        )
        mock_setup_use_case.return_value.execute.return_value = mock_setup_result

        with patch.dict(os.environ, mock_environment):
            result = runner.invoke(
                setup_environment,
                ["--dev-folder", temp_dev_folder, "--skip-npmrc", "--skip-software"],
            )

        assert result.exit_code == 1
        assert "Setup completed with" in result.output
        assert "failures" in result.output

    def test_cli_exits_when_no_repositories_found(self, runner, temp_dev_folder):
        """Test CLI exits when no repositories are found."""
        with runner.isolated_filesystem():
            # Mock load_repositories_from_config to return empty list
            with patch(
                "src.setup_environment.presentation.cli.load_repositories_from_config"
            ) as mock_load:
                mock_load.return_value = []
                result = runner.invoke(
                    setup_environment,
                    ["--dev-folder", temp_dev_folder, "--skip-software"],
                )

        assert result.exit_code == 1
        assert "No repositories found" in result.output

    @patch("src.setup_environment.presentation.cli.SetupRepositoriesUseCase")
    def test_cli_skip_npm_flag(
        self, mock_setup_use_case, runner, temp_dev_folder, mock_environment
    ):
        """Test --skip-npmrc flag skips npmrc configuration."""
        from src.setup_environment.application.use_cases.setup_repositories import (
            SetupResult,
        )

        mock_setup_result = SetupResult(successful=[], skipped=[], failed=[])
        mock_setup_use_case.return_value.execute.return_value = mock_setup_result

        with patch.dict(os.environ, mock_environment):
            result = runner.invoke(
                setup_environment,
                ["--dev-folder", temp_dev_folder, "--skip-npmrc", "--skip-software"],
            )

        assert result.exit_code == 0
        assert "Skipped npmrc configuration" in result.output

    @patch("src.setup_environment.presentation.cli.DevFolderPath")
    def test_cli_handles_dev_folder_validation_error(
        self, mock_dev_folder_path, runner, temp_dev_folder
    ):
        """Test CLI handles development folder validation errors."""
        mock_dev_folder_path.side_effect = ValueError("Invalid path")

        result = runner.invoke(setup_environment, ["--dev-folder", temp_dev_folder])

        assert result.exit_code == 1
        assert "Error: Invalid path" in result.output

    @patch("src.setup_environment.presentation.cli.SetupRepositoriesUseCase")
    def test_cli_handles_runtime_errors(
        self, mock_setup_use_case, runner, temp_dev_folder, mock_environment
    ):
        """Test CLI handles runtime errors (e.g., Git not installed)."""
        mock_setup_use_case.return_value.execute.side_effect = RuntimeError(
            "Git is not installed"
        )

        with patch.dict(os.environ, mock_environment):
            result = runner.invoke(
                setup_environment, ["--dev-folder", temp_dev_folder, "--skip-software"]
            )

        assert result.exit_code == 1
        assert "Error: Git is not installed" in result.output

    def test_cli_help_shows_usage_information(self, runner):
        """Test that CLI help shows proper usage information."""
        result = runner.invoke(setup_environment, ["--help"])

        assert result.exit_code == 0
        assert "Configure development environment" in result.output
        assert "--dev-folder" in result.output
        assert "--skip-npmrc" in result.output
        assert "--skip-software" in result.output


# Test classes for removed functions have been deleted
# The functions load_environment_config and generate_env_template
# have been replaced with YAML-based configuration


class TestSetupEnvironmentWithRepositoryConfig:
    """Test suite for setup_environment CLI with YAML repository configuration."""

    @pytest.fixture
    def runner(self):
        """Create a Click CLI runner."""
        return CliRunner()

    @pytest.fixture
    def temp_dev_folder(self):
        """Create a temporary development folder."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def test_dev_folder_required(self, runner):
        """Test that --dev-folder is required for setup operations."""
        result = runner.invoke(setup_environment, ["--dry-run"])

        assert result.exit_code == 1
        assert "--dev-folder is required" in result.output

    def test_custom_repository_config_option(self, runner, temp_dev_folder):
        """Test --repositories-config option with custom file."""
        with runner.isolated_filesystem():
            # Create custom repository config
            import yaml

            custom_config = Path("custom-repos.yaml")
            config_data = {
                "repositories": [
                    {
                        "name": "Test Repo",
                        "url": "https://github.com/test/custom.git",
                        "description": "Test repository",
                    }
                ]
            }
            custom_config.write_text(yaml.dump(config_data))

            # Mock the repository loading to avoid actual file operations
            from src.setup_environment.domain.entities import Repository

            with patch(
                "src.setup_environment.presentation.cli.load_repositories_from_config"
            ) as mock_load:
                # Return a mock repository to avoid "no repositories found" error
                mock_repo = Repository.from_url("https://github.com/test/custom.git")
                mock_load.return_value = [mock_repo]

                result = runner.invoke(
                    setup_environment,
                    [
                        "--dev-folder",
                        temp_dev_folder,
                        "--repositories-config",
                        str(custom_config),
                        "--dry-run",
                    ],
                )

                # Verify the custom config path was passed
                mock_load.assert_called_once_with(custom_config)
                assert result.exit_code == 0

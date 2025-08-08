"""Unit tests for CLI."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from src.setup_environment.application.interfaces.git_service import CloneStatus
from src.setup_environment.application.use_cases.configure_npm import (
    ConfigurationStatus,
)
from src.setup_environment.presentation.cli import (
    generate_env_template,
    get_repositories_from_environment,
    load_environment_config,
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
        result = runner.invoke(
            setup_environment, ["--dev-folder", "/does/not/exist"]
        )
        
        assert result.exit_code != 0
        assert "does not exist" in result.output.lower()

    @patch("src.setup_environment.presentation.cli.SetupRepositoriesUseCase")
    @patch("src.setup_environment.presentation.cli.ConfigureNPMUseCase")
    @patch("src.setup_environment.presentation.cli.GitPythonService")
    @patch("src.setup_environment.presentation.cli.NPMFileService")
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
        from src.setup_environment.application.use_cases.setup_repositories import (
            SetupResult,
        )
        from src.setup_environment.application.use_cases.configure_npm import (
            ConfigureResult,
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
                setup_environment, ["--dev-folder", temp_dev_folder]
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
        from src.setup_environment.application.use_cases.setup_repositories import (
            SetupResult,
        )
        from src.setup_environment.application.interfaces import CloneResult
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
                setup_environment, ["--dev-folder", temp_dev_folder, "--skip-npm"]
            )
        
        assert result.exit_code == 1
        assert "Setup completed with" in result.output
        assert "failures" in result.output

    def test_cli_exits_when_no_repositories_found(self, runner, temp_dev_folder):
        """Test CLI exits when no repositories are found in environment."""
        with runner.isolated_filesystem():
            # Ensure no .env file exists in the test directory
            with patch.dict(os.environ, {}, clear=True):
                result = runner.invoke(
                    setup_environment, ["--dev-folder", temp_dev_folder]
                )
        
        assert result.exit_code == 1
        assert "No repositories found" in result.output

    @patch("src.setup_environment.presentation.cli.SetupRepositoriesUseCase")
    def test_cli_skip_npm_flag(
        self, mock_setup_use_case, runner, temp_dev_folder, mock_environment
    ):
        """Test --skip-npm flag skips NPM configuration."""
        from src.setup_environment.application.use_cases.setup_repositories import (
            SetupResult,
        )
        
        mock_setup_result = SetupResult(successful=[], skipped=[], failed=[])
        mock_setup_use_case.return_value.execute.return_value = mock_setup_result
        
        with patch.dict(os.environ, mock_environment):
            result = runner.invoke(
                setup_environment,
                ["--dev-folder", temp_dev_folder, "--skip-npm"],
            )
        
        assert result.exit_code == 0
        assert "Skipped NPM configuration" in result.output

    @patch("src.setup_environment.presentation.cli.DevFolderPath")
    def test_cli_handles_dev_folder_validation_error(
        self, mock_dev_folder_path, runner, temp_dev_folder
    ):
        """Test CLI handles development folder validation errors."""
        mock_dev_folder_path.side_effect = ValueError("Invalid path")
        
        result = runner.invoke(
            setup_environment, ["--dev-folder", temp_dev_folder]
        )
        
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
                setup_environment, ["--dev-folder", temp_dev_folder]
            )
        
        assert result.exit_code == 1
        assert "Error: Git is not installed" in result.output

    def test_cli_help_shows_usage_information(self, runner):
        """Test that CLI help shows proper usage information."""
        result = runner.invoke(setup_environment, ["--help"])
        
        assert result.exit_code == 0
        assert "Configure Git repositories" in result.output
        assert "--dev-folder" in result.output
        assert "--skip-npm" in result.output
        assert "GIT_REPO_*" in result.output


class TestLoadEnvironmentConfig:
    """Test suite for load_environment_config function."""

    def test_load_from_specified_file(self):
        """Test loading from specified .env file."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env.test"
            env_file.write_text("GIT_REPO_TEST=https://github.com/test/repo.git\n")
            
            # Clear environment first
            if "GIT_REPO_TEST" in os.environ:
                del os.environ["GIT_REPO_TEST"]
            
            with patch("builtins.print"):  # Suppress output
                load_environment_config(env_file)
            
            assert os.environ.get("GIT_REPO_TEST") == "https://github.com/test/repo.git"
            
            # Cleanup
            if "GIT_REPO_TEST" in os.environ:
                del os.environ["GIT_REPO_TEST"]

    def test_load_from_default_env_file(self):
        """Test loading from default .env file."""
        import tempfile
        import os as temp_os
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            original_cwd = temp_os.getcwd()
            try:
                temp_os.chdir(temp_dir)
                
                env_file = Path(".env")
                env_file.write_text("GIT_REPO_DEFAULT=https://github.com/default/repo.git\n")
                
                # Clear environment first
                if "GIT_REPO_DEFAULT" in os.environ:
                    del os.environ["GIT_REPO_DEFAULT"]
                
                with patch("builtins.print"):  # Suppress output
                    load_environment_config()
                
                assert os.environ.get("GIT_REPO_DEFAULT") == "https://github.com/default/repo.git"
                
                # Cleanup
                if "GIT_REPO_DEFAULT" in os.environ:
                    del os.environ["GIT_REPO_DEFAULT"]
            finally:
                temp_os.chdir(original_cwd)

    def test_no_error_when_file_missing(self):
        """Test that missing .env file doesn't cause errors."""
        non_existent = Path("/does/not/exist/.env")
        
        # Should not raise exception
        load_environment_config(non_existent)


class TestGenerateEnvTemplate:
    """Test suite for generate_env_template function."""

    def test_generate_regular_template(self):
        """Test generating regular .env template."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            
            with patch("click.echo"):  # Suppress output
                generate_env_template(env_file, example=False)
            
            assert env_file.exists()
            content = env_file.read_text()
            assert "GIT_REPO_1=https://github.com/facebook/react.git" in content
            assert "GIT_REPO_FRONTEND=" in content
            assert "# For private repositories" in content

    def test_generate_example_template(self):
        """Test generating .env.example template."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            
            with patch("click.echo"):  # Suppress output
                generate_env_template(env_file, example=True)
            
            example_file = Path(temp_dir) / ".env.example"
            assert example_file.exists()
            content = example_file.read_text()
            assert "GIT_REPO_1=https://github.com/facebook/react.git" in content
            assert "# Setup Environment Configuration" in content

    def test_template_contains_expected_content(self):
        """Test that template contains all expected sections."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            
            with patch("click.echo"):  # Suppress output
                generate_env_template(env_file)
            
            content = env_file.read_text()
            
            # Check for key sections
            assert "# Setup Environment Configuration" in content
            assert "GIT_REPO_*" in content
            assert "HTTPS and SSH URLs" in content
            assert "private repositories" in content
            assert "git@github.com" in content


class TestSetupEnvironmentWithEnvFiles:
    """Test suite for setup_environment CLI with .env file support."""

    @pytest.fixture
    def runner(self):
        """Create a Click CLI runner."""
        return CliRunner()

    @pytest.fixture
    def temp_dev_folder(self):
        """Create a temporary development folder."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def test_generate_env_option(self, runner):
        """Test --generate-env option."""
        with runner.isolated_filesystem():
            result = runner.invoke(setup_environment, ["--generate-env"])
            
            assert result.exit_code == 0
            assert "Generated template" in result.output
            assert Path(".env").exists()
            
            content = Path(".env").read_text()
            assert "GIT_REPO_1=" in content

    def test_generate_env_example_option(self, runner):
        """Test --generate-env-example option."""
        with runner.isolated_filesystem():
            result = runner.invoke(setup_environment, ["--generate-env-example"])
            
            assert result.exit_code == 0
            assert "Generated template" in result.output
            assert Path(".env.example").exists()
            
            content = Path(".env.example").read_text()
            assert "GIT_REPO_1=" in content

    def test_custom_env_file_option(self, runner, temp_dev_folder):
        """Test --env-file option with custom file."""
        with runner.isolated_filesystem():
            # Create custom env file
            custom_env = Path(".env.custom")
            custom_env.write_text("GIT_REPO_CUSTOM=https://github.com/test/custom.git\n")
            
            result = runner.invoke(
                setup_environment,
                [
                    "--dev-folder", temp_dev_folder,
                    "--env-file", str(custom_env),
                    "--dry-run"
                ]
            )
            
            assert result.exit_code == 0
            assert "Loading configuration from" in result.output
            assert "test/custom" in result.output

    def test_dev_folder_required_for_non_generation(self, runner):
        """Test that --dev-folder is required for non-generation operations."""
        result = runner.invoke(setup_environment, ["--dry-run"])
        
        assert result.exit_code == 1
        assert "--dev-folder is required" in result.output

    def test_env_file_integration_with_repositories(self, runner, temp_dev_folder):
        """Test .env file loading integrates with repository processing."""
        with runner.isolated_filesystem():
            # Create .env file with repositories
            env_file = Path(".env")
            env_file.write_text(
                "GIT_REPO_1=https://github.com/octocat/Hello-World.git\n"
                "GIT_REPO_2=https://github.com/octocat/Spoon-Knife.git\n"
            )
            
            result = runner.invoke(
                setup_environment,
                ["--dev-folder", temp_dev_folder, "--dry-run"]
            )
            
            assert result.exit_code == 0
            assert "Loading configuration" in result.output
            assert "octocat/Hello-World" in result.output
            assert "octocat/Spoon-Knife" in result.output
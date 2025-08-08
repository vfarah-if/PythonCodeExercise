"""Integration tests for the complete setup workflow."""

import tempfile

import pytest
from click.testing import CliRunner

from src.setup_environment.presentation.cli import setup_environment


@pytest.mark.integration
class TestSetupWorkflowIntegration:
    """Integration tests for the complete setup workflow."""

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
    def temp_home_dir(self):
        """Create a temporary home directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def test_complete_workflow_dry_run(self, runner, temp_dev_folder):
        """Test complete workflow in dry-run mode."""
        test_env = {
            "GIT_REPO_1": "https://github.com/octocat/Hello-World.git",
            "GIT_REPO_2": "https://github.com/octocat/Spoon-Knife.git",
        }

        with runner.isolated_filesystem():
            result = runner.invoke(
                setup_environment,
                ["--dev-folder", temp_dev_folder, "--dry-run"],
                env=test_env,
            )

        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "No changes will be made" in result.output
        assert "octocat/Hello-World" in result.output
        assert "octocat/Spoon-Knife" in result.output
        assert "Would clone" in result.output or "Git is not installed" in result.output

    def test_complete_workflow_skip_npmrc(self, runner, temp_dev_folder):
        """Test complete workflow skipping npmrc configuration."""
        test_env = {
            "GIT_REPO_1": "https://github.com/octocat/Hello-World.git",
        }

        with runner.isolated_filesystem():
            result = runner.invoke(
                setup_environment,
                ["--dev-folder", temp_dev_folder, "--skip-npmrc", "--skip-software"],
                env=test_env,
            )

        # Should exit successfully even if Git operations fail
        # because we're testing the overall flow
        assert "Skipped npmrc configuration" in result.output
        assert "octocat/Hello-World" in result.output

    def test_workflow_with_no_repositories(self, runner, temp_dev_folder):
        """Test workflow when no repositories are configured."""
        with runner.isolated_filesystem():
            result = runner.invoke(
                setup_environment,
                ["--dev-folder", temp_dev_folder, "--skip-software"],
                env={},  # No GIT_REPO_* variables
            )

        assert result.exit_code == 1
        assert "No repositories found" in result.output

    def test_workflow_with_invalid_dev_folder(self, runner):
        """Test workflow with invalid development folder."""
        test_env = {
            "GIT_REPO_1": "https://github.com/octocat/Hello-World.git",
        }

        with runner.isolated_filesystem():
            result = runner.invoke(
                setup_environment,
                ["--dev-folder", "/does/not/exist", "--skip-software"],
                env=test_env,
            )

        assert result.exit_code != 0

    def test_workflow_with_invalid_repository_urls(self, runner, temp_dev_folder):
        """Test workflow with invalid repository URLs."""
        test_env = {
            "GIT_REPO_1": "https://github.com/octocat/Hello-World.git",  # Valid
            "GIT_REPO_2": "invalid-url",  # Invalid
            "GIT_REPO_3": "https://gitlab.com/user/repo.git",  # Not supported
        }

        with runner.isolated_filesystem():
            result = runner.invoke(
                setup_environment,
                ["--dev-folder", temp_dev_folder, "--dry-run"],
                env=test_env,
            )

        # Should process the valid repository and skip invalid ones
        assert "octocat/Hello-World" in result.output
        # Invalid URLs should generate warnings but not stop execution
        assert result.exit_code == 0

    def test_help_command(self, runner):
        """Test that help command provides useful information."""
        result = runner.invoke(setup_environment, ["--help"])

        assert result.exit_code == 0
        assert "Configure development environment" in result.output
        assert "--dev-folder" in result.output
        assert "--skip-npmrc" in result.output
        assert "--skip-software" in result.output
        assert "--dry-run" in result.output

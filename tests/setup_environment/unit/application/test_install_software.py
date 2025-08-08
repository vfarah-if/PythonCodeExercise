"""Tests for InstallSoftwareUseCase."""

from unittest.mock import Mock, patch

import pytest

from src.setup_environment.application.use_cases.install_software import (
    InstallationStatus,
    InstallSoftwareResult,
    InstallSoftwareUseCase,
)
from src.setup_environment.domain.entities.software import Software


class TestInstallSoftwareUseCase:
    """Test suite for InstallSoftwareUseCase."""

    @pytest.fixture
    def mock_software_service(self):
        """Create mock software service."""
        return Mock()

    @pytest.fixture
    def mock_python_service(self):
        """Create mock Python service."""
        return Mock()

    @pytest.fixture
    def mock_git_service(self):
        """Create mock Git service."""
        return Mock()

    @pytest.fixture
    def mock_nvm_service(self):
        """Create mock NVM service."""
        return Mock()

    @pytest.fixture
    def use_case(
        self,
        mock_software_service,
        mock_python_service,
        mock_git_service,
        mock_nvm_service,
    ):
        """Create InstallSoftwareUseCase with all services."""
        return InstallSoftwareUseCase(
            mock_software_service,
            python_service=mock_python_service,
            git_service=mock_git_service,
            nvm_service=mock_nvm_service,
        )

    @pytest.fixture
    def sample_software_list(self):
        """Create sample software list."""
        return [
            Software(
                "gh", "GitHub CLI", "gh --version", "brew install gh", required=True
            ),
            Software(
                "slack",
                "Slack",
                "test -d /Applications/Slack.app",
                "brew install --cask slack",
                required=False,
            ),
        ]

    def test_init_with_only_software_service(self, mock_software_service):
        """Test initialization with only software service."""
        use_case = InstallSoftwareUseCase(mock_software_service)

        assert use_case._software_service == mock_software_service
        assert use_case._python_service is None
        assert use_case._git_service is None
        assert use_case._nvm_service is None

    def test_init_with_all_services(
        self,
        mock_software_service,
        mock_python_service,
        mock_git_service,
        mock_nvm_service,
    ):
        """Test initialization with all specialized services."""
        use_case = InstallSoftwareUseCase(
            mock_software_service,
            python_service=mock_python_service,
            git_service=mock_git_service,
            nvm_service=mock_nvm_service,
        )

        assert use_case._software_service == mock_software_service
        assert use_case._python_service == mock_python_service
        assert use_case._git_service == mock_git_service
        assert use_case._nvm_service == mock_nvm_service

    def test_execute_skip_all_software(self, use_case, sample_software_list):
        """Test execution with skip_all=True."""
        use_case._software_service.is_package_manager_installed.return_value = True
        use_case._software_service.load_software_config.return_value = (
            sample_software_list
        )

        result = use_case.execute(skip_all=True)

        assert isinstance(result, InstallSoftwareResult)
        # Should have results from specialized services (skipped) + regular software (skipped)
        assert len(result.skipped) >= 3  # At least Python, Git, NVM environments

    def test_execute_dry_run_mode(self, use_case, sample_software_list):
        """Test execution in dry-run mode."""
        use_case._software_service.is_package_manager_installed.return_value = True
        use_case._software_service.load_software_config.return_value = (
            sample_software_list
        )
        use_case._python_service.setup_python_environment.return_value = (
            True,
            "Would setup Python",
        )
        use_case._git_service.setup_git.return_value = (True, "Would setup Git")
        use_case._nvm_service.setup_node_environment.return_value = (
            True,
            "Would setup NVM",
        )

        result = use_case.execute(dry_run=True)

        assert isinstance(result, InstallSoftwareResult)
        # Verify specialized services were called with dry_run=True
        use_case._python_service.setup_python_environment.assert_called_with(True)
        use_case._git_service.setup_git.assert_called_with(True, setup_ssh=False)
        use_case._nvm_service.setup_node_environment.assert_called_with(True)

    def test_execute_package_manager_not_installed_dry_run(self, use_case):
        """Test execution when package manager not installed in dry-run."""
        use_case._software_service.is_package_manager_installed.return_value = False

        result = use_case.execute(dry_run=True)

        assert isinstance(result, InstallSoftwareResult)
        assert len(result.results) == 1
        assert result.results[0].software.name == "homebrew"
        assert result.results[0].status == InstallationStatus.SKIPPED

    @patch("click.confirm")
    def test_execute_package_manager_installation_declined(
        self, mock_confirm, use_case
    ):
        """Test execution when user declines Homebrew installation."""
        use_case._software_service.is_package_manager_installed.return_value = False
        mock_confirm.return_value = False

        result = use_case.execute()

        assert isinstance(result, InstallSoftwareResult)
        assert len(result.results) == 1
        assert result.results[0].status == InstallationStatus.SKIPPED
        assert "User declined Homebrew installation" in result.results[0].message

    @patch("click.confirm")
    def test_execute_config_file_not_found(self, mock_confirm, use_case):
        """Test execution when config file not found."""
        use_case._software_service.is_package_manager_installed.return_value = True
        use_case._software_service.load_software_config.side_effect = FileNotFoundError(
            "Config not found"
        )
        mock_confirm.return_value = True  # Accept all specialised service installations
        use_case._python_service.setup_python_environment.return_value = (
            True,
            "Python setup",
        )
        use_case._git_service.setup_git.return_value = (True, "Git setup")
        use_case._nvm_service.setup_node_environment.return_value = (True, "NVM setup")

        result = use_case.execute()

        assert isinstance(result, InstallSoftwareResult)
        assert len(result.results) >= 3  # At least specialised services results

    @patch("click.confirm")
    def test_handle_python_service_interactive_accept(self, mock_confirm, use_case):
        """Test Python service handling with user acceptance."""
        mock_confirm.return_value = True
        use_case._python_service.setup_python_environment.return_value = (
            True,
            "Python setup complete",
        )

        results = use_case._handle_python_service(False, False, False, None)

        assert len(results) == 1
        assert results[0].status == InstallationStatus.INSTALLED
        assert "Python setup complete" in results[0].message

    @patch("click.confirm")
    def test_handle_git_service_interactive_decline(self, mock_confirm, use_case):
        """Test Git service handling with user decline."""
        mock_confirm.return_value = False

        results = use_case._handle_git_service(False, False, False, None)

        assert len(results) == 1
        assert results[0].status == InstallationStatus.SKIPPED
        assert "Skipped by user" in results[0].message

    def test_handle_nvm_service_install_all(self, use_case):
        """Test NVM service handling with install_all=True."""
        use_case._nvm_service.setup_node_environment.return_value = (
            True,
            "NVM setup complete",
        )

        results = use_case._handle_nvm_service(False, True, False, None)

        assert len(results) == 1
        assert results[0].status == InstallationStatus.INSTALLED
        assert "NVM setup complete" in results[0].message

    def test_execute_with_ssh_setup(self, use_case, sample_software_list):
        """Test execution with SSH setup enabled."""
        use_case._software_service.is_package_manager_installed.return_value = True
        use_case._software_service.load_software_config.return_value = (
            sample_software_list
        )
        use_case._python_service.setup_python_environment.return_value = (
            True,
            "Python setup",
        )
        use_case._git_service.setup_git.return_value = (True, "Git+SSH setup")
        use_case._nvm_service.setup_node_environment.return_value = (True, "NVM setup")

        result = use_case.execute(dry_run=True, setup_ssh=True)

        assert isinstance(result, InstallSoftwareResult)
        # Verify Git service was called with SSH setup
        use_case._git_service.setup_git.assert_called_with(True, setup_ssh=True)

    def test_handle_git_service_with_ssh(self, use_case):
        """Test Git service handling with SSH setup."""
        use_case._git_service.setup_git.return_value = (True, "Git+SSH setup complete")

        results = use_case._handle_git_service(False, True, False, None, setup_ssh=True)

        assert len(results) == 1
        assert results[0].status == InstallationStatus.INSTALLED
        assert results[0].software.description == "Git + Configuration + SSH"
        use_case._git_service.setup_git.assert_called_with(False, setup_ssh=True)

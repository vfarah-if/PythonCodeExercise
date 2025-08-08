"""Tests for NVMService."""

import subprocess
from unittest.mock import Mock, patch

import pytest

from src.setup_environment.infrastructure.software.nvm_service import NVMService


class TestNVMService:
    """Test suite for NVMService."""

    @pytest.fixture
    def service(self):
        """Create NVMService instance."""
        return NVMService()

    @patch("os.path.exists")
    def test_is_nvm_installed_success(self, mock_exists, service):
        """Test successful NVM detection."""
        mock_exists.side_effect = [True, True]  # ~/.nvm exists, ~/.nvm/nvm.sh exists

        result = service.is_nvm_installed()

        assert result is True
        assert mock_exists.call_count == 2

    @patch("os.path.exists")
    def test_is_nvm_installed_directory_missing(self, mock_exists, service):
        """Test NVM directory missing."""
        mock_exists.side_effect = [False, False]  # ~/.nvm doesn't exist

        result = service.is_nvm_installed()

        assert result is False

    @patch("os.path.exists")
    def test_is_nvm_installed_script_missing(self, mock_exists, service):
        """Test NVM script missing."""
        mock_exists.side_effect = [True, False]  # ~/.nvm exists but nvm.sh doesn't

        result = service.is_nvm_installed()

        assert result is False

    @patch("subprocess.run")
    def test_install_nvm_success(self, mock_run, service):
        """Test successful NVM installation."""
        mock_run.return_value = Mock(returncode=0)

        success, message = service.install_nvm()

        assert success is True
        assert "NVM installed successfully" in message
        mock_run.assert_called_once_with(
            [
                "/bin/bash",
                "-c",
                "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash",
            ],
            timeout=300,
            text=True,
        )

    @patch("subprocess.run")
    def test_install_nvm_failure(self, mock_run, service):
        """Test failed NVM installation."""
        mock_run.return_value = Mock(returncode=1)

        success, message = service.install_nvm()

        assert success is False
        assert "NVM installation failed" in message

    def test_install_nvm_dry_run(self, service):
        """Test NVM installation in dry-run mode."""
        success, message = service.install_nvm(dry_run=True)

        assert success is True
        assert "Would install NVM via official script" in message

    @patch("subprocess.run")
    def test_install_latest_node_success(self, mock_run, service):
        """Test successful Node.js installation."""
        mock_run.return_value = Mock(returncode=0)

        success, message = service.install_latest_node()

        assert success is True
        assert "Latest Node.js LTS installed and set as default" in message

    @patch("subprocess.run")
    def test_install_latest_node_timeout(self, mock_run, service):
        """Test Node.js installation timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("bash", 600)

        success, message = service.install_latest_node()

        assert success is False
        assert "Node.js installation timed out" in message

    def test_install_latest_node_dry_run(self, service):
        """Test Node.js installation in dry-run mode."""
        success, message = service.install_latest_node(dry_run=True)

        assert success is True
        assert "Would install latest Node.js LTS via NVM" in message

    @patch("subprocess.run")
    def test_get_node_version_success(self, mock_run, service):
        """Test getting Node.js version."""
        mock_run.return_value = Mock(returncode=0, stdout="v18.17.0\n")

        version = service.get_node_version()

        assert version == "v18.17.0"

    @patch("subprocess.run")
    def test_get_node_version_failure(self, mock_run, service):
        """Test getting Node.js version when not available."""
        mock_run.return_value = Mock(returncode=1)

        version = service.get_node_version()

        assert version == "unknown"

    @patch(
        "src.setup_environment.infrastructure.software.nvm_service.NVMService.is_nvm_installed"
    )
    @patch(
        "src.setup_environment.infrastructure.software.nvm_service.NVMService.install_nvm"
    )
    @patch(
        "src.setup_environment.infrastructure.software.nvm_service.NVMService.install_latest_node"
    )
    def test_setup_node_environment_new_installation(
        self, mock_install_node, mock_install_nvm, mock_is_installed, service
    ):
        """Test Node.js environment setup with new installation."""
        mock_is_installed.side_effect = [
            False,
            True,
        ]  # Not installed, then installed after setup
        mock_install_nvm.return_value = (True, "NVM installed")
        mock_install_node.return_value = (True, "Node.js installed")

        success, message = service.setup_node_environment()

        assert success is True
        assert "NVM: NVM installed" in message
        assert "Node.js: Node.js installed" in message

    @patch(
        "src.setup_environment.infrastructure.software.nvm_service.NVMService.is_nvm_installed"
    )
    def test_setup_node_environment_already_installed(self, mock_is_installed, service):
        """Test Node.js environment setup when already installed."""
        mock_is_installed.return_value = True

        success, message = service.setup_node_environment()

        assert success is True
        assert "NVM: already installed" in message

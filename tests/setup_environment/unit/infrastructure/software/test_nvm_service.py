"""Tests for NodeEnvironmentService."""

import subprocess
from unittest.mock import Mock, patch

import pytest

from src.setup_environment.infrastructure.software.nvm_service import (
    NodeEnvironmentService,
)


class TestNodeEnvironmentService:
    """Test suite for NodeEnvironmentService."""

    @pytest.fixture
    def service(self):
        """Create NodeEnvironmentService instance."""
        return NodeEnvironmentService()

    @patch("subprocess.run")
    def test_is_nvm_installed_success(self, mock_run, service):
        """Test successful NVM detection."""
        mock_run.return_value = Mock(returncode=0, stdout="0.39.0\n")

        result = service.is_nvm_installed()

        assert result is True
        mock_run.assert_called_once()
        # Check that the command includes sourcing nvm and checking version
        call_args = mock_run.call_args[0][0]
        assert "/bin/bash" in call_args
        assert "nvm --version" in call_args[2]

    @patch("subprocess.run")
    def test_is_nvm_installed_not_found(self, mock_run, service):
        """Test NVM not installed."""
        mock_run.return_value = Mock(returncode=1, stdout="")

        result = service.is_nvm_installed()

        assert result is False

    @patch("subprocess.run")
    def test_is_nvm_installed_timeout(self, mock_run, service):
        """Test NVM detection timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("bash", 5)

        result = service.is_nvm_installed()

        assert result is False

    @patch(
        "src.setup_environment.infrastructure.software.nvm_service.NodeEnvironmentService.is_nvm_installed"
    )
    @patch("subprocess.run")
    def test_install_nvm_success(self, mock_run, mock_is_installed, service):
        """Test successful NVM installation."""
        mock_run.return_value = Mock(returncode=0)
        mock_is_installed.return_value = True  # Verification succeeds

        success, message = service.install_nvm()

        assert success is True
        assert "NVM installed successfully" in message
        mock_run.assert_called_once_with(
            [
                "/bin/bash",
                "-c",
                "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash",
            ],
            timeout=300,
            text=True,
        )

    @patch(
        "src.setup_environment.infrastructure.software.nvm_service.NodeEnvironmentService.is_nvm_installed"
    )
    @patch("subprocess.run")
    def test_install_nvm_failure(self, mock_run, mock_is_installed, service):
        """Test failed NVM installation."""
        mock_run.return_value = Mock(returncode=1)
        mock_is_installed.return_value = False

        success, message = service.install_nvm()

        assert success is False
        assert "NVM installation failed" in message

    @patch(
        "src.setup_environment.infrastructure.software.nvm_service.NodeEnvironmentService.is_nvm_installed"
    )
    @patch("subprocess.run")
    def test_install_nvm_verification_fails(self, mock_run, mock_is_installed, service):
        """Test NVM installation succeeds but verification fails."""
        mock_run.return_value = Mock(returncode=0)
        mock_is_installed.return_value = False  # Verification fails

        success, message = service.install_nvm()

        assert success is False
        assert "verification failed" in message

    def test_install_nvm_dry_run(self, service):
        """Test NVM installation in dry-run mode."""
        success, message = service.install_nvm(dry_run=True)

        assert success is True
        assert "Would install NVM via official script" in message

    @patch(
        "src.setup_environment.infrastructure.software.nvm_service.NodeEnvironmentService.get_node_version"
    )
    @patch("subprocess.run")
    def test_install_latest_node_success(self, mock_run, mock_get_version, service):
        """Test successful Node.js installation."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_get_version.return_value = "v20.11.0"

        success, message = service.install_latest_node()

        assert success is True
        assert "Node.js LTS v20.11.0 installed and set as default" in message

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
        "src.setup_environment.infrastructure.software.nvm_service.NodeEnvironmentService.get_node_version"
    )
    @patch("subprocess.run")
    def test_install_node_version_lts(self, mock_run, mock_get_version, service):
        """Test installing LTS version of Node.js."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_get_version.return_value = "v20.11.0"

        success, message = service.install_node_version("lts")

        assert success is True
        assert "Node.js v20.11.0 installed successfully" in message
        # Check the command includes --lts
        call_args = mock_run.call_args[0][0]
        assert "nvm install --lts" in call_args[2]

    @patch(
        "src.setup_environment.infrastructure.software.nvm_service.NodeEnvironmentService.get_node_version"
    )
    @patch("subprocess.run")
    def test_install_node_version_latest(self, mock_run, mock_get_version, service):
        """Test installing latest version of Node.js."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_get_version.return_value = "v21.6.0"

        success, message = service.install_node_version("latest")

        assert success is True
        assert "Node.js v21.6.0 installed successfully" in message
        # Check the command includes 'node' (NVM's alias for latest)
        call_args = mock_run.call_args[0][0]
        assert "nvm install node" in call_args[2]

    @patch(
        "src.setup_environment.infrastructure.software.nvm_service.NodeEnvironmentService.get_node_version"
    )
    @patch("subprocess.run")
    def test_install_node_version_specific(self, mock_run, mock_get_version, service):
        """Test installing specific version of Node.js."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_get_version.return_value = "v18.17.0"

        success, message = service.install_node_version("18.17.0")

        assert success is True
        assert "Node.js v18.17.0 installed successfully" in message
        # Check the command includes the specific version
        call_args = mock_run.call_args[0][0]
        assert "nvm install 18.17.0" in call_args[2]

    @patch("subprocess.run")
    def test_install_node_version_failure(self, mock_run, service):
        """Test failed Node.js installation."""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Version not found")

        success, message = service.install_node_version("99.99.99")

        assert success is False
        assert "Version not found" in message

    def test_install_node_version_dry_run(self, service):
        """Test Node.js installation in dry-run mode."""
        success, message = service.install_node_version("lts", dry_run=True)

        assert success is True
        assert "Would install Node.js lts via NVM" in message

    @patch(
        "src.setup_environment.infrastructure.software.nvm_service.NodeEnvironmentService.is_nvm_installed"
    )
    @patch(
        "src.setup_environment.infrastructure.software.nvm_service.NodeEnvironmentService.install_nvm"
    )
    @patch(
        "src.setup_environment.infrastructure.software.nvm_service.NodeEnvironmentService.install_latest_node"
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
        "src.setup_environment.infrastructure.software.nvm_service.NodeEnvironmentService.is_nvm_installed"
    )
    def test_setup_node_environment_already_installed(self, mock_is_installed, service):
        """Test Node.js environment setup when already installed."""
        mock_is_installed.return_value = True

        success, message = service.setup_node_environment()

        assert success is True
        assert "NVM: already installed" in message

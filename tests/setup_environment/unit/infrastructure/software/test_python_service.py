"""Tests for BrewPythonService."""

import subprocess
from unittest.mock import Mock, patch

import pytest

from src.setup_environment.infrastructure.software.python_service import (
    BrewPythonService,
)


class TestBrewPythonService:
    """Test suite for BrewPythonService."""

    @pytest.fixture
    def service(self):
        """Create BrewPythonService instance."""
        return BrewPythonService()

    @patch("subprocess.run")
    def test_is_python_installed_success(self, mock_run, service):
        """Test successful Python detection."""
        mock_run.return_value = Mock(returncode=0)

        result = service.is_python_installed()

        assert result is True
        mock_run.assert_called_once_with(
            ["python3", "--version"], capture_output=True, text=True, timeout=10
        )

    @patch("subprocess.run")
    def test_is_python_installed_not_found(self, mock_run, service):
        """Test Python not installed."""
        mock_run.side_effect = FileNotFoundError()

        result = service.is_python_installed()

        assert result is False

    @patch("subprocess.run")
    def test_is_uv_installed_success(self, mock_run, service):
        """Test successful uv detection."""
        mock_run.return_value = Mock(returncode=0)

        result = service.is_uv_installed()

        assert result is True
        mock_run.assert_called_once_with(
            ["uv", "--version"], capture_output=True, text=True, timeout=10
        )

    @patch("subprocess.run")
    def test_is_uv_installed_not_found(self, mock_run, service):
        """Test uv not installed."""
        mock_run.side_effect = FileNotFoundError()

        result = service.is_uv_installed()

        assert result is False

    @patch("subprocess.run")
    def test_install_python_success(self, mock_run, service):
        """Test successful Python installation."""
        mock_run.return_value = Mock(returncode=0)

        success, message = service.install_python()

        assert success is True
        assert "Python installed successfully" in message
        mock_run.assert_called_once_with(
            ["brew", "install", "python"], capture_output=True, text=True, timeout=300
        )

    @patch("subprocess.run")
    def test_install_python_failure(self, mock_run, service):
        """Test failed Python installation."""
        mock_run.return_value = Mock(
            returncode=1, stderr="Package not found", stdout=""
        )

        success, message = service.install_python()

        assert success is False
        assert "Failed to install Python" in message
        assert "Package not found" in message

    def test_install_python_dry_run(self, service):
        """Test Python installation in dry-run mode."""
        success, message = service.install_python(dry_run=True)

        assert success is True
        assert "Would install Python via Homebrew" in message

    @patch("subprocess.run")
    def test_install_uv_success(self, mock_run, service):
        """Test successful uv installation."""
        mock_run.return_value = Mock(returncode=0)

        success, message = service.install_uv()

        assert success is True
        assert "uv installed successfully" in message

    @patch("subprocess.run")
    def test_install_uv_timeout(self, mock_run, service):
        """Test uv installation timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("brew", 300)

        success, message = service.install_uv()

        assert success is False
        assert "uv installation timed out" in message

    def test_install_uv_dry_run(self, service):
        """Test uv installation in dry-run mode."""
        success, message = service.install_uv(dry_run=True)

        assert success is True
        assert "Would install uv via Homebrew" in message

    @patch(
        "src.setup_environment.infrastructure.software.python_service.BrewPythonService.is_python_installed"
    )
    @patch(
        "src.setup_environment.infrastructure.software.python_service.BrewPythonService.is_uv_installed"
    )
    @patch(
        "src.setup_environment.infrastructure.software.python_service.BrewPythonService.install_python"
    )
    @patch(
        "src.setup_environment.infrastructure.software.python_service.BrewPythonService.install_uv"
    )
    def test_setup_python_environment_both_missing(
        self,
        mock_install_uv,
        mock_install_python,
        mock_is_uv_installed,
        mock_is_python_installed,
        service,
    ):
        """Test setup when both Python and uv are missing."""
        mock_is_python_installed.return_value = False
        mock_is_uv_installed.return_value = False
        mock_install_python.return_value = (True, "Python installed")
        mock_install_uv.return_value = (True, "uv installed")

        success, message = service.setup_python_environment()

        assert success is True
        assert "Python: Python installed" in message
        assert "uv: uv installed" in message

    @patch(
        "src.setup_environment.infrastructure.software.python_service.BrewPythonService.is_python_installed"
    )
    @patch(
        "src.setup_environment.infrastructure.software.python_service.BrewPythonService.is_uv_installed"
    )
    def test_setup_python_environment_both_installed(
        self, mock_is_uv_installed, mock_is_python_installed, service
    ):
        """Test setup when both Python and uv are already installed."""
        mock_is_python_installed.return_value = True
        mock_is_uv_installed.return_value = True

        success, message = service.setup_python_environment()

        assert success is True
        assert "Python: already installed" in message
        assert "uv: already installed" in message

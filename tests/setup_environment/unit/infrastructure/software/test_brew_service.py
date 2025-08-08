"""Tests for BrewSoftwareService."""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.setup_environment.domain.entities.software import Software
from src.setup_environment.infrastructure.software.brew_service import (
    BrewSoftwareService,
)


class TestBrewSoftwareService:
    """Test suite for BrewSoftwareService."""

    @pytest.fixture
    def sample_software(self):
        """Create sample software for testing."""
        return Software(
            name="git",
            description="Version control system",
            check_command="git --version",
            install_command="brew install git",
            required=True,
        )

    @pytest.fixture
    def custom_software(self):
        """Create custom install software for testing."""
        return Software(
            name="nvm",
            description="Node Version Manager",
            check_command="nvm --version",
            install_command="curl -o- https://example.com/install.sh | bash",
            custom_install=True,
        )

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def sample_config_file(self, temp_config_dir):
        """Create sample configuration file."""
        config_content = """software:
  - name: git
    description: "Version control system"
    check_command: "git --version"
    install_command: "brew install git"
    required: true

  - name: terraform
    description: "Infrastructure as Code"
    check_command: "terraform --version"
    install_command: "brew install terraform"
    required: false
"""
        config_file = temp_config_dir / "software.yaml"
        config_file.write_text(config_content)
        return config_file

    def test_init_with_default_config_dir(self):
        """Test initialization with default config directory."""
        service = BrewSoftwareService()
        expected_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "src"
            / "setup_environment"
            / "config"
        )
        assert service._config_dir == expected_path

    def test_init_with_custom_config_dir(self, temp_config_dir):
        """Test initialization with custom config directory."""
        service = BrewSoftwareService(config_dir=temp_config_dir)
        assert service._config_dir == temp_config_dir

    @patch("subprocess.run")
    def test_is_package_manager_installed_success(self, mock_run):
        """Test successful Homebrew detection."""
        mock_run.return_value = Mock(returncode=0)

        service = BrewSoftwareService()
        result = service.is_package_manager_installed()

        assert result is True
        mock_run.assert_called_once_with(
            ["brew", "--version"], capture_output=True, text=True, timeout=10
        )

    @patch("subprocess.run")
    def test_is_package_manager_installed_not_found(self, mock_run):
        """Test Homebrew not installed."""
        mock_run.side_effect = FileNotFoundError()

        service = BrewSoftwareService()
        result = service.is_package_manager_installed()

        assert result is False

    @patch("subprocess.run")
    def test_is_package_manager_installed_command_fails(self, mock_run):
        """Test Homebrew command fails."""
        mock_run.return_value = Mock(returncode=1)

        service = BrewSoftwareService()
        result = service.is_package_manager_installed()

        assert result is False

    @patch("subprocess.run")
    def test_is_installed_success(self, mock_run, sample_software):
        """Test software is installed."""
        mock_run.return_value = Mock(returncode=0)

        service = BrewSoftwareService()
        result = service.is_installed(sample_software)

        assert result is True
        mock_run.assert_called_once_with(
            ["git", "--version"], capture_output=True, text=True, timeout=10
        )

    @patch("subprocess.run")
    def test_is_installed_not_found(self, mock_run, sample_software):
        """Test software is not installed."""
        mock_run.side_effect = FileNotFoundError()

        service = BrewSoftwareService()
        result = service.is_installed(sample_software)

        assert result is False

    @patch("subprocess.run")
    def test_install_success(self, mock_run, sample_software):
        """Test successful software installation."""
        mock_run.return_value = Mock(returncode=0, stdout="Installed git", stderr="")

        service = BrewSoftwareService()
        success, message = service.install(sample_software)

        assert success is True
        assert "Successfully installed git" in message
        mock_run.assert_called_once_with(
            ["brew", "install", "git"], capture_output=True, text=True, timeout=300
        )

    @patch("subprocess.run")
    def test_install_failure(self, mock_run, sample_software):
        """Test failed software installation."""
        mock_run.return_value = Mock(
            returncode=1, stdout="", stderr="Package not found"
        )

        service = BrewSoftwareService()
        success, message = service.install(sample_software)

        assert success is False
        assert "Failed to install git" in message
        assert "Package not found" in message

    def test_install_dry_run(self, sample_software):
        """Test dry run installation."""
        service = BrewSoftwareService()
        success, message = service.install(sample_software, dry_run=True)

        assert success is True
        assert "Would execute: brew install git" in message

    def test_load_software_config_success(self, sample_config_file, temp_config_dir):
        """Test loading software configuration."""
        service = BrewSoftwareService(config_dir=temp_config_dir)
        software_list = service.load_software_config()

        assert len(software_list) == 2
        assert software_list[0].name == "git"
        assert software_list[0].required is True
        assert software_list[1].name == "terraform"
        assert software_list[1].required is False

    def test_load_software_config_file_not_found(self, temp_config_dir):
        """Test loading config when file doesn't exist."""
        service = BrewSoftwareService(config_dir=temp_config_dir)

        with pytest.raises(FileNotFoundError, match="Software configuration not found"):
            service.load_software_config()

    def test_load_software_config_invalid_yaml(self, temp_config_dir):
        """Test loading invalid YAML configuration."""
        config_file = temp_config_dir / "software.yaml"
        config_file.write_text("invalid: yaml: content: [")

        service = BrewSoftwareService(config_dir=temp_config_dir)

        with pytest.raises(ValueError, match="Error parsing software configuration"):
            service.load_software_config()

    def test_load_software_config_missing_software_key(self, temp_config_dir):
        """Test loading config missing software key."""
        config_file = temp_config_dir / "software.yaml"
        config_file.write_text("tools: []")

        service = BrewSoftwareService(config_dir=temp_config_dir)

        with pytest.raises(ValueError, match="missing 'software' key"):
            service.load_software_config()

    def test_parse_software_item_missing_required_field(self, temp_config_dir):
        """Test parsing software item with missing required field."""
        config_content = """software:
  - name: git
    description: "Version control"
    # Missing check_command and install_command
"""
        config_file = temp_config_dir / "software.yaml"
        config_file.write_text(config_content)

        service = BrewSoftwareService(config_dir=temp_config_dir)

        with pytest.raises(ValueError, match="Missing required field"):
            service.load_software_config()

    @patch("subprocess.run")
    def test_install_package_manager_success(self, mock_run):
        """Test successful Homebrew installation."""
        mock_run.return_value = Mock(returncode=0)

        service = BrewSoftwareService()
        success, message = service.install_package_manager()

        assert success is True
        assert "Homebrew installed successfully" in message
        mock_run.assert_called_once_with(
            [
                "/bin/bash",
                "-c",
                "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)",
            ],
            timeout=600,
            text=True,
        )

    @patch("subprocess.run")
    def test_install_package_manager_failure(self, mock_run):
        """Test failed Homebrew installation."""
        mock_run.return_value = Mock(returncode=1)

        service = BrewSoftwareService()
        success, message = service.install_package_manager()

        assert success is False
        assert "Homebrew installation failed" in message

    @patch("subprocess.run")
    def test_install_package_manager_timeout(self, mock_run):
        """Test Homebrew installation timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("bash", 600)

        service = BrewSoftwareService()
        success, message = service.install_package_manager()

        assert success is False
        assert "Homebrew installation timed out" in message

    @patch("subprocess.run")
    def test_install_package_manager_exception(self, mock_run):
        """Test Homebrew installation with unexpected exception."""
        mock_run.side_effect = Exception("Unexpected error")

        service = BrewSoftwareService()
        success, message = service.install_package_manager()

        assert success is False
        assert "Error installing Homebrew: Unexpected error" in message

    def test_install_package_manager_dry_run(self):
        """Test Homebrew installation in dry-run mode."""
        service = BrewSoftwareService()
        success, message = service.install_package_manager(dry_run=True)

        assert success is True
        assert "Would install Homebrew" in message

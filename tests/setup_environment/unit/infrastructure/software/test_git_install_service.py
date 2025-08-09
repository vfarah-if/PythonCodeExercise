"""Tests for GitService (installation service)."""

from unittest.mock import Mock, patch

import pytest

from src.setup_environment.infrastructure.software.git_service import GitService


class TestGitInstallService:
    """Test suite for GitService (installation service)."""

    @pytest.fixture
    def service(self):
        """Create GitService instance."""
        return GitService()

    @patch("subprocess.run")
    def test_is_git_installed_success(self, mock_run, service):
        """Test successful Git detection."""
        mock_run.return_value = Mock(returncode=0)

        result = service.is_git_installed()

        assert result is True
        mock_run.assert_called_once_with(
            ["git", "--version"], capture_output=True, text=True, timeout=10
        )

    @patch("subprocess.run")
    def test_is_git_installed_not_found(self, mock_run, service):
        """Test Git not installed."""
        mock_run.side_effect = FileNotFoundError()

        result = service.is_git_installed()

        assert result is False

    @patch("subprocess.run")
    def test_is_git_configured_success(self, mock_run, service):
        """Test Git is properly configured."""
        mock_run.side_effect = [
            Mock(returncode=0, stdout="John Doe\n"),  # user.name
            Mock(returncode=0, stdout="john@example.com\n"),  # user.email
        ]

        result = service.is_git_configured()

        assert result is True
        assert mock_run.call_count == 2

    @patch("subprocess.run")
    def test_is_git_configured_missing_name(self, mock_run, service):
        """Test Git missing user.name."""
        mock_run.side_effect = [
            Mock(returncode=1, stdout=""),  # user.name missing
            Mock(returncode=0, stdout="john@example.com\n"),  # user.email exists
        ]

        result = service.is_git_configured()

        assert result is False

    @patch("subprocess.run")
    def test_install_git_success(self, mock_run, service):
        """Test successful Git installation."""
        mock_run.return_value = Mock(returncode=0)

        success, message = service.install_git()

        assert success is True
        assert "Git installed successfully" in message
        mock_run.assert_called_once_with(
            ["brew", "install", "git"], capture_output=True, text=True, timeout=300
        )

    @patch("subprocess.run")
    def test_install_git_failure(self, mock_run, service):
        """Test failed Git installation."""
        mock_run.return_value = Mock(
            returncode=1, stderr="Package not found", stdout=""
        )

        success, message = service.install_git()

        assert success is False
        assert "Failed to install Git" in message

    def test_install_git_dry_run(self, service):
        """Test Git installation in dry-run mode."""
        success, message = service.install_git(dry_run=True)

        assert success is True
        assert "Would install Git via Homebrew" in message

    @patch("subprocess.run")
    def test_configure_git_success(self, mock_run, service):
        """Test successful Git configuration."""
        mock_run.side_effect = [
            Mock(returncode=0),  # user.name
            Mock(returncode=0),  # user.email
        ]

        success, message = service.configure_git("John Doe", "john@example.com")

        assert success is True
        assert "Git configured: John Doe <john@example.com>" in message
        assert mock_run.call_count == 2

    @patch("subprocess.run")
    def test_configure_git_failure(self, mock_run, service):
        """Test failed Git configuration."""
        mock_run.side_effect = [
            Mock(returncode=0),  # user.name succeeds
            Mock(returncode=1),  # user.email fails
        ]

        success, message = service.configure_git("John Doe", "john@example.com")

        assert success is False
        assert "Failed to configure Git user settings" in message

    def test_configure_git_dry_run(self, service):
        """Test Git configuration in dry-run mode."""
        success, message = service.configure_git(
            "John Doe", "john@example.com", dry_run=True
        )

        assert success is True
        assert (
            "Would configure Git: user.name='John Doe', user.email='john@example.com'"
            in message
        )

    @patch("click.prompt")
    def test_prompt_for_git_config(self, mock_prompt, service):
        """Test prompting for Git configuration."""
        mock_prompt.side_effect = ["John Doe", "john@example.com"]

        username, email = service.prompt_for_git_config()

        assert username == "John Doe"
        assert email == "john@example.com"
        assert mock_prompt.call_count == 2

    @patch(
        "src.setup_environment.infrastructure.software.git_service.GitService.is_git_installed"
    )
    @patch(
        "src.setup_environment.infrastructure.software.git_service.GitService.is_git_configured"
    )
    @patch(
        "src.setup_environment.infrastructure.software.git_service.GitService.install_git"
    )
    @patch(
        "src.setup_environment.infrastructure.software.git_service.GitService.prompt_for_git_config"
    )
    @patch(
        "src.setup_environment.infrastructure.software.git_service.GitService.configure_git"
    )
    def test_setup_git_new_installation(
        self,
        mock_configure,
        mock_prompt,
        mock_install,
        mock_configured,
        mock_installed,
        service,
    ):
        """Test Git setup with new installation."""
        mock_installed.return_value = False
        mock_configured.return_value = False
        mock_install.return_value = (True, "Git installed")
        mock_prompt.return_value = ("John Doe", "john@example.com")
        mock_configure.return_value = (True, "Git configured")

        success, message = service.setup_git()

        assert success is True
        assert "Installation: Git installed" in message
        assert "Configuration: Git configured" in message

    @patch("pathlib.Path.exists")
    def test_has_ssh_key_exists(self, mock_exists, service):
        """Test SSH key detection when key exists."""
        mock_exists.return_value = True

        result = service.has_ssh_key()

        assert result is True

    @patch("pathlib.Path.exists")
    def test_has_ssh_key_not_exists(self, mock_exists, service):
        """Test SSH key detection when no keys exist."""
        mock_exists.return_value = False

        result = service.has_ssh_key()

        assert result is False

    @patch("subprocess.run")
    @patch("pathlib.Path.mkdir")
    def test_generate_ssh_key_success(self, mock_mkdir, mock_run, service):
        """Test successful SSH key generation."""
        mock_run.return_value = Mock(returncode=0)

        success, message = service.generate_ssh_key("test@example.com")

        assert success is True
        assert "SSH key generated" in message

    def test_generate_ssh_key_dry_run(self, service):
        """Test SSH key generation in dry-run mode."""
        success, message = service.generate_ssh_key("test@example.com", dry_run=True)

        assert success is True
        assert "Would generate SSH key for test@example.com" in message

    @patch("subprocess.run")
    def test_add_ssh_key_to_agent_success(self, mock_run, service):
        """Test successful SSH key addition to agent."""
        # Mock ssh-add -l (check agent) and ssh-add key
        mock_run.side_effect = [
            Mock(returncode=0),  # ssh-add -l
            Mock(returncode=0),  # ssh-add key
        ]

        with patch("pathlib.Path.exists", return_value=True):
            success, message = service.add_ssh_key_to_agent()

        assert success is True
        assert "added to ssh-agent" in message

    @patch("subprocess.run")
    def test_test_ssh_connection_success(self, mock_run, service):
        """Test successful SSH connection test."""
        mock_run.return_value = Mock(
            returncode=1,  # GitHub returns 1 but with success message
            stderr="Hi username! You've successfully authenticated",
        )

        success, message = service.test_ssh_connection()

        assert success is True
        assert "SSH connection to GitHub successful" in message

    @patch("subprocess.run")
    def test_test_ssh_connection_failure(self, mock_run, service):
        """Test failed SSH connection test."""
        mock_run.return_value = Mock(returncode=255, stderr="Connection refused")

        success, message = service.test_ssh_connection()

        assert success is False
        assert "SSH connection failed" in message

    @patch(
        "src.setup_environment.infrastructure.software.git_service.GitService.has_ssh_key"
    )
    @patch(
        "src.setup_environment.infrastructure.software.git_service.GitService.generate_ssh_key"
    )
    @patch(
        "src.setup_environment.infrastructure.software.git_service.GitService.add_ssh_key_to_agent"
    )
    @patch(
        "src.setup_environment.infrastructure.software.git_service.GitService.test_ssh_connection"
    )
    def test_setup_ssh_configuration_new_key(
        self, mock_test, mock_add, mock_generate, mock_has_key, service
    ):
        """Test SSH configuration setup with new key generation."""
        mock_has_key.side_effect = [
            False,
            True,
            True,
        ]  # No key initially, then has key after generation
        mock_generate.return_value = (True, "SSH key generated")
        mock_add.return_value = (True, "Key added to agent")
        mock_test.return_value = (True, "Connection successful")

        success, message = service.setup_ssh_configuration("test@example.com")

        assert success is True
        assert "SSH Key: SSH key generated" in message
        assert "SSH Agent: Key added to agent" in message
        assert "SSH Test: Connection successful" in message

    @patch(
        "src.setup_environment.infrastructure.software.git_service.GitService.has_ssh_key"
    )
    def test_setup_ssh_configuration_existing_key(self, mock_has_key, service):
        """Test SSH configuration with existing key."""
        mock_has_key.return_value = True

        with patch.object(
            service, "add_ssh_key_to_agent", return_value=(True, "Key added")
        ):
            with patch.object(
                service, "test_ssh_connection", return_value=(True, "Connected")
            ):
                success, message = service.setup_ssh_configuration("test@example.com")

        assert success is True
        assert "SSH Key: already exists" in message

    @patch(
        "src.setup_environment.infrastructure.software.git_service.GitService.is_git_installed"
    )
    @patch(
        "src.setup_environment.infrastructure.software.git_service.GitService.is_git_configured"
    )
    @patch(
        "src.setup_environment.infrastructure.software.git_service.GitService.prompt_for_git_config"
    )
    @patch(
        "src.setup_environment.infrastructure.software.git_service.GitService.configure_git"
    )
    @patch(
        "src.setup_environment.infrastructure.software.git_service.GitService.setup_ssh_configuration"
    )
    def test_setup_git_with_ssh(
        self,
        mock_ssh_setup,
        mock_configure,
        mock_prompt,
        mock_configured,
        mock_installed,
        service,
    ):
        """Test Git setup with SSH configuration."""
        mock_installed.return_value = True  # Git already installed
        mock_configured.return_value = True  # Git already configured
        mock_ssh_setup.return_value = (True, "SSH configured")

        # Mock subprocess.run for getting git config email
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="user@example.com\n")

            success, message = service.setup_git(setup_ssh=True)

        assert success is True
        assert "Installation: already installed" in message
        assert "Configuration: already configured" in message
        assert "SSH: SSH configured" in message
        mock_ssh_setup.assert_called_once_with("user@example.com", False)

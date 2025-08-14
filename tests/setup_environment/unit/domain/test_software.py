"""Tests for Software entity."""

import pytest

from src.setup_environment.domain.entities.software import Software


class TestSoftware:
    """Test suite for Software entity."""

    def test_software_creation_success(self):
        """Test successful software creation."""
        software = Software(
            name="git",
            description="Version control system",
            check_command="git --version",
            install_command="brew install git",
            required=True,
        )

        assert software.name == "git"
        assert software.description == "Version control system"
        assert software.check_command == "git --version"
        assert software.install_command == "brew install git"
        assert software.required is True
        assert software.custom_install is False

    def test_software_with_custom_install(self):
        """Test software with custom install flag."""
        software = Software(
            name="nvm",
            description="Node Version Manager",
            check_command="nvm --version",
            install_command="curl -o- https://example.com/install.sh | bash",
            custom_install=True,
        )

        assert software.custom_install is True
        assert software.required is False

    def test_software_display_name_required(self):
        """Test display name with required flag."""
        software = Software(
            name="git",
            description="Version control",
            check_command="git --version",
            install_command="brew install git",
            required=True,
        )

        assert software.display_name == "git (required)"

    def test_software_display_name_optional(self):
        """Test display name without required flag."""
        software = Software(
            name="terraform",
            description="Infrastructure tool",
            check_command="terraform --version",
            install_command="brew install terraform",
        )

        assert software.display_name == "terraform"

    def test_software_string_representation(self):
        """Test string representation."""
        software = Software(
            name="aws-cli",
            description="AWS CLI",
            check_command="aws --version",
            install_command="brew install awscli",
        )

        assert str(software) == "aws-cli"

    def test_software_empty_name_raises_error(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Software name cannot be empty"):
            Software(
                name="",
                description="Test",
                check_command="test --version",
                install_command="brew install test",
            )

    def test_software_empty_check_command_raises_error(self):
        """Test that empty check command raises ValueError."""
        with pytest.raises(ValueError, match="Check command required for test"):
            Software(
                name="test",
                description="Test software",
                check_command="",
                install_command="brew install test",
            )

    def test_software_empty_install_command_raises_error(self):
        """Test that empty install command raises ValueError."""
        with pytest.raises(ValueError, match="Install command required for test"):
            Software(
                name="test",
                description="Test software",
                check_command="test --version",
                install_command="",
            )

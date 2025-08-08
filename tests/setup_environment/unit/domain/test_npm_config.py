"""Unit tests for NPMConfiguration entity."""

import tempfile
from pathlib import Path

import pytest

from src.setup_environment.domain.entities import NPMConfiguration
from src.setup_environment.domain.value_objects import PersonalAccessToken


class TestNPMConfiguration:
    """Test suite for NPMConfiguration entity."""

    @pytest.fixture
    def valid_token(self):
        """Provide a valid personal access token."""
        return PersonalAccessToken("ghp_" + "a" * 36)

    def test_create_npm_configuration_with_defaults(self, valid_token):
        """Test creating NPM configuration with default values."""
        config = NPMConfiguration(token=valid_token)
        
        assert config.token == valid_token
        assert config.registry_url == "https://npm.pkg.github.com"
        assert config.organisation == "@webuild-ai"
        assert config.package_lock is True
        assert config.legacy_peer_deps is True

    def test_create_npm_configuration_with_custom_values(self, valid_token):
        """Test creating NPM configuration with custom values."""
        config = NPMConfiguration(
            token=valid_token,
            registry_url="https://custom.registry.com",
            organisation="@custom-org",
            package_lock=False,
            legacy_peer_deps=False
        )
        
        assert config.token == valid_token
        assert config.registry_url == "https://custom.registry.com"
        assert config.organisation == "@custom-org"
        assert config.package_lock is False
        assert config.legacy_peer_deps is False

    def test_generate_config_content_with_defaults(self, valid_token):
        """Test generating config content with default settings."""
        config = NPMConfiguration(token=valid_token)
        content = config.generate_config_content()
        
        expected_lines = [
            "package-lock=true",
            "legacy-peer-deps=true",
            f"//npm.pkg.github.com/:_authToken={valid_token.value}",
            "@webuild-ai:registry=https://npm.pkg.github.com"
        ]
        
        assert content == "\n".join(expected_lines)

    def test_generate_config_content_without_package_lock(self, valid_token):
        """Test generating config without package-lock setting."""
        config = NPMConfiguration(
            token=valid_token,
            package_lock=False
        )
        content = config.generate_config_content()
        
        assert "package-lock=true" not in content
        assert "legacy-peer-deps=true" in content
        assert f"//npm.pkg.github.com/:_authToken={valid_token.value}" in content

    def test_generate_config_content_without_legacy_peer_deps(self, valid_token):
        """Test generating config without legacy-peer-deps setting."""
        config = NPMConfiguration(
            token=valid_token,
            legacy_peer_deps=False
        )
        content = config.generate_config_content()
        
        assert "package-lock=true" in content
        assert "legacy-peer-deps=true" not in content
        assert f"//npm.pkg.github.com/:_authToken={valid_token.value}" in content

    def test_generate_config_with_custom_registry(self, valid_token):
        """Test generating config with custom registry URL."""
        config = NPMConfiguration(
            token=valid_token,
            registry_url="https://custom.registry.com",
            organisation="@my-org"
        )
        content = config.generate_config_content()
        
        assert "//custom.registry.com/:_authToken=" in content
        assert "@my-org:registry=https://custom.registry.com" in content

    def test_write_to_file(self, valid_token):
        """Test writing configuration to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / ".npmrc"
            config = NPMConfiguration(token=valid_token)
            
            config.write_to_file(config_path)
            
            assert config_path.exists()
            assert config_path.is_file()
            
            content = config_path.read_text()
            assert "package-lock=true" in content
            assert "legacy-peer-deps=true" in content
            assert f"_authToken={valid_token.value}" in content
            assert "@webuild-ai:registry=" in content

    def test_write_to_file_creates_parent_directory(self, valid_token):
        """Test that writing to file creates parent directory if needed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nested" / "dir" / ".npmrc"
            config = NPMConfiguration(token=valid_token)
            
            config.write_to_file(config_path)
            
            assert config_path.exists()
            assert config_path.parent.exists()

    def test_exists_at_path_returns_true_for_valid_config(self, valid_token):
        """Test checking if valid config exists at path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / ".npmrc"
            config = NPMConfiguration(token=valid_token)
            config.write_to_file(config_path)
            
            assert NPMConfiguration.exists_at_path(config_path) is True

    def test_exists_at_path_returns_false_for_non_existent_file(self):
        """Test checking non-existent file."""
        non_existent = Path("/does/not/exist/.npmrc")
        assert NPMConfiguration.exists_at_path(non_existent) is False

    def test_exists_at_path_returns_false_for_invalid_content(self):
        """Test checking file with invalid content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / ".npmrc"
            config_path.write_text("some other content")
            
            assert NPMConfiguration.exists_at_path(config_path) is False

    def test_exists_at_path_returns_false_for_partial_content(self):
        """Test checking file with partial valid content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / ".npmrc"
            
            # Only has auth token, missing registry
            config_path.write_text("//npm.pkg.github.com/:_authToken=token")
            assert NPMConfiguration.exists_at_path(config_path) is True
            
            # Only has registry, missing auth token
            config_path.write_text("@org:registry=https://npm.pkg.github.com")
            assert NPMConfiguration.exists_at_path(config_path) is False

    def test_immutability(self, valid_token):
        """Test that NPMConfiguration is immutable."""
        config = NPMConfiguration(token=valid_token)
        
        with pytest.raises(AttributeError):
            config.token = PersonalAccessToken("ghp_" + "b" * 36)
        
        with pytest.raises(AttributeError):
            config.registry_url = "https://other.registry.com"
        
        with pytest.raises(AttributeError):
            config.organisation = "@other-org"

    def test_http_registry_url_handling(self, valid_token):
        """Test handling of HTTP (non-HTTPS) registry URLs."""
        config = NPMConfiguration(
            token=valid_token,
            registry_url="http://insecure.registry.com"
        )
        content = config.generate_config_content()
        
        # Should strip protocol correctly
        assert "//insecure.registry.com/:_authToken=" in content
        assert "http://" not in content.split("_authToken")[0]
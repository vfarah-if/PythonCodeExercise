"""Unit tests for NPMRCFileService."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.setup_environment.domain.entities import NPMRCConfiguration
from src.setup_environment.domain.value_objects import PersonalAccessToken
from src.setup_environment.infrastructure.npmrc import NPMRCFileService


class TestNPMRCFileService:
    """Test suite for NPMRCFileService."""

    @pytest.fixture
    def temp_home_dir(self):
        """Create a temporary home directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def npmrc_service(self, temp_home_dir):
        """Create an NPMRCFileService with temporary home directory."""
        return NPMRCFileService(home_dir=temp_home_dir)

    @pytest.fixture
    def valid_token(self):
        """Create a valid personal access token."""
        return PersonalAccessToken("ghp_" + "a" * 36)

    def test_config_exists_returns_false_when_file_missing(self, npmrc_service):
        """Test config_exists returns False when .npmrc doesn't exist."""
        assert npmrc_service.config_exists() is False

    def test_config_exists_returns_true_when_file_exists(
        self, npmrc_service, temp_home_dir
    ):
        """Test config_exists returns True when .npmrc exists."""
        npmrc_path = temp_home_dir / ".npmrc"
        npmrc_path.write_text("some content")

        assert npmrc_service.config_exists() is True

    def test_get_config_path_returns_correct_path(self, npmrc_service, temp_home_dir):
        """Test get_config_path returns the correct path."""
        expected_path = temp_home_dir / ".npmrc"
        assert npmrc_service.get_config_path() == expected_path

    def test_get_config_path_uses_home_directory_by_default(self):
        """Test that default home directory is used when not specified."""
        service = NPMRCFileService()
        assert service.get_config_path() == Path.home() / ".npmrc"

    def test_has_github_token_returns_false_when_file_missing(self, npmrc_service):
        """Test has_github_token returns False when .npmrc doesn't exist."""
        assert npmrc_service.has_github_token() is False

    def test_has_github_token_returns_false_when_no_token(
        self, npmrc_service, temp_home_dir
    ):
        """Test has_github_token returns False when file has no token."""
        npmrc_path = temp_home_dir / ".npmrc"
        npmrc_path.write_text("registry=https://registry.npmjs.org/")

        assert npmrc_service.has_github_token() is False

    def test_has_github_token_returns_true_when_token_present(
        self, npmrc_service, temp_home_dir
    ):
        """Test has_github_token returns True when token is present."""
        npmrc_path = temp_home_dir / ".npmrc"
        npmrc_path.write_text(
            "//npm.pkg.github.com/:_authToken=ghp_xxxxx\n"
            "@org:registry=https://npm.pkg.github.com"
        )

        assert npmrc_service.has_github_token() is True

    def test_has_github_token_returns_false_on_read_error(
        self, npmrc_service, temp_home_dir
    ):
        """Test has_github_token returns False when file can't be read."""
        npmrc_path = temp_home_dir / ".npmrc"
        npmrc_path.mkdir()  # Create as directory instead of file

        assert npmrc_service.has_github_token() is False

    def test_write_config_creates_new_file(
        self, npmrc_service, temp_home_dir, valid_token
    ):
        """Test write_config creates new .npmrc file."""
        config = NPMRCConfiguration(token=valid_token)
        npmrc_path = temp_home_dir / ".npmrc"

        npmrc_service.write_config(config)

        assert npmrc_path.exists()
        content = npmrc_path.read_text()
        assert valid_token.value in content
        assert "npm.pkg.github.com" in content
        assert "@webuild-ai:registry" in content

    def test_write_config_overwrites_existing_github_config(
        self, npmrc_service, temp_home_dir, valid_token
    ):
        """Test write_config overwrites existing GitHub configuration."""
        npmrc_path = temp_home_dir / ".npmrc"
        npmrc_path.write_text(
            "//npm.pkg.github.com/:_authToken=old_token\n"
            "@webuild-ai:registry=https://npm.pkg.github.com\n"
            "other-setting=value"
        )

        new_config = NPMRCConfiguration(token=valid_token)
        npmrc_service.write_config(new_config)

        content = npmrc_path.read_text()
        assert valid_token.value in content
        assert "old_token" not in content
        # Other settings should be preserved
        assert "other-setting=value" in content

    def test_write_config_preserves_non_github_settings(
        self, npmrc_service, temp_home_dir, valid_token
    ):
        """Test write_config preserves non-GitHub settings."""
        npmrc_path = temp_home_dir / ".npmrc"
        npmrc_path.write_text(
            "registry=https://registry.npmjs.org/\nsave-exact=true\nprogress=false"
        )

        config = NPMRCConfiguration(token=valid_token)
        npmrc_service.write_config(config)

        content = npmrc_path.read_text()
        # GitHub config should be added
        assert valid_token.value in content
        # Other settings should be preserved
        assert "registry=https://registry.npmjs.org/" in content
        assert "save-exact=true" in content
        assert "progress=false" in content

    @patch("click.confirm")
    @patch("click.prompt")
    @patch("webbrowser.open")
    @patch("builtins.input")
    def test_prompt_for_token_success(
        self,
        mock_input,
        mock_webbrowser,
        mock_click_prompt,
        mock_click_confirm,
        npmrc_service,
        valid_token,
    ):
        """Test prompt_for_token with valid token input."""
        mock_input.return_value = ""  # For "Press Enter to continue"
        mock_click_prompt.return_value = valid_token.value

        result = npmrc_service.prompt_for_token()

        assert result == valid_token
        mock_webbrowser.assert_called_once_with(
            "https://github.com/settings/tokens/new"
        )
        mock_click_prompt.assert_called_once()

    @patch("click.confirm")
    @patch("click.prompt")
    @patch("webbrowser.open")
    @patch("builtins.input")
    def test_prompt_for_token_retries_on_invalid(
        self,
        mock_input,
        mock_webbrowser,
        mock_click_prompt,
        mock_click_confirm,
        npmrc_service,
        valid_token,
    ):
        """Test prompt_for_token retries on invalid token."""
        mock_input.return_value = ""  # For "Press Enter to continue"
        # First empty, then invalid, then valid
        mock_click_prompt.side_effect = ["", "invalid_token", valid_token.value]
        mock_click_confirm.return_value = True  # Retry on invalid

        result = npmrc_service.prompt_for_token()

        assert result == valid_token
        assert mock_click_prompt.call_count == 3

    @patch("click.prompt")
    @patch("webbrowser.open")
    @patch("builtins.input")
    def test_prompt_for_token_handles_browser_error(
        self, mock_input, mock_webbrowser, mock_click_prompt, npmrc_service, valid_token
    ):
        """Test prompt_for_token handles browser open error."""
        mock_input.return_value = ""  # For "Press Enter to continue"
        mock_webbrowser.side_effect = Exception("Browser error")
        mock_click_prompt.return_value = valid_token.value

        # Should not raise exception
        result = npmrc_service.prompt_for_token()

        assert result == valid_token

    @patch("click.prompt")
    @patch("click.echo")
    @patch("webbrowser.open")
    @patch("builtins.input")
    def test_prompt_for_token_provides_instructions(
        self,
        mock_input,
        mock_webbrowser,
        mock_click_echo,
        mock_click_prompt,
        npmrc_service,
        valid_token,
    ):
        """Test prompt_for_token provides clear instructions."""
        mock_input.return_value = ""  # For "Press Enter to continue"
        mock_click_prompt.return_value = valid_token.value

        npmrc_service.prompt_for_token()

        # Check that instructions were displayed via click.echo
        echo_calls = [str(call) for call in mock_click_echo.call_args_list]
        instructions_text = " ".join(echo_calls)

        assert "Personal Access Token" in instructions_text
        assert "write:packages" in instructions_text
        assert "read:packages" in instructions_text
        assert "delete:packages" in instructions_text
        assert "repo" in instructions_text

    @patch("click.confirm")
    @patch("click.prompt")
    @patch("webbrowser.open")
    @patch("builtins.input")
    def test_prompt_for_token_user_cancellation(
        self,
        mock_input,
        mock_webbrowser,
        mock_click_prompt,
        mock_click_confirm,
        npmrc_service,
    ):
        """Test prompt_for_token handles user cancellation."""
        mock_input.return_value = ""  # For "Press Enter to continue"
        mock_click_prompt.return_value = "invalid_token"
        mock_click_confirm.return_value = False  # User doesn't want to retry

        with pytest.raises(ValueError, match="Token creation cancelled by user"):
            npmrc_service.prompt_for_token()

"""Unit tests for PersonalAccessToken value object."""

import pytest

from src.setup_environment.domain.value_objects import PersonalAccessToken


class TestPersonalAccessToken:
    """Test suite for PersonalAccessToken value object."""

    def test_create_with_valid_classic_token(self):
        """Test creating token with valid classic format."""
        valid_token = "ghp_" + "a" * 36
        token = PersonalAccessToken(valid_token)
        assert token.value == valid_token

    def test_create_with_valid_fine_grained_token(self):
        """Test creating token with valid fine-grained format."""
        valid_token = "github_pat_" + "a" * 82
        token = PersonalAccessToken(valid_token)
        assert token.value == valid_token

    def test_raises_error_for_empty_token(self):
        """Test that empty token raises ValueError."""
        with pytest.raises(ValueError, match="Personal access token cannot be empty"):
            PersonalAccessToken("")

    def test_raises_error_for_invalid_format(self):
        """Test that invalid format raises ValueError."""
        invalid_tokens = [
            "invalid_token",
            "ghp_short",
            "github_pat_short",
            "ghs_wrongprefix",
            "ghp_" + "a" * 35,  # Too short
            "ghp_" + "a" * 37,  # Too long
            "github_pat_" + "a" * 81,  # Too short
            "github_pat_" + "a" * 83,  # Too long
        ]
        
        for invalid_token in invalid_tokens:
            with pytest.raises(ValueError, match="Invalid token format"):
                PersonalAccessToken(invalid_token)

    def test_string_representation_masks_token(self):
        """Test that string representation masks the token for security."""
        token = PersonalAccessToken("ghp_" + "a" * 36)
        str_repr = str(token)
        assert str_repr == "ghp_...aaaa"
        assert token.value not in str_repr

    def test_repr_masks_token(self):
        """Test that repr also masks the token."""
        token = PersonalAccessToken("ghp_" + "a" * 36)
        repr_str = repr(token)
        assert "PersonalAccessToken(ghp_...aaaa)" == repr_str
        assert token.value not in repr_str

    def test_short_token_masking(self):
        """Test masking of tokens shorter than 8 characters."""
        # This would normally be invalid, but testing the masking logic
        class TestToken(PersonalAccessToken):
            def __post_init__(self):
                pass  # Skip validation for this test
        
        token = TestToken("short")
        assert str(token) == "***"

    def test_immutability(self):
        """Test that PersonalAccessToken is immutable."""
        token = PersonalAccessToken("ghp_" + "a" * 36)
        
        with pytest.raises(AttributeError):
            token.value = "ghp_" + "b" * 36

    @pytest.mark.parametrize("valid_token", [
        "ghp_" + "a" * 36,
        "ghp_" + "A" * 36,
        "ghp_" + "1" * 36,
        "ghp_" + "aA1" * 12,
        "github_pat_" + "a" * 82,
        "github_pat_" + "A" * 82,
        "github_pat_" + "1" * 82,
        "github_pat_" + "aA1_" * 20 + "aa",
    ])
    def test_valid_token_formats(self, valid_token):
        """Test various valid token formats."""
        token = PersonalAccessToken(valid_token)
        assert token.value == valid_token

    def test_token_equality(self):
        """Test token equality based on value."""
        token1 = PersonalAccessToken("ghp_" + "a" * 36)
        token2 = PersonalAccessToken("ghp_" + "a" * 36)
        token3 = PersonalAccessToken("ghp_" + "b" * 36)
        
        assert token1 == token2
        assert token1 != token3
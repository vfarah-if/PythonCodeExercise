"""Tests for InstallResponse value object."""

import pytest

from src.setup_environment.domain.value_objects.install_response import InstallResponse


class TestInstallResponse:
    """Test suite for InstallResponse value object."""

    def test_from_input_yes_variations(self):
        """Test various yes inputs."""
        yes_inputs = ["y", "Y", "yes", "YES", "Yes", " y ", " YES "]

        for input_val in yes_inputs:
            response = InstallResponse.from_input(input_val)
            assert response == InstallResponse.YES
            assert response.should_install() is True
            assert response.is_all_response() is False

    def test_from_input_no_variations(self):
        """Test various no inputs."""
        no_inputs = ["n", "N", "no", "NO", "No", " n ", " NO "]

        for input_val in no_inputs:
            response = InstallResponse.from_input(input_val)
            assert response == InstallResponse.NO
            assert response.should_install() is False
            assert response.is_all_response() is False

    def test_from_input_all_variations(self):
        """Test various all inputs."""
        all_inputs = ["a", "A", "all", "ALL", "All", " a ", " ALL "]

        for input_val in all_inputs:
            response = InstallResponse.from_input(input_val)
            assert response == InstallResponse.YES_TO_ALL
            assert response.should_install() is True
            assert response.is_all_response() is True

    def test_from_input_skip_variations(self):
        """Test various skip inputs."""
        skip_inputs = [
            "s",
            "S",
            "skip",
            "SKIP",
            "Skip",
            "skip all",
            "SKIP ALL",
            " s ",
            " SKIP ",
        ]

        for input_val in skip_inputs:
            response = InstallResponse.from_input(input_val)
            assert response == InstallResponse.NO_TO_ALL
            assert response.should_install() is False
            assert response.is_all_response() is True

    def test_from_input_invalid_raises_error(self):
        """Test that invalid input raises ValueError."""
        invalid_inputs = ["z", "maybe", "quit", "1", "", "yesno"]

        for input_val in invalid_inputs:
            with pytest.raises(ValueError) as exc_info:
                InstallResponse.from_input(input_val)
            assert "Invalid response" in str(exc_info.value)
            assert "Please enter: [Y]es, [N]o, [A]ll, or [S]kip all" in str(
                exc_info.value
            )

    def test_should_install_logic(self):
        """Test should_install logic."""
        assert InstallResponse.YES.should_install() is True
        assert InstallResponse.YES_TO_ALL.should_install() is True
        assert InstallResponse.NO.should_install() is False
        assert InstallResponse.NO_TO_ALL.should_install() is False

    def test_is_all_response_logic(self):
        """Test is_all_response logic."""
        assert InstallResponse.YES.is_all_response() is False
        assert InstallResponse.NO.is_all_response() is False
        assert InstallResponse.YES_TO_ALL.is_all_response() is True
        assert InstallResponse.NO_TO_ALL.is_all_response() is True

    def test_enum_values(self):
        """Test enum string values."""
        assert InstallResponse.YES.value == "yes"
        assert InstallResponse.NO.value == "no"
        assert InstallResponse.YES_TO_ALL.value == "all"
        assert InstallResponse.NO_TO_ALL.value == "skip"

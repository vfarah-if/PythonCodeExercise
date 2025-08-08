"""Unit tests for DevFolderPath value object."""

import tempfile
from pathlib import Path

import pytest

from src.setup_environment.domain.value_objects import DevFolderPath


class TestDevFolderPath:
    """Test suite for DevFolderPath value object."""

    def test_create_with_valid_directory(self):
        """Test creating DevFolderPath with a valid directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            dev_folder = DevFolderPath(path)
            assert dev_folder.value == path
            assert dev_folder.value.exists()
            assert dev_folder.value.is_dir()

    def test_create_with_string_path(self):
        """Test creating DevFolderPath with a string path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_folder = DevFolderPath(temp_dir)
            assert dev_folder.value == Path(temp_dir)
            assert isinstance(dev_folder.value, Path)

    def test_raises_error_for_non_existent_path(self):
        """Test that non-existent path raises ValueError."""
        non_existent = Path("/this/does/not/exist")
        with pytest.raises(ValueError, match="Development folder does not exist"):
            DevFolderPath(non_existent)

    def test_raises_error_for_file_path(self):
        """Test that file path raises ValueError."""
        with tempfile.NamedTemporaryFile() as temp_file:
            file_path = Path(temp_file.name)
            with pytest.raises(ValueError, match="Path is not a directory"):
                DevFolderPath(file_path)

    def test_converts_relative_to_absolute_path(self):
        """Test that relative paths are converted to absolute."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a subdirectory
            sub_dir = Path(temp_dir) / "subdir"
            sub_dir.mkdir()
            
            # Change to temp directory and use relative path
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                dev_folder = DevFolderPath("subdir")
                assert dev_folder.value.is_absolute()
                assert dev_folder.value == sub_dir.resolve()
            finally:
                os.chdir(original_cwd)

    def test_string_representation(self):
        """Test string representation of DevFolderPath."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_folder = DevFolderPath(temp_dir)
            assert str(dev_folder) == temp_dir

    def test_create_subdirectory(self):
        """Test creating subdirectory under development folder."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_folder = DevFolderPath(temp_dir)
            
            # Create nested subdirectory
            sub_path = dev_folder.create_subdirectory("org", "repo")
            
            assert sub_path.exists()
            assert sub_path.is_dir()
            assert sub_path == Path(temp_dir) / "org" / "repo"
            
            # Test idempotency - creating again should not fail
            sub_path2 = dev_folder.create_subdirectory("org", "repo")
            assert sub_path2 == sub_path

    def test_immutability(self):
        """Test that DevFolderPath is immutable."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_folder = DevFolderPath(temp_dir)
            
            # Attempt to modify value should raise error
            with pytest.raises(AttributeError):
                dev_folder.value = Path("/different/path")

    @pytest.mark.parametrize("invalid_path", [
        None,
        "",
        " ",
    ])
    def test_invalid_path_inputs(self, invalid_path):
        """Test handling of invalid path inputs."""
        with pytest.raises((ValueError, TypeError)):
            DevFolderPath(invalid_path)
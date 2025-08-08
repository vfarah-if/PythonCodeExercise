"""Unit tests for Repository entity."""

from pathlib import Path

import pytest

from src.setup_environment.domain.entities import Repository


class TestRepository:
    """Test suite for Repository entity."""

    def test_create_repository_from_https_url(self):
        """Test creating repository from HTTPS URL."""
        url = "https://github.com/webuild-ai/repo-name.git"
        repo = Repository.from_url(url)
        
        assert repo.url == url
        assert repo.organisation == "webuild-ai"
        assert repo.name == "repo-name"

    def test_create_repository_from_https_url_without_git_extension(self):
        """Test creating repository from HTTPS URL without .git extension."""
        url = "https://github.com/webuild-ai/repo-name"
        repo = Repository.from_url(url)
        
        assert repo.url == url
        assert repo.organisation == "webuild-ai"
        assert repo.name == "repo-name"

    def test_create_repository_from_ssh_url(self):
        """Test creating repository from SSH URL."""
        url = "git@github.com:webuild-ai/repo-name.git"
        repo = Repository.from_url(url)
        
        assert repo.url == url
        assert repo.organisation == "webuild-ai"
        assert repo.name == "repo-name"

    def test_create_repository_from_ssh_url_without_git_extension(self):
        """Test creating repository from SSH URL without .git extension."""
        url = "git@github.com:webuild-ai/repo-name"
        repo = Repository.from_url(url)
        
        assert repo.url == url
        assert repo.organisation == "webuild-ai"
        assert repo.name == "repo-name"

    def test_raises_error_for_empty_url(self):
        """Test that empty URL raises ValueError."""
        with pytest.raises(ValueError, match="Repository URL cannot be empty"):
            Repository.from_url("")

    def test_raises_error_for_non_github_url(self):
        """Test that non-GitHub URL raises ValueError."""
        url = "https://gitlab.com/org/repo.git"
        with pytest.raises(ValueError, match="Only GitHub repositories are supported"):
            Repository.from_url(url)

    def test_raises_error_for_invalid_https_format(self):
        """Test that invalid HTTPS format raises ValueError."""
        invalid_urls = [
            "https://github.com/",
            "https://github.com/only-org",
            "https://github.com/",
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError, match="Invalid repository URL format"):
                Repository.from_url(url)

    def test_raises_error_for_invalid_ssh_format(self):
        """Test that invalid SSH format raises ValueError."""
        invalid_urls = [
            "git@github.com:",
            "git@github.com:only-org",
            "git@gitlab.com:org/repo.git",
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError, match="Invalid SSH repository URL"):
                Repository.from_url(url)

    def test_calculate_target_path(self):
        """Test calculating target path for repository."""
        repo = Repository.from_url("https://github.com/webuild-ai/repo-name.git")
        base_path = Path("/home/user/dev")
        
        target_path = repo.calculate_target_path(base_path)
        
        assert target_path == Path("/home/user/dev/webuild-ai/repo-name")

    def test_string_representation(self):
        """Test string representation of repository."""
        repo = Repository.from_url("https://github.com/webuild-ai/repo-name.git")
        assert str(repo) == "webuild-ai/repo-name"

    def test_equality_based_on_org_and_name(self):
        """Test that equality is based on organisation and name."""
        repo1 = Repository.from_url("https://github.com/webuild-ai/repo-name.git")
        repo2 = Repository.from_url("git@github.com:webuild-ai/repo-name.git")
        repo3 = Repository.from_url("https://github.com/other-org/repo-name.git")
        repo4 = Repository.from_url("https://github.com/webuild-ai/other-repo.git")
        
        # Same org and name, different URLs
        assert repo1 == repo2
        
        # Different org
        assert repo1 != repo3
        
        # Different name
        assert repo1 != repo4

    def test_inequality_with_non_repository_object(self):
        """Test inequality with non-Repository objects."""
        repo = Repository.from_url("https://github.com/webuild-ai/repo-name.git")
        
        assert repo != "webuild-ai/repo-name"
        assert repo != None
        assert repo != 42

    def test_immutability(self):
        """Test that Repository is immutable."""
        repo = Repository.from_url("https://github.com/webuild-ai/repo-name.git")
        
        with pytest.raises(AttributeError):
            repo.url = "https://github.com/other-org/other-repo.git"
        
        with pytest.raises(AttributeError):
            repo.organisation = "other-org"
        
        with pytest.raises(AttributeError):
            repo.name = "other-repo"

    @pytest.mark.parametrize("url,expected_org,expected_name", [
        ("https://github.com/facebook/react.git", "facebook", "react"),
        ("https://github.com/microsoft/vscode", "microsoft", "vscode"),
        ("git@github.com:torvalds/linux.git", "torvalds", "linux"),
        ("https://github.com/user-name/repo-with-dashes.git", "user-name", "repo-with-dashes"),
        ("https://github.com/org123/repo_with_underscores", "org123", "repo_with_underscores"),
    ])
    def test_various_repository_formats(self, url, expected_org, expected_name):
        """Test parsing various repository URL formats."""
        repo = Repository.from_url(url)
        assert repo.organisation == expected_org
        assert repo.name == expected_name
"""Git service implementation using GitPython."""

import subprocess
from pathlib import Path

from src.setup_environment.application.interfaces import CloneResult, GitService
from src.setup_environment.application.interfaces.git_service import CloneStatus
from src.setup_environment.domain.entities import Repository


class GitPythonService(GitService):
    """Git service implementation using subprocess for Git operations."""

    def clone_repository(self, repository: Repository, target_path: Path) -> CloneResult:
        """Clone a repository to the specified path."""
        try:
            # Ensure parent directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Clone the repository
            result = subprocess.run(
                ["git", "clone", repository.url, str(target_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            
            if result.returncode == 0:
                return CloneResult(
                    repository=repository,
                    status=CloneStatus.SUCCESS,
                    path=target_path,
                )
            else:
                error_message = result.stderr.strip() or result.stdout.strip()
                return CloneResult(
                    repository=repository,
                    status=CloneStatus.FAILED,
                    error_message=f"Git clone failed: {error_message}",
                )
        except FileNotFoundError:
            return CloneResult(
                repository=repository,
                status=CloneStatus.FAILED,
                error_message="Git command not found. Please ensure Git is installed.",
            )
        except Exception as e:
            return CloneResult(
                repository=repository,
                status=CloneStatus.FAILED,
                error_message=f"Unexpected error: {str(e)}",
            )

    def repository_exists(self, path: Path) -> bool:
        """Check if a valid Git repository exists at the given path."""
        if not path.exists() or not path.is_dir():
            return False
        
        git_dir = path / ".git"
        if not git_dir.exists():
            return False
        
        try:
            # Verify it's a valid Git repository
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=str(path),
                capture_output=True,
                check=False,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def is_git_installed(self) -> bool:
        """Check if Git is installed and available."""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                check=False,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
        except Exception:
            return False
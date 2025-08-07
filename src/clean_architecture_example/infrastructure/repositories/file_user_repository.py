"""
File-based User Repository Implementation
Stores users in JSON files for persistence across application restarts.
Demonstrates how to implement different storage strategies.
"""
import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from ...domain.entities.user import User
from ...domain.interfaces.user_repository import UserRepository
from ...domain.value_objects.email import Email
from ...shared.exceptions.domain_exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from ...shared.exceptions.repository_exceptions import RepositoryException


class FileUserRepository(UserRepository):
    """
    File-based implementation of UserRepository.

    Stores users as JSON files in a specified directory.
    Each user is stored in a separate file named by their ID.

    Features:
    - Persistent storage
    - Thread-safe operations
    - JSON serialization/deserialization
    - Directory-based organization
    """

    def __init__(self, storage_path: str = "data/users"):
        """
        Initialize file repository.

        Args:
            storage_path: Directory path to store user files
        """
        self._storage_path = Path(storage_path)
        self._email_index_file = self._storage_path / "email_index.json"
        self._executor = ThreadPoolExecutor(max_workers=4)

        # Create storage directory if it doesn't exist
        self._storage_path.mkdir(parents=True, exist_ok=True)

        # Load email index
        self._email_index = self._load_email_index()

    def _load_email_index(self) -> dict[str, str]:
        """Load email -> user_id index from file."""
        if self._email_index_file.exists():
            try:
                with open(self._email_index_file) as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError):
                # If index is corrupted, rebuild it
                return self._rebuild_email_index()
        return {}

    def _rebuild_email_index(self) -> dict[str, str]:
        """Rebuild email index by scanning all user files."""
        index = {}

        for user_file in self._storage_path.glob("*.json"):
            if user_file.name == "email_index.json":
                continue

            try:
                with open(user_file) as f:
                    user_data = json.load(f)
                    index[user_data['email']] = user_data['id']
            except (OSError, json.JSONDecodeError, KeyError):
                # Skip corrupted files
                continue

        self._save_email_index(index)
        return index

    def _save_email_index(self, index: dict[str, str]) -> None:
        """Save email index to file."""
        try:
            with open(self._email_index_file, 'w') as f:
                json.dump(index, f, indent=2)
        except OSError as e:
            raise RepositoryException(f"Failed to save email index: {e}")

    def _user_file_path(self, user_id: str) -> Path:
        """Get file path for a user ID."""
        return self._storage_path / f"{user_id}.json"

    def _serialize_user(self, user: User) -> dict:
        """Convert User entity to JSON-serializable dictionary."""
        return {
            'id': user.id,
            'email': user.email.value,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        }

    def _deserialize_user(self, data: dict) -> User:
        """Convert dictionary to User entity."""
        # Create user with required fields
        email = Email(data['email'])

        user = User(
            email=email,
            first_name=data['first_name'],
            last_name=data['last_name'],
            is_active=data.get('is_active', True),
            created_at=datetime.fromisoformat(data['created_at'])
        )

        # Set ID and updated_at
        object.__setattr__(user, 'id', data['id'])
        user.updated_at = (
            datetime.fromisoformat(data['updated_at'])
            if data.get('updated_at') else None
        )

        return user

    async def save(self, user: User) -> User:
        """Save user to file system."""
        # Check if email already exists
        if await self.exists_with_email(user.email):
            raise UserAlreadyExistsError(user.email.value)

        def _write_user():
            user_file = self._user_file_path(user.id)
            user_data = self._serialize_user(user)

            with open(user_file, 'w') as f:
                json.dump(user_data, f, indent=2)

            return user

        # Execute file I/O in thread pool to avoid blocking
        result = await asyncio.get_event_loop().run_in_executor(
            self._executor, _write_user
        )

        # Update email index
        self._email_index[user.email.value] = user.id
        self._save_email_index(self._email_index)

        return result

    async def get_by_id(self, user_id: str) -> User | None:
        """Get user by ID from file system."""
        def _read_user():
            user_file = self._user_file_path(user_id)

            if not user_file.exists():
                return None

            try:
                with open(user_file) as f:
                    user_data = json.load(f)
                return self._deserialize_user(user_data)
            except (OSError, json.JSONDecodeError, KeyError):
                return None

        return await asyncio.get_event_loop().run_in_executor(
            self._executor, _read_user
        )

    async def get_by_email(self, email: Email) -> User | None:
        """Get user by email using index."""
        user_id = self._email_index.get(email.value)
        if user_id:
            return await self.get_by_id(user_id)
        return None

    async def get_all(self) -> list[User]:
        """Get all users from file system."""
        def _read_all_users():
            users = []

            for user_file in self._storage_path.glob("*.json"):
                if user_file.name == "email_index.json":
                    continue

                try:
                    with open(user_file) as f:
                        user_data = json.load(f)
                    user = self._deserialize_user(user_data)
                    users.append(user)
                except (OSError, json.JSONDecodeError, KeyError):
                    # Skip corrupted files
                    continue

            return users

        return await asyncio.get_event_loop().run_in_executor(
            self._executor, _read_all_users
        )

    async def update(self, user: User) -> User:
        """Update user in file system."""
        user_file = self._user_file_path(user.id)

        if not user_file.exists():
            raise UserNotFoundError(user.id, "id")

        def _update_user():
            user_data = self._serialize_user(user)

            with open(user_file, 'w') as f:
                json.dump(user_data, f, indent=2)

            return user

        result = await asyncio.get_event_loop().run_in_executor(
            self._executor, _update_user
        )

        # Update email index
        self._email_index[user.email.value] = user.id
        self._save_email_index(self._email_index)

        return result

    async def delete(self, user_id: str) -> bool:
        """Delete user from file system."""
        user_file = self._user_file_path(user_id)

        if not user_file.exists():
            return False

        # Get user email for index cleanup
        user = await self.get_by_id(user_id)

        def _delete_user():
            user_file.unlink()
            return True

        result = await asyncio.get_event_loop().run_in_executor(
            self._executor, _delete_user
        )

        # Remove from email index
        if user:
            self._email_index.pop(user.email.value, None)
            self._save_email_index(self._email_index)

        return result

    async def exists_with_email(self, email: Email) -> bool:
        """Check if user exists with given email."""
        return email.value in self._email_index

    # Cleanup method

    def close(self) -> None:
        """Close the repository and cleanup resources."""
        self._executor.shutdown(wait=True)

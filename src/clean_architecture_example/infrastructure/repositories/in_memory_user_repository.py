"""
In-Memory User Repository Implementation
Concrete implementation of UserRepository using in-memory storage.
Perfect for testing, demos, and development.
Similar to C# in-memory implementations for unit testing.
"""

from ...domain.entities.user import User
from ...domain.interfaces.user_repository import UserRepository
from ...domain.value_objects.email import Email
from ...shared.exceptions.domain_exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)


class InMemoryUserRepository(UserRepository):
    """
    In-memory implementation of UserRepository.

    Stores users in memory using dictionaries.
    Useful for:
    - Unit testing (no external dependencies)
    - Development and demos
    - Rapid prototyping
    """

    def __init__(self):
        """Initialize empty storage."""
        self._users: dict[str, User] = {}
        self._email_index: dict[str, str] = {}  # email -> user_id mapping

    async def save(self, user: User) -> User:
        """
        Save user to memory storage.

        Args:
            user: User entity to save

        Returns:
            Saved user entity

        Raises:
            UserAlreadyExistsError: If user with same email exists
        """
        # Check if email already exists
        if await self.exists_with_email(user.email):
            raise UserAlreadyExistsError(user.email.value)

        # Store user and update email index
        self._users[user.id] = user
        self._email_index[user.email.value] = user.id

        return user

    async def get_by_id(self, user_id: str) -> User | None:
        """Get user by ID from memory."""
        return self._users.get(user_id)

    async def get_by_email(self, email: Email) -> User | None:
        """Get user by email from memory."""
        user_id = self._email_index.get(email.value)
        if user_id:
            return self._users.get(user_id)
        return None

    async def get_all(self) -> list[User]:
        """Get all users from memory."""
        return list(self._users.values())

    async def update(self, user: User) -> User:
        """
        Update user in memory storage.

        Args:
            user: User entity with updated data

        Returns:
            Updated user entity

        Raises:
            UserNotFoundError: If user doesn't exist
        """
        if user.id not in self._users:
            raise UserNotFoundError(user.id, "id")

        # Update user in storage
        self._users[user.id] = user

        # Update email index if email changed
        self._email_index[user.email.value] = user.id

        return user

    async def delete(self, user_id: str) -> bool:
        """
        Delete user from memory storage.

        Args:
            user_id: ID of user to delete

        Returns:
            True if deleted, False if not found
        """
        user = self._users.get(user_id)
        if not user:
            return False

        # Remove from both storage and email index
        del self._users[user_id]
        del self._email_index[user.email.value]

        return True

    async def exists_with_email(self, email: Email) -> bool:
        """Check if user exists with given email."""
        return email.value in self._email_index

    # Helper methods for testing and debugging

    def clear(self) -> None:
        """Clear all data (useful for testing)."""
        self._users.clear()
        self._email_index.clear()

    def count(self) -> int:
        """Get total number of users stored."""
        return len(self._users)

    def get_all_emails(self) -> list[str]:
        """Get all stored email addresses (useful for debugging)."""
        return list(self._email_index.keys())

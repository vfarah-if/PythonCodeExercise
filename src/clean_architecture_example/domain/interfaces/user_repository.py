"""
User Repository Interface (Port)
Defines contract for data access without implementation details.
Similar to C# interfaces - pure abstraction.
"""
from abc import ABC, abstractmethod

from ..entities.user import User
from ..value_objects.email import Email


class UserRepository(ABC):
    """
    Abstract repository interface defining user data access contract.

    This is a "Port" in Hexagonal Architecture - it defines what we need
    without specifying how it's implemented. The actual implementation
    (Adapter) will be in the Infrastructure layer.

    Benefits:
    - Domain layer independent of data storage
    - Easy to test with mocks
    - Can swap implementations (in-memory, SQL, NoSQL, etc.)
    - Follows Dependency Inversion Principle
    """

    @abstractmethod
    async def save(self, user: User) -> User:
        """
        Save a user entity.

        Args:
            user: User entity to save

        Returns:
            Saved user entity

        Raises:
            UserAlreadyExistsError: If user with same email already exists
            RepositoryError: For other persistence errors
        """
        pass

    @abstractmethod
    async def get_by_id(self, user_id: str) -> User | None:
        """
        Retrieve user by unique identifier.

        Args:
            user_id: Unique user identifier

        Returns:
            User entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: Email) -> User | None:
        """
        Retrieve user by email address.

        Args:
            email: User's email address

        Returns:
            User entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_all(self) -> list[User]:
        """
        Retrieve all users.

        Returns:
            List of all user entities
        """
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """
        Update an existing user.

        Args:
            user: User entity with updated data

        Returns:
            Updated user entity

        Raises:
            UserNotFoundError: If user doesn't exist
            RepositoryError: For other persistence errors
        """
        pass

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """
        Delete a user by ID.

        Args:
            user_id: Unique user identifier

        Returns:
            True if user was deleted, False if not found

        Raises:
            RepositoryError: For persistence errors
        """
        pass

    @abstractmethod
    async def exists_with_email(self, email: Email) -> bool:
        """
        Check if a user exists with the given email.

        Args:
            email: Email address to check

        Returns:
            True if user exists with this email, False otherwise
        """
        pass

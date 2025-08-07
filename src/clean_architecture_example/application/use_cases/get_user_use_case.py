"""
Get User Use Case
Implements business logic for user retrieval.
"""

from ...domain.interfaces.user_repository import UserRepository
from ...domain.value_objects.email import Email
from ...shared.exceptions.domain_exceptions import UserNotFoundError
from ..dto.user_dto import UserListResponse, UserResponse


class GetUserUseCase:
    """
    Use case for retrieving user information.

    Supports multiple retrieval methods:
    - By ID
    - By email
    - All users
    """

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def get_by_id(self, user_id: str) -> UserResponse:
        """
        Get user by unique identifier.

        Args:
            user_id: User's unique identifier

        Returns:
            User response DTO

        Raises:
            UserNotFoundError: If user doesn't exist
        """
        user = await self._user_repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundError(user_id, "id")

        return self._map_to_response(user)

    async def get_by_email(self, email_str: str) -> UserResponse:
        """
        Get user by email address.

        Args:
            email_str: User's email address

        Returns:
            User response DTO

        Raises:
            UserNotFoundError: If user doesn't exist
            ValueError: If email format is invalid
        """
        email = Email(email_str)  # This validates the email format
        user = await self._user_repository.get_by_email(email)

        if not user:
            raise UserNotFoundError(email.value, "email")

        return self._map_to_response(user)

    async def get_all(self) -> UserListResponse:
        """
        Get all users.

        Returns:
            List response containing all users
        """
        users = await self._user_repository.get_all()

        user_responses = [
            self._map_to_response(user)
            for user in users
        ]

        return UserListResponse.from_users(user_responses)

    def _map_to_response(self, user) -> UserResponse:
        """Map domain entity to response DTO."""
        return UserResponse(
            id=user.id,
            email=user.email.value,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

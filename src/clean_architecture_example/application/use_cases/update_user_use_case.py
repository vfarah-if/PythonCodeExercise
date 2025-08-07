"""
Update User Use Case
Implements business logic for user updates.
"""

from ...domain.interfaces.user_repository import UserRepository
from ...shared.exceptions.domain_exceptions import UserNotFoundError
from ..dto.user_dto import UpdateUserRequest, UserResponse


class UpdateUserUseCase:
    """
    Use case for updating user information.

    Handles partial updates - only specified fields are changed.
    """

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def execute(self, request: UpdateUserRequest) -> UserResponse:
        """
        Execute user update use case.

        Args:
            request: Update request with user ID and fields to change

        Returns:
            Updated user response DTO

        Raises:
            UserNotFoundError: If user doesn't exist
            ValueError: If update data is invalid
        """
        # 1. Retrieve existing user
        user = await self._user_repository.get_by_id(request.user_id)

        if not user:
            raise UserNotFoundError(request.user_id, "id")

        # 2. Apply updates using domain methods
        if request.first_name is not None or request.last_name is not None:
            # Use domain entity's business method for name updates
            new_first = (
                request.first_name
                if request.first_name is not None
                else user.first_name
            )
            new_last = (
                request.last_name if request.last_name is not None else user.last_name
            )
            user.update_name(new_first.strip(), new_last.strip())

        # 3. Persist changes
        updated_user = await self._user_repository.update(user)

        # 4. Return response DTO
        return self._map_to_response(updated_user)

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
            updated_at=user.updated_at,
        )

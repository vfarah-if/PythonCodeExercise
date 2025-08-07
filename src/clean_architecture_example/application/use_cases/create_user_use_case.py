"""
Create User Use Case
Implements business logic for user creation.
Similar to C# application services - orchestrates domain operations.
"""

from ...domain.entities.user import User
from ...domain.interfaces.user_repository import UserRepository
from ...domain.value_objects.email import Email
from ...shared.exceptions.domain_exceptions import UserAlreadyExistsError
from ..dto.user_dto import CreateUserRequest, UserResponse


class CreateUserUseCase:
    """
    Use case for creating a new user.

    Handles:
    - Input validation
    - Business rule enforcement
    - Coordination between domain objects
    - Error handling and translation

    This follows the Single Responsibility Principle -
    only responsible for user creation logic.
    """

    def __init__(self, user_repository: UserRepository):
        """
        Initialize use case with dependencies.

        Args:
            user_repository: Repository for user data access

        Note: Dependencies are injected (Dependency Inversion Principle)
        """
        self._user_repository = user_repository

    async def execute(self, request: CreateUserRequest) -> UserResponse:
        """
        Execute the create user use case.

        Args:
            request: User creation request data

        Returns:
            Response containing created user data

        Raises:
            UserAlreadyExistsError: If user with email already exists
            ValueError: If request data is invalid
        """
        # 1. Validate and create value objects
        email = Email(request.email)

        # 2. Check business rules
        if await self._user_repository.exists_with_email(email):
            raise UserAlreadyExistsError(email.value)

        # 3. Create domain entity
        user = User(
            email=email,
            first_name=request.first_name.strip(),
            last_name=request.last_name.strip()
        )

        # 4. Persist through repository
        saved_user = await self._user_repository.save(user)

        # 5. Return response DTO
        return self._map_to_response(saved_user)

    def _map_to_response(self, user: User) -> UserResponse:
        """
        Map domain entity to response DTO.

        This keeps domain entities from leaking to external layers.
        """
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

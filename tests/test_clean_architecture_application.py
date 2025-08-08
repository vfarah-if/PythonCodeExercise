"""
Tests for Application Layer
Tests use cases and application services.
Uses mocks for dependencies to isolate application logic.
"""

from unittest.mock import AsyncMock

import pytest

from src.clean_architecture_example.application.dto.user_dto import (
    CreateUserRequest,
    UpdateUserRequest,
    UserResponse,
)
from src.clean_architecture_example.application.use_cases.create_user_use_case import (
    CreateUserUseCase,
)
from src.clean_architecture_example.application.use_cases.get_user_use_case import (
    GetUserUseCase,
)
from src.clean_architecture_example.application.use_cases.update_user_use_case import (
    UpdateUserUseCase,
)
from src.clean_architecture_example.domain.entities.user import User
from src.clean_architecture_example.domain.value_objects.email import Email
from src.clean_architecture_example.shared.exceptions.domain_exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)


class TestCreateUserUseCase:
    """Test CreateUserUseCase behaviour."""

    @pytest.fixture
    def mock_repository(self):
        """Create mock repository for testing."""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository):
        """Create use case with mock repository."""
        return CreateUserUseCase(mock_repository)

    @pytest.mark.asyncio
    async def test_create_user_success(self, use_case, mock_repository):
        """Test successful user creation."""
        # Arrange
        request = CreateUserRequest(
            email="new@example.com", first_name="New", last_name="User"
        )

        # Mock repository responses
        mock_repository.exists_with_email.return_value = False

        created_user = User(
            email=Email("new@example.com"), first_name="New", last_name="User"
        )
        mock_repository.save.return_value = created_user

        # Act
        result = await use_case.execute(request)

        # Assert
        assert isinstance(result, UserResponse)
        assert result.email == "new@example.com"
        assert result.first_name == "New"
        assert result.last_name == "User"
        assert result.full_name == "New User"
        assert result.is_active is True

        # Verify repository calls
        mock_repository.exists_with_email.assert_called_once()
        mock_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_with_existing_email_fails(
        self, use_case, mock_repository
    ):
        """Test creating user with existing email fails."""
        # Arrange
        request = CreateUserRequest(
            email="existing@example.com", first_name="Test", last_name="User"
        )

        mock_repository.exists_with_email.return_value = True

        # Act & Assert
        with pytest.raises(UserAlreadyExistsError) as exc_info:
            await use_case.execute(request)

        assert "existing@example.com" in str(exc_info.value)
        mock_repository.exists_with_email.assert_called_once()
        mock_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_user_with_invalid_email_fails(
        self, use_case, mock_repository
    ):
        """Test creating user with invalid email fails."""
        # Arrange
        request = CreateUserRequest(
            email="invalid-email", first_name="Test", last_name="User"
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email format"):
            await use_case.execute(request)

        # Repository should not be called
        mock_repository.exists_with_email.assert_not_called()
        mock_repository.save.assert_not_called()


class TestGetUserUseCase:
    """Test GetUserUseCase behaviour."""

    @pytest.fixture
    def mock_repository(self):
        """Create mock repository for testing."""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository):
        """Create use case with mock repository."""
        return GetUserUseCase(mock_repository)

    @pytest.fixture
    def sample_user(self):
        """Create sample user for testing."""
        return User(
            email=Email("test@example.com"), first_name="Test", last_name="User"
        )

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, use_case, mock_repository, sample_user):
        """Test successful user retrieval by ID."""
        # Arrange
        user_id = sample_user.id
        mock_repository.get_by_id.return_value = sample_user

        # Act
        result = await use_case.get_by_id(user_id)

        # Assert
        assert isinstance(result, UserResponse)
        assert result.id == user_id
        assert result.email == "test@example.com"
        assert result.full_name == "Test User"

        mock_repository.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, use_case, mock_repository):
        """Test user retrieval by ID when user doesn't exist."""
        # Arrange
        user_id = "non-existent-id"
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFoundError) as exc_info:
            await use_case.get_by_id(user_id)

        assert user_id in str(exc_info.value)
        assert "id" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(
        self, use_case, mock_repository, sample_user
    ):
        """Test successful user retrieval by email."""
        # Arrange
        email_str = "test@example.com"
        mock_repository.get_by_email.return_value = sample_user

        # Act
        result = await use_case.get_by_email(email_str)

        # Assert
        assert isinstance(result, UserResponse)
        assert result.email == email_str

        # Verify called with Email value object
        mock_repository.get_by_email.assert_called_once()
        call_args = mock_repository.get_by_email.call_args[0][0]
        assert isinstance(call_args, Email)
        assert call_args.value == email_str

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, use_case, mock_repository):
        """Test user retrieval by email when user doesn't exist."""
        # Arrange
        email_str = "notfound@example.com"
        mock_repository.get_by_email.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFoundError) as exc_info:
            await use_case.get_by_email(email_str)

        assert email_str in str(exc_info.value)
        assert "email" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_user_by_invalid_email_format(self, use_case, mock_repository):
        """Test user retrieval with invalid email format."""
        # Arrange
        invalid_email = "invalid-email-format"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email format"):
            await use_case.get_by_email(invalid_email)

        mock_repository.get_by_email.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_all_users_success(self, use_case, mock_repository):
        """Test successful retrieval of all users."""
        # Arrange
        users = [
            User(email=Email("user1@example.com"), first_name="User", last_name="One"),
            User(email=Email("user2@example.com"), first_name="User", last_name="Two"),
        ]
        mock_repository.get_all.return_value = users

        # Act
        result = await use_case.get_all()

        # Assert
        assert result.total_count == 2
        assert len(result.users) == 2

        assert result.users[0].email == "user1@example.com"
        assert result.users[1].email == "user2@example.com"

        mock_repository.get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_users_empty_list(self, use_case, mock_repository):
        """Test retrieval when no users exist."""
        # Arrange
        mock_repository.get_all.return_value = []

        # Act
        result = await use_case.get_all()

        # Assert
        assert result.total_count == 0
        assert len(result.users) == 0


class TestUpdateUserUseCase:
    """Test UpdateUserUseCase behaviour."""

    @pytest.fixture
    def mock_repository(self):
        """Create mock repository for testing."""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository):
        """Create use case with mock repository."""
        return UpdateUserUseCase(mock_repository)

    @pytest.fixture
    def sample_user(self):
        """Create sample user for testing."""
        return User(
            email=Email("update@example.com"), first_name="Original", last_name="Name"
        )

    @pytest.mark.asyncio
    async def test_update_user_name_success(
        self, use_case, mock_repository, sample_user
    ):
        """Test successful user name update."""
        # Arrange
        request = UpdateUserRequest(
            user_id=sample_user.id, first_name="Updated", last_name="Name"
        )

        mock_repository.get_by_id.return_value = sample_user
        mock_repository.update.return_value = sample_user

        # Act
        result = await use_case.execute(request)

        # Assert
        assert isinstance(result, UserResponse)
        assert result.first_name == "Updated"
        assert result.last_name == "Name"
        assert result.full_name == "Updated Name"

        mock_repository.get_by_id.assert_called_once_with(sample_user.id)
        mock_repository.update.assert_called_once_with(sample_user)

    @pytest.mark.asyncio
    async def test_update_user_partial_update(
        self, use_case, mock_repository, sample_user
    ):
        """Test partial user update (only first name)."""
        # Arrange
        request = UpdateUserRequest(
            user_id=sample_user.id,
            first_name="NewFirst",
            last_name=None,  # Don't update last name
        )

        mock_repository.get_by_id.return_value = sample_user
        mock_repository.update.return_value = sample_user

        # Act
        result = await use_case.execute(request)

        # Assert
        assert result.first_name == "NewFirst"
        assert result.last_name == "Name"  # Should keep original

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, use_case, mock_repository):
        """Test updating non-existent user."""
        # Arrange
        request = UpdateUserRequest(
            user_id="non-existent-id", first_name="New", last_name="Name"
        )

        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFoundError) as exc_info:
            await use_case.execute(request)

        assert "non-existent-id" in str(exc_info.value)
        mock_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_user_with_invalid_name(
        self, use_case, mock_repository, sample_user
    ):
        """Test updating user with invalid name."""
        # Arrange
        request = UpdateUserRequest(
            user_id=sample_user.id,
            first_name="",  # Empty name should fail
            last_name="Valid",
        )

        mock_repository.get_by_id.return_value = sample_user

        # Act & Assert
        with pytest.raises(ValueError, match="First name cannot be empty"):
            await use_case.execute(request)

        mock_repository.update.assert_not_called()

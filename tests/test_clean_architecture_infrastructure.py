"""
Tests for Infrastructure Layer
Tests repository implementations and external integrations.
These tests may use real or fake external dependencies.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from src.clean_architecture_example.domain.entities.user import User
from src.clean_architecture_example.domain.value_objects.email import Email
from src.clean_architecture_example.infrastructure.repositories.file_user_repository import (
    FileUserRepository,
)
from src.clean_architecture_example.infrastructure.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)
from src.clean_architecture_example.shared.exceptions.domain_exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)


class TestInMemoryUserRepository:
    """Test in-memory repository implementation."""

    @pytest.fixture
    def repository(self):
        """Create fresh in-memory repository for each test."""
        return InMemoryUserRepository()

    @pytest.fixture
    def sample_user(self):
        """Create sample user for testing."""
        return User(
            email=Email("test@example.com"), first_name="Test", last_name="User"
        )

    @pytest.mark.asyncio
    async def test_save_user_success(self, repository, sample_user):
        """Test saving a user successfully."""
        # Act
        saved_user = await repository.save(sample_user)

        # Assert
        assert saved_user == sample_user
        assert saved_user.id == sample_user.id
        assert repository.count() == 1

    @pytest.mark.asyncio
    async def test_save_duplicate_email_fails(self, repository, sample_user):
        """Test saving user with duplicate email fails."""
        # Arrange
        await repository.save(sample_user)

        duplicate_user = User(
            email=Email("test@example.com"),  # Same email
            first_name="Different",
            last_name="User",
        )

        # Act & Assert
        with pytest.raises(UserAlreadyExistsError) as exc_info:
            await repository.save(duplicate_user)

        assert "test@example.com" in str(exc_info.value)
        assert repository.count() == 1  # Should still be 1

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, repository, sample_user):
        """Test retrieving user by ID."""
        # Arrange
        await repository.save(sample_user)

        # Act
        found_user = await repository.get_by_id(sample_user.id)

        # Assert
        assert found_user is not None
        assert found_user.id == sample_user.id
        assert found_user.email == sample_user.email

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test retrieving non-existent user by ID."""
        # Act
        found_user = await repository.get_by_id("non-existent-id")

        # Assert
        assert found_user is None

    @pytest.mark.asyncio
    async def test_get_by_email_success(self, repository, sample_user):
        """Test retrieving user by email."""
        # Arrange
        await repository.save(sample_user)

        # Act
        found_user = await repository.get_by_email(sample_user.email)

        # Assert
        assert found_user is not None
        assert found_user.email == sample_user.email
        assert found_user.id == sample_user.id

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, repository):
        """Test retrieving non-existent user by email."""
        # Act
        found_user = await repository.get_by_email(Email("notfound@example.com"))

        # Assert
        assert found_user is None

    @pytest.mark.asyncio
    async def test_get_all_users(self, repository):
        """Test retrieving all users."""
        # Arrange
        user1 = User(
            email=Email("user1@example.com"), first_name="User", last_name="One"
        )
        user2 = User(
            email=Email("user2@example.com"), first_name="User", last_name="Two"
        )

        await repository.save(user1)
        await repository.save(user2)

        # Act
        all_users = await repository.get_all()

        # Assert
        assert len(all_users) == 2
        user_ids = {user.id for user in all_users}
        assert user1.id in user_ids
        assert user2.id in user_ids

    @pytest.mark.asyncio
    async def test_get_all_empty_repository(self, repository):
        """Test retrieving all users from empty repository."""
        # Act
        all_users = await repository.get_all()

        # Assert
        assert len(all_users) == 0

    @pytest.mark.asyncio
    async def test_update_user_success(self, repository, sample_user):
        """Test updating an existing user."""
        # Arrange
        await repository.save(sample_user)
        sample_user.update_name("Updated", "Name")

        # Act
        updated_user = await repository.update(sample_user)

        # Assert
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"

        # Verify it's persisted
        found_user = await repository.get_by_id(sample_user.id)
        assert found_user.first_name == "Updated"

    @pytest.mark.asyncio
    async def test_update_non_existent_user_fails(self, repository):
        """Test updating non-existent user fails."""
        # Arrange
        non_existent_user = User(
            email=Email("notexist@example.com"), first_name="Not", last_name="Exist"
        )

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await repository.update(non_existent_user)

    @pytest.mark.asyncio
    async def test_delete_user_success(self, repository, sample_user):
        """Test deleting an existing user."""
        # Arrange
        await repository.save(sample_user)

        # Act
        deleted = await repository.delete(sample_user.id)

        # Assert
        assert deleted is True
        assert repository.count() == 0

        # Verify user is gone
        found_user = await repository.get_by_id(sample_user.id)
        assert found_user is None

    @pytest.mark.asyncio
    async def test_delete_non_existent_user(self, repository):
        """Test deleting non-existent user returns False."""
        # Act
        deleted = await repository.delete("non-existent-id")

        # Assert
        assert deleted is False

    @pytest.mark.asyncio
    async def test_exists_with_email(self, repository, sample_user):
        """Test checking if user exists with email."""
        # Before saving
        exists = await repository.exists_with_email(sample_user.email)
        assert exists is False

        # After saving
        await repository.save(sample_user)
        exists = await repository.exists_with_email(sample_user.email)
        assert exists is True

    def test_clear_repository(self, repository, sample_user):
        """Test clearing repository removes all data."""
        # This is a synchronous test since clear() is not async
        # In a real async test, we'd need to run this in async context
        import asyncio

        async def test_clear():
            await repository.save(sample_user)
            assert repository.count() == 1

            repository.clear()
            assert repository.count() == 0

            all_users = await repository.get_all()
            assert len(all_users) == 0

        asyncio.run(test_clear())

    def test_helper_methods(self, repository):
        """Test repository helper methods."""
        import asyncio

        async def test_helpers():
            user1 = User(
                email=Email("test1@example.com"), first_name="Test", last_name="One"
            )
            user2 = User(
                email=Email("test2@example.com"), first_name="Test", last_name="Two"
            )

            await repository.save(user1)
            await repository.save(user2)

            # Test count
            assert repository.count() == 2

            # Test get_all_emails
            emails = repository.get_all_emails()
            assert "test1@example.com" in emails
            assert "test2@example.com" in emails
            assert len(emails) == 2

        asyncio.run(test_helpers())


class TestFileUserRepository:
    """Test file-based repository implementation."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def repository(self, temp_dir):
        """Create file repository with temporary directory."""
        repo = FileUserRepository(temp_dir)
        yield repo
        repo.close()

    @pytest.fixture
    def sample_user(self):
        """Create sample user for testing."""
        return User(
            email=Email("file@example.com"), first_name="File", last_name="User"
        )

    @pytest.mark.asyncio
    async def test_save_and_retrieve_user(self, repository, sample_user):
        """Test saving and retrieving user from file system."""
        # Save user
        saved_user = await repository.save(sample_user)
        assert saved_user.id == sample_user.id

        # Retrieve by ID
        found_user = await repository.get_by_id(sample_user.id)
        assert found_user is not None
        assert found_user.id == sample_user.id
        assert found_user.email.value == sample_user.email.value
        assert found_user.first_name == sample_user.first_name
        assert found_user.last_name == sample_user.last_name

    @pytest.mark.asyncio
    async def test_persistence_across_instances(self, temp_dir, sample_user):
        """Test data persists across repository instances."""
        # Create first repository instance and save user
        repo1 = FileUserRepository(temp_dir)
        await repo1.save(sample_user)
        repo1.close()

        # Create second repository instance and retrieve user
        repo2 = FileUserRepository(temp_dir)
        found_user = await repo2.get_by_id(sample_user.id)
        repo2.close()

        assert found_user is not None
        assert found_user.id == sample_user.id
        assert found_user.email.value == sample_user.email.value

    @pytest.mark.asyncio
    async def test_email_index_functionality(self, repository, sample_user):
        """Test email index is maintained correctly."""
        # Save user
        await repository.save(sample_user)

        # Retrieve by email
        found_user = await repository.get_by_email(sample_user.email)
        assert found_user is not None
        assert found_user.id == sample_user.id

    @pytest.mark.asyncio
    async def test_update_user_file(self, repository, sample_user):
        """Test updating user updates file correctly."""
        # Save initial user
        await repository.save(sample_user)

        # Update user
        sample_user.update_name("Updated", "FileUser")
        await repository.update(sample_user)

        # Retrieve and verify update
        found_user = await repository.get_by_id(sample_user.id)
        assert found_user.first_name == "Updated"
        assert found_user.last_name == "FileUser"
        assert found_user.updated_at is not None

    @pytest.mark.asyncio
    async def test_delete_user_removes_file(self, repository, sample_user, temp_dir):
        """Test deleting user removes file from filesystem."""
        # Save user
        await repository.save(sample_user)

        # Verify file exists
        user_file = Path(temp_dir) / f"{sample_user.id}.json"
        assert user_file.exists()

        # Delete user
        deleted = await repository.delete(sample_user.id)
        assert deleted is True

        # Verify file is removed
        assert not user_file.exists()

        # Verify user can't be found
        found_user = await repository.get_by_id(sample_user.id)
        assert found_user is None

    @pytest.mark.asyncio
    async def test_multiple_users_file_operations(self, repository):
        """Test multiple users with file operations."""
        # Create multiple users
        users = [
            User(
                email=Email(f"user{i}@example.com"),
                first_name=f"User{i}",
                last_name="Test",
            )
            for i in range(3)
        ]

        # Save all users
        for user in users:
            await repository.save(user)

        # Retrieve all users
        all_users = await repository.get_all()
        assert len(all_users) == 3

        # Verify each user can be found
        for original_user in users:
            found_user = await repository.get_by_id(original_user.id)
            assert found_user is not None
            assert found_user.email.value == original_user.email.value

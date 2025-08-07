"""
Data Transfer Objects (DTOs) for User operations.
Similar to C# DTOs - simple data containers for transferring data
between layers without exposing domain entities directly.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreateUserRequest:
    """
    DTO for user creation requests.
    Contains only the data needed to create a user.
    """

    email: str
    first_name: str
    last_name: str


@dataclass(frozen=True)
class UpdateUserRequest:
    """
    DTO for user update requests.
    Contains user ID and fields to update.
    """

    user_id: str
    first_name: str | None = None
    last_name: str | None = None


@dataclass(frozen=True)
class UserResponse:
    """
    DTO for user data responses.
    Contains user information for external consumption.
    """

    id: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None


@dataclass(frozen=True)
class UserListResponse:
    """
    DTO for user list responses.
    Contains a list of users with metadata.
    """

    users: list[UserResponse]
    total_count: int

    @classmethod
    def from_users(cls, users: list[UserResponse]) -> "UserListResponse":
        """Create response from user list"""
        return cls(users=users, total_count=len(users))

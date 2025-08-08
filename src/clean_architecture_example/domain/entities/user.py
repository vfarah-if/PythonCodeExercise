"""
User Entity
Demonstrates entity pattern - has identity and can change over time.
Similar to C# domain entities with business logic.
"""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from ..value_objects.email import Email


@dataclass
class User:
    """
    User domain entity with business identity and behaviour.

    Key characteristics:
    - Has unique identity (id)
    - Mutable state (unlike value objects)
    - Contains business logic
    - Independent of persistence concerns
    """

    # Identity field - immutable after creation
    id: str = field(init=False)

    # Core attributes
    email: Email
    first_name: str
    last_name: str

    # Optional attributes with defaults
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Initialize entity after creation (similar to constructor in C#)"""
        if not hasattr(self, "id") or not self.id:
            # Generate unique identifier
            object.__setattr__(self, "id", str(uuid.uuid4()))

        self._validate_names()

    def _validate_names(self) -> None:
        """Private validation method (similar to private methods in C#)"""
        if not self.first_name or not self.first_name.strip():
            raise ValueError("First name cannot be empty")

        if not self.last_name or not self.last_name.strip():
            raise ValueError("Last name cannot be empty")

    @property
    def full_name(self) -> str:
        """Computed property (similar to C# properties)"""
        return f"{self.first_name} {self.last_name}"

    @property
    def display_name(self) -> str:
        """Business logic for display name"""
        return f"{self.full_name} ({self.email})"

    def update_name(self, first_name: str, last_name: str) -> None:
        """
        Business method to update name with validation.
        Updates timestamp automatically.
        """
        old_first, old_last = self.first_name, self.last_name

        # Validate before changing
        self.first_name = first_name
        self.last_name = last_name

        try:
            self._validate_names()
            self.updated_at = datetime.now(UTC)
        except ValueError:
            # Rollback on validation failure
            self.first_name = old_first
            self.last_name = old_last
            raise

    def deactivate(self) -> None:
        """Business method to deactivate user"""
        if not self.is_active:
            raise ValueError("User is already inactive")

        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        """Business method to activate user"""
        if self.is_active:
            raise ValueError("User is already active")

        self.is_active = True
        self.updated_at = datetime.now(UTC)

    def __eq__(self, other) -> bool:
        """Equality based on identity (id), not all attributes"""
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on identity for use in sets/dicts"""
        return hash(self.id)

    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return f"User(id={self.id}, email={self.email}, name={self.full_name})"

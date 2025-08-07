"""
Email Value Object
Demonstrates value object pattern - immutable with validation.
Similar to C# value types or records, but with behaviour.
"""
import re
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class Email:
    """
    Value object representing an email address.

    Key characteristics:
    - Immutable (frozen=True)
    - Validates format on creation
    - Equality based on value, not identity
    - No database concerns (pure domain logic)
    """

    value: str

    # Class-level validation pattern (similar to static readonly in C#)
    _EMAIL_PATTERN: ClassVar[re.Pattern] = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    def __post_init__(self) -> None:
        """Validate email format on creation (similar to constructor validation in C#)"""
        if not self.value:
            raise ValueError("Email cannot be empty")

        if not self._EMAIL_PATTERN.match(self.value):
            raise ValueError(f"Invalid email format: {self.value}")

        # Convert to lowercase for consistency
        object.__setattr__(self, 'value', self.value.lower())

    def __str__(self) -> str:
        """String representation"""
        return self.value

    @property
    def domain(self) -> str:
        """Extract domain part of email"""
        return self.value.split('@')[1]

    @property
    def local_part(self) -> str:
        """Extract local part of email (before @)"""
        return self.value.split('@')[0]

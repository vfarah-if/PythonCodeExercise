"""
Validation Utilities
Common validation functions used across the application.
Similar to C# validation attributes or FluentValidation.
"""

import re
from typing import Any


class ValidationError(ValueError):
    """Raised when validation fails."""

    def __init__(self, field: str, value: Any, message: str):
        self.field = field
        self.value = value
        self.message = message
        super().__init__(f"Validation failed for '{field}': {message}")


class ValidationResult:
    """Result of validation operation."""

    def __init__(self):
        self.errors: list[ValidationError] = []

    @property
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return len(self.errors) == 0

    def add_error(self, field: str, value: Any, message: str) -> None:
        """Add validation error."""
        self.errors.append(ValidationError(field, value, message))

    def get_error_messages(self) -> list[str]:
        """Get all error messages."""
        return [error.message for error in self.errors]


def validate_required(value: Any, field_name: str) -> None:
    """
    Validate that a value is not None or empty.

    Args:
        value: Value to validate
        field_name: Name of the field being validated

    Raises:
        ValidationError: If value is None or empty
    """
    if value is None:
        raise ValidationError(field_name, value, "is required")

    if isinstance(value, str) and not value.strip():
        raise ValidationError(field_name, value, "cannot be empty")


def validate_string_length(
    value: str, field_name: str, min_length: int = 0, max_length: int | None = None
) -> None:
    """
    Validate string length constraints.

    Args:
        value: String value to validate
        field_name: Name of the field
        min_length: Minimum allowed length
        max_length: Maximum allowed length (optional)

    Raises:
        ValidationError: If length constraints are violated
    """
    if not isinstance(value, str):
        raise ValidationError(field_name, value, "must be a string")

    length = len(value.strip())

    if length < min_length:
        raise ValidationError(
            field_name, value, f"must be at least {min_length} characters long"
        )

    if max_length is not None and length > max_length:
        raise ValidationError(
            field_name, value, f"must be no more than {max_length} characters long"
        )


def validate_email_format(email: str, field_name: str = "email") -> None:
    """
    Validate email format using regex.

    Args:
        email: Email string to validate
        field_name: Name of the field

    Raises:
        ValidationError: If email format is invalid
    """
    if not isinstance(email, str):
        raise ValidationError(field_name, email, "must be a string")

    email = email.strip().lower()

    if not email:
        raise ValidationError(field_name, email, "cannot be empty")

    # Basic email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        raise ValidationError(field_name, email, "is not a valid email format")


def validate_name(name: str, field_name: str) -> None:
    """
    Validate person name (first name, last name, etc.).

    Args:
        name: Name to validate
        field_name: Name of the field

    Raises:
        ValidationError: If name is invalid
    """
    validate_required(name, field_name)
    validate_string_length(name, field_name, min_length=1, max_length=50)

    # Check for invalid characters (optional - depends on requirements)
    if not re.match(r"^[a-zA-Z\s\'-]+$", name.strip()):
        raise ValidationError(
            field_name,
            name,
            "can only contain letters, spaces, hyphens, and apostrophes",
        )


def validate_multiple(
    validators: list[tuple], result: ValidationResult = None
) -> ValidationResult:
    """
    Run multiple validations and collect all errors.

    Args:
        validators: List of (validator_func, *args) tuples
        result: Existing ValidationResult to add to (optional)

    Returns:
        ValidationResult with all validation errors
    """
    if result is None:
        result = ValidationResult()

    for validator_tuple in validators:
        validator_func = validator_tuple[0]
        args = validator_tuple[1:]

        try:
            validator_func(*args)
        except ValidationError as e:
            result.errors.append(e)

    return result

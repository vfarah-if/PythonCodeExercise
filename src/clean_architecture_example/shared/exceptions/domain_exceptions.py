"""
Domain Exception Hierarchy
Custom exceptions for domain-specific errors.
Similar to C# custom exception classes with inheritance.
"""


class DomainError(Exception):
    """
    Base exception for all domain-related errors.
    Similar to C# base exception classes.
    """

    def __init__(self, message: str, inner_exception: Exception | None = None):
        """
        Initialize domain exception.

        Args:
            message: Error message
            inner_exception: Underlying exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.inner_exception = inner_exception


class UserDomainError(DomainError):
    """Base exception for user-related domain errors."""

    pass


class UserNotFoundError(UserDomainError):
    """Raised when a user cannot be found."""

    def __init__(self, identifier: str, identifier_type: str = "id"):
        message = f"User not found with {identifier_type}: {identifier}"
        super().__init__(message)
        self.identifier = identifier
        self.identifier_type = identifier_type


class UserAlreadyExistsError(UserDomainError):
    """Raised when attempting to create a user that already exists."""

    def __init__(self, email: str):
        message = f"User already exists with email: {email}"
        super().__init__(message)
        self.email = email


class InvalidUserDataError(UserDomainError):
    """Raised when user data is invalid."""

    def __init__(self, field: str, value: str, reason: str):
        message = f"Invalid {field} '{value}': {reason}"
        super().__init__(message)
        self.field = field
        self.value = value
        self.reason = reason


class UserStateError(UserDomainError):
    """Raised when user is in invalid state for operation."""

    def __init__(self, operation: str, current_state: str):
        message = f"Cannot {operation}: user is {current_state}"
        super().__init__(message)
        self.operation = operation
        self.current_state = current_state

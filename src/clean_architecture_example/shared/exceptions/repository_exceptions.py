"""
Repository Exception Hierarchy
Exceptions for repository/persistence layer errors.
Similar to C# data access exceptions.
"""

from .domain_exceptions import DomainError


class RepositoryException(DomainError):
    """Base exception for repository-related errors."""

    pass


class RepositoryConnectionError(RepositoryException):
    """Raised when repository cannot connect to data store."""

    def __init__(self, data_store: str, details: str | None = None):
        message = f"Failed to connect to {data_store}"
        if details:
            message += f": {details}"
        super().__init__(message)
        self.data_store = data_store


class RepositoryTimeoutError(RepositoryException):
    """Raised when repository operation times out."""

    def __init__(self, operation: str, timeout_seconds: float):
        message = (
            f"Repository operation '{operation}' timed out after {timeout_seconds}s"
        )
        super().__init__(message)
        self.operation = operation
        self.timeout_seconds = timeout_seconds


class DataIntegrityError(RepositoryException):
    """Raised when data integrity constraints are violated."""

    def __init__(self, constraint: str, details: str | None = None):
        message = f"Data integrity violation: {constraint}"
        if details:
            message += f" - {details}"
        super().__init__(message)
        self.constraint = constraint


class ConcurrencyError(RepositoryException):
    """Raised when concurrent modification conflicts occur."""

    def __init__(self, entity_id: str, entity_type: str):
        message = f"Concurrent modification detected for {entity_type} {entity_id}"
        super().__init__(message)
        self.entity_id = entity_id
        self.entity_type = entity_type

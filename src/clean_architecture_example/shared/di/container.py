"""
Dependency Injection Container
Simple DI container for managing dependencies and their lifetimes.
Similar to C# DI containers but lightweight and Python-specific.
"""
import inspect
from collections.abc import Callable
from enum import Enum
from typing import Any, TypeVar

T = TypeVar('T')


class ServiceLifetime(Enum):
    """Service lifetime options."""
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


class ServiceDescriptor:
    """Describes how to create a service."""

    def __init__(
        self,
        service_type: type,
        implementation: Any = None,
        factory: Callable | None = None,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    ):
        self.service_type = service_type
        self.implementation = implementation
        self.factory = factory
        self.lifetime = lifetime
        self.instance = None  # For singleton storage


class DIContainer:
    """
    Simple Dependency Injection Container.

    Features:
    - Service registration with different lifetimes
    - Automatic constructor injection
    - Factory method support
    - Circular dependency detection
    - Similar to .NET Core DI container
    """

    def __init__(self):
        self._services: dict[type, ServiceDescriptor] = {}
        self._resolving_stack: set = set()  # For circular dependency detection

    def register_singleton(self, service_type: type[T], implementation: type[T] | None = None) -> 'DIContainer':
        """
        Register a singleton service.

        Args:
            service_type: Interface or base type
            implementation: Concrete implementation (optional if service_type is concrete)
        """
        impl = implementation or service_type
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=impl,
            lifetime=ServiceLifetime.SINGLETON
        )
        self._services[service_type] = descriptor
        return self

    def register_transient(self, service_type: type[T], implementation: type[T] | None = None) -> 'DIContainer':
        """
        Register a transient service (new instance each time).

        Args:
            service_type: Interface or base type
            implementation: Concrete implementation (optional if service_type is concrete)
        """
        impl = implementation or service_type
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=impl,
            lifetime=ServiceLifetime.TRANSIENT
        )
        self._services[service_type] = descriptor
        return self

    def register_factory(
        self,
        service_type: type[T],
        factory: Callable[['DIContainer'], T],
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    ) -> 'DIContainer':
        """
        Register a service with a factory method.

        Args:
            service_type: Service type to register
            factory: Factory function that takes container and returns instance
            lifetime: Service lifetime
        """
        descriptor = ServiceDescriptor(
            service_type=service_type,
            factory=factory,
            lifetime=lifetime
        )
        self._services[service_type] = descriptor
        return self

    def resolve(self, service_type: type[T]) -> T:
        """
        Resolve a service from the container.

        Args:
            service_type: Type of service to resolve

        Returns:
            Service instance

        Raises:
            ValueError: If service not registered or circular dependency detected
        """
        # Check for circular dependencies
        if service_type in self._resolving_stack:
            service_name = getattr(service_type, '__name__', str(service_type))
            raise ValueError(f"Circular dependency detected for {service_name}")

        # Get service descriptor
        descriptor = self._services.get(service_type)
        if not descriptor:
            service_name = getattr(service_type, '__name__', str(service_type))
            raise ValueError(f"Service {service_name} not registered")

        # Handle singleton
        if descriptor.lifetime == ServiceLifetime.SINGLETON and descriptor.instance:
            return descriptor.instance

        # Add to resolving stack
        self._resolving_stack.add(service_type)

        try:
            # Create instance
            if descriptor.factory:
                instance = descriptor.factory(self)
            else:
                instance = self._create_instance(descriptor.implementation)

            # Store singleton instance
            if descriptor.lifetime == ServiceLifetime.SINGLETON:
                descriptor.instance = instance

            return instance

        finally:
            # Remove from resolving stack
            self._resolving_stack.discard(service_type)

    def _create_instance(self, implementation_type: type[T]) -> T:
        """
        Create instance with constructor injection.

        Args:
            implementation_type: Type to instantiate

        Returns:
            Created instance
        """
        # Get constructor signature
        signature = inspect.signature(implementation_type.__init__)

        # Resolve constructor parameters (skip 'self', *args, **kwargs)
        kwargs = {}
        for param_name, param in signature.parameters.items():
            if param_name == 'self':
                continue

            # Skip *args and **kwargs parameters
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue

            # Get parameter type annotation
            param_type = param.annotation
            if param_type == inspect.Parameter.empty:
                raise ValueError(
                    f"Parameter '{param_name}' in {implementation_type.__name__} "
                    "must have type annotation for dependency injection"
                )

            # Handle string annotations (forward references)
            if isinstance(param_type, str):
                # For forward references, we need to resolve them in the global context
                # This is a simplified approach - in production, you'd want proper resolution
                param_type = param_type

            # Resolve dependency
            kwargs[param_name] = self.resolve(param_type)

        # Create instance
        return implementation_type(**kwargs)

    def is_registered(self, service_type: type) -> bool:
        """Check if a service type is registered."""
        return service_type in self._services

    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()

    def get_registered_services(self) -> dict[type, ServiceDescriptor]:
        """Get all registered services (useful for debugging)."""
        return self._services.copy()


# Global container instance (similar to .NET's IServiceProvider)
_default_container = DIContainer()


def get_container() -> DIContainer:
    """Get the default global container."""
    return _default_container


def configure_services(config_func: Callable[[DIContainer], None]) -> None:
    """
    Configure services in the default container.

    Args:
        config_func: Function that configures the container
    """
    config_func(_default_container)

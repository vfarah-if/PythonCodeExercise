"""
Tests for Dependency Injection Container
Tests DI container functionality and service resolution.
"""

from typing import Protocol

import pytest

from src.clean_architecture_example.shared.di.container import (
    DIContainer,
    ServiceLifetime,
)


# Test interfaces and classes for DI testing
class ITestService(Protocol):
    """Test service interface."""

    def get_message(self) -> str:
        pass


class ServiceImpl:
    """Test service implementation."""

    def __init__(self):
        pass

    def get_message(self) -> str:
        return "Hello from TestService"


class DependentService:
    """Service that depends on ITestService."""

    def __init__(self, test_service: ITestService):
        self.test_service = test_service

    def get_combined_message(self) -> str:
        return f"Combined: {self.test_service.get_message()}"


class ComplexDependentService:
    """Service with multiple dependencies."""

    def __init__(self, test_service: ITestService, dependent_service: DependentService):
        self.test_service = test_service
        self.dependent_service = dependent_service

    def get_complex_message(self) -> str:
        return f"Complex: {self.dependent_service.get_combined_message()}"


class TestDIContainer:
    """Test DI container functionality."""

    @pytest.fixture
    def container(self):
        """Create fresh container for each test."""
        return DIContainer()

    def test_register_and_resolve_transient(self, container):
        """Test registering and resolving transient services."""
        # Arrange
        container.register_transient(ITestService, ServiceImpl)

        # Act
        service1 = container.resolve(ITestService)
        service2 = container.resolve(ITestService)

        # Assert
        assert isinstance(service1, ServiceImpl)
        assert isinstance(service2, ServiceImpl)
        assert service1 is not service2  # Different instances for transient
        assert service1.get_message() == "Hello from TestService"

    def test_register_and_resolve_singleton(self, container):
        """Test registering and resolving singleton services."""
        # Arrange
        container.register_singleton(ITestService, ServiceImpl)

        # Act
        service1 = container.resolve(ITestService)
        service2 = container.resolve(ITestService)

        # Assert
        assert isinstance(service1, ServiceImpl)
        assert isinstance(service2, ServiceImpl)
        assert service1 is service2  # Same instance for singleton

    def test_register_concrete_class(self, container):
        """Test registering concrete class without interface."""
        # Arrange
        container.register_transient(ServiceImpl)

        # Act
        service = container.resolve(ServiceImpl)

        # Assert
        assert isinstance(service, ServiceImpl)
        assert service.get_message() == "Hello from TestService"

    def test_constructor_injection(self, container):
        """Test automatic constructor injection."""
        # Arrange
        container.register_singleton(ITestService, ServiceImpl)
        container.register_transient(DependentService)

        # Act
        service = container.resolve(DependentService)

        # Assert
        assert isinstance(service, DependentService)
        assert isinstance(service.test_service, ServiceImpl)
        assert service.get_combined_message() == "Combined: Hello from TestService"

    def test_complex_dependency_resolution(self, container):
        """Test resolving service with multiple levels of dependencies."""
        # Arrange
        container.register_singleton(ITestService, ServiceImpl)
        container.register_transient(DependentService)
        container.register_transient(ComplexDependentService)

        # Act
        service = container.resolve(ComplexDependentService)

        # Assert
        assert isinstance(service, ComplexDependentService)
        assert isinstance(service.test_service, ServiceImpl)
        assert isinstance(service.dependent_service, DependentService)

        expected_message = "Complex: Combined: Hello from TestService"
        assert service.get_complex_message() == expected_message

    def test_factory_registration(self, container):
        """Test registering service with factory method."""

        # Arrange
        def create_test_service(c: DIContainer) -> ServiceImpl:
            service = ServiceImpl()
            # Could modify service here if needed
            return service

        container.register_factory(ITestService, create_test_service)

        # Act
        service = container.resolve(ITestService)

        # Assert
        assert isinstance(service, ServiceImpl)
        assert service.get_message() == "Hello from TestService"

    def test_factory_with_dependencies(self, container):
        """Test factory method that uses other services."""
        # Arrange
        container.register_singleton(ITestService, ServiceImpl)

        def create_dependent_service(c: DIContainer) -> DependentService:
            test_service = c.resolve(ITestService)
            return DependentService(test_service)

        container.register_factory(DependentService, create_dependent_service)

        # Act
        service = container.resolve(DependentService)

        # Assert
        assert isinstance(service, DependentService)
        assert service.get_combined_message() == "Combined: Hello from TestService"

    def test_unregistered_service_raises_error(self, container):
        """Test resolving unregistered service raises error."""
        # Act & Assert
        with pytest.raises(ValueError, match="Service .* not registered"):
            container.resolve(ITestService)

    def test_circular_dependency_detection(self, container):
        """Test circular dependency detection."""

        # Create a factory that will cause circular dependency
        def create_service_a(container: DIContainer):
            container.resolve(ServiceB)  # This will cause circular dependency
            return ServiceImpl()

        class ServiceB:
            def __init__(self, service_a: ServiceImpl):
                self.service_a = service_a

        # Arrange - register with factory that causes circular dependency
        container.register_factory(ServiceImpl, create_service_a)
        container.register_transient(ServiceB)

        # Act & Assert
        with pytest.raises(ValueError, match="Circular dependency detected"):
            container.resolve(ServiceImpl)

    def test_missing_type_annotation_raises_error(self, container):
        """Test missing type annotation raises error."""

        class BadService:
            def __init__(self, dependency):  # No type annotation
                self.dependency = dependency

        # Arrange
        container.register_transient(BadService)

        # Act & Assert
        with pytest.raises(ValueError, match="must have type annotation"):
            container.resolve(BadService)

    def test_is_registered(self, container):
        """Test checking if service is registered."""
        # Before registration
        assert not container.is_registered(ITestService)

        # After registration
        container.register_transient(ITestService, ServiceImpl)
        assert container.is_registered(ITestService)

    def test_clear_container(self, container):
        """Test clearing container removes all registrations."""
        # Arrange
        container.register_transient(ITestService, ServiceImpl)
        assert container.is_registered(ITestService)

        # Act
        container.clear()

        # Assert
        assert not container.is_registered(ITestService)

        with pytest.raises(ValueError, match="not registered"):
            container.resolve(ITestService)

    def test_get_registered_services(self, container):
        """Test getting all registered services."""
        # Arrange
        container.register_transient(ITestService, ServiceImpl)
        container.register_singleton(DependentService)

        # Act
        services = container.get_registered_services()

        # Assert
        assert len(services) == 2
        assert ITestService in services
        assert DependentService in services

        # Verify it's a copy (mutations don't affect container)
        services.clear()
        assert container.is_registered(ITestService)

    def test_singleton_factory_creates_once(self, container):
        """Test singleton factory is only called once."""
        call_count = 0

        def create_service(c: DIContainer) -> ServiceImpl:
            nonlocal call_count
            call_count += 1
            return ServiceImpl()

        # Arrange
        container.register_factory(
            ITestService, create_service, ServiceLifetime.SINGLETON
        )

        # Act
        service1 = container.resolve(ITestService)
        service2 = container.resolve(ITestService)

        # Assert
        assert call_count == 1  # Factory called only once
        assert service1 is service2  # Same instance returned


class TestServiceDescriptor:
    """Test ServiceDescriptor functionality."""

    def test_service_descriptor_creation(self):
        """Test creating service descriptor with different parameters."""
        from src.clean_architecture_example.shared.di.container import ServiceDescriptor

        # Test with implementation
        descriptor1 = ServiceDescriptor(
            service_type=ITestService,
            implementation=ServiceImpl,
            lifetime=ServiceLifetime.SINGLETON,
        )

        assert descriptor1.service_type == ITestService
        assert descriptor1.implementation == ServiceImpl
        assert descriptor1.lifetime == ServiceLifetime.SINGLETON
        assert descriptor1.factory is None
        assert descriptor1.instance is None

        # Test with factory
        def factory(c):
            return ServiceImpl()

        descriptor2 = ServiceDescriptor(
            service_type=ITestService,
            factory=factory,
            lifetime=ServiceLifetime.TRANSIENT,
        )

        assert descriptor2.factory == factory
        assert descriptor2.implementation is None

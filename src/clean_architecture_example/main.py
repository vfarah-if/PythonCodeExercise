"""
Application Entry Point and Dependency Configuration
Demonstrates how to wire up all dependencies and start the application.
Similar to C# Program.cs or Startup.cs in .NET applications.
"""
import asyncio
from pathlib import Path

from .application.use_cases.create_user_use_case import CreateUserUseCase
from .application.use_cases.get_user_use_case import GetUserUseCase
from .application.use_cases.update_user_use_case import UpdateUserUseCase
from .domain.interfaces.user_repository import UserRepository
from .infrastructure.repositories.file_user_repository import FileUserRepository
from .infrastructure.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)
from .presentation.cli.user_cli import UserCLI
from .shared.di.container import DIContainer, ServiceLifetime


def configure_dependencies(container: DIContainer, use_file_storage: bool = False) -> None:
    """
    Configure all application dependencies.

    This is where we decide which concrete implementations to use.
    Similar to ConfigureServices in .NET Core.

    Args:
        container: DI container to configure
        use_file_storage: Whether to use file storage or in-memory storage
    """

    # Configure repository (Infrastructure Layer)
    if use_file_storage:
        # Use file-based storage for persistence
        storage_path = Path("data/users")
        container.register_factory(
            UserRepository,
            lambda c: FileUserRepository(str(storage_path)),
            ServiceLifetime.SINGLETON  # Single instance for file operations
        )
    else:
        # Use in-memory storage (good for demos/testing)
        container.register_singleton(
            UserRepository,
            InMemoryUserRepository
        )

    # Configure use cases (Application Layer)
    container.register_transient(CreateUserUseCase)
    container.register_transient(GetUserUseCase)
    container.register_transient(UpdateUserUseCase)

    # Configure presentation layer
    container.register_transient(UserCLI)


async def main() -> None:
    """
    Main application entry point.

    This is where everything comes together:
    1. Configure dependencies
    2. Resolve root object
    3. Start application
    """

    print("🏗️  Clean Architecture Demo")
    print("Configuring dependencies...")

    # Create and configure DI container
    container = DIContainer()

    # Ask user for storage preference
    storage_choice = input("Use file storage? (y/N): ").strip().lower()
    use_file_storage = storage_choice in ['y', 'yes']

    # Configure all dependencies
    configure_dependencies(container, use_file_storage)

    if use_file_storage:
        print("📁 Using file-based storage (data will persist)")
    else:
        print("💾 Using in-memory storage (data will be lost on exit)")

    print("✅ Dependencies configured")
    print()

    # Resolve and start the CLI application
    try:
        cli = container.resolve(UserCLI)
        await cli.run_interactive()
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        print("Check your configuration and try again.")


def create_demo_data(container: DIContainer) -> None:
    """
    Create some demo data for testing.
    This demonstrates how to use the application programmatically.
    """

    async def _create_demo():
        create_use_case = container.resolve(CreateUserUseCase)

        from .application.dto.user_dto import CreateUserRequest

        # Create demo users
        demo_users = [
            CreateUserRequest("john.doe@example.com", "John", "Doe"),
            CreateUserRequest("jane.smith@example.com", "Jane", "Smith"),
            CreateUserRequest("bob.wilson@example.com", "Bob", "Wilson")
        ]

        print("Creating demo users...")

        for user_request in demo_users:
            try:
                user = await create_use_case.execute(user_request)
                print(f"✅ Created: {user.full_name} ({user.email})")
            except Exception as e:
                print(f"❌ Failed to create {user_request.first_name}: {e}")

        print()

    asyncio.run(_create_demo())


if __name__ == "__main__":
    """Entry point when running this module directly."""

    # Handle demo data creation
    if input("Create demo data? (y/N): ").strip().lower() in ['y', 'yes']:
        print()
        container = DIContainer()
        configure_dependencies(container, use_file_storage=False)
        create_demo_data(container)

    # Start main application
    asyncio.run(main())

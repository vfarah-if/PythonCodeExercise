"""
Command Line Interface for User Management
Demonstrates how the presentation layer interacts with use cases.
Similar to C# console applications or CLI controllers.
"""

from ...application.dto.user_dto import CreateUserRequest, UpdateUserRequest
from ...application.use_cases.create_user_use_case import CreateUserUseCase
from ...application.use_cases.get_user_use_case import GetUserUseCase
from ...application.use_cases.update_user_use_case import UpdateUserUseCase
from ...shared.exceptions.domain_exceptions import (
    DomainError,
    UserAlreadyExistsError,
    UserNotFoundError,
)


class UserCLI:
    """
    Command-line interface for user management operations.

    This is the presentation layer - it handles:
    - User input/output
    - Command parsing
    - Error display
    - Calling appropriate use cases
    """

    def __init__(
        self,
        create_user_use_case: CreateUserUseCase,
        get_user_use_case: GetUserUseCase,
        update_user_use_case: UpdateUserUseCase,
    ):
        """
        Initialize CLI with use case dependencies.

        Note: Dependencies are injected, not created here.
        This follows Dependency Inversion Principle.
        """
        self._create_user = create_user_use_case
        self._get_user = get_user_use_case
        self._update_user = update_user_use_case

    async def run_interactive(self) -> None:
        """Run interactive CLI session."""
        print("👥 User Management CLI")
        print("Type 'help' for available commands or 'exit' to quit")
        print()

        while True:
            try:
                command = input("> ").strip().lower()

                if command == "exit":
                    print("Goodbye!")
                    break
                elif command == "help":
                    self._show_help()
                elif command == "create":
                    await self._handle_create_user()
                elif command == "list":
                    await self._handle_list_users()
                elif command == "get":
                    await self._handle_get_user()
                elif command == "update":
                    await self._handle_update_user()
                elif command == "":
                    continue
                else:
                    print(
                        f"Unknown command: {command}. Type 'help' for available commands."
                    )

                print()  # Add spacing between commands

            except KeyboardInterrupt:
                print("\\nGoodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

    def _show_help(self) -> None:
        """Display available commands."""
        print("📋 Available Commands:")
        print("  create  - Create a new user")
        print("  list    - List all users")
        print("  get     - Get user by ID or email")
        print("  update  - Update user information")
        print("  help    - Show this help message")
        print("  exit    - Exit the application")

    async def _handle_create_user(self) -> None:
        """Handle user creation command."""
        try:
            print("Creating new user...")

            email = input("Email: ").strip()
            first_name = input("First name: ").strip()
            last_name = input("Last name: ").strip()

            if not email or not first_name or not last_name:
                print("❌ All fields are required")
                return

            request = CreateUserRequest(
                email=email, first_name=first_name, last_name=last_name
            )

            user = await self._create_user.execute(request)

            print("✅ User created successfully!")
            print(f"   ID: {user.id}")
            print(f"   Name: {user.full_name}")
            print(f"   Email: {user.email}")

        except UserAlreadyExistsError as e:
            print(f"❌ {e.message}")
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
        except DomainError as e:
            print(f"❌ {e.message}")

    async def _handle_list_users(self) -> None:
        """Handle list users command."""
        try:
            response = await self._get_user.get_all()

            if not response.users:
                print("📝 No users found")
                return

            print(f"👥 Found {response.total_count} user(s):")
            print()

            for user in response.users:
                status = "🟢 Active" if user.is_active else "🔴 Inactive"
                print(f"  📋 {user.full_name}")
                print(f"     ID: {user.id}")
                print(f"     Email: {user.email}")
                print(f"     Status: {status}")
                print(f"     Created: {user.created_at.strftime('%Y-%m-%d %H:%M')}")
                print()

        except DomainError as e:
            print(f"❌ {e.message}")

    async def _handle_get_user(self) -> None:
        """Handle get user command."""
        try:
            search_by = input("Search by (id/email): ").strip().lower()

            if search_by not in ["id", "email"]:
                print("❌ Please specify 'id' or 'email'")
                return

            search_value = input(f"Enter {search_by}: ").strip()

            if not search_value:
                print(f"❌ {search_by} cannot be empty")
                return

            if search_by == "id":
                user = await self._get_user.get_by_id(search_value)
            else:
                user = await self._get_user.get_by_email(search_value)

            status = "🟢 Active" if user.is_active else "🔴 Inactive"

            print("👤 User Details:")
            print(f"   ID: {user.id}")
            print(f"   Name: {user.full_name}")
            print(f"   Email: {user.email}")
            print(f"   Status: {status}")
            print(f"   Created: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if user.updated_at:
                print(f"   Updated: {user.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")

        except UserNotFoundError as e:
            print(f"❌ {e.message}")
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
        except DomainError as e:
            print(f"❌ {e.message}")

    async def _handle_update_user(self) -> None:
        """Handle update user command."""
        try:
            user_id = input("User ID to update: ").strip()

            if not user_id:
                print("❌ User ID is required")
                return

            # Get current user details
            try:
                current_user = await self._get_user.get_by_id(user_id)
                print("\\nCurrent details:")
                print(f"  Name: {current_user.full_name}")
                print(f"  Email: {current_user.email}")
                print()
            except UserNotFoundError:
                print("❌ User not found")
                return

            print("Enter new values (press Enter to keep current value):")

            first_name_input = input(
                f"First name [{current_user.first_name}]: "
            ).strip()
            last_name_input = input(f"Last name [{current_user.last_name}]: ").strip()

            # Only update if new values provided
            first_name = first_name_input if first_name_input else None
            last_name = last_name_input if last_name_input else None

            if not first_name and not last_name:
                print("Info: No changes made")
                return

            request = UpdateUserRequest(
                user_id=user_id, first_name=first_name, last_name=last_name
            )

            updated_user = await self._update_user.execute(request)

            print("✅ User updated successfully!")
            print(f"   New name: {updated_user.full_name}")

        except UserNotFoundError as e:
            print(f"❌ {e.message}")
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
        except DomainError as e:
            print(f"❌ {e.message}")


# Factory function for creating CLI with dependencies
async def create_user_cli() -> UserCLI:
    """
    Factory function to create UserCLI with all dependencies.
    This would typically use a DI container in a real application.
    """
    from ...shared.di.container import get_container

    # Resolve dependencies from container
    container = get_container()

    create_use_case = container.resolve(CreateUserUseCase)
    get_use_case = container.resolve(GetUserUseCase)
    update_use_case = container.resolve(UpdateUserUseCase)

    return UserCLI(create_use_case, get_use_case, update_use_case)

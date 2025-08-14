"""Value object for user installation responses."""

from enum import Enum


class InstallResponse(Enum):
    """User response to software installation prompt."""

    YES = "yes"
    NO = "no"
    YES_TO_ALL = "all"
    NO_TO_ALL = "skip"

    @classmethod
    def from_input(cls, user_input: str) -> "InstallResponse":
        """Parse user input to response enum.

        Args:
            user_input: User's input string

        Returns:
            InstallResponse enum value

        Raises:
            ValueError: If input is not recognized
        """
        normalized = user_input.lower().strip()

        # Map various inputs to responses
        mapping = {
            "y": cls.YES,
            "yes": cls.YES,
            "n": cls.NO,
            "no": cls.NO,
            "a": cls.YES_TO_ALL,
            "all": cls.YES_TO_ALL,
            "s": cls.NO_TO_ALL,
            "skip": cls.NO_TO_ALL,
            "skip all": cls.NO_TO_ALL,
        }

        if normalized in mapping:
            return mapping[normalized]

        raise ValueError(
            f"Invalid response: '{user_input}'. "
            "Please enter: [Y]es, [N]o, [A]ll, or [S]kip all"
        )

    def should_install(self) -> bool:
        """Check if this response means to install."""
        return self in (self.YES, self.YES_TO_ALL)

    def is_all_response(self) -> bool:
        """Check if this is an 'all' type response."""
        return self in (self.YES_TO_ALL, self.NO_TO_ALL)

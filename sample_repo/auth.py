"""Sample auth module for demo."""

from typing import Optional


class AuthService:
    """Handles user authentication."""

    def __init__(self):
        self._users = {"alice": "secret"}

    def login_user(self, username: str, password: str) -> bool:
        """Return True if credentials match."""
        stored = self._users.get(username)
        return stored is not None and stored == password


def logout_user(username: str) -> None:
    """Log out a user (noop in demo)."""
    print(f"Logging out {username}")

"""
GitHub integration package.

Provides clean separation between PyGithub boundary and business logic.
"""

from typing import Any
from .boundary import GitHubApiBoundary
from . import converters


# Import service-related classes only when needed to avoid
# forcing requests-cache dependency for boundary-only usage
def get_github_service(*args: Any, **kwargs: Any) -> Any:
    """Get GitHubService with lazy import to avoid dependency issues."""
    from .service import GitHubService

    return GitHubService(*args, **kwargs)


def create_github_service(*args: Any, **kwargs: Any) -> Any:
    """Create configured GitHubService with lazy import."""
    from .service import create_github_service as _create_github_service

    return _create_github_service(*args, **kwargs)


__all__ = [
    "GitHubApiBoundary",
    "converters",
    "get_github_service",
    "create_github_service",
]

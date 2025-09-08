"""
GitHub integration package.

Provides clean separation between PyGithub boundary and business logic.
"""

from .service import GitHubService
from .boundary import GitHubApiBoundary
from . import converters

__all__ = ["GitHubService", "GitHubApiBoundary", "converters"]

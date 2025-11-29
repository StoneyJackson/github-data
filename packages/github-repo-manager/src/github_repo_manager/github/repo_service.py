"""GitHub repository service with rate limiting and retry logic.

This service provides high-level repository operations with cross-cutting concerns.
"""

from typing import Dict, Any
from .repo_boundary import GitHubRepositoryBoundary


class GitHubRepositoryService:
    """High-level service for GitHub repository operations.

    This service wraps the boundary with rate limiting, retry logic,
    and other cross-cutting concerns.
    """

    def __init__(self, boundary: GitHubRepositoryBoundary):
        """Initialize repository service.

        Args:
            boundary: GitHub repository boundary
        """
        self._boundary = boundary

    def create_repository(
        self, repo_name: str, private: bool = False, description: str = ""
    ) -> Dict[str, Any]:
        """Create repository.

        Args:
            repo_name: Repository name in format "owner/repo"
            private: Whether repository should be private
            description: Repository description

        Returns:
            Dictionary containing repository metadata
        """
        # TODO: Add rate limiting and retry logic in future phases
        return self._boundary.create_repository(repo_name, private, description)

    def repository_exists(self, repo_name: str) -> bool:
        """Check if repository exists.

        Args:
            repo_name: Repository name in format "owner/repo"

        Returns:
            True if repository exists, False otherwise
        """
        # TODO: Add rate limiting in future phases
        return self._boundary.repository_exists(repo_name)

    def get_repository(self, repo_name: str) -> Dict[str, Any]:
        """Get repository metadata.

        Args:
            repo_name: Repository name in format "owner/repo"

        Returns:
            Dictionary containing repository metadata
        """
        # TODO: Add rate limiting and caching in future phases
        return self._boundary.get_repository(repo_name)

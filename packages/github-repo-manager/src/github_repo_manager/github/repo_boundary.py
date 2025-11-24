"""Narrow REST API boundary for GitHub repository operations.

This module provides a focused interface for repository CRUD operations only.
"""

from typing import Dict, Any, cast
from github import Github, AuthenticatedUser


class GitHubRepositoryBoundary:
    """Narrow boundary for GitHub repository operations.

    This class provides only repository-level CRUD operations,
    keeping the API surface minimal and focused.
    """

    def __init__(self, github_client: Github):
        """Initialize repository boundary.

        Args:
            github_client: Authenticated PyGithub client
        """
        self._github = github_client

    def create_repository(
        self, repo_name: str, private: bool = False, description: str = ""
    ) -> Dict[str, Any]:
        """Create a new repository.

        Args:
            repo_name: Repository name in format "owner/repo"
            private: Whether repository should be private
            description: Repository description

        Returns:
            Raw JSON dictionary of created repository

        Raises:
            GithubException: If repository creation fails
        """
        owner, repo = repo_name.split("/", 1)
        user = cast(AuthenticatedUser, self._github.get_user())

        if user.login.lower() == owner.lower():
            # Create in user account
            created_repo = user.create_repo(
                name=repo, private=private, description=description
            )
        else:
            # Create in organization
            org = self._github.get_organization(owner)
            created_repo = org.create_repo(
                name=repo, private=private, description=description
            )

        return created_repo.raw_data

    def repository_exists(self, repo_name: str) -> bool:
        """Check if a repository exists.

        Args:
            repo_name: Repository name in format "owner/repo"

        Returns:
            True if repository exists, False otherwise
        """
        try:
            self._github.get_repo(repo_name)
            return True
        except Exception:
            return False

    def get_repository(self, repo_name: str) -> Dict[str, Any]:
        """Get repository metadata.

        Args:
            repo_name: Repository name in format "owner/repo"

        Returns:
            Raw JSON dictionary of repository

        Raises:
            GithubException: If repository not found
        """
        repo = self._github.get_repo(repo_name)
        return repo.raw_data

"""Repository creation operation."""

from typing import Dict, Any
from ..github.repo_service import GitHubRepositoryService


def create_repository_operation(
    service: GitHubRepositoryService,
    repo_name: str,
    private: bool = False,
    description: str = "",
) -> Dict[str, Any]:
    """Create a new GitHub repository.

    Args:
        service: GitHub repository service
        repo_name: Repository name in format "owner/repo"
        private: Whether repository should be private
        description: Repository description

    Returns:
        Dictionary containing created repository metadata
    """
    return service.create_repository(repo_name, private, description)

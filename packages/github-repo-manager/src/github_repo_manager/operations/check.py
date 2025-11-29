"""Repository check operation."""

from ..github.repo_service import GitHubRepositoryService


def check_repository_operation(
    service: GitHubRepositoryService,
    repo_name: str,
    create_if_missing: bool = False,
    private: bool = False,
    description: str = "",
) -> bool:
    """Check if repository exists, optionally creating if missing.

    Args:
        service: GitHub repository service
        repo_name: Repository name in format "owner/repo"
        create_if_missing: Create repository if it doesn't exist
        private: Whether repository should be private (if creating)
        description: Repository description (if creating)

    Returns:
        True if repository exists (or was created), False otherwise
    """
    exists = service.repository_exists(repo_name)

    if not exists and create_if_missing:
        service.create_repository(repo_name, private, description)
        return True

    return exists

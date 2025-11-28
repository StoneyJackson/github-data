"""Main entry point for kit-orchestrator CLI.

Provides backward-compatible interface matching the original monolithic container.
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

from github_data_core.entities.registry import EntityRegistry
from github_data_tools.operations.save.orchestrator import StrategyBasedSaveOrchestrator
from github_data_tools.operations.restore.orchestrator import (
    StrategyBasedRestoreOrchestrator,
)
from github_data_tools.github.service import create_github_service
from github_data_core.storage import create_storage_service
from git_repo_tools.git.service import GitRepositoryServiceImpl


def create_monorepo_entity_registry() -> EntityRegistry:
    """Create EntityRegistry with all entities from the monorepo.

    In the monorepo structure, entities are distributed across multiple packages:
    - github-data-tools: labels, milestones, releases, issues, comments, etc.
    - git-repo-tools: git_repository

    This function creates a registry that discovers entities from github-data-tools
    (which has most entities), then manually registers entities from git-repo-tools.

    Returns:
        EntityRegistry instance with all monorepo entities registered
    """
    # Start with github-data-tools entities (the majority)
    # Try different paths based on installation mode:
    # 1. Development/editable mode: /app/packages/...
    # 2. Docker production mode: /app/packages/...
    # 3. Installed package mode: use package __file__ location

    # First, try to find entities relative to this file (dev/docker mode)
    app_packages_dir = Path(__file__).parent.parent.parent.parent
    github_data_tools_entities = (
        app_packages_dir / "github-data-tools/src/github_data_tools/entities"
    )

    # If that doesn't exist, try /app/packages (docker runtime)
    if not github_data_tools_entities.exists():
        app_packages_dir = Path("/app/packages")
        github_data_tools_entities = (
            app_packages_dir / "github-data-tools/src/github_data_tools/entities"
        )

    registry = EntityRegistry(entities_dir=github_data_tools_entities)

    # Manually register git-repo-tools entities
    from git_repo_tools.entities.git_repositories.entity_config import (
        GitRepositoryEntityConfig,
    )
    from github_data_core.entities.base import RegisteredEntity, EntityConfig
    from typing import cast

    # Create RegisteredEntity with default enabled state
    # Instantiate the config class (following the same pattern as EntityDiscovery)
    config = GitRepositoryEntityConfig()
    # Cast to EntityConfig to satisfy mypy's strict protocol checking
    git_repo_entity = RegisteredEntity(
        config=cast(EntityConfig, config),
        enabled=config.default_value,
    )
    registry._entities[config.name] = git_repo_entity

    return registry


def main() -> None:
    """Entry point for the kit-orchestrator CLI."""
    Main().main()


class Main:
    """Main orchestrator class that coordinates all subproject operations."""

    def __init__(self) -> None:
        self._operation: str = "save"
        self._registry: EntityRegistry
        self._github_token: Optional[str]
        self._github_repo: str
        self._data_path: str
        self._orchestrator: Any
        self._git_service: Optional[GitRepositoryServiceImpl] = None
        self._create_repository_if_missing: bool = True
        self._repository_visibility: str = "public"

    def main(self) -> None:
        """Execute save or restore operation based on environment variables."""
        self._load_operation_from_environment()
        self._load_registry_from_environment()
        self._load_github_token_from_environment()
        self._load_github_repo_from_environment()
        self._load_data_path_from_environment()
        self._load_create_repository_if_missing_from_environment()
        self._load_repository_visibility_from_environment()
        self._build_github_service()
        self._build_storage_service()
        self._ensure_repository_exists()
        self._build_git_service()
        self._build_orchestrator()
        self._execute_operation()

    def _load_operation_from_environment(self) -> None:
        op = os.getenv("OPERATION")
        if op is None:
            exit("Error: OPERATION environment variable required")
        else:
            self._operation = op.lower()
            if self._operation not in ["save", "restore"]:
                exit(f"Error: Invalid OPERATION '{op}'. Must be 'save' or 'restore'.")

    def _load_registry_from_environment(self) -> None:
        try:
            self._registry = create_monorepo_entity_registry()
            self._registry._load_from_environment(is_strict=False)
        except ValueError as e:
            exit(f"Error initializing registry: {e}")

    def _load_github_token_from_environment(self) -> None:
        token = os.getenv("GITHUB_TOKEN")
        if token is None or not token:
            exit("Error: GITHUB_TOKEN environment variable required")
        else:
            self._github_token = token

    def _load_github_repo_from_environment(self) -> None:
        repo_name = os.getenv("GITHUB_REPO")
        if repo_name is None or not repo_name:
            exit("Error: GITHUB_REPO environment variable required")
        else:
            self._repo_name = repo_name

    def _load_data_path_from_environment(self) -> None:
        self._data_path = os.getenv("DATA_PATH", "/data")

    def _load_create_repository_if_missing_from_environment(self) -> None:
        """Load CREATE_REPOSITORY_IF_MISSING setting (restore only)."""
        if self._operation != "restore":
            return

        value = os.getenv("CREATE_REPOSITORY_IF_MISSING", "true")
        try:
            from github_data_core.config.number_parser import NumberSpecificationParser

            self._create_repository_if_missing = (
                NumberSpecificationParser.parse_boolean_value(value)
            )
        except ValueError as e:
            exit(f"Error: Invalid CREATE_REPOSITORY_IF_MISSING value. {e}")

    def _load_repository_visibility_from_environment(self) -> None:
        """Load REPOSITORY_VISIBILITY setting (restore only)."""
        if self._operation != "restore":
            return

        value = os.getenv("REPOSITORY_VISIBILITY", "public").lower()
        if value not in ["public", "private"]:
            exit(
                f"Error: Invalid REPOSITORY_VISIBILITY '{value}'. "
                f"Must be 'public' or 'private'."
            )
        self._repository_visibility = value

    def _ensure_repository_exists(self) -> None:
        """Ensure target repository exists, creating if necessary.

        Only runs for restore operations.
        Checks if repository exists and creates it if
        CREATE_REPOSITORY_IF_MISSING is true.
        """
        if self._operation != "restore":
            return

        # Check if repository exists
        metadata = self._github_service.get_repository_metadata(self._repo_name)

        if metadata is not None:
            # Repository exists, nothing to do
            return

        # Repository doesn't exist
        if not self._create_repository_if_missing:
            exit(
                f"Error: Repository '{self._repo_name}' does not exist. "
                f"Set CREATE_REPOSITORY_IF_MISSING=true to create it "
                f"automatically."
            )

        # Create repository using github-repo-manager
        from github import Github
        from github_repo_manager.github.repo_boundary import (
            GitHubRepositoryBoundary,
        )
        from github_repo_manager.github.repo_service import (
            GitHubRepositoryService,
        )
        from github_repo_manager.operations.create import (
            create_repository_operation,
        )

        print(f"Repository '{self._repo_name}' does not exist. Creating...")
        private = self._repository_visibility == "private"

        assert self._github_token is not None
        github_client = Github(self._github_token)
        repo_boundary = GitHubRepositoryBoundary(github_client)
        repo_service = GitHubRepositoryService(repo_boundary)
        create_repository_operation(
            repo_service, self._repo_name, private=private, description=""
        )

        visibility = "private" if private else "public"
        print(f"Created {visibility} repository: {self._repo_name}")

        # Wait for repository to be available
        self._wait_for_repository_availability()

    def _wait_for_repository_availability(
        self, max_attempts: int = 10, delay_seconds: float = 2.0
    ) -> None:
        """Wait for newly created repository to be available via API.

        After creating a repository, GitHub's eventual consistency may cause
        a brief delay before the repository is accessible through all API endpoints.
        This method polls the repository until it's accessible or timeout occurs.

        Args:
            max_attempts: Maximum number of attempts to check availability
            delay_seconds: Seconds to wait between attempts
        """
        import logging

        logger = logging.getLogger(__name__)

        print("Waiting for repository to be available...")
        for attempt in range(1, max_attempts + 1):
            time.sleep(delay_seconds)

            try:
                # Attempt to verify repository is accessible
                metadata = self._github_service.get_repository_metadata(self._repo_name)
                if metadata is not None:
                    verify_time = attempt * delay_seconds
                    print(
                        f"Repository is available " f"(verified after {verify_time}s)"
                    )
                    repo_id = metadata.get("id", "unknown")
                    logger.info(
                        f"Repository {self._repo_name} verified available "
                        f"with metadata: {repo_id}"
                    )
                    return
                else:
                    logger.debug(
                        f"Attempt {attempt}: get_repository_metadata returned None"
                    )
            except Exception as e:
                # Repository still not available, continue waiting
                logger.debug(
                    f"Attempt {attempt}: Exception during availability check: {e}"
                )
                pass

            if attempt < max_attempts:
                print(
                    f"Repository not yet available, retrying... "
                    f"(attempt {attempt}/{max_attempts})"
                )

        # Timeout reached but continue anyway - the repository was created
        # and might become available during the restore process
        timeout_duration = max_attempts * delay_seconds
        print(
            f"Warning: Repository availability check timed out "
            f"after {timeout_duration}s"
        )
        print("Continuing with restore operation...")

    def _build_github_service(self) -> None:
        assert self._github_token is not None
        self._github_service = create_github_service(self._github_token)

    def _build_storage_service(self) -> None:
        self._storage_service = create_storage_service("json")

    def _build_git_service(self) -> None:
        self._git_service = None
        if self._registry.get_entity("git_repository").is_enabled():
            self._git_service = GitRepositoryServiceImpl(auth_token=self._github_token)

    def _build_orchestrator(self) -> None:
        if self._operation == "save":
            self._orchestrator = StrategyBasedSaveOrchestrator(
                registry=self._registry,
                github_service=self._github_service,
                storage_service=self._storage_service,
                git_service=self._git_service,
            )
        else:
            self._orchestrator = StrategyBasedRestoreOrchestrator(
                registry=self._registry,
                github_service=self._github_service,
                storage_service=self._storage_service,
                git_service=self._git_service,
            )

    def _execute_operation(self) -> None:
        self._print_start_message()
        try:
            results = self._orchestrator.execute(self._repo_name, self._data_path)
            self._print_results(results)
        except Exception as e:
            exit(f"\nError during {self._operation} operation: {e}")

    def _print_start_message(self) -> None:
        print(f"Starting {self._operation} operation for {self._repo_name}")
        print(f"{self._get_path_direction()} path: {self._data_path}")
        self._print_enabled_entities()

    def _print_results(self, results: List[Dict[str, Any]]) -> None:
        failures = [r for r in results if not r.get("success", True)]
        if failures:
            messages = [f"\n{self._operation.title()} operation completed with errors:"]
            messages += get_failure_messages(failures)
            exit("\n".join(messages))

        print(f"\n{self._operation.title()} operation completed successfully")
        print(f"Total entities saved: {len(results)}")

    def _print_enabled_entities(self) -> None:
        enabled = self._registry.get_enabled_entities()
        print(f"\nEnabled entities ({len(enabled)}):")
        for entity in enabled:
            print(f"  - {entity.config.name}")

    def _get_path_direction(self) -> str:
        if self._operation == "save":
            return "Output"
        else:
            return "Input"


def stderr(m: str) -> None:
    """Print message to stderr."""
    print(m, file=sys.stderr)


def exit(m: str) -> None:
    """Print error message and exit with error code."""
    stderr(m)
    sys.exit(1)


def get_failure_messages(failures: List[Dict[str, Any]]) -> List[str]:
    """Format failure messages for display."""
    messages = []
    for failure in failures:
        entity_name = failure.get("entity_name", "unknown")
        error_msg = failure.get("error", "unknown error")
        messages.append(f"  - {entity_name}: {error_msg}")
    return messages


if __name__ == "__main__":
    main()

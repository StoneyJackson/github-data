"""Main entry point for GitHub data save/restore operations."""

import os
import sys

from src.entities.registry import EntityRegistry
from src.operations.save.orchestrator import StrategyBasedSaveOrchestrator
from src.operations.restore.orchestrator import StrategyBasedRestoreOrchestrator
from src.github import create_github_service
from src.storage import create_storage_service
from src.git.service import GitRepositoryServiceImpl


def main():
    """Execute save or restore operation based on environment variables."""
    # Get operation type
    operation = os.getenv("OPERATION", "save").lower()

    if operation not in ["save", "restore"]:
        print(f"Error: Invalid OPERATION '{operation}'. Must be 'save' or 'restore'.", file=sys.stderr)
        sys.exit(1)

    # Initialize EntityRegistry from environment
    try:
        registry = EntityRegistry.from_environment(strict=False)
    except ValueError as e:
        print(f"Error initializing registry: {e}", file=sys.stderr)
        sys.exit(1)

    # Get required environment variables
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPO")
    data_path = os.getenv("DATA_PATH", "./data")

    if not github_token:
        print("Error: GITHUB_TOKEN environment variable required", file=sys.stderr)
        sys.exit(1)

    if not repo_name:
        print("Error: GITHUB_REPO environment variable required", file=sys.stderr)
        sys.exit(1)

    # Initialize services
    github_service = create_github_service(github_token)
    storage_service = create_storage_service("json")
    git_service = (
        GitRepositoryServiceImpl(auth_token=github_token)
        if registry.get_entity("git_repository").is_enabled()
        else None
    )

    # Execute operation
    if operation == "save":
        execute_save(
            registry, github_service, storage_service, git_service, repo_name, data_path
        )
    else:
        execute_restore(registry, github_service, storage_service, repo_name, data_path)


def execute_save(
    registry, github_service, storage_service, git_service, repo_name, output_path
):
    """Execute save operation."""
    print(f"Starting save operation for {repo_name}")
    print(f"Output path: {output_path}")

    # Show enabled entities
    enabled = registry.get_enabled_entities()
    print(f"\nEnabled entities ({len(enabled)}):")
    for entity in enabled:
        print(f"  - {entity.config.name}")

    orchestrator = StrategyBasedSaveOrchestrator(
        registry=registry,
        github_service=github_service,
        storage_service=storage_service,
        git_service=git_service,
    )

    try:
        results = orchestrator.execute_save(repo_name, output_path)

        # Check if any entity save operations failed
        failures = [r for r in results if not r.get("success", True)]
        if failures:
            print("\nSave operation completed with errors:", file=sys.stderr)
            for failure in failures:
                entity_name = failure.get("entity_name", "unknown")
                error_msg = failure.get("error", "unknown error")
                print(f"  - {entity_name}: {error_msg}", file=sys.stderr)
            sys.exit(1)

        print("\nSave operation completed successfully")
        print(f"Total entities saved: {len(results)}")
    except Exception as e:
        print(f"\nError during save operation: {e}", file=sys.stderr)
        sys.exit(1)


def execute_restore(registry, github_service, storage_service, repo_name, input_path):
    """Execute restore operation."""
    print(f"Starting restore operation for {repo_name}")
    print(f"Input path: {input_path}")

    # Show enabled entities
    enabled = registry.get_enabled_entities()
    print(f"\nEnabled entities ({len(enabled)}):")
    for entity in enabled:
        print(f"  - {entity.config.name}")

    orchestrator = StrategyBasedRestoreOrchestrator(
        registry=registry,
        github_service=github_service,
        storage_service=storage_service,
    )

    try:
        results = orchestrator.execute_restore(repo_name, input_path)

        # Check if any entity restore operations failed
        failures = [r for r in results if not r.get("success", True)]
        if failures:
            print("\nRestore operation completed with errors:", file=sys.stderr)
            for failure in failures:
                entity_name = failure.get("entity_name", "unknown")
                error_msg = failure.get("error", "unknown error")
                print(f"  - {entity_name}: {error_msg}", file=sys.stderr)
            sys.exit(1)

        print("\nRestore operation completed successfully")
        print(f"Total entities restored: {len(results)}")
    except Exception as e:
        print(f"\nError during restore operation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

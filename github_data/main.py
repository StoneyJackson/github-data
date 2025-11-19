"""Main entry point for GitHub data save/restore operations."""

import os
import sys
from typing import Optional, List, Dict, Any

from github_data.entities.registry import EntityRegistry
from github_data.operations import StrategyBasedOrchestrator
from github_data.operations.save.orchestrator import StrategyBasedSaveOrchestrator
from github_data.operations.restore.orchestrator import StrategyBasedRestoreOrchestrator
from github_data.github import create_github_service
from github_data.storage import create_storage_service
from github_data.git.service import GitRepositoryServiceImpl


def main() -> None:
    Main().main()


class Main:
    def __init__(self) -> None:
        self._operation: str = "save"
        self._registry: EntityRegistry
        self._github_token: Optional[str]
        self._github_repo: str
        self._data_path: str
        self._orchestrator: StrategyBasedOrchestrator
        self._git_service: Optional[GitRepositoryServiceImpl] = None

    def main(self) -> None:
        """Execute save or restore operation based on environment variables."""
        self._load_operation_from_environment()
        self._load_registry_from_environment()
        self._load_github_token_from_environment()
        self._load_github_repo_from_environment()
        self._load_data_path_from_environment()
        self._build_github_service()
        self._build_storage_service()
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
            self._registry = EntityRegistry.from_environment(is_strict=False)
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

    def _build_github_service(self) -> None:
        self._github_service = create_github_service(self._github_token)

    def _build_storage_service(self) -> None:
        self._storage_service = create_storage_service("json")

    def _build_git_service(self) -> None:
        self._git_service = None
        if self._registry.get_entity("git_repository").is_enabled():
            self._git_service = GitRepositoryServiceImpl(auth_token=self._github_token)

    def _build_orchestrator(self) -> None:
        Orchestrator: type[StrategyBasedOrchestrator]
        if self._operation == "save":
            Orchestrator = StrategyBasedSaveOrchestrator
        else:
            Orchestrator = StrategyBasedRestoreOrchestrator
        self._orchestrator = Orchestrator(
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
    print(m, file=sys.stderr)


def exit(m: str) -> None:
    stderr(m)
    sys.exit(1)


def get_failure_messages(failures: List[Dict[str, Any]]) -> List[str]:
    messages = []
    for failure in failures:
        entity_name = failure.get("entity_name", "unknown")
        error_msg = failure.get("error", "unknown error")
        messages.append(f"  - {entity_name}: {error_msg}")
    return messages


if __name__ == "__main__":
    main()

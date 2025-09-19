"""Labels restore strategy implementation."""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path

from ...strategies.restore_strategy import (
    RestoreEntityStrategy,
    RestoreConflictStrategy,
)
from .models import Label
from ...conflict_strategies import (
    LabelConflictStrategy,
    parse_conflict_strategy,
    detect_label_conflicts,
)
from ...github import converters

if TYPE_CHECKING:
    from ...storage.protocols import StorageService
    from ...github.protocols import RepositoryService


class LabelsRestoreStrategy(RestoreEntityStrategy):
    """Strategy for restoring GitHub labels."""

    def __init__(self, conflict_strategy: RestoreConflictStrategy):
        self._conflict_strategy = conflict_strategy

    def get_entity_name(self) -> str:
        return "labels"

    def get_dependencies(self) -> List[str]:
        return []  # Labels have no dependencies

    def load_data(
        self, input_path: str, storage_service: "StorageService"
    ) -> List[Label]:
        labels_file = Path(input_path) / "labels.json"
        return storage_service.load_data(labels_file, Label)

    def transform_for_creation(
        self, label: Label, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        return {
            "name": label.name,
            "color": label.color,
            "description": label.description or "",
        }

    def create_entity(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        github_service.create_label(
            repo_name,
            entity_data["name"],
            entity_data["color"],
            entity_data["description"],
        )
        return {"name": entity_data["name"]}  # Return identifier

    def post_create_actions(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entity: Label,
        created_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        # Labels don't need post-creation actions
        pass

    def resolve_conflicts(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        entities_to_restore: List[Label],
    ) -> List[Label]:
        """Resolve conflicts and return entities to create."""
        # Get existing labels
        raw_existing = github_service.get_repository_labels(repo_name)
        existing_labels = [
            converters.convert_to_label(label_dict) for label_dict in raw_existing
        ]

        # Apply conflict resolution strategy
        return self._conflict_strategy.resolve_conflicts(
            existing_labels, entities_to_restore
        )


class FailIfExistingConflictStrategy(RestoreConflictStrategy):
    """Strategy that fails if any existing labels are found."""

    def resolve_conflicts(
        self, existing_entities: List[Label], entities_to_restore: List[Label]
    ) -> List[Label]:
        if existing_entities:
            raise RuntimeError(
                f"Repository has {len(existing_entities)} existing labels. "
                f"Set LABEL_CONFLICT_STRATEGY to allow restoration with "
                f"existing labels."
            )
        return entities_to_restore


class FailIfConflictStrategy(RestoreConflictStrategy):
    """Strategy that fails if there are name conflicts between existing and
    restore labels."""

    def resolve_conflicts(
        self, existing_entities: List[Label], entities_to_restore: List[Label]
    ) -> List[Label]:
        conflicts = detect_label_conflicts(existing_entities, entities_to_restore)
        if conflicts:
            raise RuntimeError(
                f"Label name conflicts detected: {', '.join(conflicts)}. "
                f"Set LABEL_CONFLICT_STRATEGY to resolve conflicts automatically."
            )
        return entities_to_restore


class DeleteAllConflictStrategy(RestoreConflictStrategy):
    """Strategy that deletes all existing labels before restoration."""

    def __init__(self, github_service: "RepositoryService") -> None:
        self._github_service = github_service

    def resolve_conflicts(
        self, existing_entities: List[Label], entities_to_restore: List[Label]
    ) -> List[Label]:
        if existing_entities:
            for label in existing_entities:
                try:
                    self._github_service.delete_label("placeholder_repo", label.name)
                    print(f"Deleted label: {label.name}")
                except Exception as e:
                    raise RuntimeError(
                        f"Failed to delete label '{label.name}': {e}"
                    ) from e
        return entities_to_restore


class OverwriteConflictStrategy(RestoreConflictStrategy):
    """Strategy that overwrites existing labels and creates new ones."""

    def __init__(self, github_service: "RepositoryService") -> None:
        self._github_service = github_service
        self._repo_name: Optional[str] = None

    def resolve_conflicts(
        self, existing_entities: List[Label], entities_to_restore: List[Label]
    ) -> List[Label]:
        # This strategy handles creation directly, so return empty list
        # The actual overwrite logic will be handled in a separate method
        return []

    def handle_overwrite(
        self,
        github_service: "RepositoryService",
        repo_name: str,
        existing_entities: List[Label],
        entities_to_restore: List[Label],
    ) -> None:
        """Handle overwrite logic directly."""
        existing_names = {label.name for label in existing_entities}

        for label in entities_to_restore:
            try:
                if label.name in existing_names:
                    # Update existing label
                    github_service.update_label(
                        repo_name,
                        label.name,
                        label.name,
                        label.color,
                        label.description or "",
                    )
                    print(f"Updated label: {label.name}")
                else:
                    # Create new label
                    github_service.create_label(
                        repo_name, label.name, label.color, label.description or ""
                    )
                    print(f"Created label: {label.name}")
            except Exception as e:
                action = "update" if label.name in existing_names else "create"
                raise RuntimeError(
                    f"Failed to {action} label '{label.name}': {e}"
                ) from e


class SkipConflictStrategy(RestoreConflictStrategy):
    """Strategy that skips labels that already exist."""

    def resolve_conflicts(
        self, existing_entities: List[Label], entities_to_restore: List[Label]
    ) -> List[Label]:
        existing_names = {label.name for label in existing_entities}
        non_conflicting_labels = [
            label for label in entities_to_restore if label.name not in existing_names
        ]

        skipped_count = len(entities_to_restore) - len(non_conflicting_labels)
        if skipped_count > 0:
            print(f"Skipping {skipped_count} labels that already exist")

        return non_conflicting_labels


def create_conflict_strategy(
    strategy_name: str, github_service: Optional["RepositoryService"] = None
) -> RestoreConflictStrategy:
    """Factory function to create conflict resolution strategies."""
    strategy_enum = parse_conflict_strategy(strategy_name)

    if strategy_enum == LabelConflictStrategy.FAIL_IF_EXISTING:
        return FailIfExistingConflictStrategy()
    elif strategy_enum == LabelConflictStrategy.FAIL_IF_CONFLICT:
        return FailIfConflictStrategy()
    elif strategy_enum == LabelConflictStrategy.DELETE_ALL:
        if github_service is None:
            raise ValueError("github_service required for delete-all strategy")
        return DeleteAllConflictStrategy(github_service)
    elif strategy_enum == LabelConflictStrategy.OVERWRITE:
        if github_service is None:
            raise ValueError("github_service required for overwrite strategy")
        return OverwriteConflictStrategy(github_service)
    elif strategy_enum == LabelConflictStrategy.SKIP:
        return SkipConflictStrategy()
    else:
        raise ValueError(f"Unsupported conflict strategy: {strategy_name}")

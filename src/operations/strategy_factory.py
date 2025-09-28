from typing import List, Optional, TYPE_CHECKING
from src.config.settings import ApplicationConfig

if TYPE_CHECKING:
    from src.github.protocols import RepositoryService
    from src.operations.save.strategy import SaveEntityStrategy
    from src.operations.restore.strategy import RestoreEntityStrategy


class StrategyFactory:
    """Factory for creating operation strategies based on configuration."""

    @staticmethod
    def create_save_strategies(config: ApplicationConfig) -> List["SaveEntityStrategy"]:
        """Create save strategies based on configuration."""
        from src.operations.save.strategies.labels_strategy import LabelsSaveStrategy
        from src.operations.save.strategies.issues_strategy import IssuesSaveStrategy
        from src.operations.save.strategies.comments_strategy import (
            CommentsSaveStrategy,
        )

        strategies = [
            LabelsSaveStrategy(),
            IssuesSaveStrategy(),
        ]

        if config.include_issue_comments:
            strategies.append(CommentsSaveStrategy())

        return strategies

    @staticmethod
    def create_restore_strategies(
        config: ApplicationConfig,
        github_service: Optional["RepositoryService"] = None,
        include_original_metadata: bool = True,
    ) -> List["RestoreEntityStrategy"]:
        """Create restore strategies based on configuration."""
        from src.operations.restore.strategies.labels_strategy import (
            LabelsRestoreStrategy,
            create_conflict_strategy,
        )
        from src.operations.restore.strategies.issues_strategy import (
            IssuesRestoreStrategy,
        )
        from src.operations.restore.strategies.comments_strategy import (
            CommentsRestoreStrategy,
        )

        strategies: List["RestoreEntityStrategy"] = []

        # Create labels strategy with conflict resolution
        if github_service:
            conflict_strategy = create_conflict_strategy(
                config.label_conflict_strategy, github_service
            )
            strategies.append(LabelsRestoreStrategy(conflict_strategy))

        # Create issues strategy
        strategies.append(IssuesRestoreStrategy(include_original_metadata))

        # Create comments strategy if enabled
        if config.include_issue_comments:
            strategies.append(CommentsRestoreStrategy(include_original_metadata))

        return strategies

    @staticmethod
    def get_enabled_entities(config: ApplicationConfig) -> List[str]:
        """Get list of entities that should be processed based on configuration."""
        entities = ["labels", "issues"]

        if config.include_issue_comments:
            entities.append("comments")

        return entities

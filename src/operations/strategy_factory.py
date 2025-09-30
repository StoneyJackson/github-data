from typing import List, Optional, TYPE_CHECKING
import logging
from src.config.settings import ApplicationConfig

if TYPE_CHECKING:
    from src.github.protocols import RepositoryService
    from src.git.protocols import GitRepositoryService
    from src.operations.save.strategy import SaveEntityStrategy
    from src.operations.restore.strategy import RestoreEntityStrategy


class StrategyFactory:
    """Factory for creating operation strategies based on configuration."""

    @staticmethod
    def create_save_strategies(
        config: ApplicationConfig, git_service: Optional["GitRepositoryService"] = None
    ) -> List["SaveEntityStrategy"]:
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

        if config.include_pull_requests:
            from src.operations.save.strategies.pull_requests_strategy import (
                PullRequestsSaveStrategy,
            )

            strategies.append(PullRequestsSaveStrategy())

            if config.include_pull_request_comments:
                from src.operations.save.strategies.pr_comments_strategy import (
                    PullRequestCommentsSaveStrategy,
                )

                strategies.append(PullRequestCommentsSaveStrategy())
        elif config.include_pull_request_comments:
            # Warn if PR comments are enabled but PRs are not
            logging.warning(
                "Warning: INCLUDE_PULL_REQUEST_COMMENTS=true requires "
                "INCLUDE_PULL_REQUESTS=true. Ignoring PR comments."
            )

        if config.include_sub_issues:
            from src.operations.save.strategies.sub_issues_strategy import (
                SubIssuesSaveStrategy,
            )

            strategies.append(SubIssuesSaveStrategy())

        if config.include_git_repo and git_service:
            from src.operations.save.strategies.git_repository_strategy import (
                GitRepositoryStrategy,
            )

            strategies.append(GitRepositoryStrategy(git_service))

        return strategies

    @staticmethod
    def create_restore_strategies(
        config: ApplicationConfig,
        github_service: Optional["RepositoryService"] = None,
        include_original_metadata: bool = True,
        git_service: Optional["GitRepositoryService"] = None,
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

        # Create PR strategies if enabled
        if config.include_pull_requests:
            from src.operations.restore.strategies.pull_requests_strategy import (
                PullRequestsRestoreStrategy,
                create_conflict_strategy as create_pr_conflict_strategy,
            )

            pr_conflict_strategy = create_pr_conflict_strategy()

            strategies.append(
                PullRequestsRestoreStrategy(
                    pr_conflict_strategy, include_original_metadata
                )
            )

            if config.include_pull_request_comments:
                from src.operations.restore.strategies.pr_comments_strategy import (
                    PullRequestCommentsRestoreStrategy,
                    create_conflict_strategy as create_pr_comment_conflict_strategy,
                )

                pr_comment_conflict_strategy = create_pr_comment_conflict_strategy()
                strategies.append(
                    PullRequestCommentsRestoreStrategy(
                        pr_comment_conflict_strategy, include_original_metadata
                    )
                )
        elif config.include_pull_request_comments:
            # Warn if PR comments are enabled but PRs are not
            logging.warning(
                "Warning: INCLUDE_PULL_REQUEST_COMMENTS=true requires "
                "INCLUDE_PULL_REQUESTS=true. Ignoring PR comments."
            )

        # Create sub-issues strategy if enabled
        if config.include_sub_issues:
            from src.operations.restore.strategies.sub_issues_strategy import (
                SubIssuesRestoreStrategy,
            )

            strategies.append(SubIssuesRestoreStrategy(include_original_metadata))

        # Create git repository strategy if enabled
        if config.include_git_repo and git_service:
            from src.operations.restore.strategies.git_repository_strategy import (
                GitRepositoryRestoreStrategy,
            )

            strategies.append(GitRepositoryRestoreStrategy(git_service))

        return strategies

    @staticmethod
    def get_enabled_entities(config: ApplicationConfig) -> List[str]:
        """Get list of entities that should be processed based on configuration."""
        entities = ["labels", "issues"]

        if config.include_issue_comments:
            entities.append("comments")

        if config.include_pull_requests:
            entities.append("pull_requests")
            if config.include_pull_request_comments:
                entities.append("pr_comments")

        if config.include_sub_issues:
            entities.append("sub_issues")

        if config.include_git_repo:
            entities.append("git_repository")

        return entities

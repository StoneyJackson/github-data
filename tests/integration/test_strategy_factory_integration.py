import pytest
from src.operations.strategy_factory import StrategyFactory
from src.operations.save.orchestrator import StrategyBasedSaveOrchestrator
from src.operations.restore.orchestrator import StrategyBasedRestoreOrchestrator
from src.config.settings import ApplicationConfig

# Test markers for organization and selective execution
pytestmark = [
    pytest.mark.integration,
    pytest.mark.medium,
    pytest.mark.strategy_factory,
]


@pytest.fixture
def base_config():
    """Base configuration for testing."""
    return ApplicationConfig(
        operation="save",
        github_token="test-token",
        github_repo="test-owner/test-repo",
        data_path="/tmp/test-data",
        label_conflict_strategy="fail-if-existing",
        include_git_repo=True,
        include_issue_comments=True,
        include_pull_requests=False,
        include_sub_issues=False,
        git_auth_method="token",
    )


@pytest.fixture
def config_with_comments_disabled():
    """Configuration with issue comments disabled."""
    return ApplicationConfig(
        operation="save",
        github_token="test-token",
        github_repo="test-owner/test-repo",
        data_path="/tmp/test-data",
        label_conflict_strategy="fail-if-existing",
        include_git_repo=True,
        include_issue_comments=False,
        include_pull_requests=False,
        include_sub_issues=False,
        git_auth_method="token",
    )


class TestStrategyFactoryIntegration:
    """Test integration between strategy factory and orchestrators."""

    def test_save_orchestrator_auto_registers_comments_strategy(
        self, base_config, github_service_mock, storage_service_mock
    ):
        """Test that save orchestrator includes comments strategy when enabled."""
        base_config.include_issue_comments = True

        orchestrator = StrategyBasedSaveOrchestrator(
            base_config, github_service_mock, storage_service_mock
        )

        # Verify comments strategy is registered
        strategy_names = [type(s).__name__ for s in orchestrator._strategies.values()]
        assert "CommentsSaveStrategy" in strategy_names
        assert "LabelsSaveStrategy" in strategy_names
        assert "IssuesSaveStrategy" in strategy_names

    def test_save_orchestrator_excludes_comments_strategy_when_disabled(
        self,
        config_with_comments_disabled,
        github_service_mock,
        storage_service_mock,
    ):
        """Test that save orchestrator excludes comments strategy when disabled."""
        orchestrator = StrategyBasedSaveOrchestrator(
            config_with_comments_disabled, github_service_mock, storage_service_mock
        )

        # Verify comments strategy is NOT registered
        strategy_names = [type(s).__name__ for s in orchestrator._strategies.values()]
        assert "CommentsSaveStrategy" not in strategy_names
        assert "LabelsSaveStrategy" in strategy_names
        assert "IssuesSaveStrategy" in strategy_names

    def test_restore_orchestrator_respects_config(
        self, base_config, github_service_mock, storage_service_mock
    ):
        """Test that restore orchestrator respects configuration."""
        base_config.include_issue_comments = False

        orchestrator = StrategyBasedRestoreOrchestrator(
            base_config, github_service_mock, storage_service_mock
        )

        strategy_names = [type(s).__name__ for s in orchestrator._strategies.values()]
        assert "CommentsRestoreStrategy" not in strategy_names

    def test_entity_list_matches_registered_strategies(
        self, base_config, github_service_mock, storage_service_mock
    ):
        """Test that entity list from factory matches what orchestrator registers."""
        base_config.include_issue_comments = True
        base_config.include_git_repo = (
            False  # Disable git repo for this test to avoid needing git_service
        )

        # Get entities from factory
        expected_entities = StrategyFactory.get_enabled_entities(base_config)

        # Create orchestrator and get its strategy entities
        orchestrator = StrategyBasedSaveOrchestrator(
            base_config, github_service_mock, storage_service_mock
        )

        registered_entities = [
            strategy.get_entity_name() for strategy in orchestrator._strategies.values()
        ]

        # Core entities should match
        for entity in expected_entities:
            assert entity in registered_entities

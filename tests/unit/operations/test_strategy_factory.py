from unittest.mock import Mock
from src.operations.strategy_factory import StrategyFactory

# Import fixtures from shared fixtures
pytest_plugins = ["tests.shared.fixtures.config_fixtures"]


class TestStrategyFactory:
    """Test cases for StrategyFactory."""

    def test_create_save_strategies_with_comments_enabled(self, base_config):
        """Test save strategy creation with comments enabled."""
        base_config.include_issue_comments = True
        strategies = StrategyFactory.create_save_strategies(base_config)

        strategy_types = [type(s).__name__ for s in strategies]
        assert "LabelsSaveStrategy" in strategy_types
        assert "IssuesSaveStrategy" in strategy_types
        assert "CommentsSaveStrategy" in strategy_types

    def test_create_save_strategies_with_comments_disabled(
        self, config_with_comments_disabled
    ):
        """Test save strategy creation with comments disabled."""
        strategies = StrategyFactory.create_save_strategies(
            config_with_comments_disabled
        )

        strategy_types = [type(s).__name__ for s in strategies]
        assert "LabelsSaveStrategy" in strategy_types
        assert "IssuesSaveStrategy" in strategy_types
        assert "CommentsSaveStrategy" not in strategy_types

    def test_create_restore_strategies_with_comments_enabled(self, base_config):
        """Test restore strategy creation with comments enabled."""
        base_config.include_issue_comments = True
        mock_github_service = Mock()

        strategies = StrategyFactory.create_restore_strategies(
            base_config,
            github_service=mock_github_service,
            include_original_metadata=True,
        )

        strategy_types = [type(s).__name__ for s in strategies]
        assert "LabelsRestoreStrategy" in strategy_types
        assert "IssuesRestoreStrategy" in strategy_types
        assert "CommentsRestoreStrategy" in strategy_types

    def test_create_restore_strategies_with_comments_disabled(
        self, config_with_comments_disabled
    ):
        """Test restore strategy creation with comments disabled."""
        mock_github_service = Mock()

        strategies = StrategyFactory.create_restore_strategies(
            config_with_comments_disabled,
            github_service=mock_github_service,
            include_original_metadata=True,
        )

        strategy_types = [type(s).__name__ for s in strategies]
        assert "LabelsRestoreStrategy" in strategy_types
        assert "IssuesRestoreStrategy" in strategy_types
        assert "CommentsRestoreStrategy" not in strategy_types

    def test_create_restore_strategies_without_github_service(self, base_config):
        """Test restore strategy creation without GitHub service."""
        strategies = StrategyFactory.create_restore_strategies(
            base_config, github_service=None, include_original_metadata=True
        )

        strategy_types = [type(s).__name__ for s in strategies]
        # Should not include labels strategy without GitHub service
        assert "LabelsRestoreStrategy" not in strategy_types
        assert "IssuesRestoreStrategy" in strategy_types
        # Should include comments if enabled
        if base_config.include_issue_comments:
            assert "CommentsRestoreStrategy" in strategy_types

    def test_get_enabled_entities_with_all_features(self, base_config):
        """Test entity list generation with all features enabled."""
        base_config.include_issue_comments = True
        entities = StrategyFactory.get_enabled_entities(base_config)

        expected_entities = ["labels", "issues", "comments"]
        assert entities == expected_entities

    def test_get_enabled_entities_with_comments_disabled(
        self, config_with_comments_disabled
    ):
        """Test entity list generation with comments disabled."""
        entities = StrategyFactory.get_enabled_entities(config_with_comments_disabled)

        expected_entities = ["labels", "issues"]
        assert entities == expected_entities

    def test_get_enabled_entities_with_minimal_features(
        self, config_with_minimal_features
    ):
        """Test entity list generation with minimal features."""
        entities = StrategyFactory.get_enabled_entities(config_with_minimal_features)

        expected_entities = ["labels", "issues"]
        assert entities == expected_entities

    def test_restore_strategies_metadata_parameter(self, base_config):
        """Test that restore strategies respect metadata parameter."""
        mock_github_service = Mock()

        # Test with metadata enabled
        strategies = StrategyFactory.create_restore_strategies(
            base_config,
            github_service=mock_github_service,
            include_original_metadata=True,
        )

        # Find the issues strategy and check it has metadata enabled
        issues_strategy = next(
            (s for s in strategies if type(s).__name__ == "IssuesRestoreStrategy"), None
        )
        assert issues_strategy is not None
        assert issues_strategy._include_original_metadata is True

        # Test with metadata disabled
        strategies = StrategyFactory.create_restore_strategies(
            base_config,
            github_service=mock_github_service,
            include_original_metadata=False,
        )

        # Find the issues strategy and check it has metadata disabled
        issues_strategy = next(
            (s for s in strategies if type(s).__name__ == "IssuesRestoreStrategy"), None
        )
        assert issues_strategy is not None
        assert issues_strategy._include_original_metadata is False

    def test_restore_strategies_conflict_strategy_configuration(self, base_config):
        """Test that restore strategies use proper conflict strategy."""
        mock_github_service = Mock()
        base_config.label_conflict_strategy = "overwrite"

        strategies = StrategyFactory.create_restore_strategies(
            base_config,
            github_service=mock_github_service,
            include_original_metadata=True,
        )

        # Find the labels strategy and check it has the correct conflict strategy
        labels_strategy = next(
            (
                s
                for s in strategies
                if type(s).__name__ == "LabelsRestoreStrategy"
            ),
            None,
        )
        assert labels_strategy is not None
        # The conflict strategy should be configured based on
        # config.label_conflict_strategy
        assert hasattr(labels_strategy, "_conflict_strategy")

    def test_factory_creates_proper_instances(self, base_config):
        """Test that factory creates proper strategy instances."""
        # Test save strategies
        save_strategies = StrategyFactory.create_save_strategies(base_config)

        for strategy in save_strategies:
            assert hasattr(strategy, "get_entity_name")
            assert hasattr(strategy, "get_dependencies")
            assert hasattr(strategy, "collect_data")
            assert hasattr(strategy, "process_data")
            assert hasattr(strategy, "save_data")

        # Test restore strategies
        mock_github_service = Mock()
        restore_strategies = StrategyFactory.create_restore_strategies(
            base_config,
            github_service=mock_github_service,
            include_original_metadata=True,
        )

        for strategy in restore_strategies:
            assert hasattr(strategy, "get_entity_name")
            assert hasattr(strategy, "get_dependencies")
            assert hasattr(strategy, "load_data")
            assert hasattr(strategy, "transform_for_creation")
            assert hasattr(strategy, "create_entity")
            assert hasattr(strategy, "post_create_actions")

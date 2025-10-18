import pytest
import logging
from unittest.mock import patch
from src.config.settings import ApplicationConfig
from src.operations.strategy_factory import StrategyFactory

# Test markers for organization and selective execution
pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast,
    pytest.mark.issue_comments_validation,
]


class TestIssueCommentsValidationUnit:
    """Unit tests for INCLUDE_ISSUE_COMMENTS dependency validation."""

    @pytest.fixture
    def base_env_vars(self):
        """Base environment variables for testing."""
        return {
            "OPERATION": "save",
            "GITHUB_TOKEN": "test-token",
            "GITHUB_REPO": "owner/repo",
            "DATA_PATH": "/tmp/test-data",
        }

    def test_config_validation_issue_comments_without_issues_from_env(
        self, base_env_vars, caplog
    ):
        """Test config from env with invalid issue comments dependency."""
        env_vars = {
            **base_env_vars,
            "INCLUDE_ISSUES": "false",
            "INCLUDE_ISSUE_COMMENTS": "true",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            config = ApplicationConfig.from_environment()

        # Config should parse successfully
        assert config.include_issues is False
        assert config.include_issue_comments is True

        # But when used with strategy factory, should generate warning
        caplog.clear()
        StrategyFactory.create_save_strategies(config)

        # Should have warning about dependency not met
        warning_found = any(
            "INCLUDE_ISSUE_COMMENTS=true requires INCLUDE_ISSUES=true" in record.message
            for record in caplog.records
            if record.levelname == "WARNING"
        )
        assert warning_found, "Expected warning about issue comments dependency"

    def test_config_validation_issue_comments_with_issues_from_env(
        self, base_env_vars, caplog
    ):
        """Test configuration from environment with valid issue comments dependency."""
        env_vars = {
            **base_env_vars,
            "INCLUDE_ISSUES": "true",
            "INCLUDE_ISSUE_COMMENTS": "true",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            config = ApplicationConfig.from_environment()

        # Config should parse successfully
        assert config.include_issues is True
        assert config.include_issue_comments is True

        # Should not generate any warnings
        caplog.clear()
        StrategyFactory.create_save_strategies(config)

        # Should NOT have warning about dependency
        warning_found = any(
            "INCLUDE_ISSUE_COMMENTS=true requires INCLUDE_ISSUES=true" in record.message
            for record in caplog.records
            if record.levelname == "WARNING"
        )
        assert not warning_found, "Unexpected warning about issue comments dependency"

    def test_config_validate_disables_issue_comments_when_issues_disabled(
        self, base_env_vars
    ):
        """Test config.validate() disables issue comments when issues disabled."""
        env_vars = {
            **base_env_vars,
            "INCLUDE_ISSUES": "false",
            "INCLUDE_ISSUE_COMMENTS": "true",
            "INCLUDE_PULL_REQUEST_COMMENTS": "false",  # Avoid second warning
            "INCLUDE_MILESTONES": "false",  # Avoid milestone warning
        }

        with patch.dict("os.environ", env_vars, clear=True):
            config = ApplicationConfig.from_environment()

        # Before validation
        assert config.include_issues is False
        assert config.include_issue_comments is True

        # Call validate
        with patch("src.config.settings.logging.warning") as mock_warning:
            config.validate()

            # After validation, issue comments should be disabled
            assert config.include_issues is False
            assert config.include_issue_comments is False

            # Should have logged warning
            mock_warning.assert_called_once_with(
                "Warning: INCLUDE_ISSUE_COMMENTS=true requires "
                "INCLUDE_ISSUES=true. Ignoring issue comments."
            )

    def test_save_strategy_factory_issue_comments_dependency_warning(
        self, base_env_vars, caplog
    ):
        """Test that save strategy factory warns about issue comments dependency."""
        caplog.set_level(logging.WARNING)

        env_vars = {
            **base_env_vars,
            "INCLUDE_ISSUES": "false",
            "INCLUDE_ISSUE_COMMENTS": "true",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            config = ApplicationConfig.from_environment()

        caplog.clear()
        strategies = StrategyFactory.create_save_strategies(config)

        # Should have generated warning
        warning_messages = [
            record.message for record in caplog.records if record.levelname == "WARNING"
        ]

        assert any(
            "INCLUDE_ISSUE_COMMENTS=true requires INCLUDE_ISSUES=true" in msg
            for msg in warning_messages
        ), (
            f"Expected warning about issue comments dependency. "
            f"Got warnings: {warning_messages}"
        )

        # Should not include comments strategy since dependency not met
        strategy_types = [type(s).__name__ for s in strategies]
        assert "CommentsSaveStrategy" not in strategy_types

    def test_restore_strategy_factory_issue_comments_dependency_warning(
        self, base_env_vars, caplog
    ):
        """Test that restore strategy factory warns about issue comments dependency."""
        caplog.set_level(logging.WARNING)

        env_vars = {
            **base_env_vars,
            "INCLUDE_ISSUES": "false",
            "INCLUDE_ISSUE_COMMENTS": "true",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            config = ApplicationConfig.from_environment()

        caplog.clear()
        strategies = StrategyFactory.create_restore_strategies(config)

        # Should have generated warning
        warning_messages = [
            record.message for record in caplog.records if record.levelname == "WARNING"
        ]

        assert any(
            "INCLUDE_ISSUE_COMMENTS=true requires INCLUDE_ISSUES=true" in msg
            for msg in warning_messages
        ), (
            f"Expected warning about issue comments dependency. "
            f"Got warnings: {warning_messages}"
        )

        # Should not include comments strategy since dependency not met
        strategy_types = [type(s).__name__ for s in strategies]
        assert "CommentsRestoreStrategy" not in strategy_types

    def test_save_strategy_factory_with_valid_issue_comments_dependency(
        self, base_env_vars, caplog
    ):
        """Test that save strategy factory includes comments when dependency is met."""
        caplog.set_level(logging.WARNING)

        env_vars = {
            **base_env_vars,
            "INCLUDE_ISSUES": "true",
            "INCLUDE_ISSUE_COMMENTS": "true",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            config = ApplicationConfig.from_environment()

        caplog.clear()
        strategies = StrategyFactory.create_save_strategies(config)

        # Should NOT have generated warning
        warning_messages = [
            record.message for record in caplog.records if record.levelname == "WARNING"
        ]

        assert not any(
            "INCLUDE_ISSUE_COMMENTS=true requires INCLUDE_ISSUES=true" in msg
            for msg in warning_messages
        ), (
            f"Unexpected warning about issue comments dependency. "
            f"Got warnings: {warning_messages}"
        )

        # Should include both issues and comments strategies
        strategy_types = [type(s).__name__ for s in strategies]
        assert "IssuesSaveStrategy" in strategy_types
        assert "CommentsSaveStrategy" in strategy_types

    def test_restore_strategy_factory_with_valid_issue_comments_dependency(
        self, base_env_vars, caplog
    ):
        """Test restore strategy factory includes comments when dependency met."""
        caplog.set_level(logging.WARNING)

        env_vars = {
            **base_env_vars,
            "INCLUDE_ISSUES": "true",
            "INCLUDE_ISSUE_COMMENTS": "true",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            config = ApplicationConfig.from_environment()

        caplog.clear()
        strategies = StrategyFactory.create_restore_strategies(config)

        # Should NOT have generated warning
        warning_messages = [
            record.message for record in caplog.records if record.levelname == "WARNING"
        ]

        assert not any(
            "INCLUDE_ISSUE_COMMENTS=true requires INCLUDE_ISSUES=true" in msg
            for msg in warning_messages
        ), (
            f"Unexpected warning about issue comments dependency. "
            f"Got warnings: {warning_messages}"
        )

        # Should include both issues and comments strategies
        strategy_types = [type(s).__name__ for s in strategies]
        assert "IssuesRestoreStrategy" in strategy_types
        assert "CommentsRestoreStrategy" in strategy_types

    def test_get_enabled_entities_with_issues_disabled(self, base_env_vars):
        """Test enabled entities excludes issues/comments when disabled."""
        env_vars = {
            **base_env_vars,
            "INCLUDE_ISSUES": "false",
            "INCLUDE_ISSUE_COMMENTS": "true",  # Should be ignored
        }

        with patch.dict("os.environ", env_vars, clear=True):
            config = ApplicationConfig.from_environment()

        entities = StrategyFactory.get_enabled_entities(config)

        assert "labels" in entities  # Always included
        assert "issues" not in entities  # Explicitly disabled
        assert (
            "comments" not in entities
        )  # Excluded because issues are disabled (dependency requirement)

    def test_get_enabled_entities_with_issues_enabled(self, base_env_vars):
        """Test enabled entities includes issues/comments when enabled."""
        env_vars = {
            **base_env_vars,
            "INCLUDE_ISSUES": "true",
            "INCLUDE_ISSUE_COMMENTS": "true",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            config = ApplicationConfig.from_environment()

        entities = StrategyFactory.get_enabled_entities(config)

        assert "labels" in entities
        assert "issues" in entities
        assert "comments" in entities


# Use shared fixtures from conftest.py

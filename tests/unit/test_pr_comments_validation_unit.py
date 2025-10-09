import pytest
from unittest.mock import patch
from src.operations.strategy_factory import StrategyFactory
from src.config.settings import ApplicationConfig
from tests.shared.builders import ConfigBuilder, ConfigFactory

# Test markers for organization and selective execution
pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast,
    pytest.mark.pr_comments,
]


class TestPullRequestCommentsValidation:
    """Test cases for PR comments dependency validation and warnings."""

    @pytest.fixture
    def base_env_vars(self):
        """Base environment variables for testing."""
        return ConfigBuilder().as_env_dict()

    def test_config_validation_pr_comments_without_prs_from_env(
        self, base_env_vars, caplog
    ):
        """Test configuration from environment with invalid PR comments dependency."""
        env_vars = {
            **base_env_vars,
            "INCLUDE_PULL_REQUESTS": "false",
            "INCLUDE_PULL_REQUEST_COMMENTS": "true",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            config = ApplicationConfig.from_environment()

        # Config should parse successfully
        assert config.include_pull_requests is False
        assert config.include_pull_request_comments is True

        # But when used with strategy factory, should generate warning
        caplog.clear()
        StrategyFactory.create_save_strategies(config)

        # Should have warning about dependency not met
        warning_found = any(
            "INCLUDE_PULL_REQUEST_COMMENTS=true requires INCLUDE_PULL_REQUESTS=true"
            in record.message
            for record in caplog.records
            if record.levelname == "WARNING"
        )
        assert warning_found, "Expected warning about PR comments dependency"

    def test_config_validation_pr_comments_with_prs_from_env(
        self, base_env_vars, caplog
    ):
        """Test configuration from environment with valid PR comments dependency."""
        env_vars = {
            **base_env_vars,
            "INCLUDE_PULL_REQUESTS": "true",
            "INCLUDE_PULL_REQUEST_COMMENTS": "true",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            config = ApplicationConfig.from_environment()

        # Config should parse successfully
        assert config.include_pull_requests is True
        assert config.include_pull_request_comments is True

        # When used with strategy factory, should NOT generate warning
        caplog.clear()
        StrategyFactory.create_save_strategies(config)

        # Should NOT have warning about dependency
        warning_found = any(
            "INCLUDE_PULL_REQUEST_COMMENTS=true requires INCLUDE_PULL_REQUESTS=true"
            in record.message
            for record in caplog.records
            if record.levelname == "WARNING"
        )
        assert not warning_found, "Unexpected warning about PR comments dependency"

    def test_dependency_validation_shows_correct_warning_message(self, caplog):
        """Test dependency validation shows correct warning message."""
        config = ConfigFactory.create_save_config(
            include_pull_requests=False,
            include_pull_request_comments=True
        )

        caplog.clear()
        StrategyFactory.create_save_strategies(config)

        # Check for exact warning message from use cases document
        expected_warning = (
            "Warning: INCLUDE_PULL_REQUEST_COMMENTS=true requires "
            "INCLUDE_PULL_REQUESTS=true. Ignoring PR comments."
        )
        warning_found = any(
            expected_warning in record.message
            for record in caplog.records
            if record.levelname == "WARNING"
        )
        assert warning_found, f"Expected exact warning message: '{expected_warning}'"

    def test_dependency_validation_for_restore_operations(self, caplog):
        """Test that dependency validation works for restore operations too."""
        config = ConfigFactory.create_restore_config(
            include_pull_requests=False,
            include_pull_request_comments=True
        )

        from unittest.mock import Mock

        mock_github_service = Mock()

        caplog.clear()
        StrategyFactory.create_restore_strategies(
            config, github_service=mock_github_service, include_original_metadata=True
        )

        # Should have warning about dependency not met for restore too
        warning_found = any(
            "INCLUDE_PULL_REQUEST_COMMENTS=true requires INCLUDE_PULL_REQUESTS=true"
            in record.message
            for record in caplog.records
            if record.levelname == "WARNING"
        )
        assert warning_found, "Expected warning about PR comments dependency in restore"

    def test_entity_list_excludes_pr_comments_when_dependency_not_met(self):
        """Test that get_enabled_entities excludes pr_comments when dependency unmet."""
        config = ConfigFactory.create_save_config(
            include_pull_requests=False,
            include_pull_request_comments=True
        )

        entities = StrategyFactory.get_enabled_entities(config)

        # pr_comments should be excluded due to dependency validation
        assert "pr_comments" not in entities
        # But other entities should be included normally
        assert "labels" in entities
        assert "issues" in entities
        assert "comments" in entities  # Issue comments
        assert "git_repository" in entities

    def test_entity_list_includes_pr_comments_when_dependency_met(self):
        """Test that get_enabled_entities includes pr_comments when dependency met."""
        config = ConfigFactory.create_pr_config()

        entities = StrategyFactory.get_enabled_entities(config)

        # pr_comments should be included when dependency is met
        assert "pr_comments" in entities
        assert "pull_requests" in entities
        # Other entities should be included too
        assert "labels" in entities
        assert "issues" in entities
        assert "comments" in entities
        assert "git_repository" in entities

    def test_no_warning_when_both_disabled(self, caplog):
        """Test that no warning is shown when both PRs and PR comments are disabled."""
        config = ConfigFactory.create_save_config(
            include_pull_requests=False,
            include_pull_request_comments=False
        )

        caplog.clear()
        StrategyFactory.create_save_strategies(config)

        # Should NOT have warning when both are disabled
        warning_found = any(
            "INCLUDE_PULL_REQUEST_COMMENTS=true requires INCLUDE_PULL_REQUESTS=true"
            in record.message
            for record in caplog.records
            if record.levelname == "WARNING"
        )
        assert (
            not warning_found
        ), "Unexpected warning when both PR features are disabled"

    def test_no_warning_when_pr_comments_explicitly_disabled(self, caplog):
        """Test that no warning is shown when PR comments are explicitly disabled."""
        config = ConfigFactory.create_save_config(
            include_pull_requests=True,
            include_pull_request_comments=False
        )

        caplog.clear()
        StrategyFactory.create_save_strategies(config)

        # Should NOT have warning when PR comments are explicitly disabled
        warning_found = any(
            "INCLUDE_PULL_REQUEST_COMMENTS=true requires INCLUDE_PULL_REQUESTS=true"
            in record.message
            for record in caplog.records
            if record.levelname == "WARNING"
        )
        assert (
            not warning_found
        ), "Unexpected warning when PR comments are explicitly disabled"

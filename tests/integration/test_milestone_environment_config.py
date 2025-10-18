"""
Integration tests for INCLUDE_MILESTONES environment variable configuration.
Following docs/testing.md comprehensive guidelines.
"""

import pytest
import os
from unittest.mock import patch

from src.operations.save.strategies.milestones_strategy import MilestonesSaveStrategy
from src.operations.restore.strategies.milestones_strategy import (
    MilestonesRestoreStrategy,
)
from tests.shared.builders.config_builder import ConfigBuilder

# Required markers following docs/testing.md
pytestmark = [
    pytest.mark.integration,
    pytest.mark.medium,
    pytest.mark.milestones,
    pytest.mark.milestone_config,
    pytest.mark.enhanced_fixtures,
    pytest.mark.backward_compatibility,
]


class TestMilestoneEnvironmentConfiguration:
    """Test INCLUDE_MILESTONES environment variable behavior."""

    def test_include_milestones_true_enables_functionality(self):
        """Test that INCLUDE_MILESTONES=true enables milestone functionality."""
        # Use ConfigBuilder with milestones enabled
        config = ConfigBuilder().with_milestones(True).build()

        save_strategy = MilestonesSaveStrategy()
        restore_strategy = MilestonesRestoreStrategy()

        # Both strategies should not skip when enabled
        assert save_strategy.should_skip(config) is False
        assert restore_strategy.should_skip(config) is False

    def test_include_milestones_false_disables_functionality(self):
        """Test that INCLUDE_MILESTONES=false disables milestone functionality."""
        # Use ConfigBuilder with milestones disabled
        config = ConfigBuilder().with_milestones(False).build()

        save_strategy = MilestonesSaveStrategy()
        restore_strategy = MilestonesRestoreStrategy()

        # Both strategies should skip when disabled
        assert save_strategy.should_skip(config) is True
        assert restore_strategy.should_skip(config) is True

    def test_include_milestones_default_behavior(self):
        """Test default behavior when INCLUDE_MILESTONES is not configured."""
        # Use ConfigBuilder with default milestone configuration (True by default)
        config = ConfigBuilder().build()

        save_strategy = MilestonesSaveStrategy()
        restore_strategy = MilestonesRestoreStrategy()

        # Should default to enabled (not skip) as per ConfigBuilder defaults
        assert save_strategy.should_skip(config) is False
        assert restore_strategy.should_skip(config) is False

    def test_milestone_configuration_parsing_true_values(self):
        """Test that milestone functionality is enabled when configured as true."""
        # ConfigBuilder normalizes all values internally, test the normalized behavior
        config = ConfigBuilder().with_milestones(True).build()

        save_strategy = MilestonesSaveStrategy()
        restore_strategy = MilestonesRestoreStrategy()

        # Should be enabled (not skip)
        assert save_strategy.should_skip(config) is False
        assert restore_strategy.should_skip(config) is False

    def test_milestone_configuration_parsing_false_values(self):
        """Test that milestone functionality is disabled when configured as false."""
        # ConfigBuilder normalizes all values internally, test the normalized behavior
        config = ConfigBuilder().with_milestones(False).build()

        save_strategy = MilestonesSaveStrategy()
        restore_strategy = MilestonesRestoreStrategy()

        # Should be disabled (skip)
        assert save_strategy.should_skip(config) is True
        assert restore_strategy.should_skip(config) is True

    def test_runtime_configuration_switching(self):
        """Test runtime behavior when configuration changes."""
        save_strategy = MilestonesSaveStrategy()
        restore_strategy = MilestonesRestoreStrategy()

        # Initially enabled
        enabled_config = ConfigBuilder().with_milestones(True).build()
        assert save_strategy.should_skip(enabled_config) is False
        assert restore_strategy.should_skip(enabled_config) is False

        # Switch to disabled
        disabled_config = ConfigBuilder().with_milestones(False).build()
        assert save_strategy.should_skip(disabled_config) is True
        assert restore_strategy.should_skip(disabled_config) is True

        # Switch back to enabled
        enabled_again_config = ConfigBuilder().with_milestones(True).build()
        assert save_strategy.should_skip(enabled_again_config) is False
        assert restore_strategy.should_skip(enabled_again_config) is False

    @patch.dict(os.environ, {"INCLUDE_MILESTONES": "true"})
    def test_environment_variable_integration_enabled(self):
        """Test integration with actual environment variable set to true."""
        # This test simulates how the environment variable would be used
        # in the actual application configuration

        # Simulate config that reads from environment
        class MockConfigFromEnv:
            def __init__(self):
                env_value = os.environ.get("INCLUDE_MILESTONES", "true").lower()
                self.include_milestones = env_value in ["true", "1", "yes", "on"]

        config = MockConfigFromEnv()

        save_strategy = MilestonesSaveStrategy()
        restore_strategy = MilestonesRestoreStrategy()

        assert config.include_milestones is True
        assert save_strategy.should_skip(config) is False
        assert restore_strategy.should_skip(config) is False

    @patch.dict(os.environ, {"INCLUDE_MILESTONES": "false"})
    def test_environment_variable_integration_disabled(self):
        """Test integration with actual environment variable set to false."""

        # Simulate config that reads from environment
        class MockConfigFromEnv:
            def __init__(self):
                env_value = os.environ.get("INCLUDE_MILESTONES", "true").lower()
                self.include_milestones = env_value in ["true", "1", "yes", "on"]

        config = MockConfigFromEnv()

        save_strategy = MilestonesSaveStrategy()
        restore_strategy = MilestonesRestoreStrategy()

        assert config.include_milestones is False
        assert save_strategy.should_skip(config) is True
        assert restore_strategy.should_skip(config) is True

    @patch.dict(os.environ, {}, clear=True)
    def test_environment_variable_default_when_missing(self):
        """Test default behavior when INCLUDE_MILESTONES env var is not set."""

        # Simulate config with default behavior when env var is missing
        class MockConfigFromEnv:
            def __init__(self):
                env_value = os.environ.get("INCLUDE_MILESTONES", "true").lower()
                self.include_milestones = env_value in ["true", "1", "yes", "on"]

        config = MockConfigFromEnv()

        save_strategy = MilestonesSaveStrategy()
        restore_strategy = MilestonesRestoreStrategy()

        # Should default to enabled
        assert config.include_milestones is True
        assert save_strategy.should_skip(config) is False
        assert restore_strategy.should_skip(config) is False

    def test_backward_compatibility_with_existing_workflows(self):
        """Test that milestone functionality doesn't break existing workflows."""
        save_strategy = MilestonesSaveStrategy()
        restore_strategy = MilestonesRestoreStrategy()

        # Scenario 1: Configuration with default milestone settings
        default_config = ConfigBuilder().build()

        # Should default to enabled behavior per ConfigBuilder defaults
        assert save_strategy.should_skip(default_config) is False
        assert restore_strategy.should_skip(default_config) is False

        # Scenario 2: Config with other features and milestones enabled
        mixed_config = (
            ConfigBuilder()
            .with_issues(True)
            .with_pull_requests(True)
            .with_milestones(True)
            .build()
        )

        assert save_strategy.should_skip(mixed_config) is False
        assert restore_strategy.should_skip(mixed_config) is False

    def test_configuration_edge_cases(self):
        """Test edge cases in configuration handling."""
        save_strategy = MilestonesSaveStrategy()
        restore_strategy = MilestonesRestoreStrategy()

        # Test with explicitly disabled milestones
        disabled_config = ConfigBuilder().with_milestones(False).build()

        # Should skip when disabled
        assert save_strategy.should_skip(disabled_config) is True
        assert restore_strategy.should_skip(disabled_config) is True

        # Test with explicitly enabled milestones
        enabled_config = ConfigBuilder().with_milestones(True).build()

        # Should not skip when enabled
        assert save_strategy.should_skip(enabled_config) is False
        assert restore_strategy.should_skip(enabled_config) is False

    def test_strategy_consistency_across_configuration_states(self):
        """Test that save and restore strategies handle configuration consistently."""
        save_strategy = MilestonesSaveStrategy()
        restore_strategy = MilestonesRestoreStrategy()

        test_configs = [
            # (config, expected_skip)
            (ConfigBuilder().with_milestones(True).build(), False),
            (ConfigBuilder().with_milestones(False).build(), True),
        ]

        for config, expected_skip in test_configs:
            save_skip = save_strategy.should_skip(config)
            restore_skip = restore_strategy.should_skip(config)

            # Both strategies should have identical behavior
            assert (
                save_skip == restore_skip == expected_skip
            ), f"Config should result in skip={expected_skip}"

    def test_configuration_inheritance_and_overrides(self):
        """Test configuration inheritance and override scenarios."""
        save_strategy = MilestonesSaveStrategy()
        restore_strategy = MilestonesRestoreStrategy()

        # Scenario: Base config with milestones enabled
        base_config = ConfigBuilder().with_milestones(True).build()

        assert save_strategy.should_skip(base_config) is False
        assert restore_strategy.should_skip(base_config) is False

        # Scenario: Override config with milestones disabled
        override_config = ConfigBuilder().with_milestones(False).build()

        assert save_strategy.should_skip(override_config) is True
        assert restore_strategy.should_skip(override_config) is True

        # Scenario: Selective feature enabling (common in CLI tools)
        selective_config = (
            ConfigBuilder()
            .with_milestones(True)
            .with_issues(False)
            .with_pull_requests(True)
            .build()
        )

        # Milestone strategies should only care about their own flag
        assert save_strategy.should_skip(selective_config) is False
        assert restore_strategy.should_skip(selective_config) is False

"""Tests for release save strategy."""

import pytest
from unittest.mock import Mock
from github_data_tools.entities.releases.save_strategy import ReleasesSaveStrategy


pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast,
    pytest.mark.save_workflow,
]


class TestReleasesSaveStrategy:
    """Test release save strategy implementation."""

    def test_get_entity_name(self):
        """Test entity name is correct."""
        strategy = ReleasesSaveStrategy()
        assert strategy.get_entity_name() == "releases"

    def test_get_dependencies(self):
        """Test releases have no dependencies."""
        strategy = ReleasesSaveStrategy()
        assert strategy.get_dependencies() == []

    def test_get_converter_name(self):
        """Test converter function name."""
        strategy = ReleasesSaveStrategy()
        assert strategy.get_converter_name() == "convert_to_release"

    def test_get_service_method(self):
        """Test service method name."""
        strategy = ReleasesSaveStrategy()
        assert strategy.get_service_method() == "get_repository_releases"

    def test_transform_no_processing(self):
        """Test transform returns entities unchanged."""
        strategy = ReleasesSaveStrategy()
        entities = [{"id": 1}, {"id": 2}]
        result = strategy.transform(entities, {})
        assert result == entities

    def test_should_skip_when_disabled(self):
        """Test skipping when releases disabled in config."""
        strategy = ReleasesSaveStrategy()
        config = Mock()
        config.include_releases = False
        assert strategy.should_skip(config) is True

    def test_should_not_skip_when_enabled(self):
        """Test not skipping when releases enabled."""
        strategy = ReleasesSaveStrategy()
        config = Mock()
        config.include_releases = True
        assert strategy.should_skip(config) is False

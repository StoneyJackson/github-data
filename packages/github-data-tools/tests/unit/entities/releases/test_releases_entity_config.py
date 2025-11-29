"""Tests for releases entity configuration."""

import pytest
from github_data_tools.entities.releases.entity_config import ReleasesEntityConfig
from github_data_core.entities.strategy_context import StrategyContext


pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast,
]


def test_releases_entity_config_attributes():
    """Test entity config has required attributes."""
    assert ReleasesEntityConfig.name == "releases"
    assert ReleasesEntityConfig.env_var == "INCLUDE_RELEASES"
    assert ReleasesEntityConfig.default_value is True
    assert ReleasesEntityConfig.value_type == bool
    assert ReleasesEntityConfig.dependencies == []
    assert ReleasesEntityConfig.description == "Repository releases and tags"
    assert ReleasesEntityConfig.required_services_save == []
    assert ReleasesEntityConfig.required_services_restore == []


def test_releases_create_save_strategy():
    """Test save strategy factory method."""
    context = StrategyContext()
    strategy = ReleasesEntityConfig.create_save_strategy(context)
    assert strategy is not None
    assert strategy.get_entity_name() == "releases"


def test_releases_create_restore_strategy():
    """Test restore strategy factory method."""
    context = StrategyContext()
    strategy = ReleasesEntityConfig.create_restore_strategy(context)
    assert strategy is not None
    assert strategy.get_entity_name() == "releases"


def test_releases_config_declares_github_api_operations():
    """Releases config should declare github_api_operations."""
    assert hasattr(ReleasesEntityConfig, "github_api_operations")
    assert "get_repository_releases" in ReleasesEntityConfig.github_api_operations

    # Validate spec structure
    get_releases_spec = ReleasesEntityConfig.github_api_operations[
        "get_repository_releases"
    ]
    assert get_releases_spec["boundary_method"] == "get_repository_releases"
    assert get_releases_spec["converter"] == "convert_to_release"

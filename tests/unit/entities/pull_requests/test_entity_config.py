"""Tests for pull_requests entity configuration."""

import pytest
from src.entities.registry import EntityRegistry
from typing import Union, Set


@pytest.mark.unit
def test_pull_requests_entity_discovered():
    """Test pull_requests entity discovered."""
    registry = EntityRegistry()
    entity = registry.get_entity("pull_requests")

    assert entity.config.name == "pull_requests"
    assert entity.config.env_var == "INCLUDE_PULL_REQUESTS"
    assert entity.config.default_value is True
    assert entity.config.value_type == Union[bool, Set[int]]
    assert entity.config.dependencies == ["milestones"]


@pytest.mark.unit
def test_pull_requests_depends_on_milestones():
    """Test pull_requests depend on milestones."""
    registry = EntityRegistry()
    entity = registry.get_entity("pull_requests")

    assert "milestones" in entity.get_dependencies()

"""Tests for entity discovery fixtures."""

from github_data.entities.registry import EntityRegistry


def test_entity_registry_fixture_provides_fresh_instance(entity_registry):
    """Test entity_registry fixture provides a fresh EntityRegistry."""
    assert isinstance(entity_registry, EntityRegistry)
    assert entity_registry is not None


def test_all_entity_names_fixture_returns_list(all_entity_names):
    """Test all_entity_names fixture returns list of entity names."""
    assert isinstance(all_entity_names, list)
    assert len(all_entity_names) > 0
    assert all(isinstance(name, str) for name in all_entity_names)


def test_all_entity_names_includes_known_entities(all_entity_names):
    """Test all_entity_names includes expected entities."""
    # Check for a few known entities that should always exist
    assert "labels" in all_entity_names
    assert "issues" in all_entity_names
    assert "milestones" in all_entity_names


def test_enabled_entity_names_returns_enabled_only(
    enabled_entity_names, entity_registry
):
    """Test enabled_entity_names returns only enabled entities."""
    assert isinstance(enabled_entity_names, list)

    # Verify all returned entities are actually enabled
    for name in enabled_entity_names:
        entity = entity_registry.get_entity(name)
        assert entity.is_enabled(), f"{name} should be enabled"


def test_enabled_entity_names_subset_of_all(enabled_entity_names, all_entity_names):
    """Test enabled entities are subset of all entities."""
    assert set(enabled_entity_names).issubset(set(all_entity_names))


def test_entity_names_by_dependency_order_respects_dependencies(
    entity_names_by_dependency_order, entity_registry
):
    """Test dependency order fixture returns valid topological sort."""
    names = entity_names_by_dependency_order

    # Create position lookup
    positions = {name: idx for idx, name in enumerate(names)}

    # Verify each entity comes after its dependencies
    for name in names:
        entity = entity_registry.get_entity(name)
        for dep in entity.get_dependencies():
            assert (
                positions[dep] < positions[name]
            ), f"{name} depends on {dep}, but {dep} comes after {name}"


def test_independent_entity_names_have_no_dependencies(
    independent_entity_names, entity_registry
):
    """Test independent entities have empty dependency lists."""
    for name in independent_entity_names:
        entity = entity_registry.get_entity(name)
        deps = entity.get_dependencies()
        assert len(deps) == 0, f"{name} should have no dependencies, has {deps}"

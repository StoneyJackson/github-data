from src.entities.registry import EntityRegistry


def test_entity_registry_initializes():
    """Test EntityRegistry can be instantiated."""
    registry = EntityRegistry()
    assert registry is not None
    assert hasattr(registry, "_entities")
    assert isinstance(registry._entities, dict)


def test_entity_registry_from_environment_creates_instance():
    """Test from_environment class method creates registry."""
    registry = EntityRegistry.from_environment()
    assert isinstance(registry, EntityRegistry)

import sys
from github_data.entities.registry import EntityRegistry


def test_discover_entities_finds_entity_configs(tmp_path, monkeypatch):
    """Test _discover_entities finds EntityConfig classes."""
    # Create temporary entity structure
    entity_dir = tmp_path / "entities" / "test_entity"
    entity_dir.mkdir(parents=True)

    # Write entity_config.py
    config_file = entity_dir / "entity_config.py"
    config_file.write_text(
        """
class TestEntityEntityConfig:
    name = "test_entity"
    env_var = "INCLUDE_TEST_ENTITY"
    default_value = True
    value_type = bool
    dependencies = []
    description = "Test"
"""
    )

    # Write __init__.py
    (entity_dir / "__init__.py").write_text("")

    # Add temp path to sys.path for imports
    sys.path.insert(0, str(tmp_path))

    try:
        registry = EntityRegistry(tmp_path / "entities")

        # Should have discovered test_entity
        assert "test_entity" in registry._entities
        entity = registry._entities["test_entity"]
        assert entity.config.name == "test_entity"
        assert entity.config.env_var == "INCLUDE_TEST_ENTITY"
        assert entity.enabled is True  # default_value
    finally:
        sys.path.remove(str(tmp_path))

"""Test fixture entity config."""


class SimpleEntityEntityConfig:
    """Test entity for discovery testing."""

    name = "simple_entity"
    env_var = "INCLUDE_SIMPLE_ENTITY"
    default_value = True
    value_type = bool
    dependencies = []
    storage_filename = None
    description = "Simple test entity"

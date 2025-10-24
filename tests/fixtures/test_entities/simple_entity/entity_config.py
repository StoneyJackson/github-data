"""Test fixture entity config."""


class SimpleEntityEntityConfig:
    """Test entity for discovery testing."""

    name = "simple_entity"
    env_var = "INCLUDE_SIMPLE_ENTITY"
    default_value = True
    value_type = bool
    dependencies = []
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Simple test entity"

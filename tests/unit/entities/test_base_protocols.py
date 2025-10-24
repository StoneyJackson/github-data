from src.entities.base import EntityConfig


def test_entity_config_protocol_has_required_attributes():
    """Test that EntityConfig protocol defines required attributes."""
    # This test validates the protocol structure exists
    assert hasattr(EntityConfig, '__annotations__')
    annotations = EntityConfig.__annotations__

    assert 'name' in annotations
    assert 'env_var' in annotations
    assert 'default_value' in annotations
    assert 'value_type' in annotations
    assert 'dependencies' in annotations

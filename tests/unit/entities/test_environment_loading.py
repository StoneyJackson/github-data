import pytest
from github_data.entities.registry import EntityRegistry
from github_data.entities.base import RegisteredEntity


@pytest.fixture
def mock_entity_registry(monkeypatch):
    """Create registry with mock entity for testing."""

    class MockConfig:
        name = "test_entity"
        env_var = "INCLUDE_TEST_ENTITY"
        default_value = True
        value_type = bool
        dependencies = []
        description = "Test"

    registry = EntityRegistry.__new__(EntityRegistry)
    registry._entities = {
        "test_entity": RegisteredEntity(config=MockConfig(), enabled=True)  # default
    }
    registry._explicitly_set = set()
    return registry


def test_load_from_environment_bool_true(mock_entity_registry, monkeypatch):
    """Test loading boolean true from environment."""
    monkeypatch.setenv("INCLUDE_TEST_ENTITY", "true")

    mock_entity_registry._load_from_environment(strict=False)

    assert mock_entity_registry._entities["test_entity"].enabled is True


def test_load_from_environment_bool_false(mock_entity_registry, monkeypatch):
    """Test loading boolean false from environment."""
    monkeypatch.setenv("INCLUDE_TEST_ENTITY", "false")

    mock_entity_registry._load_from_environment(strict=False)

    assert mock_entity_registry._entities["test_entity"].enabled is False


def test_load_from_environment_uses_default_when_not_set(
    mock_entity_registry, monkeypatch
):
    """Test uses default value when env var not set."""
    monkeypatch.delenv("INCLUDE_TEST_ENTITY", raising=False)

    mock_entity_registry._load_from_environment(strict=False)

    # Should use default_value=True
    assert mock_entity_registry._entities["test_entity"].enabled is True

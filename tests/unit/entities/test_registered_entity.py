from typing import List, Optional, Type, Union, Set
from src.entities.base import RegisteredEntity


class MockEntityConfig:
    """Mock entity config for testing."""

    name: str = "test_entity"
    env_var: str = "INCLUDE_TEST_ENTITY"
    default_value: Union[bool, Set[int]] = True
    value_type: Type = bool
    dependencies: List[str] = []
    description: str = "Test entity"


def test_registered_entity_is_enabled_with_bool_true() -> None:
    """Test is_enabled returns True for boolean True."""
    entity = RegisteredEntity(config=MockEntityConfig(), enabled=True)

    assert entity.is_enabled() is True


def test_registered_entity_is_enabled_with_bool_false() -> None:
    """Test is_enabled returns False for boolean False."""
    entity = RegisteredEntity(config=MockEntityConfig(), enabled=False)

    assert entity.is_enabled() is False


def test_registered_entity_is_enabled_with_non_empty_set() -> None:
    """Test is_enabled returns True for non-empty set."""
    entity = RegisteredEntity(config=MockEntityConfig(), enabled={1, 2, 3})

    assert entity.is_enabled() is True


def test_registered_entity_is_enabled_with_empty_set() -> None:
    """Test is_enabled returns False for empty set."""
    entity = RegisteredEntity(config=MockEntityConfig(), enabled=set())

    assert entity.is_enabled() is False


def test_registered_entity_get_dependencies() -> None:
    """Test get_dependencies returns config dependencies."""

    class ConfigWithDeps:
        name: str = "test"
        env_var: str = "TEST"
        default_value: Union[bool, Set[int]] = True
        value_type: Type = bool
        dependencies: List[str] = ["issues", "comments"]
        description: str = ""

    entity = RegisteredEntity(config=ConfigWithDeps(), enabled=True)

    assert entity.get_dependencies() == ["issues", "comments"]

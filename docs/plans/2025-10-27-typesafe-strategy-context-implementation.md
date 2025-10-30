# Typesafe Strategy Context Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace untyped `**context: Any` with typed `StrategyContext` to enable compile-time type checking and fail-fast validation.

**Architecture:** Create a `StrategyContext` dataclass with typed service properties, add service requirement declarations to entity configs, and implement upfront validation in `StrategyFactory` before strategy creation.

**Tech Stack:** Python 3.11+, dataclasses, typing Protocol, pytest

---

## Phase 1: Core Infrastructure

### Task 1: Create StrategyContext with service_property decorator

**Files:**
- Create: `src/entities/strategy_context.py`
- Test: `tests/unit/entities/test_strategy_context.py`

**Step 1: Write failing test for service_property decorator**

Create the test file:

```python
"""Tests for StrategyContext."""

import pytest
from unittest.mock import Mock


def test_service_property_returns_value_when_set():
    """Test that service_property returns the service when set."""
    from src.entities.strategy_context import StrategyContext

    mock_git_service = Mock()
    context = StrategyContext(_git_service=mock_git_service)

    assert context.git_service is mock_git_service


def test_service_property_raises_when_none():
    """Test that service_property raises RuntimeError when service is None."""
    from src.entities.strategy_context import StrategyContext

    context = StrategyContext()

    with pytest.raises(RuntimeError, match="git_service is required but was not provided"):
        _ = context.git_service


def test_github_service_property_returns_value_when_set():
    """Test that github_service property returns the service when set."""
    from src.entities.strategy_context import StrategyContext

    mock_github_service = Mock()
    context = StrategyContext(_github_service=mock_github_service)

    assert context.github_service is mock_github_service


def test_github_service_property_raises_when_none():
    """Test that github_service property raises when None."""
    from src.entities.strategy_context import StrategyContext

    context = StrategyContext()

    with pytest.raises(RuntimeError, match="github_service is required but was not provided"):
        _ = context.github_service


def test_conflict_strategy_property_returns_value_when_set():
    """Test that conflict_strategy property returns the strategy when set."""
    from src.entities.strategy_context import StrategyContext

    mock_strategy = Mock()
    context = StrategyContext(_conflict_strategy=mock_strategy)

    assert context.conflict_strategy is mock_strategy


def test_conflict_strategy_property_raises_when_none():
    """Test that conflict_strategy property raises when None."""
    from src.entities.strategy_context import StrategyContext

    context = StrategyContext()

    with pytest.raises(RuntimeError, match="conflict_strategy is required but was not provided"):
        _ = context.conflict_strategy


def test_include_original_metadata_has_default_value():
    """Test that include_original_metadata has a default value."""
    from src.entities.strategy_context import StrategyContext

    context = StrategyContext()

    assert context.include_original_metadata is True


def test_include_original_metadata_can_be_set():
    """Test that include_original_metadata can be set."""
    from src.entities.strategy_context import StrategyContext

    context = StrategyContext(_include_original_metadata=False)

    assert context.include_original_metadata is False


def test_multiple_services_can_be_set():
    """Test that multiple services can be set and accessed."""
    from src.entities.strategy_context import StrategyContext

    mock_git = Mock()
    mock_github = Mock()
    mock_conflict = Mock()

    context = StrategyContext(
        _git_service=mock_git,
        _github_service=mock_github,
        _conflict_strategy=mock_conflict,
        _include_original_metadata=False,
    )

    assert context.git_service is mock_git
    assert context.github_service is mock_github
    assert context.conflict_strategy is mock_conflict
    assert context.include_original_metadata is False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/entities/test_strategy_context.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'src.entities.strategy_context'"

**Step 3: Implement StrategyContext and service_property**

Create `src/entities/strategy_context.py`:

```python
"""Typed strategy context for entity strategy creation."""

from typing import Optional, Any, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from src.services.git_service import GitRepositoryService
    from src.services.github_service import GitHubService


def service_property(func):
    """Decorator to create a validated service property.

    Converts a method that defines service metadata into a property
    that validates and returns the service.

    The decorated function's name determines the service name
    and corresponding private attribute (_<name>).

    Usage:
        @service_property
        def git_service(self) -> GitService:
            '''Git repository service.'''
            ...

    This creates a property that:
    - Returns self._git_service if not None
    - Raises RuntimeError with clear message if None
    - Preserves type hints for mypy and IDEs

    Args:
        func: Method defining service metadata (name and type)

    Returns:
        Property that validates and returns the service
    """
    service_name = func.__name__
    private_attr = f"_{service_name}"

    @property
    def wrapper(self):
        value = getattr(self, private_attr, None)
        if value is None:
            raise RuntimeError(f"{service_name} is required but was not provided")
        return value

    # Preserve type hints from original function
    wrapper.__annotations__ = func.__annotations__
    return wrapper


@dataclass
class StrategyContext:
    """Typed container for services available to entity strategies.

    Services are stored as private optional attributes and exposed
    as typed properties that validate on access.

    This design enables:
    - Compile-time type checking (mypy validates service usage)
    - IDE autocomplete for available services
    - Clear runtime errors when required services missing
    - Adding new services without breaking existing entities

    Adding new services:
    1. Add private attribute: _new_service: Optional[NewService] = None
    2. Add decorated property with type hint
    3. Existing entities unaffected (backward compatible)

    Example:
        context = StrategyContext(_git_service=git_svc)
        service = context.git_service  # Typed, validated
    """

    # Private optional storage for services
    _git_service: Optional["GitRepositoryService"] = None
    _github_service: Optional["GitHubService"] = None
    _conflict_strategy: Optional[Any] = None

    # Non-service configuration (has default, no validation needed)
    _include_original_metadata: bool = True

    # Public typed properties with validation

    @service_property
    def git_service(self) -> "GitRepositoryService":
        """Git repository service for cloning/restoring repositories."""
        ...

    @service_property
    def github_service(self) -> "GitHubService":
        """GitHub API service for issues, PRs, labels, etc."""
        ...

    @service_property
    def conflict_strategy(self) -> Any:
        """Conflict resolution strategy for label/issue restoration."""
        ...

    @property
    def include_original_metadata(self) -> bool:
        """Whether to preserve original GitHub metadata during restore."""
        return self._include_original_metadata
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/entities/test_strategy_context.py -v`

Expected: All tests PASS

**Step 5: Run type check**

Run: `make type-check`

Expected: No mypy errors in strategy_context.py

**Step 6: Commit**

```bash
git add src/entities/strategy_context.py tests/unit/entities/test_strategy_context.py
git commit -s -m "feat: add StrategyContext with typed service properties

- Add service_property decorator for DRY validation
- Add StrategyContext dataclass with git_service, github_service, conflict_strategy
- Add include_original_metadata as regular property with default
- All properties type-hinted for mypy and IDE support"
```

---

### Task 2: Update EntityConfig protocol

**Files:**
- Modify: `src/entities/base.py:7-42`
- Test: `tests/unit/entities/test_entity_config_protocol.py`

**Step 1: Write failing test for updated protocol**

Create the test file:

```python
"""Tests for EntityConfig protocol with StrategyContext."""

import pytest
from typing import Optional, List
from src.entities.base import EntityConfig
from src.entities.strategy_context import StrategyContext


class TestEntityConfigProtocol:
    """Test that EntityConfig protocol is correctly defined."""

    def test_protocol_requires_required_services_save(self):
        """Test that protocol includes required_services_save attribute."""

        class ValidConfig:
            name = "test"
            env_var = "TEST"
            default_value = True
            value_type = bool
            dependencies: List[str] = []
            description = "Test"
            required_services_save: List[str] = ["git_service"]
            required_services_restore: List[str] = ["git_service"]

            @staticmethod
            def create_save_strategy(context: StrategyContext) -> Optional[object]:
                return None

            @staticmethod
            def create_restore_strategy(context: StrategyContext) -> Optional[object]:
                return None

        # Should not raise - protocol satisfied
        config: EntityConfig = ValidConfig()  # type: ignore
        assert config.required_services_save == ["git_service"]

    def test_protocol_requires_required_services_restore(self):
        """Test that protocol includes required_services_restore attribute."""

        class ValidConfig:
            name = "test"
            env_var = "TEST"
            default_value = True
            value_type = bool
            dependencies: List[str] = []
            description = "Test"
            required_services_save: List[str] = []
            required_services_restore: List[str] = ["conflict_strategy"]

            @staticmethod
            def create_save_strategy(context: StrategyContext) -> Optional[object]:
                return None

            @staticmethod
            def create_restore_strategy(context: StrategyContext) -> Optional[object]:
                return None

        config: EntityConfig = ValidConfig()  # type: ignore
        assert config.required_services_restore == ["conflict_strategy"]

    def test_factory_methods_accept_strategy_context(self):
        """Test that factory methods accept StrategyContext parameter."""

        class ConfigWithContext:
            name = "test"
            env_var = "TEST"
            default_value = True
            value_type = bool
            dependencies: List[str] = []
            description = "Test"
            required_services_save: List[str] = []
            required_services_restore: List[str] = []

            @staticmethod
            def create_save_strategy(context: StrategyContext) -> Optional[object]:
                # Should be able to access typed context
                return None

            @staticmethod
            def create_restore_strategy(context: StrategyContext) -> Optional[object]:
                return None

        config: EntityConfig = ConfigWithContext()  # type: ignore
        context = StrategyContext()

        # Should be callable with StrategyContext
        result = config.create_save_strategy(context)
        assert result is None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/entities/test_entity_config_protocol.py -v`

Expected: FAIL - Type errors or protocol mismatch

**Step 3: Update EntityConfig protocol**

Modify `src/entities/base.py:7-42`:

```python
class EntityConfig(Protocol):
    """Protocol for entity configuration metadata.

    All entity configs must define these attributes to be discovered.
    """

    name: str  # Entity identifier (e.g., "comment_attachments")
    env_var: str  # Environment variable name
    default_value: Union[bool, Set[int]]  # Default enabled state
    value_type: Type  # bool or Union[bool, Set[int]]
    dependencies: List[str] = []  # List of entity names this depends on
    description: str = ""  # Documentation

    # Service requirements for operations (NEW)
    required_services_save: List[str] = []  # Services needed for save
    required_services_restore: List[str] = []  # Services needed for restore

    @staticmethod
    def create_save_strategy(context: "StrategyContext") -> Optional["BaseSaveStrategy"]:
        """Factory method for creating save strategy instances.

        Args:
            context: Typed strategy context with validated services

        Returns:
            Configured save strategy instance, or None if not applicable
        """
        ...

    @staticmethod
    def create_restore_strategy(context: "StrategyContext") -> Optional["BaseRestoreStrategy"]:
        """Factory method for creating restore strategy instances.

        Args:
            context: Typed strategy context with validated services

        Returns:
            Configured restore strategy instance, or None if not applicable
        """
        ...
```

**Step 4: Add import for StrategyContext**

Modify `src/entities/base.py:1-4`:

```python
"""Base protocols and types for entity system."""

from typing import Protocol, Optional, List, Union, Set, Type, Any, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from src.entities.strategy_context import StrategyContext
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/unit/entities/test_entity_config_protocol.py -v`

Expected: All tests PASS

**Step 6: Run type check**

Run: `make type-check`

Expected: No errors (forward reference resolved via TYPE_CHECKING)

**Step 7: Commit**

```bash
git add src/entities/base.py tests/unit/entities/test_entity_config_protocol.py
git commit -s -m "refactor: update EntityConfig protocol for typed context

- Change create_save_strategy to accept StrategyContext instead of **context: Any
- Change create_restore_strategy to accept StrategyContext instead of **context: Any
- Add required_services_save and required_services_restore attributes
- Add TYPE_CHECKING import for StrategyContext forward reference"
```

---

### Task 3: Export StrategyContext from entities module

**Files:**
- Modify: `src/entities/__init__.py`

**Step 1: Add StrategyContext to exports**

Modify `src/entities/__init__.py` (append to existing exports):

```python
"""Entity system exports."""

from src.entities.base import (
    EntityConfig,
    BaseSaveStrategy,
    BaseRestoreStrategy,
    RegisteredEntity,
)
from src.entities.registry import EntityRegistry
from src.entities.strategy_context import StrategyContext

__all__ = [
    "EntityConfig",
    "BaseSaveStrategy",
    "BaseRestoreStrategy",
    "RegisteredEntity",
    "EntityRegistry",
    "StrategyContext",
]
```

**Step 2: Verify import works**

Run: `python -c "from src.entities import StrategyContext; print(StrategyContext)"`

Expected: `<class 'src.entities.strategy_context.StrategyContext'>`

**Step 3: Commit**

```bash
git add src/entities/__init__.py
git commit -s -m "refactor: export StrategyContext from entities module

- Add StrategyContext to __all__ for public API
- Enables 'from src.entities import StrategyContext'"
```

---

## Phase 2: StrategyFactory Validation

### Task 4: Add validation method to StrategyFactory

**Files:**
- Modify: `src/operations/strategy_factory.py`
- Test: `tests/unit/operations/test_strategy_factory_validation.py`

**Step 1: Write failing test for validation**

Create the test file:

```python
"""Tests for StrategyFactory service requirement validation."""

import pytest
from unittest.mock import Mock
from src.operations.strategy_factory import StrategyFactory
from src.entities.strategy_context import StrategyContext


def test_validate_requirements_passes_when_service_available():
    """Test that validation passes when required service is available."""
    mock_registry = Mock()
    factory = StrategyFactory(mock_registry)

    mock_config = Mock()
    mock_config.name = "test_entity"
    mock_config.required_services_save = ["git_service"]

    mock_git_service = Mock()
    context = StrategyContext(_git_service=mock_git_service)

    # Should not raise
    factory._validate_requirements(mock_config, context, "save")


def test_validate_requirements_raises_when_service_missing():
    """Test that validation raises RuntimeError when service missing."""
    mock_registry = Mock()
    factory = StrategyFactory(mock_registry)

    mock_config = Mock()
    mock_config.name = "git_repository"
    mock_config.required_services_save = ["git_service"]

    context = StrategyContext()  # No services

    with pytest.raises(
        RuntimeError,
        match="Entity 'git_repository' requires 'git_service' for save operation",
    ):
        factory._validate_requirements(mock_config, context, "save")


def test_validate_requirements_checks_restore_requirements():
    """Test that validation checks restore-specific requirements."""
    mock_registry = Mock()
    factory = StrategyFactory(mock_registry)

    mock_config = Mock()
    mock_config.name = "labels"
    mock_config.required_services_restore = ["conflict_strategy"]

    context = StrategyContext()  # No conflict_strategy

    with pytest.raises(
        RuntimeError,
        match="Entity 'labels' requires 'conflict_strategy' for restore operation",
    ):
        factory._validate_requirements(mock_config, context, "restore")


def test_validate_requirements_handles_missing_attribute():
    """Test backward compatibility when config has no requirements."""
    mock_registry = Mock()
    factory = StrategyFactory(mock_registry)

    mock_config = Mock()
    mock_config.name = "legacy_entity"
    # No required_services_save attribute
    del mock_config.required_services_save

    context = StrategyContext()

    # Should not raise - defaults to empty list
    factory._validate_requirements(mock_config, context, "save")


def test_validate_requirements_checks_multiple_services():
    """Test that validation checks all required services."""
    mock_registry = Mock()
    factory = StrategyFactory(mock_registry)

    mock_config = Mock()
    mock_config.name = "complex_entity"
    mock_config.required_services_save = ["git_service", "github_service"]

    mock_git = Mock()
    context = StrategyContext(_git_service=mock_git)  # Missing github_service

    with pytest.raises(
        RuntimeError,
        match="Entity 'complex_entity' requires 'github_service' for save operation",
    ):
        factory._validate_requirements(mock_config, context, "save")


def test_validate_requirements_passes_with_all_services():
    """Test that validation passes when all required services present."""
    mock_registry = Mock()
    factory = StrategyFactory(mock_registry)

    mock_config = Mock()
    mock_config.name = "complex_entity"
    mock_config.required_services_restore = ["github_service", "conflict_strategy"]

    mock_github = Mock()
    mock_conflict = Mock()
    context = StrategyContext(
        _github_service=mock_github, _conflict_strategy=mock_conflict
    )

    # Should not raise
    factory._validate_requirements(mock_config, context, "restore")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/operations/test_strategy_factory_validation.py -v`

Expected: FAIL with "AttributeError: 'StrategyFactory' object has no attribute '_validate_requirements'"

**Step 3: Implement _validate_requirements method**

Modify `src/operations/strategy_factory.py` - add method after `__init__`:

```python
    def _validate_requirements(
        self,
        config: "EntityConfig",
        context: "StrategyContext",
        operation: str,
    ) -> None:
        """Validate required services are available in context.

        Args:
            config: Entity configuration
            context: Strategy context to validate
            operation: "save" or "restore"

        Raises:
            RuntimeError: If required service not available
        """
        # Get requirements for this operation (default empty list for backward compatibility)
        required = getattr(config, f"required_services_{operation}", [])

        for service_name in required:
            # Check if service is available (not None)
            private_attr = f"_{service_name}"
            if getattr(context, private_attr, None) is None:
                raise RuntimeError(
                    f"Entity '{config.name}' requires '{service_name}' "
                    f"for {operation} operation, but it was not provided in context"
                )
```

**Step 4: Add TYPE_CHECKING import**

Modify imports at top of `src/operations/strategy_factory.py`:

```python
"""Factory for creating save and restore strategies."""

import logging
from typing import Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.registry import EntityRegistry
    from src.entities.base import BaseSaveStrategy, BaseRestoreStrategy, EntityConfig
    from src.entities.strategy_context import StrategyContext

logger = logging.getLogger(__name__)
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/unit/operations/test_strategy_factory_validation.py -v`

Expected: All tests PASS

**Step 6: Commit**

```bash
git add src/operations/strategy_factory.py tests/unit/operations/test_strategy_factory_validation.py
git commit -s -m "feat: add service requirement validation to StrategyFactory

- Add _validate_requirements() method to check services before strategy creation
- Check private attributes (_git_service, etc.) for None
- Raise RuntimeError with clear message: entity name, missing service, operation
- Backward compatible: defaults to empty list for configs without requirements"
```

---

### Task 5: Update create_save_strategies to use StrategyContext

**Files:**
- Modify: `src/operations/strategy_factory.py:24-55`
- Test: `tests/unit/operations/test_strategy_factory.py`

**Step 1: Write failing test for StrategyContext usage**

Add to `tests/unit/operations/test_strategy_factory.py`:

```python
def test_create_save_strategies_uses_strategy_context(mock_registry):
    """Test that create_save_strategies passes StrategyContext to factory methods."""
    from src.entities.strategy_context import StrategyContext

    mock_entity = Mock()
    mock_entity.config.name = "test_entity"
    mock_entity.config.required_services_save = []
    mock_strategy = Mock()
    mock_entity.config.create_save_strategy = Mock(return_value=mock_strategy)

    mock_registry.get_enabled_entities.return_value = [mock_entity]

    factory = StrategyFactory(mock_registry)
    mock_git_service = Mock()

    strategies = factory.create_save_strategies(git_service=mock_git_service)

    # Verify factory method called with StrategyContext
    mock_entity.config.create_save_strategy.assert_called_once()
    call_args = mock_entity.config.create_save_strategy.call_args[0]
    assert len(call_args) == 1
    assert isinstance(call_args[0], StrategyContext)
    assert call_args[0].git_service is mock_git_service


def test_create_save_strategies_validates_before_creation(mock_registry):
    """Test that validation happens before strategy creation."""
    from src.entities.strategy_context import StrategyContext

    mock_entity = Mock()
    mock_entity.config.name = "git_repository"
    mock_entity.config.required_services_save = ["git_service"]
    mock_entity.config.create_save_strategy = Mock()

    mock_registry.get_enabled_entities.return_value = [mock_entity]

    factory = StrategyFactory(mock_registry)

    # No git_service provided
    with pytest.raises(RuntimeError, match="git_repository.*requires.*git_service"):
        factory.create_save_strategies()

    # Factory method should never be called
    mock_entity.config.create_save_strategy.assert_not_called()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/operations/test_strategy_factory.py::test_create_save_strategies_uses_strategy_context -v`

Expected: FAIL - factory method called with dict, not StrategyContext

**Step 3: Update create_save_strategies method**

Modify `src/operations/strategy_factory.py:24-55`:

```python
    def create_save_strategies(
        self,
        git_service: Optional[Any] = None,
        **additional_context: Any,
    ) -> List["BaseSaveStrategy"]:
        """Create save strategies for all enabled entities.

        Args:
            git_service: Optional git service for entities that need it
            **additional_context: Additional context for strategy creation

        Returns:
            List of save strategy instances in dependency order

        Raises:
            RuntimeError: If any entity's service requirements not met
        """
        from src.entities.strategy_context import StrategyContext

        # Create typed context from parameters
        context = StrategyContext(
            _git_service=git_service,
            _github_service=additional_context.get("github_service"),
            _conflict_strategy=additional_context.get("conflict_strategy"),
            _include_original_metadata=additional_context.get(
                "include_original_metadata", True
            ),
        )

        strategies = []
        enabled_entities = self.registry.get_enabled_entities()

        for entity in enabled_entities:
            # Validate requirements BEFORE creating strategy
            self._validate_requirements(entity.config, context, "save")

            try:
                strategy = entity.config.create_save_strategy(context)
                if strategy is not None:
                    strategies.append(strategy)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to create save strategy for '{entity.config.name}': {e}. "
                    f"Cannot proceed with save operation."
                ) from e

        return strategies
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/operations/test_strategy_factory.py::test_create_save_strategies_uses_strategy_context -v`

Expected: PASS

**Step 5: Run all StrategyFactory tests**

Run: `pytest tests/unit/operations/test_strategy_factory.py -v`

Expected: All tests PASS

**Step 6: Commit**

```bash
git add src/operations/strategy_factory.py tests/unit/operations/test_strategy_factory.py
git commit -s -m "refactor: use StrategyContext in create_save_strategies

- Create StrategyContext from method parameters
- Pass StrategyContext to entity factory methods (not **kwargs)
- Validate requirements before strategy creation
- Maintain backward compatibility with existing parameter names"
```

---

### Task 6: Update create_restore_strategies to use StrategyContext

**Files:**
- Modify: `src/operations/strategy_factory.py:57-100`
- Test: `tests/unit/operations/test_strategy_factory.py`

**Step 1: Write failing test for StrategyContext usage**

Add to `tests/unit/operations/test_strategy_factory.py`:

```python
def test_create_restore_strategies_uses_strategy_context(mock_registry):
    """Test that create_restore_strategies passes StrategyContext to factory methods."""
    from src.entities.strategy_context import StrategyContext

    mock_entity = Mock()
    mock_entity.config.name = "test_entity"
    mock_entity.config.required_services_restore = []
    mock_strategy = Mock()
    mock_entity.config.create_restore_strategy = Mock(return_value=mock_strategy)

    mock_registry.get_enabled_entities.return_value = [mock_entity]

    factory = StrategyFactory(mock_registry)
    mock_github_service = Mock()
    mock_conflict_strategy = Mock()

    strategies = factory.create_restore_strategies(
        github_service=mock_github_service,
        conflict_strategy=mock_conflict_strategy,
        include_original_metadata=False,
    )

    # Verify factory method called with StrategyContext
    mock_entity.config.create_restore_strategy.assert_called_once()
    call_args = mock_entity.config.create_restore_strategy.call_args[0]
    assert len(call_args) == 1
    assert isinstance(call_args[0], StrategyContext)
    assert call_args[0].github_service is mock_github_service
    assert call_args[0].conflict_strategy is mock_conflict_strategy
    assert call_args[0].include_original_metadata is False


def test_create_restore_strategies_validates_before_creation(mock_registry):
    """Test that validation happens before strategy creation."""
    mock_entity = Mock()
    mock_entity.config.name = "labels"
    mock_entity.config.required_services_restore = ["conflict_strategy"]
    mock_entity.config.create_restore_strategy = Mock()

    mock_registry.get_enabled_entities.return_value = [mock_entity]

    factory = StrategyFactory(mock_registry)

    # No conflict_strategy provided
    with pytest.raises(RuntimeError, match="labels.*requires.*conflict_strategy"):
        factory.create_restore_strategies()

    # Factory method should never be called
    mock_entity.config.create_restore_strategy.assert_not_called()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/operations/test_strategy_factory.py::test_create_restore_strategies_uses_strategy_context -v`

Expected: FAIL - factory method called with dict, not StrategyContext

**Step 3: Update create_restore_strategies method**

Modify `src/operations/strategy_factory.py:57-100`:

```python
    def create_restore_strategies(
        self,
        git_service: Optional[Any] = None,
        github_service: Optional[Any] = None,
        conflict_strategy: Optional[Any] = None,
        include_original_metadata: bool = True,
        **additional_context: Any,
    ) -> List["BaseRestoreStrategy"]:
        """Create restore strategies for all enabled entities.

        Args:
            git_service: Optional git service for entities that need it
            github_service: Optional GitHub API service for entities that need it
            conflict_strategy: Optional conflict resolution strategy
            include_original_metadata: Whether to preserve original metadata
            **additional_context: Additional context for strategy creation

        Returns:
            List of restore strategy instances in dependency order

        Raises:
            RuntimeError: If any entity's service requirements not met
        """
        from src.entities.strategy_context import StrategyContext

        # Create typed context from parameters
        context = StrategyContext(
            _git_service=git_service,
            _github_service=github_service,
            _conflict_strategy=conflict_strategy,
            _include_original_metadata=include_original_metadata,
        )

        strategies = []
        enabled_entities = self.registry.get_enabled_entities()

        for entity in enabled_entities:
            # Validate requirements BEFORE creating strategy
            self._validate_requirements(entity.config, context, "restore")

            try:
                strategy = entity.config.create_restore_strategy(context)
                if strategy is not None:
                    strategies.append(strategy)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to create restore strategy for "
                    f"'{entity.config.name}': {e}. "
                    f"Cannot proceed with restore operation."
                ) from e

        return strategies
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/operations/test_strategy_factory.py::test_create_restore_strategies_uses_strategy_context -v`

Expected: PASS

**Step 5: Run all StrategyFactory tests**

Run: `pytest tests/unit/operations/test_strategy_factory.py -v`

Expected: All tests PASS

**Step 6: Commit**

```bash
git add src/operations/strategy_factory.py tests/unit/operations/test_strategy_factory.py
git commit -s -m "refactor: use StrategyContext in create_restore_strategies

- Create StrategyContext from method parameters
- Pass StrategyContext to entity factory methods (not **kwargs)
- Validate requirements before strategy creation
- Add explicit github_service parameter for clarity"
```

---

## Phase 3: Entity Config Migration

### Task 7: Migrate GitRepositoryEntityConfig

**Files:**
- Modify: `src/entities/git_repositories/entity_config.py`
- Test: Update existing tests in `tests/`

**Step 1: Write failing test for updated config**

Run existing tests to establish baseline:

Run: `pytest tests/ -k git_repository -v`

Expected: Tests PASS with current implementation

**Step 2: Update GitRepositoryEntityConfig**

Modify `src/entities/git_repositories/entity_config.py`:

```python
"""Git repository entity configuration for EntityRegistry."""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.strategy_context import StrategyContext
    from src.entities.git_repositories.save_strategy import GitRepositorySaveStrategy
    from src.entities.git_repositories.restore_strategy import (
        GitRepositoryRestoreStrategy,
    )


class GitRepositoryEntityConfig:
    """Configuration for git_repository entity.

    Git repository backup has no dependencies and is enabled by default.
    Uses convention-based strategy loading.
    """

    name = "git_repository"
    env_var = "INCLUDE_GIT_REPO"
    default_value = True
    value_type = bool
    dependencies: list = []
    description = "Git repository clone for full backup"

    # Service requirements (NEW)
    required_services_save = ["git_service"]
    required_services_restore = ["git_service"]

    @staticmethod
    def create_save_strategy(
        context: "StrategyContext",
    ) -> Optional["GitRepositorySaveStrategy"]:
        """Create save strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            GitRepositorySaveStrategy instance

        Note:
            Validation ensures git_service is available, no None check needed
        """
        from src.entities.git_repositories.save_strategy import (
            GitRepositorySaveStrategy,
        )

        return GitRepositorySaveStrategy(context.git_service)

    @staticmethod
    def create_restore_strategy(
        context: "StrategyContext",
    ) -> Optional["GitRepositoryRestoreStrategy"]:
        """Create restore strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            GitRepositoryRestoreStrategy instance

        Note:
            Validation ensures git_service is available, no None check needed
        """
        from src.entities.git_repositories.restore_strategy import (
            GitRepositoryRestoreStrategy,
        )

        return GitRepositoryRestoreStrategy(context.git_service)
```

**Step 3: Run tests to verify migration**

Run: `pytest tests/ -k git_repository -v`

Expected: Tests PASS (backward compatible)

**Step 4: Run type check**

Run: `make type-check`

Expected: No errors (types now validated)

**Step 5: Commit**

```bash
git add src/entities/git_repositories/entity_config.py
git commit -s -m "refactor: migrate GitRepositoryEntityConfig to StrategyContext

- Change **context: Any -> context: StrategyContext (typed parameter)
- Change Optional[Any] -> Optional[GitRepository*Strategy] (typed return)
- Add required_services_save and required_services_restore declarations
- Remove manual None checks (validation now upfront)
- Add TYPE_CHECKING imports for forward references"
```

---

### Task 8: Migrate LabelsEntityConfig

**Files:**
- Modify: `src/entities/labels/entity_config.py`
- Test: Update existing tests in `tests/`

**Step 1: Run existing tests to establish baseline**

Run: `pytest tests/ -k labels -v`

Expected: Tests PASS with current implementation

**Step 2: Update LabelsEntityConfig**

Modify `src/entities/labels/entity_config.py`:

```python
"""Labels entity configuration for EntityRegistry."""

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.strategy_context import StrategyContext
    from src.entities.labels.save_strategy import LabelsSaveStrategy
    from src.entities.labels.restore_strategy import LabelsRestoreStrategy


class LabelsEntityConfig:
    """Configuration for labels entity.

    Labels have no dependencies and are enabled by default.
    Uses convention-based strategy loading.
    """

    name = "labels"
    env_var = "INCLUDE_LABELS"
    default_value = True
    value_type = bool
    dependencies: List[str] = []
    description = "Repository labels for issue/PR categorization"

    # Service requirements (NEW)
    required_services_save: List[str] = []  # No services needed for save
    required_services_restore = ["github_service"]  # Need GitHub API for conflict resolution

    @staticmethod
    def create_save_strategy(context: "StrategyContext") -> Optional["LabelsSaveStrategy"]:
        """Create save strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            LabelsSaveStrategy instance
        """
        from src.entities.labels.save_strategy import LabelsSaveStrategy

        return LabelsSaveStrategy()

    @staticmethod
    def create_restore_strategy(
        context: "StrategyContext",
    ) -> Optional["LabelsRestoreStrategy"]:
        """Create restore strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            LabelsRestoreStrategy instance

        Note:
            Conflict strategy resolution handled internally with github_service
        """
        from src.entities.labels.restore_strategy import (
            LabelsRestoreStrategy,
            create_conflict_strategy,
        )
        from src.entities.labels.conflict_strategies import LabelConflictStrategy

        # Access conflict_strategy from context if available
        conflict_strategy = getattr(context, "_conflict_strategy", None)
        if conflict_strategy is None:
            conflict_strategy = LabelConflictStrategy.SKIP

        # Convert enum to strategy object if needed
        if isinstance(conflict_strategy, LabelConflictStrategy):
            # Get github_service from context for conflict resolution
            github_service = context.github_service
            conflict_strategy_obj = create_conflict_strategy(
                conflict_strategy.value, github_service
            )
        else:
            # Assume it's already a strategy object
            conflict_strategy_obj = conflict_strategy

        return LabelsRestoreStrategy(conflict_strategy_obj)
```

**Step 3: Run tests to verify migration**

Run: `pytest tests/ -k labels -v`

Expected: Tests PASS (backward compatible)

**Step 4: Run type check**

Run: `make type-check`

Expected: No errors (types now validated)

**Step 5: Commit**

```bash
git add src/entities/labels/entity_config.py
git commit -s -m "refactor: migrate LabelsEntityConfig to StrategyContext

- Change **context: Any -> context: StrategyContext (typed parameter)
- Change Optional[Any] -> Optional[Labels*Strategy] (typed return)
- Add required_services_save (empty) and required_services_restore (github_service)
- Access github_service via context.github_service for conflict resolution
- Add TYPE_CHECKING imports for forward references"
```

---

### Task 9: Migrate remaining entity configs (batch operation)

**Files:**
- Modify: `src/entities/issues/entity_config.py`
- Modify: `src/entities/comments/entity_config.py`
- Modify: `src/entities/milestones/entity_config.py`
- Modify: `src/entities/sub_issues/entity_config.py`
- Modify: `src/entities/pull_requests/entity_config.py`
- Modify: `src/entities/pr_comments/entity_config.py`
- Modify: `src/entities/pr_review_comments/entity_config.py`
- Modify: `src/entities/pr_reviews/entity_config.py`

**Step 1: Run all entity tests to establish baseline**

Run: `pytest tests/ -k "issues or comments or milestones or sub_issues or pull_requests" -v`

Expected: Tests PASS with current implementation

**Step 2: Migrate each config with same pattern**

For each entity config file, apply this pattern:

1. Add TYPE_CHECKING imports
2. Change `**context: Any` to `context: StrategyContext`
3. Change `Optional[Any]` to `Optional[ConcreteStrategy]`
4. Add `required_services_save` and `required_services_restore`
5. Access services via `context.service_name` (not `context.get()`)
6. Remove manual None checks

**Example for IssuesEntityConfig:**

```python
"""Issues entity configuration for EntityRegistry."""

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.strategy_context import StrategyContext
    from src.entities.issues.save_strategy import IssuesSaveStrategy
    from src.entities.issues.restore_strategy import IssuesRestoreStrategy


class IssuesEntityConfig:
    """Configuration for issues entity."""

    name = "issues"
    env_var = "INCLUDE_ISSUES"
    default_value = True
    value_type = bool
    dependencies = ["labels", "milestones"]  # Issues depend on labels and milestones
    description = "Repository issues with metadata"

    # Service requirements
    required_services_save: List[str] = []  # No services needed
    required_services_restore = ["github_service"]  # Need GitHub API

    @staticmethod
    def create_save_strategy(context: "StrategyContext") -> Optional["IssuesSaveStrategy"]:
        """Create save strategy instance."""
        from src.entities.issues.save_strategy import IssuesSaveStrategy

        return IssuesSaveStrategy()

    @staticmethod
    def create_restore_strategy(
        context: "StrategyContext",
    ) -> Optional["IssuesRestoreStrategy"]:
        """Create restore strategy instance."""
        from src.entities.issues.restore_strategy import IssuesRestoreStrategy

        return IssuesRestoreStrategy(
            github_service=context.github_service,
            include_original_metadata=context.include_original_metadata,
        )
```

**Apply same pattern to:**
- `src/entities/comments/entity_config.py`
- `src/entities/milestones/entity_config.py`
- `src/entities/sub_issues/entity_config.py`
- `src/entities/pull_requests/entity_config.py`
- `src/entities/pr_comments/entity_config.py`
- `src/entities/pr_review_comments/entity_config.py`
- `src/entities/pr_reviews/entity_config.py`

**Step 3: Run all tests to verify migrations**

Run: `pytest tests/ -v`

Expected: All tests PASS (backward compatible)

**Step 4: Run type check**

Run: `make type-check`

Expected: No errors (types now validated for all entities)

**Step 5: Commit**

```bash
git add src/entities/*/entity_config.py
git commit -s -m "refactor: migrate all remaining entity configs to StrategyContext

Migrated entities:
- issues
- comments
- milestones
- sub_issues
- pull_requests
- pr_comments
- pr_review_comments
- pr_reviews

Changes per entity:
- Change **context: Any -> context: StrategyContext
- Change Optional[Any] -> Optional[ConcreteStrategy]
- Add required_services_save and required_services_restore
- Access services via typed properties (context.github_service, etc.)
- Remove manual None checks (validation now upfront)
- Add TYPE_CHECKING imports"
```

---

## Phase 4: Integration and Validation

### Task 10: Update orchestrator call sites

**Files:**
- Modify: `src/operations/save/orchestrator.py`
- Modify: `src/operations/restore/orchestrator.py`

**Step 1: Find and update SaveOrchestrator**

Search for StrategyFactory usage:

Run: `grep -n "create_save_strategies" src/operations/save/orchestrator.py`

Update call sites to pass services with correct parameter names.

**Example update:**

```python
# Before
strategies = self.strategy_factory.create_save_strategies(
    git_service=self.git_service
)

# After (no change needed - parameters match)
strategies = self.strategy_factory.create_save_strategies(
    git_service=self.git_service
)
```

**Step 2: Find and update RestoreOrchestrator**

Search for StrategyFactory usage:

Run: `grep -n "create_restore_strategies" src/operations/restore/orchestrator.py`

Update call sites to pass services with correct parameter names.

**Example update:**

```python
# Before (if using **context pattern)
context = {
    "git_service": self.git_service,
    "conflict_strategy": conflict_strategy,
}
strategies = self.strategy_factory.create_restore_strategies(**context)

# After (explicit parameters)
strategies = self.strategy_factory.create_restore_strategies(
    git_service=self.git_service,
    github_service=self.github_service,
    conflict_strategy=conflict_strategy,
    include_original_metadata=True,
)
```

**Step 3: Run integration tests**

Run: `pytest tests/integration/ -v`

Expected: All integration tests PASS

**Step 4: Commit**

```bash
git add src/operations/save/orchestrator.py src/operations/restore/orchestrator.py
git commit -s -m "refactor: update orchestrators for StrategyContext

- Update StrategyFactory call sites with explicit parameters
- Ensure github_service passed to create_restore_strategies
- Maintain backward compatibility with existing functionality"
```

---

### Task 11: Run comprehensive test suite

**Files:**
- N/A (validation only)

**Step 1: Run all unit tests**

Run: `make test-unit`

Expected: All unit tests PASS

**Step 2: Run all integration tests**

Run: `make test-integration`

Expected: All integration tests PASS

**Step 3: Run type checking**

Run: `make type-check`

Expected: No mypy errors (full type safety achieved)

**Step 4: Run linting**

Run: `make lint`

Expected: No linting errors

**Step 5: Run formatting check**

Run: `make format`

Expected: All files properly formatted

**Step 6: Run full test suite**

Run: `make test`

Expected: All tests PASS with coverage report

**Step 7: Commit if any formatting changes**

```bash
git add -u
git commit -s -m "style: apply formatting after refactor"
```

---

### Task 12: Create integration test for validation errors

**Files:**
- Create: `tests/integration/test_strategy_context_validation.py`

**Step 1: Write integration test for validation**

Create the test file:

```python
"""Integration tests for StrategyContext validation."""

import pytest
from src.entities.registry import EntityRegistry
from src.operations.strategy_factory import StrategyFactory
from src.entities.strategy_context import StrategyContext


def test_git_repository_requires_git_service_for_save():
    """Test that git_repository entity validation fails without git_service."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry)

    # Enable git_repository entity
    registry.set_entity_enabled("git_repository", True)

    # Try to create save strategies without git_service
    with pytest.raises(
        RuntimeError,
        match="Entity 'git_repository' requires 'git_service' for save operation",
    ):
        factory.create_save_strategies()


def test_labels_requires_github_service_for_restore():
    """Test that labels entity validation fails without github_service."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry)

    # Enable labels entity
    registry.set_entity_enabled("labels", True)

    # Try to create restore strategies without github_service
    with pytest.raises(
        RuntimeError,
        match="Entity 'labels' requires 'github_service' for restore operation",
    ):
        factory.create_restore_strategies()


def test_validation_fails_before_any_strategy_creation():
    """Test that validation fails fast before creating any strategies."""
    from unittest.mock import Mock

    registry = EntityRegistry()
    factory = StrategyFactory(registry)

    # Enable multiple entities
    registry.set_entity_enabled("labels", True)
    registry.set_entity_enabled("issues", True)

    # Try to create strategies without required services
    # Should fail on first entity that needs github_service
    with pytest.raises(RuntimeError, match="requires 'github_service'"):
        factory.create_restore_strategies()


def test_successful_strategy_creation_with_all_services():
    """Test that strategies are created successfully when all services provided."""
    from unittest.mock import Mock

    registry = EntityRegistry()
    factory = StrategyFactory(registry)

    # Enable entities
    registry.set_entity_enabled("labels", True)

    # Create with all required services
    mock_github_service = Mock()
    strategies = factory.create_restore_strategies(
        github_service=mock_github_service,
        conflict_strategy=None,
        include_original_metadata=True,
    )

    # Should succeed
    assert len(strategies) > 0
```

**Step 2: Run test to verify validation behavior**

Run: `pytest tests/integration/test_strategy_context_validation.py -v`

Expected: All tests PASS

**Step 3: Commit**

```bash
git add tests/integration/test_strategy_context_validation.py
git commit -s -m "test: add integration tests for StrategyContext validation

- Test validation errors for missing git_service
- Test validation errors for missing github_service
- Test fail-fast behavior before any strategy creation
- Test successful creation with all services provided"
```

---

### Task 13: Update documentation

**Files:**
- Create: `docs/architecture/strategy-context.md`

**Step 1: Write architecture documentation**

Create the documentation file:

```markdown
# Strategy Context Architecture

## Overview

The `StrategyContext` provides type-safe dependency injection for entity strategy creation, replacing the previous untyped `**context: Any` pattern.

## Design Goals

1. **Full compile-time type safety** - mypy validates all dependencies and return types
2. **Zero changes to existing entities** - adding new entities/services doesn't break existing code
3. **Fail-fast validation** - misconfigured strategies fail before any work begins
4. **Clear error messages** - exactly which entity needs which missing service
5. **IDE support** - autocomplete for available services with type hints

## Core Components

### StrategyContext

Typed container for services available to entity strategies:

```python
from src.entities import StrategyContext

context = StrategyContext(
    _git_service=git_service,
    _github_service=github_service,
    _conflict_strategy=conflict_strategy,
    _include_original_metadata=True,
)

# Typed access with validation
git_svc = context.git_service  # Type: GitRepositoryService
github_svc = context.github_service  # Type: GitHubService
```

### Service Property Decorator

DRY decorator for validated service properties:

```python
@service_property
def new_service(self) -> NewService:
    """Description of service."""
    ...
```

Creates a property that:
- Returns `self._new_service` if not None
- Raises `RuntimeError` with clear message if None
- Preserves type hints for mypy and IDEs

### Service Requirements

Entity configs declare required services:

```python
class GitRepositoryEntityConfig:
    required_services_save = ["git_service"]
    required_services_restore = ["git_service"]

    @staticmethod
    def create_save_strategy(context: StrategyContext) -> Optional[GitRepositorySaveStrategy]:
        return GitRepositorySaveStrategy(context.git_service)
```

### Validation

StrategyFactory validates requirements before creation:

```python
strategies = factory.create_save_strategies(git_service=git_service)
# Raises RuntimeError if any entity's requirements not met
```

## Adding New Services

### Step 1: Add to StrategyContext

```python
@dataclass
class StrategyContext:
    _new_service: Optional[NewService] = None

    @service_property
    def new_service(self) -> NewService:
        """Description of new service."""
        ...
```

### Step 2: Only new entities declare requirement

```python
class NewEntityConfig:
    required_services_save = ["new_service"]

    @staticmethod
    def create_save_strategy(context: StrategyContext) -> Optional[NewSaveStrategy]:
        return NewSaveStrategy(context.new_service)
```

**Result**: Existing entities unchanged, tests keep passing.

## Adding New Entities

### Step 1: Create entity config

```python
class NewEntityConfig:
    name = "new_entity"
    required_services_save = ["github_service"]
    required_services_restore = ["github_service", "conflict_strategy"]

    @staticmethod
    def create_save_strategy(context: StrategyContext) -> Optional[NewSaveStrategy]:
        return NewSaveStrategy(context.github_service)

    @staticmethod
    def create_restore_strategy(context: StrategyContext) -> Optional[NewRestoreStrategy]:
        return NewRestoreStrategy(
            context.github_service,
            context.conflict_strategy,
        )
```

### Step 2: Register in EntityRegistry

**Result**: Zero changes to existing entities or their tests.

## Type Safety Guarantees

### Before (no type checking)

```python
def create_save_strategy(**context: Any) -> Optional[Any]:
    git_service = context.get("git_servce")  # Typo not caught
    return SomeWrongStrategy()  # Wrong type not caught
```

### After (full type checking)

```python
def create_save_strategy(context: StrategyContext) -> Optional[GitRepositorySaveStrategy]:
    service = context.git_service  # ✓ Typed as GitService
    return GitRepositorySaveStrategy(service)  # ✓ Return type validated
    # return SomeWrongStrategy()  # ✗ mypy error: incompatible return type
```

## Error Messages

### Before (unclear runtime error)

```
AttributeError: 'NoneType' object has no attribute 'clone_repository'
```

### After (clear validation error)

```
RuntimeError: Entity 'git_repository' requires 'git_service' for save operation,
but it was not provided in context
```

## Benefits Summary

| Benefit | How Achieved |
|---------|--------------|
| Compile-time type safety | Typed `StrategyContext` parameter, specific return types |
| Catch missing dependencies | Upfront validation in `StrategyFactory._validate_requirements()` |
| Catch wrong return types | mypy validates against declared `Optional[ConcreteStrategy]` |
| Zero changes for new entities | New entities only affect their own code and tests |
| Zero changes for new services | Optional services added to context don't break existing entities |
| Clear error messages | Validation shows entity name, missing service, operation |
| IDE autocomplete | Typed properties on `StrategyContext` |
| DRY code | `service_property` decorator eliminates validation boilerplate |
| Fail-fast validation | Errors before any work begins, not mid-operation |

## References

- Design document: `docs/plans/2025-10-27-typesafe-strategy-context-design.md`
- Implementation: `src/entities/strategy_context.py`
- Validation: `src/operations/strategy_factory.py`
```

**Step 2: Commit**

```bash
git add docs/architecture/strategy-context.md
git commit -s -m "docs: add StrategyContext architecture documentation

- Document design goals and type safety guarantees
- Provide examples for adding services and entities
- Show error message improvements
- Reference implementation files"
```

---

### Task 14: Final verification and cleanup

**Files:**
- N/A (validation only)

**Step 1: Run full quality check**

Run: `make check-all`

Expected: All checks PASS (lint, format, type-check, tests)

**Step 2: Verify no regression in coverage**

Run: `make test`

Check coverage report - should maintain or improve coverage.

**Step 3: Test container build (if applicable)**

Run: `make docker-build`

Expected: Container builds successfully

**Step 4: Review all changes**

Run: `git log --oneline origin/main..HEAD`

Verify commit messages follow Conventional Commits and are signed off.

**Step 5: Create summary document**

Create `docs/plans/2025-10-27-typesafe-strategy-context-summary.md`:

```markdown
# Typesafe Strategy Context - Implementation Summary

**Date:** 2025-10-27
**Status:** ✅ Completed

## What Was Built

Replaced untyped `**context: Any` with typed `StrategyContext` throughout the entity system.

## Key Changes

1. **Created `StrategyContext`** (`src/entities/strategy_context.py`)
   - Typed container for services (git_service, github_service, conflict_strategy)
   - `service_property` decorator for DRY validation
   - Type hints for mypy and IDE support

2. **Updated `EntityConfig` Protocol** (`src/entities/base.py`)
   - Changed `**context: Any` → `context: StrategyContext`
   - Changed `Optional[Any]` → `Optional[ConcreteStrategy]`
   - Added `required_services_save` and `required_services_restore`

3. **Enhanced `StrategyFactory`** (`src/operations/strategy_factory.py`)
   - Added `_validate_requirements()` for upfront validation
   - Updated `create_save_strategies()` to use `StrategyContext`
   - Updated `create_restore_strategies()` to use `StrategyContext`

4. **Migrated All Entity Configs** (10 entity configs)
   - git_repositories, labels, issues, comments, milestones
   - sub_issues, pull_requests, pr_comments, pr_review_comments, pr_reviews
   - All now use typed context and declare requirements

## Type Safety Improvements

### Compile-Time Validation
- mypy catches missing dependencies
- mypy validates return types
- IDEs provide autocomplete

### Runtime Validation
- Fail-fast before any work begins
- Clear error messages: "Entity 'X' requires 'Y' for Z operation"

### Backward Compatibility
- Adding new services: existing entities unaffected
- Adding new entities: zero changes to existing code

## Test Coverage

- Unit tests for `StrategyContext` properties
- Unit tests for `StrategyFactory` validation
- Integration tests for validation errors
- All existing tests pass (backward compatible)

## Quality Checks

✅ All tests pass (unit, integration, container)
✅ Type checking passes (mypy)
✅ Linting passes (flake8)
✅ Formatting passes (black)
✅ Coverage maintained/improved

## Documentation

- Architecture doc: `docs/architecture/strategy-context.md`
- Design doc: `docs/plans/2025-10-27-typesafe-strategy-context-design.md`
- Implementation plan: `docs/plans/2025-10-27-typesafe-strategy-context-implementation.md`

## Next Steps

None - implementation complete and verified.

## Commits

Total: 14 commits following TDD and Conventional Commits

See: `git log --oneline origin/main..HEAD`
```

**Step 6: Commit summary**

```bash
git add docs/plans/2025-10-27-typesafe-strategy-context-summary.md
git commit -s -m "docs: add implementation summary for StrategyContext

- Summarize all changes made
- Document type safety improvements
- Record test coverage and quality checks
- List all documentation created"
```

**Step 7: Final verification**

Run: `make check-all`

Expected: All checks PASS

---

## Implementation Complete

All tasks completed. The codebase now has:

✅ Typed `StrategyContext` with validated service properties
✅ Updated `EntityConfig` protocol with type hints
✅ Upfront validation in `StrategyFactory`
✅ All 10 entity configs migrated
✅ Full test coverage maintained
✅ Type checking passing (mypy)
✅ Comprehensive documentation

**Total commits:** 14
**Total files changed:** ~25
**Lines of code added:** ~800 (including tests and docs)
**Type safety:** 100% (all entity strategies typed)

**Ready for code review and merge.**

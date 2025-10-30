# Typesafe Strategy Context Design

**Date:** 2025-10-27
**Status:** Approved Design
**Author:** Claude Code with User

## Problem Statement

The current entity strategy creation system uses untyped `**context: Any` parameters and returns `Optional[Any]`, which prevents compile-time type checking:

```python
# Current (not type-safe)
@staticmethod
def create_save_strategy(**context: Any) -> Optional[Any]:
    git_service = context.get("git_service")  # No type checking
    if git_service is None:
        return None
    return GitRepositorySaveStrategy(git_service)
```

**Issues:**
1. mypy cannot catch missing dependencies or misspelled context keys
2. Method signatures don't document required dependencies
3. Runtime errors occur mid-operation when dependencies are missing
4. Adding new services risks breaking existing entities

## Design Goals

1. **Full compile-time type safety** - mypy validates all dependencies and return types
2. **Zero changes to existing entities** - adding new entities/services doesn't break existing code
3. **Fail-fast validation** - misconfigured strategies fail before any work begins
4. **Clear error messages** - exactly which entity needs which missing service
5. **IDE support** - autocomplete for available services with type hints

## Core Architecture

### 1. StrategyContext with Typed Services

Replace `**context: Any` with a typed `StrategyContext` class:

```python
from typing import Optional, Any
from dataclasses import dataclass


def service_property(func):
    """Decorator to create a validated service property.

    Converts a method that returns the private attribute name
    into a property that validates and returns the service.

    Usage:
        @service_property
        def git_service(self) -> GitService:
            '''Git repository service.'''
            ...

    This creates a property that:
    - Returns self._git_service if not None
    - Raises RuntimeError with clear message if None
    - Preserves type hints for mypy and IDEs
    """
    service_name = func.__name__
    private_attr = f"_{service_name}"

    @property
    def wrapper(self):
        value = getattr(self, private_attr, None)
        if value is None:
            raise RuntimeError(
                f"{service_name} is required but was not provided"
            )
        return value

    # Preserve type hints from original function
    wrapper.__annotations__ = func.__annotations__
    return wrapper


@dataclass
class StrategyContext:
    """Typed container for services available to entity strategies.

    Services are stored as private optional attributes and exposed
    as typed properties that validate on access.

    Adding new services:
    1. Add private attribute: _new_service: Optional[NewService] = None
    2. Add decorated property with type hint
    3. Existing entities unaffected

    Example:
        context = StrategyContext(_git_service=git_svc)
        service = context.git_service  # Typed, validated
    """

    # Private optional storage for services
    _git_service: Optional['GitService'] = None
    _github_service: Optional['GitHubService'] = None
    _conflict_strategy: Optional[Any] = None

    # Non-service configuration (has default, no validation needed)
    _include_original_metadata: bool = True

    # Public typed properties with validation
    @service_property
    def git_service(self) -> 'GitService':
        """Git repository service for cloning/restoring repositories."""
        ...

    @service_property
    def github_service(self) -> 'GitHubService':
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

**Key Design Decisions:**

- **Private storage with public properties**: Allows validation on access
- **service_property decorator**: DRY - eliminates boilerplate validation code
- **Type hints on properties**: mypy sees non-optional return types, IDEs get autocomplete
- **Clear error messages**: "git_service is required but was not provided"
- **Boolean configs as regular properties**: No validation needed for values with defaults

### 2. EntityConfig Service Requirements

Entities declare required services as class attributes:

```python
class GitRepositoryEntityConfig:
    """Configuration for git_repository entity."""

    name = "git_repository"
    env_var = "INCLUDE_GIT_REPO"
    default_value = True
    value_type = bool
    dependencies: list = []
    description = "Git repository clone for full backup"

    # NEW: Declare service requirements
    required_services_save = ["git_service"]
    required_services_restore = ["git_service"]

    @staticmethod
    def create_save_strategy(context: StrategyContext) -> Optional[GitRepositorySaveStrategy]:
        """Create save strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            GitRepositorySaveStrategy instance
        """
        from src.entities.git_repositories.save_strategy import GitRepositorySaveStrategy

        # No None checks needed - validation already done
        return GitRepositorySaveStrategy(context.git_service)

    @staticmethod
    def create_restore_strategy(context: StrategyContext) -> Optional[GitRepositoryRestoreStrategy]:
        """Create restore strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            GitRepositoryRestoreStrategy instance
        """
        from src.entities.git_repositories.restore_strategy import GitRepositoryRestoreStrategy

        return GitRepositoryRestoreStrategy(context.git_service)
```

**Changes from Current:**
- `**context: Any` → `context: StrategyContext` (typed parameter)
- `Optional[Any]` → `Optional[GitRepositorySaveStrategy]` (typed return)
- Added `required_services_save` and `required_services_restore` class attributes
- Removed `if git_service is None: return None` checks (validated upfront)

### 3. StrategyFactory Validation

StrategyFactory validates requirements before creating strategies:

```python
class StrategyFactory:
    """Factory for creating entity strategies from EntityRegistry."""

    def __init__(self, registry: "EntityRegistry"):
        self.registry = registry

    def create_save_strategies(
        self,
        context: StrategyContext
    ) -> List[BaseSaveStrategy]:
        """Create save strategies for all enabled entities.

        Args:
            context: Strategy context with available services

        Returns:
            List of save strategy instances in dependency order

        Raises:
            RuntimeError: If any entity's service requirements not met
        """
        strategies = []
        enabled_entities = self.registry.get_enabled_entities()

        for entity in enabled_entities:
            # Validate requirements BEFORE creating strategy
            self._validate_requirements(
                entity.config,
                context,
                "save"
            )

            strategy = entity.config.create_save_strategy(context)
            if strategy is not None:
                strategies.append(strategy)

        return strategies

    def create_restore_strategies(
        self,
        context: StrategyContext
    ) -> List[BaseRestoreStrategy]:
        """Create restore strategies for all enabled entities.

        Args:
            context: Strategy context with available services

        Returns:
            List of restore strategy instances in dependency order

        Raises:
            RuntimeError: If any entity's service requirements not met
        """
        strategies = []
        enabled_entities = self.registry.get_enabled_entities()

        for entity in enabled_entities:
            # Validate requirements BEFORE creating strategy
            self._validate_requirements(
                entity.config,
                context,
                "restore"
            )

            strategy = entity.config.create_restore_strategy(context)
            if strategy is not None:
                strategies.append(strategy)

        return strategies

    def _validate_requirements(
        self,
        config: EntityConfig,
        context: StrategyContext,
        operation: str  # "save" or "restore"
    ) -> None:
        """Validate required services are available in context.

        Args:
            config: Entity configuration
            context: Strategy context to validate
            operation: "save" or "restore"

        Raises:
            RuntimeError: If required service not available
        """
        required = getattr(
            config,
            f"required_services_{operation}",
            []  # Default to empty list for backward compatibility
        )

        for service_name in required:
            # Check if service is available (not None)
            private_attr = f"_{service_name}"
            if getattr(context, private_attr, None) is None:
                raise RuntimeError(
                    f"Entity '{config.name}' requires '{service_name}' "
                    f"for {operation} operation, but it was not provided in context"
                )
```

**Validation Strategy:**
- Happens before any strategy creation
- Checks declared requirements against context
- Clear error messages with entity name and missing service
- Backward compatible (entities without requirements work fine)

### 4. Updated EntityConfig Protocol

The `EntityConfig` protocol in `src/entities/base.py` needs updating:

```python
class EntityConfig(Protocol):
    """Protocol for entity configuration metadata."""

    name: str
    env_var: str
    default_value: Union[bool, Set[int]]
    value_type: Type
    dependencies: List[str] = []
    description: str = ""

    # NEW: Optional service requirements
    required_services_save: List[str] = []
    required_services_restore: List[str] = []

    @staticmethod
    def create_save_strategy(context: StrategyContext) -> Optional[BaseSaveStrategy]:
        """Factory method for creating save strategy instances.

        Args:
            context: Typed strategy context with validated services

        Returns:
            Configured save strategy instance, or None if not applicable
        """
        ...

    @staticmethod
    def create_restore_strategy(context: StrategyContext) -> Optional[BaseRestoreStrategy]:
        """Factory method for creating restore strategy instances.

        Args:
            context: Typed strategy context with validated services

        Returns:
            Configured restore strategy instance, or None if not applicable
        """
        ...
```

## Type Safety Guarantees

### mypy Validation

**Before (no type checking):**
```python
def create_save_strategy(**context: Any) -> Optional[Any]:
    git_service = context.get("git_servce")  # Typo not caught
    return SomeWrongStrategy()  # Wrong type not caught
```

**After (full type checking):**
```python
def create_save_strategy(context: StrategyContext) -> Optional[GitRepositorySaveStrategy]:
    service = context.git_service  # ✓ Typed as GitService
    return GitRepositorySaveStrategy(service)  # ✓ Return type validated
    # return SomeWrongStrategy()  # ✗ mypy error: incompatible return type
```

### IDE Support

- **Autocomplete**: Typing `context.` shows available services with types
- **Type hints**: Hovering shows `git_service: GitService`
- **Jump to definition**: Click service to see service class
- **Refactoring**: Renaming services updates all usages

## Extensibility Patterns

### Adding a New Service

**Step 1**: Add to StrategyContext
```python
@dataclass
class StrategyContext:
    # Add private attribute
    _new_service: Optional[NewService] = None

    # Add decorated property
    @service_property
    def new_service(self) -> NewService:
        """Description of new service."""
        ...
```

**Step 2**: Only new/updated entities declare requirement
```python
class NewEntityConfig:
    required_services_save = ["new_service"]

    @staticmethod
    def create_save_strategy(context: StrategyContext) -> Optional[NewSaveStrategy]:
        return NewSaveStrategy(context.new_service)
```

**Result**: Existing entities unchanged, tests keep passing

### Adding a New Entity

**Step 1**: Create entity config
```python
class NewEntityConfig:
    name = "new_entity"
    # ... standard attributes ...
    required_services_save = ["github_service"]
    required_services_restore = ["github_service", "conflict_strategy"]

    @staticmethod
    def create_save_strategy(context: StrategyContext) -> Optional[NewSaveStrategy]:
        return NewSaveStrategy(context.github_service)
```

**Step 2**: Register in EntityRegistry

**Result**: Zero changes to existing entities or their tests

## Migration Path

### Phase 1: Add StrategyContext
1. Create `src/entities/strategy_context.py` with `StrategyContext` and `service_property`
2. Add to `src/entities/__init__.py` exports
3. Update `EntityConfig` protocol in `src/entities/base.py`

### Phase 2: Update StrategyFactory
1. Update `create_save_strategies()` to accept `StrategyContext`
2. Update `create_restore_strategies()` to accept `StrategyContext`
3. Add `_validate_requirements()` method
4. Update all call sites to create and pass `StrategyContext`

### Phase 3: Migrate Entity Configs
For each entity config (labels, issues, git_repository, etc.):
1. Add `required_services_save` and `required_services_restore` class attributes
2. Change `**context: Any` → `context: StrategyContext`
3. Change return type from `Optional[Any]` → `Optional[ConcreteStrategy]`
4. Remove manual None checks (validation now upfront)
5. Update unit tests to use `StrategyContext`

### Phase 4: Validation
1. Run `make type-check` to verify all type hints correct
2. Run `make test` to verify all tests pass
3. Test error messages for missing services

## Error Message Examples

**Before (unclear runtime error):**
```
AttributeError: 'NoneType' object has no attribute 'clone_repository'
```

**After (clear validation error):**
```
RuntimeError: Entity 'git_repository' requires 'git_service' for save operation,
but it was not provided in context
```

## Benefits Summary

| Benefit | How Achieved |
|---------|-------------|
| **Compile-time type safety** | Typed `StrategyContext` parameter, specific return types |
| **Catch missing dependencies** | Upfront validation in `StrategyFactory._validate_requirements()` |
| **Catch wrong return types** | mypy validates against declared `Optional[ConcreteStrategy]` |
| **Zero changes for new entities** | New entities only affect their own code and tests |
| **Zero changes for new services** | Optional services added to context don't break existing entities |
| **Clear error messages** | Validation shows entity name, missing service, operation |
| **IDE autocomplete** | Typed properties on `StrategyContext` |
| **DRY code** | `service_property` decorator eliminates validation boilerplate |
| **Fail-fast validation** | Errors before any work begins, not mid-operation |

## Testing Approach

### Unit Tests for StrategyContext
```python
def test_service_property_returns_value_when_set():
    context = StrategyContext(_git_service=mock_git_service)
    assert context.git_service == mock_git_service

def test_service_property_raises_when_none():
    context = StrategyContext()
    with pytest.raises(RuntimeError, match="git_service is required"):
        _ = context.git_service
```

### Unit Tests for StrategyFactory Validation
```python
def test_validate_requirements_passes_when_services_available():
    context = StrategyContext(_git_service=mock_git_service)
    config = GitRepositoryEntityConfig()
    factory._validate_requirements(config, context, "save")  # Should not raise

def test_validate_requirements_raises_when_service_missing():
    context = StrategyContext()  # No services
    config = GitRepositoryEntityConfig()
    with pytest.raises(RuntimeError, match="git_repository.*requires.*git_service"):
        factory._validate_requirements(config, context, "save")
```

### Integration Tests
- Create strategies with valid context (should succeed)
- Create strategies with missing services (should fail with clear error)
- Verify existing entity tests still pass after migration

## Future Enhancements

### Optional: Generic Type Parameters
Could make StrategyContext generic for even stronger typing:
```python
@dataclass
class StrategyContext(Generic[T]):
    """Typed context parameterized by available services."""
    ...

# Usage
def create_save_strategies(
    context: StrategyContext[GitService, GitHubService]
) -> List[BaseSaveStrategy]:
    ...
```

This is optional and can be added later if desired.

## References

- Current implementation: `src/entities/base.py`, `src/operations/strategy_factory.py`
- Entity configs: `src/entities/*/entity_config.py`
- Related design: `docs/plans/2025-10-26-strategy-factory-method-implementation.md`

## Approval

Design approved by user on 2025-10-27.

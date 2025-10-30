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

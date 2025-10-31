# Strategy Context Template Update Design

**Date:** 2025-10-30
**Status:** Approved

## Overview

Update the entity generator templates (`src/tools/templates/`) to use the new StrategyContext pattern, replacing the untyped `**context: Any` approach with type-safe dependency injection.

## Problem Statement

Current entity generator produces entity configs using the legacy pattern:
- Factory methods accept `**context: Any` (no type safety)
- No explicit service requirements declaration
- Manual documentation of available context keys
- Zero-arg strategy instantiation by default

This conflicts with the StrategyContext architecture which provides:
- Full compile-time type safety via mypy
- Explicit service requirement declarations
- Fail-fast validation in StrategyFactory
- Clear error messages for missing dependencies

## Goals

1. Generate entity configs that follow the StrategyContext pattern
2. Allow developers to specify required services via CLI or interactive prompts
3. Generate type-safe service extraction code in factory methods
4. Maintain backward compatibility for existing entities
5. Provide clear defaults for new entities

## Design

### 1. Known Services Registry

Define available services in `generate_entity.py`:

```python
KNOWN_SERVICES = {
    'github_service': 'GitHub API service for issues, PRs, labels, etc.',
    'git_service': 'Git repository service for cloning/restoring repositories',
    'conflict_strategy': 'Conflict resolution strategy for restoration'
}
```

This provides:
- Service name validation
- Documentation for interactive prompts
- Type hint generation (future enhancement)

### 2. CLI Arguments

Add two new command-line arguments:

```bash
--save-services "github_service,git_service"
--restore-services "github_service,conflict_strategy"
```

Follows the same pattern as existing `--deps` argument (comma-separated values).

### 3. Interactive Prompts

When services not provided via CLI, prompt with available options:

```
Available services:
  - github_service: GitHub API service for issues, PRs, labels, etc.
  - git_service: Git repository service for cloning/restoring repositories
  - conflict_strategy: Conflict resolution strategy for restoration

Services required for save (comma-separated, or empty):
Services required for restore (comma-separated, or empty):
```

### 4. Entity Config Template Updates

**File:** `entity_config_template.py.j2`

Key changes:
- Add `TYPE_CHECKING` import for forward references
- Import `StrategyContext` type
- Add `required_services_save` and `required_services_restore` class attributes
- Change factory method signatures: `**context: Any` → `context: "StrategyContext"`
- Generate service extraction code when services declared
- Update return type hints to specific strategy classes

**Generated example (with services):**

```python
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.strategy_context import StrategyContext
    from src.entities.issues.save_strategy import IssuesSaveStrategy

class IssuesEntityConfig:
    name = "issues"
    # ... other config ...

    required_services_save: List[str] = ["github_service"]
    required_services_restore: List[str] = ["github_service", "conflict_strategy"]

    @staticmethod
    def create_save_strategy(
        context: "StrategyContext",
    ) -> Optional["IssuesSaveStrategy"]:
        """Create save strategy instance.

        Args:
            context: Typed strategy context with validated services
        """
        from src.entities.issues.save_strategy import IssuesSaveStrategy

        # Extract required services from context
        github_service = context.github_service

        return IssuesSaveStrategy(github_service)
```

**Generated example (no services):**

```python
@staticmethod
def create_save_strategy(
    context: "StrategyContext",
) -> Optional["LabelsSaveStrategy"]:
    """Create save strategy instance.

    Args:
        context: Typed strategy context with validated services
    """
    from src.entities.labels.save_strategy import LabelsSaveStrategy

    return LabelsSaveStrategy()
```

### 5. Strategy Template Updates

**Files:** `save_strategy_template.py.j2`, `restore_strategy_template.py.j2`

Update `__init__` signatures to accept declared services:

```python
def __init__(
    self,
    {% if services %}
    {% for service in services %}
    {{ service }}: {% if service == 'github_service' %}GitHubService{% elif service == 'git_service' %}GitRepositoryService{% else %}Any{% endif %},
    {% endfor %}
    {% endif %}
    data_path: Path,
    entity_config: "EntityConfig"
):
    """Initialize the save strategy.

    Args:
        {% for service in services %}
        {{ service }}: {{ service_descriptions[service] }}
        {% endfor %}
        data_path: Base path for data files
        entity_config: Configuration for this entity
    """
    super().__init__(
        {% if 'github_service' in services %}github_service, {% endif %}
        data_path,
        entity_config
    )
    {% for service in services %}
    {% if service != 'github_service' %}
    self.{{ service }} = {{ service }}
    {% endif %}
    {% endfor %}
```

**Type mapping:**
- `github_service` → `GitHubService`
- `git_service` → `GitRepositoryService`
- `conflict_strategy` → `Any` (polymorphic strategy interface)

### 6. Template Context Updates

Extend `prepare_template_context()` in `generate_entity.py`:

```python
def prepare_template_context(
    entity_name: str,
    env_var: str,
    value_type: str,
    default_value: str,
    dependencies: List[str],
    description: str,
    save_services: List[str],  # NEW
    restore_services: List[str],  # NEW
) -> dict:
    # ... existing context preparation ...

    context.update({
        "required_services_save": repr(save_services),
        "required_services_restore": repr(restore_services),
        "save_services": save_services,
        "restore_services": restore_services,
        "service_descriptions": KNOWN_SERVICES,
    })

    return context
```

### 7. Service Validation

Add validation function in `generate_entity.py`:

```python
def validate_services(services: List[str]) -> bool:
    """Validate that all services are known.

    Args:
        services: List of service names to validate

    Returns:
        True if all services are known, False otherwise
    """
    unknown = set(services) - set(KNOWN_SERVICES.keys())
    if unknown:
        print(f"Error: Unknown services: {', '.join(unknown)}")
        print(f"Known services: {', '.join(KNOWN_SERVICES.keys())}")
        return False
    return True
```

Call during input gathering:
- After getting save_services from CLI or prompt
- After getting restore_services from CLI or prompt
- Exit with error if validation fails

### 8. Input Gathering Flow

Add new functions following existing pattern:

```python
def get_save_services(args: argparse.Namespace) -> List[str]:
    """Get save services from args or prompt."""
    if args.save_services is not None:
        if not args.save_services:
            return []
        services = [s.strip() for s in args.save_services.split(",")]
        services = [s for s in services if s]
        if not validate_services(services):
            sys.exit(1)
        return services

    # Show available services
    print("\nAvailable services:")
    for name, desc in KNOWN_SERVICES.items():
        print(f"  - {name}: {desc}")

    services_input = prompt_for_value(
        "\nServices required for save (comma-separated, or empty)",
        default=""
    )

    if not services_input:
        return []

    services = [s.strip() for s in services_input.split(",")]
    services = [s for s in services if s]

    if not validate_services(services):
        sys.exit(1)

    return services

def get_restore_services(args: argparse.Namespace) -> List[str]:
    # Similar implementation for restore services
    ...
```

## Implementation Steps

1. Update `generate_entity.py`:
   - Add `KNOWN_SERVICES` constant
   - Add `--save-services` and `--restore-services` CLI arguments
   - Add `validate_services()` function
   - Add `get_save_services()` and `get_restore_services()` functions
   - Update `prepare_template_context()` to include service info
   - Update `main()` to gather services and pass to generation

2. Update `entity_config_template.py.j2`:
   - Add TYPE_CHECKING imports
   - Add StrategyContext import
   - Add required_services_save and required_services_restore attributes
   - Update factory method signatures to use StrategyContext
   - Add conditional service extraction code
   - Update return type hints

3. Update `save_strategy_template.py.j2`:
   - Add conditional __init__ parameters for services
   - Add service storage in __init__
   - Update imports for service types

4. Update `restore_strategy_template.py.j2`:
   - Same updates as save_strategy_template.py.j2

5. Test with multiple scenarios:
   - No services required (like labels save)
   - Single service (github_service)
   - Multiple services (github_service + conflict_strategy)
   - Invalid service name (should fail validation)

## Benefits

- **Type Safety:** Factory methods use typed StrategyContext parameter
- **Explicit Requirements:** Service dependencies declared at class level
- **Validation:** StrategyFactory can validate requirements before creation
- **Developer Experience:** Clear prompts and CLI options for service selection
- **Code Generation:** Correct service extraction code generated automatically
- **Maintainability:** Adding new services to KNOWN_SERVICES enables their use

## Example Usage

### CLI Mode

```bash
python -m src.tools.generate_entity \
    --name code_scanning \
    --type bool \
    --default true \
    --save-services github_service \
    --restore-services github_service \
    --description "Save and restore code scanning alerts"
```

### Interactive Mode

```
$ python -m src.tools.generate_entity

Entity name (snake_case): code_scanning
Value type (bool/set) [bool]:
Default value (true/false) [true]:
Dependencies (comma-separated, or empty):

Available services:
  - github_service: GitHub API service for issues, PRs, labels, etc.
  - git_service: Git repository service for cloning/restoring repositories
  - conflict_strategy: Conflict resolution strategy for restoration

Services required for save (comma-separated, or empty): github_service
Services required for restore (comma-separated, or empty): github_service

Description [Entity description]: Save and restore code scanning alerts

✓ Generating entity: code_scanning
```

## References

- Architecture: `docs/architecture/strategy-context.md`
- Implementation: `src/entities/strategy_context.py`
- Existing pattern: `src/entities/labels/entity_config.py`

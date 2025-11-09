# Adding a New Entity

This guide shows how to add a new entity to the GitHub Data system using the declarative operation registry.

## Overview

Entities are self-contained packages that define:
- Data models
- Save/restore strategies
- GitHub API operations (declarative)
- Converters (entity-specific converter modules)

The operation registry auto-generates service methods from entity config declarations, eliminating manual modifications to shared service layer files.

## Step-by-Step Process

### 1. Create Entity Package Structure

```bash
github_data/entities/your_entity/
├── __init__.py
├── entity_config.py      # Configuration and API declarations
├── models.py             # Domain models
├── converters.py         # Data conversion functions
├── save_strategy.py      # Save logic
└── restore_strategy.py   # Restore logic
```

### 2. Define Entity Configuration

```python
# github_data/entities/your_entity/entity_config.py

class YourEntityConfig:
    name = "your_entity"
    env_var = "INCLUDE_YOUR_ENTITY"
    default_value = True
    value_type = bool
    dependencies = []  # List entity names this depends on
    description = "Your entity description"

    # Service requirements
    required_services_save = []
    required_services_restore = ["github_service"]

    # Converter declarations
    converters = {
        'convert_to_your_entity': {
            'module': 'github_data.entities.your_entity.converters',
            'function': 'convert_to_your_entity',
            'target_model': 'YourEntity',
        },
    }

    # Declare GitHub API operations
    github_api_operations = {
        'get_repository_your_entity': {
            'boundary_method': 'get_repository_your_entity',
            'converter': 'convert_to_your_entity',
        },
        'create_your_entity': {
            'boundary_method': 'create_your_entity',
            'converter': 'convert_to_your_entity',
        }
    }

    @staticmethod
    def create_save_strategy(context):
        from .save_strategy import YourEntitySaveStrategy
        return YourEntitySaveStrategy()

    @staticmethod
    def create_restore_strategy(context):
        from .restore_strategy import YourEntityRestoreStrategy
        return YourEntityRestoreStrategy()
```

### 3. Add Boundary Methods (If Needed)

Most entities use existing GraphQL/REST patterns. Only add custom boundary methods if needed:

```python
# github_data/github/boundary.py (only for custom API patterns)

def get_repository_your_entity(self, repo_name: str) -> List[Dict[str, Any]]:
    """Get your entity data from repository."""
    return self._rest_client.get_your_entity(repo_name)
```

### 4. Implement Converters

Create `entities/{entity_name}/converters.py` to convert raw GitHub API data to your domain models.

**File**: `github_data/entities/{entity_name}/converters.py`

```python
"""Converters for {entity_name} entity."""

from typing import Dict, Any
from .models import YourEntity
from github_data.github.converter_registry import get_converter


def convert_to_your_entity(raw_data: Dict[str, Any]) -> YourEntity:
    """
    Convert raw GitHub API data to YourEntity.

    Args:
        raw_data: Raw data from GitHub API

    Returns:
        YourEntity domain model
    """
    # Use get_converter() for nested conversions
    user = get_converter('convert_to_user')(raw_data['user'])
    labels = [get_converter('convert_to_label')(l) for l in raw_data.get('labels', [])]

    return YourEntity(
        id=raw_data["id"],
        name=raw_data["name"],
        user=user,
        labels=labels,
        # ... other fields
    )
```

**Important**:
- Always use `get_converter()` for nested conversions (labels, users, milestones, etc.)
- Never import converters directly from other entity packages
- This prevents circular import issues and maintains loose coupling

### Declare Converters in Entity Config

Update your entity config to declare the converters:

**File**: `github_data/entities/{entity_name}/entity_config.py`

```python
class YourEntityConfig:
    name = "yourentity"
    env_var = "INCLUDE_YOURENTITY"
    # ... other config ...

    # Declare all converters this entity provides
    converters = {
        'convert_to_your_entity': {
            'module': 'github_data.entities.yourentity.converters',
            'function': 'convert_to_your_entity',
            'target_model': 'YourEntity',
        },
    }

    # Reference converters in operations
    github_api_operations = {
        "get_repository_entities": {
            "boundary_method": "get_repository_entities",
            "converter": "convert_to_your_entity",  # Must match declared converter
        },
    }
```

The registry will:
- Discover your converters at startup
- Validate they exist and are callable
- Ensure operations reference valid converters
- Fail fast if configuration is incorrect

### 5. No Service Layer Changes Needed!

The service layer automatically discovers and generates methods from your `github_api_operations` declaration. No manual modifications to `service.py` or `protocols.py` needed!

## Field Reference: github_api_operations

### Required Fields
- **`boundary_method`**: Name of method on GitHubApiBoundary to call

### Optional Fields
- **`converter`**: Converter function name (default: no conversion)
- **`cache_key_template`**: Override auto-generated cache key (default: `{method_name}:{params}`)
- **`requires_retry`**: Force retry behavior (default: auto-detect from method name)

### Examples

**Simple read operation:**
```python
'get_repository_milestones': {
    'boundary_method': 'get_repository_milestones',
    'converter': 'convert_to_milestone',
}
```

**Write operation (no caching):**
```python
'create_milestone': {
    'boundary_method': 'create_milestone',
    'converter': 'convert_to_milestone',
}
```

**Custom cache key:**
```python
'get_all_comments': {
    'boundary_method': 'get_all_issue_comments',
    'converter': 'convert_to_comment',
    'cache_key_template': 'comments_all:{repo_name}',
}
```

## Escape Hatch: Complex Operations

If an operation doesn't fit the registry pattern, add it explicitly to GitHubService:

```python
# github_data/github/service.py

def complex_custom_operation(self, repo_name: str) -> ComplexResult:
    """Custom operation with complex multi-step logic."""
    # Custom implementation here
    # Explicit methods automatically override registry
```

## Testing Your Entity

```bash
# Test your entity
pytest tests/unit/entities/your_entity/ -v

# Test integration
pytest tests/integration/test_your_entity_save_restore_integration.py -v

# Validate registry registration
pytest tests/unit/github/test_operation_registry.py -v
```

## What Changed From Before?

**OLD Process (Before Registry & Distributed Converters):**
- Modify 4 shared files: `boundary.py`, `protocols.py`, `service.py`, `converters.py`
- 200+ lines of boilerplate per entity
- Manually wrap each method with caching/rate limiting
- All converters in monolithic converters.py file

**NEW Process (With Registry & Distributed Converters):**
- Create entity package with converters.py module
- Declare converters and operations in entity config (10-15 lines)
- Add boundary method only if custom API pattern needed
- Done! Service methods and converter loading auto-generated
- Converters colocated with entity models and strategies

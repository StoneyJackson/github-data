# Adding a New Entity

This guide shows how to add a new entity to the GitHub Data system using the declarative operation registry.

## Overview

Entities are self-contained packages that define:
- Data models
- Save/restore strategies
- GitHub API operations (declarative)
- Converters (if needed)

The operation registry auto-generates service methods from entity config declarations, eliminating manual modifications to shared service layer files.

## Step-by-Step Process

### 1. Create Entity Package Structure

```bash
github_data/entities/your_entity/
├── __init__.py
├── entity_config.py      # Configuration and API declarations
├── models.py             # Domain models
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

    # Declare GitHub API operations (NEW!)
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

### 4. Add Converter Functions

```python
# github_data/github/converters.py

def convert_to_your_entity(raw_data: Dict[str, Any]) -> YourEntity:
    """Convert raw GitHub API data to YourEntity model."""
    return YourEntity(
        id=raw_data['id'],
        name=raw_data['name'],
        # ... map fields ...
    )
```

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

**OLD Process (Before Registry):**
- Modify 4 shared files: `boundary.py`, `protocols.py`, `service.py`, `converters.py`
- 200+ lines of boilerplate per entity
- Manually wrap each method with caching/rate limiting

**NEW Process (With Registry):**
- Declare operations in entity config (5-10 lines)
- Add boundary method only if custom API pattern needed
- Add converter function
- Done! Service methods auto-generated

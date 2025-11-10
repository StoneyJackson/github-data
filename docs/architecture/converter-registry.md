# Converter Registry Architecture

## Overview

The Converter Registry is a centralized system for discovering, loading, and validating
converters that transform raw GitHub API responses into domain models.

## Design Principles

1. **Explicit over implicit**: Each entity explicitly declares its converters
2. **Fail-fast validation**: All converters loaded and validated at startup
3. **Colocation**: Converter implementations live with entity code
4. **No shared file modifications**: Adding entities requires zero changes to shared files

## How It Works

### Startup Sequence

1. `ConverterRegistry` instantiates
2. Loads common converters from `CommonConvertersConfig`
3. Scans all entity configs for converter declarations
4. Eagerly imports all converter modules
5. Validates all functions exist and are callable
6. Cross-validates operations reference valid converters
7. Application ready - any configuration errors caught at startup

### Declaring Converters

In your entity config:

```python
class MyEntityConfig:
    converters = {
        'convert_to_myentity': {
            'module': 'github_data.entities.myentity.converters',
            'function': 'convert_to_myentity',
            'target_model': 'MyEntity',
        },
    }
```

### Implementing Converters

In `entities/{entity}/converters.py`:

```python
from github_data.github.converter_registry import get_converter

def convert_to_myentity(raw_data):
    # Use registry for nested conversions
    user = get_converter('convert_to_user')(raw_data['user'])
    return MyEntity(user=user, ...)
```

### Common Converters

Shared converters like `convert_to_user` are declared in `CommonConvertersConfig`
and live in `github_data/github/converters.py`.

## Benefits

- **Zero coupling**: Entities don't import from each other
- **Fail-fast**: Configuration errors caught at startup
- **Self-documenting**: Entity configs show all capabilities
- **Scalable**: Adding entities doesn't modify shared files
- **Consistent**: Follows same pattern as operation registry

## See Also

- [Adding Entities Guide](../development/adding-entities.md)
- [Operation Registry](../../github_data/github/operation_registry.py)

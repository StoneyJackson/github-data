# Converter Registry Architecture

## Overview

The Converter Registry provides centralized discovery, loading, and validation of converter functions that transform raw GitHub API data into domain models.

## Design Principles

1. **Explicit Declaration**: Entity configs explicitly declare their converters
2. **Fail-Fast Validation**: All converters validated at startup before any operations
3. **Colocation**: Converters live in entity packages with their models
4. **Loose Coupling**: Converters use registry for nested conversions, not direct imports

## Component Architecture

### ConverterRegistry Class

**Location**: `github_data/github/converter_registry.py`

**Responsibilities**:
- Discover converters from entity configs at startup
- Eagerly import and validate all converter modules
- Provide converter lookup by name
- Cross-validate that operations reference valid converters

**Key Methods**:
- `get(name: str) -> Callable`: Retrieve converter by name
- `list_converters() -> list[str]`: List all registered converters
- `_load_all_converters()`: Discovery and loading at initialization
- `_validate_all()`: Comprehensive startup validation

### Entity Converter Modules

**Pattern**: Each entity package contains a `converters.py` module with entity-specific conversion functions.

**Location**: `github_data/entities/{entity}/converters.py`

**Example**:
```python
from typing import Dict, Any
from .models import Release
from github_data.github.converter_registry import get_converter


def convert_to_release(raw_data: Dict[str, Any]) -> Release:
    """Convert raw GitHub API release data to Release model."""
    # Use registry for nested conversions
    author = get_converter('convert_to_user')(raw_data['author'])

    return Release(
        id=raw_data["id"],
        author=author,
        # ...
    )
```

### Common Converters

**Location**: `github_data/github/converters.py`

Shared converters used across multiple entities:
- `convert_to_user()`: User conversion used by many entities
- `_parse_datetime()`: Common datetime parsing utility
- `_extract_pr_number_from_url()`: PR URL parsing utility

These are registered via `CommonConvertersConfig`.

## Startup Sequence

```
1. Application starts
2. ConverterRegistry.__init__() called
3. _load_all_converters():
   a. Load common converters from CommonConvertersConfig
   b. Scan all entity configs via EntityRegistry
   c. For each entity with 'converters' dict:
      - Import converter module
      - Import converter function
      - Register with metadata
   d. Check for naming collisions
4. _validate_all():
   a. Verify all converters are callable
   b. Cross-validate with GitHubOperationRegistry
   c. Ensure operations reference valid converters
5. If any validation fails → exception, app won't start
6. Success → services ready to use
```

## Runtime Usage

### Getting a Converter

```python
from github_data.github.converter_registry import get_converter

# Get converter function
converter = get_converter('convert_to_release')

# Use it
release = converter(raw_api_data)
```

### Within Converter Implementations

```python
def convert_to_issue(raw_data: Dict[str, Any]) -> Issue:
    """Convert issue with nested entities."""
    # Use get_converter() for all nested conversions
    return Issue(
        labels=[get_converter('convert_to_label')(l) for l in raw_data['labels']],
        milestone=get_converter('convert_to_milestone')(raw_data['milestone']),
        user=get_converter('convert_to_user')(raw_data['user']),
    )
```

## Error Handling

### Converter Not Found

```python
try:
    converter = get_converter('convert_to_lable')  # Typo
except ConverterNotFoundError as e:
    # Error includes suggestions: "Did you mean: convert_to_label?"
    print(e)
```

### Configuration Errors

All caught at startup:
- Missing converter module
- Function doesn't exist in module
- Function not callable
- Naming collisions
- Operations referencing non-existent converters

## Benefits

1. **Zero Shared File Modifications**: Adding entity doesn't require touching converters.py
2. **Clear Ownership**: Each entity explicitly declares its converters
3. **Better Organization**: Converters colocated with models they convert to
4. **No Circular Imports**: Registry-based lookup eliminates import coupling
5. **Fail-Fast**: Configuration errors caught at startup, not runtime
6. **Self-Documenting**: Entity configs show capabilities in one place

## Testing

Converters can be tested in isolation:

```python
def test_convert_to_release():
    """Test release converter."""
    raw_data = load_fixture('github_release_response.json')

    release = convert_to_release(raw_data)

    assert isinstance(release, Release)
    assert release.tag_name == raw_data['tag_name']
```

Registry validation is tested at unit level:

```python
def test_registry_validates_at_startup():
    """Registry fails fast on bad config."""
    with patch_bad_converter_config():
        with pytest.raises(ValidationError):
            ConverterRegistry()
```

## Adding New Converters

See [Adding Entities Guide](../development/adding-entities.md) for complete instructions.

**Quick Reference**:
1. Create `entities/{entity}/converters.py`
2. Implement converter functions
3. Declare in entity config's `converters` dict
4. Reference in operations via `converter` key
5. Registry auto-discovers at next startup

## Common Converter Config

**Location**: `github_data/github/common_converters_config.py`

Common converters are explicitly declared and loaded before entity converters:

```python
class CommonConvertersConfig:
    """Configuration for common converters used across entities."""

    name = "common"

    converters = {
        'convert_to_user': {
            'module': 'github_data.github.converters',
            'function': 'convert_to_user',
            'target_model': 'GitHubUser',
        },
        '_parse_datetime': {
            'module': 'github_data.github.converters',
            'function': '_parse_datetime',
            'target_model': None,  # Utility function
        },
        '_extract_pr_number_from_url': {
            'module': 'github_data.github.converters',
            'function': '_extract_pr_number_from_url',
            'target_model': None,  # Utility function
        },
    }
```

## Metadata Structure

Each registered converter has metadata:

```python
{
    'entity': 'releases',  # or 'common' for shared converters
    'module': 'github_data.entities.releases.converters',
    'target_model': 'Release',  # or None for utility functions
}
```

This metadata is used for:
- Debugging converter sources
- Validation error messages
- Auditing converter distribution

## Migration History

**Phase 1**: Created registry framework with backward compatibility
**Phase 2**: Migrated all 11 entities to distributed converter pattern
**Phase 3**: Removed legacy loading, created common converter config, reduced monolithic file to utilities only

The distributed converter registry migration is now complete.

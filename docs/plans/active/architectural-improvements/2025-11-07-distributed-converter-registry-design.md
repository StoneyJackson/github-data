# Distributed Converter Registry Design

**Date**: 2025-11-07
**Status**: Approved
**Related**: [Architectural Improvements Analysis](active/architectural-improvements/2025-11-03-architectural-improvements.md)

## Executive Summary

This design implements a Distributed Converter Registry that moves converter functions from the monolithic `converters.py` into individual entity packages. Entity configs will explicitly declare their converters, and a central `ConverterRegistry` class will discover and validate them at startup using eager loading and fail-fast validation.

This design follows the same pattern as the existing `GitHubOperationRegistry`, creating architectural consistency and eliminating the need to modify shared converter files when adding new entities.

## Problem Statement

### Current State

The current codebase has a monolithic `github_data/github/converters.py` file (225+ lines) containing all converter functions for transforming raw GitHub API responses into domain models:

- `convert_to_label()`
- `convert_to_issue()`
- `convert_to_release()`
- `convert_to_milestone()`
- etc.

### Issues

1. **Shared file modifications**: Every new entity requires modifying the central `converters.py`
2. **Poor organization**: Converters separated from the models they convert to
3. **Circular import risks**: Requires TYPE_CHECKING imports to avoid dependency cycles
4. **Unclear ownership**: Not obvious which entity owns which converter
5. **Scaling problems**: File grows with each entity addition

### Success Criteria

After implementation:
- Adding a new entity requires zero modifications to shared converter files
- Converters are colocated with their entity's models
- No TYPE_CHECKING import workarounds needed
- Clear ownership: each entity declares its converters
- Fail-fast validation catches configuration errors at startup

## Architecture Overview

### Design Principles

1. **Explicit over implicit**: Entity configs declare converters in a `converters` dict
2. **Fail-fast validation**: All converters loaded and validated at startup before any operations run
3. **Colocation**: Converter implementations live in entity packages alongside models
4. **Staged migration**: Backward compatibility layer allows incremental migration
5. **Consistency**: Follows the same pattern as existing `GitHubOperationRegistry`

### Core Components

#### 1. Entity Config Declaration

Each entity config adds a `converters` dict declaring all converter functions it provides:

```python
# github_data/entities/releases/entity_config.py
class ReleasesEntityConfig:
    name = "releases"
    env_var = "INCLUDE_RELEASES"
    # ... other existing fields ...

    # NEW: Explicit converter declarations
    converters = {
        'convert_to_release': {
            'module': 'github_data.entities.releases.converters',
            'function': 'convert_to_release',
            'target_model': 'Release',  # Optional, for documentation
        },
        'convert_to_release_asset': {
            'module': 'github_data.entities.releases.converters',
            'function': 'convert_to_release_asset',
            'target_model': 'ReleaseAsset',
        },
    }

    github_api_operations = {
        "get_repository_releases": {
            "boundary_method": "get_repository_releases",
            "converter": "convert_to_release",  # References declared converter
        },
    }
```

**Rationale**: Explicit declarations make entity capabilities self-documenting and enable validation that operations reference valid converters.

#### 2. ConverterRegistry Class

```python
# github_data/github/converter_registry.py
import logging
import importlib
from typing import Dict, Callable, Any

logger = logging.getLogger(__name__)


class ConverterNotFoundError(Exception):
    """Raised when a converter is not found in the registry."""
    pass


class ValidationError(Exception):
    """Raised when converter configuration is invalid."""
    pass


class ConverterRegistry:
    """
    Registry for entity data converters with eager loading.

    Scans all entity configs at initialization, imports converter modules,
    and validates all declarations. Provides fail-fast startup validation
    to catch configuration errors before any operations run.
    """

    def __init__(self):
        """Initialize registry with eager loading and validation."""
        self._converters: Dict[str, Callable] = {}
        self._converter_metadata: Dict[str, Dict[str, Any]] = {}
        self._load_all_converters()  # Eager loading
        self._validate_all()          # Fail-fast validation

        logger.info(
            f"ConverterRegistry initialized with {len(self._converters)} converters"
        )

    def get(self, name: str) -> Callable:
        """
        Get converter by name.

        Args:
            name: Converter function name (e.g., 'convert_to_release')

        Returns:
            Converter function

        Raises:
            ConverterNotFoundError: If converter not registered
        """
        if name not in self._converters:
            # Provide helpful error with suggestions for typos
            import difflib
            similar = difflib.get_close_matches(name, self._converters.keys())
            msg = f"Converter '{name}' not found"
            if similar:
                msg += f". Did you mean: {', '.join(similar)}?"
            raise ConverterNotFoundError(msg)

        return self._converters[name]

    def list_converters(self) -> list[str]:
        """List all registered converter names."""
        return list(self._converters.keys())

    def _load_all_converters(self):
        """Scan EntityRegistry and eagerly import all declared converters."""
        from github_data.entities.registry import EntityRegistry

        entity_registry = EntityRegistry()

        for entity_name, entity in entity_registry._entities.items():
            config = entity.config

            # Skip entities without converter declarations
            if not hasattr(config, "converters"):
                continue

            # Import and register each converter
            for converter_name, spec in config.converters.items():
                self._load_converter(converter_name, spec, entity_name)

        # Load legacy converters from monolithic file (backward compatibility)
        self._load_legacy_converters()

    def _load_converter(self, name: str, spec: Dict[str, Any], entity_name: str):
        """Load a single converter from spec."""
        module_path = spec['module']
        function_name = spec['function']

        try:
            # Eagerly import the module
            module = importlib.import_module(module_path)
            converter_func = getattr(module, function_name)

            # Check for naming collisions
            if name in self._converters:
                existing_meta = self._converter_metadata[name]
                raise ValidationError(
                    f"Converter naming collision: '{name}' declared by both "
                    f"'{existing_meta['entity']}' and '{entity_name}'"
                )

            # Register converter
            self._converters[name] = converter_func
            self._converter_metadata[name] = {
                'entity': entity_name,
                'module': module_path,
                'target_model': spec.get('target_model'),
            }

            logger.debug(f"Loaded converter '{name}' from {entity_name}")

        except (ImportError, AttributeError) as e:
            raise ValidationError(
                f"Failed to load converter '{name}' from entity '{entity_name}': {e}"
            ) from e

    def _load_legacy_converters(self):
        """
        Load converters from monolithic converters.py for backward compatibility.

        During migration, this provides fallback for converters not yet moved
        to entity packages. Distributed converters take precedence.
        """
        try:
            from github_data.github import converters as legacy_module

            # Find all convert_to_* functions
            for name in dir(legacy_module):
                if name.startswith('convert_to_') and callable(getattr(legacy_module, name)):
                    # Only register if not already loaded from entity package
                    if name not in self._converters:
                        self._converters[name] = getattr(legacy_module, name)
                        self._converter_metadata[name] = {
                            'entity': 'legacy',
                            'module': 'github_data.github.converters',
                            'target_model': None,
                        }
                        logger.debug(f"Loaded legacy converter '{name}'")
        except ImportError:
            # converters.py may not exist after complete migration
            pass

    def _validate_all(self):
        """Comprehensive validation at startup (fail-fast)."""
        # 1. Validate all converters are callable
        for name, func in self._converters.items():
            if not callable(func):
                meta = self._converter_metadata[name]
                raise ValidationError(
                    f"Converter '{name}' from entity '{meta['entity']}' is not callable"
                )

        # 2. Cross-validate: operations reference valid converters
        from github_data.github.operation_registry import GitHubOperationRegistry

        operation_registry = GitHubOperationRegistry()
        for op_name in operation_registry.list_operations():
            operation = operation_registry.get_operation(op_name)
            if operation.converter_name:
                if operation.converter_name not in self._converters:
                    raise ValidationError(
                        f"Operation '{op_name}' from entity '{operation.entity_name}' "
                        f"references unknown converter '{operation.converter_name}'"
                    )


# Module-level singleton instance
_registry_instance = None


def get_converter(name: str) -> Callable:
    """
    Get converter by name from the global registry.

    This is a convenience function for use within converter implementations
    that need to call other converters.

    Args:
        name: Converter function name

    Returns:
        Converter function
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ConverterRegistry()
    return _registry_instance.get(name)
```

**Key features**:
- **Eager loading**: All converters imported at startup
- **Fail-fast validation**: Configuration errors caught immediately
- **Helpful errors**: Suggestions for typos in converter names
- **Backward compatibility**: Falls back to monolithic file during migration
- **Singleton pattern**: Global instance for easy access

#### 3. Entity Converter Modules

```python
# github_data/entities/releases/converters.py (NEW file)
"""Converters for releases entity."""

from typing import Dict, Any
from .models import Release, ReleaseAsset
from github_data.github.converter_registry import get_converter


def convert_to_release(raw_data: Dict[str, Any]) -> Release:
    """
    Convert raw GitHub API release data to Release model.

    Args:
        raw_data: Raw release data from GitHub API

    Returns:
        Release domain model
    """
    # Use registry for nested conversions
    assets = [
        get_converter('convert_to_release_asset')(asset)
        for asset in raw_data.get("assets", [])
    ]

    author = get_converter('convert_to_user')(raw_data["author"])

    return Release(
        id=raw_data["id"],
        tag_name=raw_data["tag_name"],
        name=raw_data.get("name"),
        body=raw_data.get("body"),
        draft=raw_data["draft"],
        prerelease=raw_data["prerelease"],
        created_at=raw_data["created_at"],
        published_at=raw_data.get("published_at"),
        author=author,
        assets=assets,
        html_url=raw_data["html_url"],
        tarball_url=raw_data.get("tarball_url"),
        zipball_url=raw_data.get("zipball_url"),
    )


def convert_to_release_asset(raw_data: Dict[str, Any]) -> ReleaseAsset:
    """
    Convert raw GitHub API release asset data to ReleaseAsset model.

    Args:
        raw_data: Raw asset data from GitHub API

    Returns:
        ReleaseAsset domain model
    """
    uploader = get_converter('convert_to_user')(raw_data["uploader"])

    return ReleaseAsset(
        id=raw_data["id"],
        name=raw_data["name"],
        content_type=raw_data["content_type"],
        size=raw_data["size"],
        download_count=raw_data["download_count"],
        browser_download_url=raw_data["browser_download_url"],
        created_at=raw_data["created_at"],
        updated_at=raw_data["updated_at"],
        uploader=uploader,
        local_path=raw_data.get("local_path"),
    )
```

**Pattern**: Converters use `get_converter()` to access other converters via the registry, eliminating import coupling.

### Component Interactions

#### Startup Sequence (Fail-Fast)

```
1. Application starts
2. EntityRegistry loads all entity configs
3. ConverterRegistry instantiates:
   a. Reads 'converters' dict from each entity config
   b. Eagerly imports each converter module
   c. Validates each function exists and is callable
   d. Loads legacy converters from converters.py (backward compatibility)
   e. Cross-validates: operations reference valid converters
4. GitHubOperationRegistry instantiates:
   a. Validates operations reference converters in registry
5. If any validation fails → immediate exception, app won't start
6. All validations pass → services ready to use
```

**Critical**: All validation happens before any GitHub API operations can run. Configuration errors are impossible to miss.

#### Runtime Converter Access

```python
# Inside a converter needing another converter
from github_data.github.converter_registry import get_converter

def convert_to_issue(raw_data: Dict[str, Any]) -> Issue:
    """Convert issue with nested entities."""
    return Issue(
        # Use registry for all nested conversions
        labels=[get_converter('convert_to_label')(l) for l in raw_data['labels']],
        milestone=get_converter('convert_to_milestone')(raw_data['milestone']),
        user=get_converter('convert_to_user')(raw_data['user']),
        assignees=[get_converter('convert_to_user')(u) for u in raw_data['assignees']],
        # ...
    )
```

The `get_converter()` convenience function delegates to the singleton registry instance.

#### Complete Data Flow Example

Trace of fetching and converting releases:

```
1. User calls: GitHubService.get_repository_releases("owner/repo")

2. Service delegates to operation registry:
   - Registry finds 'get_repository_releases' operation
   - Operation specifies converter: 'convert_to_release'

3. Boundary layer fetches raw JSON from GitHub API

4. Service applies converter:
   - Calls: get_converter('convert_to_release')
   - Registry returns function from entities/releases/converters.py
   - Function executes, calling nested converters via registry:
     * convert_to_release_asset (from releases package)
     * convert_to_user (from common converters)

5. Returns typed Release objects to caller
```

The registry acts as the central lookup table, enabling loose coupling between converters.

## Handling Shared/Common Converters

Some converters are used across many entities (e.g., `convert_to_user`, `_parse_datetime`). Three options were considered:

**Option A: Keep in monolithic converters.py** ✅ **SELECTED**
- Common converters stay in `github_data/github/converters.py`
- Entity-specific converters move to entity packages
- Registry loads from both locations

**Option B: Create github/converters/ package**
- `github/converters/common.py` for shared converters
- Declared in a special "common" pseudo-entity config

**Option C: First entity "owns" shared converters**
- `entities/users/converters.py` owns `convert_to_user`
- Other entities reference it via registry

**Decision**: Option A provides the most pragmatic migration path. Common converters remain in their current location, reducing migration scope. We can refactor later if needed.

## Migration Strategy

### Phase 1: Framework (No Breaking Changes)

**Objective**: Build and validate the infrastructure without disrupting existing functionality.

**Tasks**:
1. Create `github_data/github/converter_registry.py` with `ConverterRegistry` class
2. Implement backward compatibility (falls back to monolithic `converters.py`)
3. Add `get_converter()` module-level function
4. Create unit tests for registry behavior
5. Integrate into startup sequence (validate registry initializes correctly)

**Validation**: All existing tests pass without modifications.

### Phase 2: Incremental Migration

**Objective**: Migrate entities one at a time to validate the pattern.

**Tasks per entity**:
1. Create `{entity}/converters.py` module
2. Move converter functions from monolithic file to entity module
3. Add `converters` dict to entity config
4. Run tests to verify converter loading works
5. Validate integration tests pass

**Order**: Start with simple entities (labels, milestones) before complex ones (issues, pull requests).

**Validation**: After each entity migration, full test suite passes.

### Phase 3: Cleanup

**Objective**: Remove legacy code after complete migration.

**Tasks**:
1. Verify all entities have migrated
2. Remove `_load_legacy_converters()` backward compatibility code
3. Reduce `converters.py` to only common converters
4. Update documentation
5. Final test run

**Validation**: No references to legacy converter loading remain.

## Testing Strategy

### Unit Tests for ConverterRegistry

```python
# tests/unit/github/test_converter_registry.py

class TestConverterRegistry:
    """Test converter registry discovery and validation."""

    def test_registry_loads_all_declared_converters(self):
        """Registry discovers and loads all entity converters."""
        registry = ConverterRegistry()

        # Should have at least the converters we know exist
        assert 'convert_to_label' in registry.list_converters()
        assert 'convert_to_release' in registry.list_converters()

    def test_registry_validates_at_startup(self):
        """Registry fails fast if converter declaration is invalid."""
        # Mock an entity config with invalid converter
        with patch_entity_config_with_bad_converter():
            with pytest.raises(ValidationError, match="not callable"):
                ConverterRegistry()

    def test_get_converter_returns_callable(self):
        """Get returns actual converter function."""
        registry = ConverterRegistry()
        converter = registry.get('convert_to_label')

        assert callable(converter)

        # Test it actually converts
        result = converter(mock_label_data())
        assert isinstance(result, Label)

    def test_get_unknown_converter_raises_helpful_error(self):
        """Get provides helpful error with suggestions for typos."""
        registry = ConverterRegistry()

        with pytest.raises(ConverterNotFoundError) as exc_info:
            # Typo: "lable" instead of "label"
            registry.get('convert_to_lable')

        # Should suggest similar names
        assert "Did you mean: convert_to_label" in str(exc_info.value)

    def test_converter_naming_collision_fails_fast(self):
        """Registry detects when two entities declare same converter name."""
        # Mock two entities declaring 'convert_to_duplicate'
        with patch_entity_configs_with_collision():
            with pytest.raises(ValidationError, match="naming collision"):
                ConverterRegistry()

    def test_operation_references_invalid_converter_fails_fast(self):
        """Registry validates operations reference valid converters."""
        # Mock operation referencing non-existent converter
        with patch_operation_with_invalid_converter():
            with pytest.raises(ValidationError, match="references unknown converter"):
                ConverterRegistry()
```

### Integration Tests for Entity Converters

```python
# tests/integration/github/test_distributed_converters.py

class TestDistributedConverters:
    """Test entity converters work correctly end-to-end."""

    def test_releases_converters_work_end_to_end(self):
        """Releases converters loaded from entity package work correctly."""
        registry = ConverterRegistry()

        # Get distributed converter
        convert_to_release = registry.get('convert_to_release')

        # Use with real GitHub API response structure
        raw_release = load_fixture('github_release_response.json')
        release = convert_to_release(raw_release)

        assert isinstance(release, Release)
        assert release.tag_name == raw_release['tag_name']
        assert len(release.assets) == len(raw_release['assets'])

    def test_cross_references_between_converters(self):
        """Entity converters can reference other converters via registry."""
        registry = ConverterRegistry()

        # Issue converter should successfully use label converter
        convert_to_issue = registry.get('convert_to_issue')
        raw_issue = load_fixture('github_issue_with_labels.json')

        issue = convert_to_issue(raw_issue)
        assert all(isinstance(label, Label) for label in issue.labels)

    def test_all_operations_have_valid_converters(self):
        """All declared operations reference converters that exist."""
        converter_registry = ConverterRegistry()
        operation_registry = GitHubOperationRegistry()

        for op_name in operation_registry.list_operations():
            operation = operation_registry.get_operation(op_name)
            if operation.converter_name:
                # Should not raise
                converter_registry.get(operation.converter_name)
```

### Migration Tests

```python
# tests/unit/github/test_converter_migration.py

class TestConverterMigration:
    """Test backward compatibility during migration."""

    def test_backward_compatibility_during_migration(self):
        """Registry falls back to monolithic converters.py during migration."""
        registry = ConverterRegistry()

        # Should work whether converter is migrated or not
        converter = registry.get('convert_to_milestone')
        assert callable(converter)

    def test_distributed_overrides_legacy(self):
        """Distributed converter takes precedence over legacy."""
        registry = ConverterRegistry()

        # If releases has been migrated, should use distributed version
        converter = registry.get('convert_to_release')
        metadata = registry._converter_metadata['convert_to_release']

        # Should be from entity package, not legacy
        assert metadata['entity'] == 'releases'
        assert 'entities.releases' in metadata['module']
```

## File Structure After Migration

```
github_data/
├── github/
│   ├── converter_registry.py       # NEW - Registry class with discovery
│   ├── converters.py                # MODIFIED - Common converters only
│   ├── operation_registry.py        # EXISTS - Parallel pattern
│   ├── service.py                   # EXISTS - Uses converter registry
│   ├── boundary.py
│   └── protocols.py
│
├── entities/
│   ├── releases/
│   │   ├── converters.py            # NEW - Entity-specific converters
│   │   ├── entity_config.py         # MODIFIED - Declares converters
│   │   ├── models.py
│   │   ├── save_strategy.py
│   │   └── restore_strategy.py
│   │
│   ├── labels/
│   │   ├── converters.py            # NEW - Entity-specific converters
│   │   ├── entity_config.py         # MODIFIED - Declares converters
│   │   ├── models.py
│   │   └── ...
│   │
│   ├── issues/
│   │   ├── converters.py            # NEW - Entity-specific converters
│   │   ├── entity_config.py         # MODIFIED - Declares converters
│   │   └── ...
│   │
│   └── [all other entities follow same pattern]
│
tests/
├── unit/
│   ├── github/
│   │   ├── test_converter_registry.py  # NEW - Registry tests
│   │   └── test_converter_migration.py # NEW - Migration tests
│   └── entities/
│       └── releases/
│           └── test_converters.py      # NEW - Entity converter tests
│
└── integration/
    └── github/
        └── test_distributed_converters.py  # NEW - End-to-end tests
```

## Documentation Updates

### 1. Entity Addition Guide

Update `docs/development/adding-entities.md`:

```markdown
## Step 3: Configure Entity

In `entities/{entity_name}/entity_config.py`:

```python
class MyEntityConfig:
    name = "myentity"
    env_var = "INCLUDE_MYENTITY"
    # ... other fields ...

    # Declare converters
    converters = {
        'convert_to_myentity': {
            'module': 'github_data.entities.myentity.converters',
            'function': 'convert_to_myentity',
            'target_model': 'MyEntity',
        },
    }

    # Reference converters in operations
    github_api_operations = {
        "get_repository_myentity": {
            "boundary_method": "get_repository_myentity",
            "converter": "convert_to_myentity",  # Must match declared converter
        },
    }
```

## Step 4: Implement Converters

Create `entities/{entity_name}/converters.py`:

```python
from typing import Dict, Any
from .models import MyEntity
from github_data.github.converter_registry import get_converter

def convert_to_myentity(raw_data: Dict[str, Any]) -> MyEntity:
    """
    Convert raw GitHub API data to MyEntity model.

    Args:
        raw_data: Raw data from GitHub API

    Returns:
        MyEntity domain model
    """
    # Use registry for nested conversions
    user = get_converter('convert_to_user')(raw_data['user'])

    return MyEntity(
        id=raw_data["id"],
        user=user,
        # ...
    )
```

**Important**: Always use `get_converter()` for nested conversions rather than direct imports.
```

### 2. Architecture Documentation

Add section to `docs/architecture/converter-registry.md` explaining:

- Registry pattern and rationale
- How converters are discovered and loaded
- Validation strategy and fail-fast behavior
- How to add new converters
- Common patterns for nested conversions

### 3. Migration Guide

Create `docs/development/converter-migration-guide.md` for developers migrating existing entities:

- Step-by-step migration process
- Before/after code examples
- Testing checklist
- Common pitfalls and solutions

## Impact Analysis

### Benefits Achieved

1. **Zero shared file modifications**: Adding new entity no longer requires touching `converters.py`
2. **Clear ownership**: Each entity explicitly declares and owns its conversion logic
3. **Better organization**: Converters colocated with the models they convert to
4. **Eliminates circular imports**: No more TYPE_CHECKING hacks needed
5. **Fail-fast validation**: Configuration errors caught at startup, not runtime
6. **Consistent patterns**: Matches existing `GitHubOperationRegistry` design
7. **Self-documenting**: Entity configs show all capabilities in one place

### Migration Scope

**Framework Development**:
- `ConverterRegistry` class: ~200 lines
- Unit tests: ~150 lines
- Integration tests: ~100 lines
- Documentation: ~4 hours
- **Total**: ~2 days

**Per Entity Migration**:
- Create `converters.py`: ~30-60 minutes
- Update `entity_config.py`: ~15 minutes
- Test converter loading: ~15 minutes
- Validate integration tests: ~30 minutes
- **Total per entity**: ~1-2 hours

**Complete Migration**:
- Framework: ~2 days
- 10 entities × 2 hours: ~20 hours (~2.5 days)
- Final cleanup: ~4 hours
- **Total effort**: ~5 days

### Risk Mitigation

1. **Backward compatibility**: Legacy fallback ensures nothing breaks during migration
2. **Incremental migration**: Can validate with one entity before proceeding
3. **Existing tests**: All tests continue passing throughout migration
4. **Fail-fast startup**: Configuration errors impossible to miss
5. **Parallel development**: Teams can continue adding features during migration

### Success Metrics

**Before Implementation**:
- Adding entity: Must modify monolithic `converters.py` (225+ lines)
- Circular import risk requires TYPE_CHECKING workarounds
- Single file contains all conversion logic for all entities
- No explicit validation of converter/operation references

**After Implementation**:
- Adding entity: Create `entity/converters.py`, declare in config, done
- Zero modifications to shared converter files
- Clean imports, no TYPE_CHECKING workarounds needed
- Entity packages are self-contained and self-documenting
- Fail-fast validation catches all configuration errors at startup

**Validation Criteria**:
- ✅ All existing tests pass after migration
- ✅ New entity can be added without touching `converters.py`
- ✅ Startup validation catches misconfigurations
- ✅ Documentation clearly explains converter pattern
- ✅ No circular import issues remain
- ✅ Converter ownership is clear and explicit

## Implementation Checklist

### Phase 1: Framework
- [ ] Create `github_data/github/converter_registry.py`
- [ ] Implement `ConverterRegistry` class with eager loading
- [ ] Implement backward compatibility fallback
- [ ] Add `get_converter()` convenience function
- [ ] Create unit tests for registry
- [ ] Integrate into application startup
- [ ] Validate all existing tests pass

### Phase 2: Pilot Migration
- [ ] Choose pilot entity (recommend: labels or releases)
- [ ] Create `entities/{entity}/converters.py`
- [ ] Add `converters` dict to entity config
- [ ] Run tests and validate
- [ ] Document any issues or improvements
- [ ] Update migration guide based on learnings

### Phase 3: Remaining Entities
- [ ] Migrate each entity (10 total)
- [ ] Validate tests after each migration
- [ ] Update entity documentation

### Phase 4: Cleanup
- [ ] Remove backward compatibility code
- [ ] Refactor `converters.py` to only common converters
- [ ] Final test suite run
- [ ] Update all documentation
- [ ] Mark architectural improvement as complete

## Appendix: Converter Declaration Examples

### Simple Entity (Labels)

```python
# entities/labels/entity_config.py
class LabelsEntityConfig:
    converters = {
        'convert_to_label': {
            'module': 'github_data.entities.labels.converters',
            'function': 'convert_to_label',
            'target_model': 'Label',
        },
    }
```

### Complex Entity with Multiple Converters (Releases)

```python
# entities/releases/entity_config.py
class ReleasesEntityConfig:
    converters = {
        'convert_to_release': {
            'module': 'github_data.entities.releases.converters',
            'function': 'convert_to_release',
            'target_model': 'Release',
        },
        'convert_to_release_asset': {
            'module': 'github_data.entities.releases.converters',
            'function': 'convert_to_release_asset',
            'target_model': 'ReleaseAsset',
        },
    }
```

### Common Converters (Legacy Location)

```python
# github_data/github/converters.py (after migration)
# Only contains shared converters used across multiple entities

def convert_to_user(raw_data: Dict[str, Any]) -> GitHubUser:
    """Convert raw user data - used by many entities."""
    # ...

def _parse_datetime(date_string: str) -> datetime:
    """Parse GitHub datetime format - utility used everywhere."""
    # ...
```

## References

- [Architectural Improvements Analysis](active/architectural-improvements/2025-11-03-architectural-improvements.md) - Original proposal
- [Entity Addition Guide](../development/adding-entities.md) - Will be updated
- [GitHubOperationRegistry](../../github_data/github/operation_registry.py) - Parallel pattern

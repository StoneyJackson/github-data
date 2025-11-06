# Service Method Registry Design

**Date**: 2025-11-05
**Status**: Approved
**Related**: [2025-11-03 Architectural Improvements Analysis](2025-11-03-architectural-improvements.md)

## Executive Summary

This design implements a **declarative operation registry** that eliminates the need to manually modify shared GitHub service layer files when adding new entities. Instead of modifying 4 files (boundary.py, protocols.py, service.py, converters.py), developers declare GitHub API operations in their entity config and the registry auto-generates service methods with cross-cutting concerns.

**Key Benefits:**
- Reduces entity addition from 13 file modifications to 0 shared file modifications
- Eliminates 200+ lines of boilerplate per entity
- Ensures consistent cross-cutting concerns (caching, rate limiting, retries)
- Maintains debuggability through rich error messages and validation

**Approach:** Fully dynamic method generation with debug-friendly infrastructure

## Problem Statement

When adding a new entity like "releases", developers must manually modify 4 shared files totaling 1,554 lines:

1. **boundary.py** (309 lines) - Add raw API access method
2. **protocols.py** (489 lines) - Add abstract method definition
3. **service.py** (457 lines) - Add method wrapper with cross-cutting concerns
4. **converters.py** (299 lines) - Add converter functions

Each entity follows the same repetitive pattern:
```python
# Pattern repeated 11+ times across entities
def get_repository_X(self, repo_name: str) -> List[Dict[str, Any]]:
    return self._execute_with_cross_cutting_concerns(
        cache_key=f"X:{repo_name}",
        operation=lambda: self._boundary.get_repository_X(repo_name),
    )
```

This creates:
- **High cognitive overhead** - Must modify 4 files in correct pattern
- **Inconsistency risk** - Manual duplication leads to divergence
- **Poor maintainability** - Changes to cross-cutting concerns require updating all methods

## Design Decisions

### Decision 1: Fully Dynamic vs Hybrid vs Code Generation

**Options Considered:**
1. **Runtime Generation** - Use `__getattr__` to generate methods dynamically
2. **Compile-Time Generation** - Generate Python files from specs via CLI
3. **Hybrid** - Keep explicit signatures, auto-generate implementations

**Decision: Runtime Generation (Option 1)**

**Rationale:**
- Simplest to implement and maintain
- No generated files to manage
- Explicit methods can coexist (escape hatch)
- Type safety less critical since developers aren't writing the code

**Trade-offs Accepted:**
- No IDE autocomplete for generated methods
- Requires debug-friendly infrastructure

### Decision 2: Debug-Friendly Infrastructure

**Options Considered:**
- Minimal infrastructure (just dynamic generation)
- Comprehensive debugging tools (introspection CLI, trace mode, etc.)
- Targeted high-impact features only

**Decision: Targeted High-Impact Features**

**Included (High Impact, Low Complexity):**
1. Rich error messages with entity/spec context (~30 lines)
2. Startup validation with fail-fast (~40 lines)
3. Test fixtures for registry validation (~20 lines)
4. Basic logging (~10 lines)

**Deferred (Lower Priority):**
- Introspection CLI tool (can add later if needed)
- Debug trace mode (can add later if debugging becomes difficult)

**Total Debug Infrastructure:** ~100 lines

### Decision 3: Cache Key Auto-Generation

**Question:** Should developers specify cache keys explicitly or auto-generate?

**Decision: Auto-generate with override option**

**Auto-generation Pattern:**
```python
# Method: get_repository_releases(repo_name="owner/repo")
# Cache key: "get_repository_releases:owner/repo"

# Method: get_issue_comments(repo_name="owner/repo", issue_number=123)
# Cache key: "get_issue_comments:owner/repo:123"
```

**Override when needed:**
```python
'cache_key_template': 'custom_key:{repo_name}'  # Rare
```

**Rationale:** Eliminates boilerplate while allowing customization

### Decision 4: Escape Hatch Strategy

**Question:** How to handle operations that don't fit the registry pattern?

**Decision: Explicit methods take precedence (Python's natural `__getattr__` behavior)**

```python
class GitHubService:
    def __getattr__(self, method_name):
        # Only called if method doesn't exist explicitly
        return self._operation_registry.generate_method(method_name)

    # Explicit method - automatically overrides registry
    def complex_custom_operation(self, **kwargs):
        # Custom multi-step logic
        pass
```

**Rationale:**
- Zero configuration needed for edge cases
- Clear in code that operation is special
- Standard Python behavior
- Enables gradual migration

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│ Entity Configs                                              │
│ ┌──────────────────┐  ┌──────────────────┐                │
│ │ ReleasesConfig   │  │ LabelsConfig     │  ...           │
│ │ github_api_ops{} │  │ github_api_ops{} │                │
│ └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ GitHubOperationRegistry                                     │
│ • Scans all entity configs at startup                       │
│ • Validates all operation specs (fail fast)                 │
│ • Builds map: {method_name -> Operation}                    │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ GitHubService                                               │
│ • __getattr__ for dynamic dispatch                          │
│ • Applies cross-cutting concerns                            │
│ • Rich error context on failures                            │
│ • Explicit methods override registry (escape hatch)         │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Boundary + Converters                                       │
│ (Unchanged - registry calls them)                           │
└─────────────────────────────────────────────────────────────┘
```

### Execution Flow

**Startup:**
1. `GitHubService.__init__` initializes `GitHubOperationRegistry`
2. Registry scans `EntityRegistry` for all `github_api_operations`
3. Registry validates each operation spec (raises `ValidationError` if invalid)
4. Registry builds internal map: `{method_name: Operation}`
5. Logs: "Registered N operations from M entities"

**Runtime:**
1. Code calls `github_service.get_repository_releases(repo_name="owner/repo")`
2. Method doesn't exist explicitly → `__getattr__` fires
3. Registry looks up `Operation` for `get_repository_releases`
4. If not found → `AttributeError` with available operations list
5. If found → Create dynamic method wrapper
6. Execute: boundary call → rate limiting → caching → converter
7. Return results OR enhanced exception with entity/spec context

### Entity Config Specification

```python
# github_data/entities/releases/entity_config.py

class ReleasesEntityConfig:
    name = "releases"
    # ... existing fields ...

    # NEW: Declarative GitHub API operations
    github_api_operations = {
        'get_repository_releases': {
            'boundary_method': 'get_repository_releases',  # Required
            'converter': 'convert_to_release',              # Optional
            'cache_key_template': 'releases:{repo_name}',   # Optional (auto-generated if omitted)
            'requires_retry': False,                        # Optional (auto-detected if omitted)
        },
        'create_release': {
            'boundary_method': 'create_release',
            'converter': 'convert_to_release',
            # Write operations auto-detected, skip caching
        }
    }
```

**Specification Fields:**

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `boundary_method` | Yes | - | Method name on `GitHubApiBoundary` |
| `converter` | No | None | Converter function name (no conversion if omitted) |
| `cache_key_template` | No | Auto-generated | Override cache key format (format string) |
| `requires_retry` | No | Auto-detected | Force retry on transient failures |

**Auto-Detection Rules:**
- **Cache keys:** `"{method_name}:{param1}:{param2}:..."`
- **Write operations:** Method names starting with `create_`, `update_`, `delete_`, `close_` skip caching
- **Retry behavior:** Write operations default to retry enabled, reads default to no retry

### GitHubOperationRegistry Implementation

```python
# github_data/github/operation_registry.py

class GitHubOperationRegistry:
    """Registry for dynamically discovered GitHub API operations."""

    def __init__(self):
        self._operations: Dict[str, Operation] = {}
        self._load_operations()
        self._validate_all()

    def _load_operations(self):
        """Scan all entity configs and register operations."""
        from github_data.entities.registry import EntityRegistry

        for entity_name, entity in EntityRegistry()._entities.items():
            config = entity.config

            if not hasattr(config, 'github_api_operations'):
                continue

            for method_name, spec in config.github_api_operations.items():
                operation = Operation(
                    method_name=method_name,
                    entity_name=entity_name,
                    spec=spec
                )
                self._operations[method_name] = operation

        logger.info(f"Registered {len(self._operations)} operations")

    def _validate_all(self):
        """Validate all specs at startup (fail fast)."""
        for method_name, operation in self._operations.items():
            try:
                operation.validate()
            except ValidationError as e:
                raise ValidationError(
                    f"Invalid spec for '{method_name}' "
                    f"in entity '{operation.entity_name}': {e}"
                ) from e

    def get_operation(self, method_name: str) -> Optional[Operation]:
        """Get registered operation by name."""
        return self._operations.get(method_name)

    def list_operations(self) -> List[str]:
        """List all registered operation names."""
        return list(self._operations.keys())
```

### Operation Class

```python
class Operation:
    """Represents a single GitHub API operation."""

    def __init__(self, method_name: str, entity_name: str, spec: Dict[str, Any]):
        self.method_name = method_name
        self.entity_name = entity_name
        self.spec = spec

        # Parse spec
        self.boundary_method = spec['boundary_method']
        self.converter_name = spec.get('converter')
        self.cache_key_template = spec.get('cache_key_template')
        self.requires_retry = spec.get('requires_retry', self._is_write_operation())

    def validate(self):
        """Validate operation spec."""
        if not self.boundary_method:
            raise ValidationError("Missing required field 'boundary_method'")

        if self.converter_name and not self._converter_exists(self.converter_name):
            raise ValidationError(f"Converter '{self.converter_name}' not found")

    def _is_write_operation(self) -> bool:
        """Detect write operations by method name."""
        write_prefixes = ('create_', 'update_', 'delete_', 'close_')
        return self.method_name.startswith(write_prefixes)

    def _converter_exists(self, converter_name: str) -> bool:
        """Check if converter function exists."""
        try:
            from github_data.github import converters
            return hasattr(converters, converter_name)
        except ImportError:
            return False

    def should_cache(self) -> bool:
        """Determine if operation should use caching."""
        return not self._is_write_operation()

    def get_cache_key(self, **kwargs) -> str:
        """Generate cache key from parameters."""
        if self.cache_key_template:
            return self.cache_key_template.format(**kwargs)

        # Auto-generate: "method_name:param1:param2:..."
        param_values = ':'.join(str(v) for v in kwargs.values())
        return f"{self.method_name}:{param_values}"
```

### GitHubService Integration

```python
# github_data/github/service.py

class GitHubService(RepositoryService):
    """Service layer for GitHub API operations."""

    def __init__(
        self,
        boundary: GitHubApiBoundary,
        rate_limiter: Optional[RateLimitHandler] = None,
        caching_enabled: bool = True,
    ):
        self._boundary = boundary
        self._rate_limiter = rate_limiter or RateLimitHandler()
        self._caching_enabled = caching_enabled

        # NEW: Initialize operation registry
        self._operation_registry = GitHubOperationRegistry()

        logger.info(
            f"GitHubService initialized with "
            f"{len(self._operation_registry.list_operations())} registered operations"
        )

    def __getattr__(self, method_name: str):
        """
        Dynamically generate methods from operation registry.

        Only called when attribute isn't found explicitly.
        Explicit methods (escape hatch) take precedence automatically.
        """
        operation = self._operation_registry.get_operation(method_name)

        if not operation:
            raise AttributeError(
                f"GitHubService has no method '{method_name}'. "
                f"Available operations: {self._operation_registry.list_operations()}"
            )

        # Create dynamic method
        def dynamic_method(**kwargs):
            return self._execute_operation(operation, **kwargs)

        # Make it debuggable
        dynamic_method.__name__ = method_name
        dynamic_method.__doc__ = f"Dynamically generated from {operation.entity_name}."

        return dynamic_method

    def _execute_operation(self, operation: Operation, **kwargs) -> Any:
        """Execute registered operation with cross-cutting concerns."""
        try:
            # Apply caching if appropriate
            if operation.should_cache() and self._caching_enabled:
                cache_key = operation.get_cache_key(**kwargs)
                return self._execute_with_cross_cutting_concerns(
                    cache_key=cache_key,
                    operation=lambda: self._call_boundary(operation, **kwargs)
                )
            else:
                return self._execute_with_cross_cutting_concerns(
                    cache_key=None,
                    operation=lambda: self._call_boundary(operation, **kwargs)
                )
        except Exception as e:
            # Enhanced error context for debugging
            raise type(e)(
                f"Operation '{operation.method_name}' failed "
                f"(entity={operation.entity_name}, spec={operation.spec}): {e}"
            ) from e

    def _call_boundary(self, operation: Operation, **kwargs) -> Any:
        """Call boundary method and apply converter if specified."""
        logger.debug(
            f"Executing {operation.method_name} "
            f"[entity={operation.entity_name}, args={kwargs}]"
        )

        # Call boundary method
        boundary_method = getattr(self._boundary, operation.boundary_method)
        raw_result = boundary_method(**kwargs)

        # Apply converter if specified
        if operation.converter_name:
            converter = self._get_converter(operation.converter_name)

            # Handle list vs single results
            if isinstance(raw_result, list):
                result = [converter(item) for item in raw_result]
            else:
                result = converter(raw_result)

            logger.debug(f"Converted results using {operation.converter_name}")
            return result

        return raw_result

    def _get_converter(self, converter_name: str):
        """Get converter function by name."""
        from github_data.github import converters
        return getattr(converters, converter_name)

    # EXISTING: _execute_with_cross_cutting_concerns unchanged
```

## Testing Strategy

### Test Coverage Areas

1. **Registry Validation Tests** - Ensure all entity operations discovered and validated
2. **Operation Spec Tests** - Validate spec parsing and auto-detection logic
3. **Dynamic Generation Tests** - Verify methods generated correctly
4. **Error Context Tests** - Ensure failures include debugging information
5. **Escape Hatch Tests** - Confirm explicit methods override registry
6. **Integration Tests** - Existing entity tests work unchanged

### Key Test Files

```python
# tests/unit/github/test_operation_registry.py
- test_all_entity_operations_registered()
- test_invalid_operation_spec_fails_at_startup()
- test_operation_cache_key_generation()
- test_write_operations_skip_caching()

# tests/unit/github/test_github_service_dynamic.py
- test_dynamic_method_generation()
- test_explicit_methods_override_dynamic()
- test_unknown_method_raises_helpful_error()
- test_dynamic_method_error_includes_context()

# tests/shared/fixtures/github_service_fixtures.py
- validate_github_service_registry() fixture
```

### Testing During Migration

- Existing entity tests continue working (they just call service methods)
- Both explicit and dynamic methods coexist during gradual migration
- Registry-specific tests added for new functionality

## Migration Strategy

### Phase 1: Add Registry Infrastructure (No Breaking Changes)
1. Add `operation_registry.py` with `GitHubOperationRegistry` and `Operation` classes
2. Update `GitHubService.__init__` to initialize registry
3. Add `GitHubService.__getattr__` for dynamic dispatch
4. Add helper methods: `_execute_operation`, `_call_boundary`
5. All existing explicit methods still work - nothing breaks

**Validation:** Run full test suite - all tests should pass

### Phase 2: Migrate One Entity at a Time
For each entity (starting with simplest):
1. Add `github_api_operations` to entity config
2. Test that dynamic methods work alongside explicit methods
3. Remove explicit methods from `service.py`, `protocols.py`
4. Remove boundary methods if not shared by other entities
5. Run entity tests - behavior should be unchanged
6. Commit with message: `refactor(entity): migrate X to operation registry`

**Suggested Order:**
1. labels (simple, no dependencies)
2. milestones (simple, no dependencies)
3. releases (simple, recently added)
4. issues (moderate complexity)
5. comments (depends on issues)
6. Continue with remaining entities...

### Phase 3: Cleanup
1. Once all entities migrated, `protocols.py` becomes optional
2. Decision: Keep for documentation or remove entirely
3. Update architecture docs to mark improvement #1 complete

### Rollback Strategy

If issues discovered during migration:
- Keep explicit methods during migration
- Can roll back entity-by-entity
- Registry infrastructure is additive - can be disabled without removing

## Documentation Updates

### New Documentation Files

**`docs/development/adding-entities.md`**
- Complete guide for adding entities with registry
- Field reference for `github_api_operations`
- Examples for common patterns
- Escape hatch documentation
- Testing guidance

### Updated Documentation

**`CLAUDE.md`**
- Add pointer to `docs/development/adding-entities.md`
- Brief mention of declarative operation registry

**Entity Generator Templates**
- Add `github_api_operations` template to `entity_config.py.template`
- Include sensible defaults for common patterns

## Success Metrics

### Before (Current State)
- **13 file modifications** per entity (4 service layer, 5 tests, 1 pytest.ini, 3 docs)
- **200+ lines of boilerplate** (boundary, protocol, service, converter)
- **50+ lines of test updates** (count assertions, entity lists)
- **Manual coordination** across multiple files

### After (With Registry)
- **0 shared file modifications** (all declared in entity config)
- **5-10 lines of declaration** in entity config
- **Test updates handled by dynamic discovery fixtures**
- **Configuration-based** with validation

### Reduction
- From 13 file modifications → 0 shared file modifications
- From 200+ lines boilerplate → 5-10 lines declaration
- From manual coordination → declarative configuration

## Implementation Checklist

### Phase 1: Core Registry Infrastructure (~4-6 hours)
- [ ] Create `github_data/github/operation_registry.py`
  - [ ] `GitHubOperationRegistry` class
  - [ ] `Operation` class
  - [ ] `ValidationError` exception
- [ ] Update `GitHubService.__init__` to initialize registry
- [ ] Add `GitHubService.__getattr__` for dynamic dispatch
- [ ] Add `GitHubService._execute_operation` helper
- [ ] Add `GitHubService._call_boundary` helper
- [ ] Add logging throughout

### Phase 2: Testing Infrastructure (~2-3 hours)
- [ ] Create `tests/unit/github/test_operation_registry.py`
  - [ ] Registry discovery tests
  - [ ] Spec validation tests
  - [ ] Cache key generation tests
- [ ] Create `tests/unit/github/test_github_service_dynamic.py`
  - [ ] Dynamic method generation tests
  - [ ] Escape hatch tests
  - [ ] Error context tests
- [ ] Add registry validation fixture to `tests/shared/fixtures/`

### Phase 3: Documentation (~2-3 hours)
- [ ] Create `docs/development/adding-entities.md`
- [ ] Update `CLAUDE.md` to reference new docs
- [ ] Update entity generator templates

### Phase 4: Entity Migration (~30 min each)
- [ ] Migrate labels entity
- [ ] Migrate milestones entity
- [ ] Migrate releases entity
- [ ] Migrate issues entity
- [ ] Migrate comments entity
- [ ] Migrate pull requests entity
- [ ] Migrate pr_comments entity
- [ ] Migrate pr_reviews entity
- [ ] Migrate pr_review_comments entity
- [ ] Migrate sub_issues entity
- [ ] Migrate git_repositories entity

### Phase 5: Cleanup
- [ ] Review protocols.py (keep or remove)
- [ ] Update architectural improvements doc
- [ ] Final test suite run

## Estimated Timeline

**Total: 2-3 days**

- **Day 1:** Core infrastructure + testing (6-9 hours)
- **Day 2:** Documentation + migrate 3-4 entities (6-8 hours)
- **Day 3:** Migrate remaining entities + cleanup (4-6 hours)

## Risks and Mitigations

### Risk 1: Dynamic Methods Hard to Debug
**Mitigation:**
- Rich error messages with entity/spec context
- Startup validation fails fast on invalid specs
- Comprehensive logging of operations
- Test fixtures validate registry completeness

### Risk 2: Performance Impact from Dynamic Dispatch
**Mitigation:**
- `__getattr__` only called once per method (Python caches result)
- Registry lookup is O(1) dictionary access
- No performance difference after first call
- Can benchmark if concerns arise

### Risk 3: Type Safety Loss
**Mitigation:**
- Accepted trade-off (developers don't write the code)
- Startup validation catches most errors
- Test coverage ensures correctness
- Can add type stubs later if needed

### Risk 4: Migration Complexity
**Mitigation:**
- Incremental migration entity-by-entity
- Both explicit and dynamic methods coexist
- Can pause migration at any point
- Easy rollback by keeping explicit methods

## Future Enhancements

### Deferred for Initial Implementation
1. **Introspection CLI Tool** - For inspecting registered operations
2. **Debug Trace Mode** - Detailed execution logging
3. **Type Stub Generation** - Auto-generate .pyi files for IDE support
4. **Converter Registry** - Move converters to entity packages (Improvement #4)

### Potential Extensions
1. **Operation Composition** - Declare multi-step operations
2. **Custom Validators** - Per-operation validation logic
3. **Performance Monitoring** - Automatic timing/metrics collection
4. **GraphQL vs REST Declaration** - Explicit API client selection

## Related Work

- **Architectural Improvements #1** - This design (Service Method Registry)
- **Architectural Improvements #2** - Dynamic Entity Count Validation (completed)
- **Architectural Improvements #3** - Test Marker Validation (completed)
- **Architectural Improvements #4** - Converter Registry (future enhancement)

## Approval

**Design Approved:** 2025-11-05
**Approved By:** User (via brainstorming session)
**Next Step:** Worktree setup and implementation planning

---

## Appendix: Example Entity Config

Complete example showing all features:

```python
# github_data/entities/releases/entity_config.py

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from github_data.entities.strategy_context import StrategyContext
    from github_data.entities.releases.save_strategy import ReleasesSaveStrategy
    from github_data.entities.releases.restore_strategy import ReleasesRestoreStrategy


class ReleasesEntityConfig:
    """Configuration for releases entity."""

    name = "releases"
    env_var = "INCLUDE_RELEASES"
    default_value = True
    value_type = bool
    dependencies: List[str] = []
    description = "Repository releases and tags"

    # Service requirements
    required_services_save: List[str] = []
    required_services_restore: List[str] = []

    # GitHub API operations (NEW!)
    github_api_operations = {
        # Simple read operation
        'get_repository_releases': {
            'boundary_method': 'get_repository_releases',
            'converter': 'convert_to_release',
            # Cache key auto-generated: "get_repository_releases:{repo_name}"
        },

        # Write operation (no caching, retry enabled)
        'create_release': {
            'boundary_method': 'create_release',
            'converter': 'convert_to_release',
            # Auto-detected as write operation, skips caching
        },

        # Operation with custom cache key (rare)
        'get_release_by_tag': {
            'boundary_method': 'get_release_by_tag',
            'converter': 'convert_to_release',
            'cache_key_template': 'release_tag:{repo_name}:{tag}',
        },
    }

    @staticmethod
    def create_save_strategy(context: "StrategyContext") -> Optional["ReleasesSaveStrategy"]:
        from github_data.entities.releases.save_strategy import ReleasesSaveStrategy
        return ReleasesSaveStrategy()

    @staticmethod
    def create_restore_strategy(context: "StrategyContext") -> Optional["ReleasesRestoreStrategy"]:
        from github_data.entities.releases.restore_strategy import ReleasesRestoreStrategy
        return ReleasesRestoreStrategy()
```

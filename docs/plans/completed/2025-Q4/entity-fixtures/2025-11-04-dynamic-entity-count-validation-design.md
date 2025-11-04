# Dynamic Entity Count Validation Design

**Date**: 2025-11-04
**Improvement**: Phase 1 Quick Win - Test Infrastructure
**Status**: Design Complete, Ready for Implementation

## Executive Summary

This design implements dynamic entity discovery in test fixtures to eliminate hardcoded entity counts and lists. When complete, adding new entities will require **0 test file updates** (down from 5+ currently).

**Approach**: Pure Discovery - EntityRegistry auto-discovery as single source of truth
**Effort**: 4-6 hours
**Impact**: Eliminates 5+ test file modifications per entity

## Problem Statement

### Current State

Multiple test files hardcode entity counts and lists that must be manually updated when adding entities:

**File 1: `tests/integration/operations/test_strategy_factory_integration.py`**
```python
def test_create_save_strategies_all_entities():
    # ...
    assert len(strategies) == 10  # Must update from 9 → 10 when adding entity
```

**File 2: `tests/unit/operations/test_strategy_factory_registry.py`**
```python
def test_strategy_factory_creates_all_10_entities():
    all_entities = [
        "labels", "milestones", ..., "releases"  # Manual list!
    ]
    assert len(strategy_names) == 11  # Must update
```

**File 3: `tests/integration/test_complete_dependency_graph.py`**
```python
def test_no_circular_dependencies():
    enabled = registry.get_enabled_entities()
    assert len(enabled) == 11  # Must update
```

### Pain Points

1. **Brittle tests** - Break when entities added/removed
2. **Manual updates** - 5+ files need changes per entity
3. **Maintenance burden** - Easy to forget a file
4. **Test coupling** - Tests know about entities they don't care about

## Design Decisions

### Decision 1: Pure Discovery vs Documented List

**Considered Approaches:**
- A. Pure Discovery - Always query EntityRegistry
- B. Documented List - Maintain canonical list in fixture
- C. Discovery with Validation - Validate discovery against documented list

**Decision**: **Pure Discovery (A)**

**Rationale:**
- Zero maintenance (no files to update)
- Tests validate actual system behavior
- Discovery is already production code path
- EntityRegistry is single source of truth

### Decision 2: Validation Style

**Considered Approaches:**
- A. Exhaustive - Ensure every discovered entity is tested
- B. Presence - Verify specific entities exist without counting
- C. Set Equality - Ensure discovered equals expected set

**Decision**: **Presence Validation (B)**

**Rationale:**
- New entities don't break existing tests
- Tests focus on behavior under test
- More flexible as system grows
- Avoids brittle count assertions

### Decision 3: Test Intent

**Considered Approaches:**
- A. Preserve test intent - Compute expected counts dynamically
- B. Change test intent - Make tests more flexible
- C. Keep some hardcoded as regression checks

**Decision**: **Change Test Intent (B)**

**Rationale:**
- Tests should focus on entity under test
- Hardcoded counts create unnecessary coupling
- Behavioral validation more robust than counts

### Decision 4: Fixture Scope

**Decision**: **Function-scoped**

**Rationale:**
- Test isolation (fresh registry per test)
- Avoid state pollution between tests
- Can optimize to session-scope later if performance issues arise

### Decision 5: Assertion Verbosity

**Decision**: **Terse assertions unless verbose adds information**

**Examples:**
```python
# Terse - preferred
assert set(strategy_names) == set(all_entity_names)

# Verbose - only when message adds value
assert "git_repository" in strategy_names, "git_service should enable git_repository"
```

## Design: Pure Discovery Fixtures

### Fixture Architecture

**File**: `tests/shared/fixtures/entity_fixtures.py` (NEW)

```python
"""Entity discovery fixtures for dynamic test validation.

These fixtures use EntityRegistry's auto-discovery to provide entity
information without requiring manual updates when entities are added.
"""

import pytest
from github_data.entities.registry import EntityRegistry
from typing import List


@pytest.fixture
def entity_registry():
    """Provide a fresh EntityRegistry instance.

    Returns:
        EntityRegistry: Fresh registry with all discovered entities
    """
    return EntityRegistry()


@pytest.fixture
def all_entity_names(entity_registry):
    """Get all registered entity names dynamically.

    Uses EntityRegistry auto-discovery to find all entities.
    No manual updates needed when adding new entities.

    Returns:
        List[str]: All discovered entity names
    """
    return entity_registry.get_all_entity_names()


@pytest.fixture
def enabled_entity_names(entity_registry):
    """Get all enabled entity names by default configuration.

    Returns:
        List[str]: Names of entities enabled by default
    """
    enabled = entity_registry.get_enabled_entities()
    return [e.config.name for e in enabled]


@pytest.fixture
def entity_names_by_dependency_order(entity_registry):
    """Get enabled entities sorted by dependency order.

    Returns:
        List[str]: Entity names in topological sort order
    """
    enabled = entity_registry.get_enabled_entities()
    return [e.config.name for e in enabled]


@pytest.fixture
def independent_entity_names(entity_registry):
    """Get entities with no dependencies.

    Returns:
        List[str]: Entity names with empty dependency lists
    """
    all_entities = entity_registry._entities.values()
    return [e.config.name for e in all_entities if not e.get_dependencies()]
```

### Integration with Test Infrastructure

**Update**: `tests/conftest.py` (add to pytest_plugins list)

```python
pytest_plugins = [
    # ... existing plugins ...
    # Entity Discovery Fixtures
    "tests.shared.fixtures.entity_fixtures",
]
```

## Test Transformation Patterns

### Pattern 1: Replace Hardcoded Count with Set Equality

**Before:**
```python
def test_create_save_strategies_all_entities():
    registry = EntityRegistry()
    registry.get_entity("git_repository").enabled = False
    factory = StrategyFactory(registry)
    strategies = factory.create_save_strategies()

    assert len(strategies) == 10  # Brittle!
    entity_names = [s.get_entity_name() for s in strategies]
    assert "labels" in entity_names
    assert "issues" in entity_names
    assert "releases" in entity_names
```

**After:**
```python
def test_create_save_strategies_all_entities(all_entity_names):
    """Test creating save strategies for all enabled entities except git_repository."""
    registry = EntityRegistry()
    registry.get_entity("git_repository").enabled = False
    factory = StrategyFactory(registry)
    strategies = factory.create_save_strategies()

    strategy_names = [s.get_entity_name() for s in strategies]

    # Verify we got all enabled entities
    expected = set(all_entity_names) - {"git_repository"}
    assert set(strategy_names) == expected
```

### Pattern 2: Replace Hardcoded List with Discovery

**Before:**
```python
def test_strategy_factory_creates_all_10_entities():
    all_entities = [
        "labels", "milestones", "issues", "comments",
        "sub_issues", "pull_requests", "pr_reviews",
        "pr_review_comments", "pr_comments", "git_repository", "releases"
    ]

    mock_git_service = Mock()
    strategies = factory.create_save_strategies(git_service=mock_git_service)
    strategy_names = [s.get_entity_name() for s in strategies]

    for entity_name in all_entities:
        assert entity_name in strategy_names, f"Failed to create {entity_name}"

    assert len(strategy_names) == 11
```

**After:**
```python
def test_strategy_factory_creates_all_entities(all_entity_names):
    """Test StrategyFactory creates strategies for all discovered entities."""
    mock_git_service = Mock()
    strategies = factory.create_save_strategies(git_service=mock_git_service)
    strategy_names = [s.get_entity_name() for s in strategies]

    # Verify all discovered entities have strategies
    assert set(strategy_names) == set(all_entity_names)
```

### Pattern 3: Testing With Conditional Inclusion

**Before:**
```python
def test_create_save_strategies_with_git_repository():
    registry = EntityRegistry()
    factory = StrategyFactory(registry)
    mock_git_service = Mock()

    strategies = factory.create_save_strategies(git_service=mock_git_service)

    entity_names = [s.get_entity_name() for s in strategies]
    assert "git_repository" in entity_names

    git_strategy = next(
        s for s in strategies if s.get_entity_name() == "git_repository"
    )
    assert git_strategy._git_service is mock_git_service
```

**After:**
```python
def test_create_save_strategies_with_git_repository(all_entity_names):
    """Test git_repository strategy is included when git_service provided."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry)
    mock_git_service = Mock()

    strategies = factory.create_save_strategies(git_service=mock_git_service)

    strategy_names = [s.get_entity_name() for s in strategies]

    # Should get ALL entities when git_service provided
    assert set(strategy_names) == set(all_entity_names)

    # Verify git_repository strategy received git_service
    git_strategy = next(
        s for s in strategies if s.get_entity_name() == "git_repository"
    )
    assert git_strategy._git_service is mock_git_service
```

### Pattern 4: Dependency Graph Validation

**Before:**
```python
def test_complete_dependency_graph():
    registry = EntityRegistry()
    enabled = registry.get_enabled_entities()
    enabled_names = [e.config.name for e in enabled]

    # Dependency checks follow...
```

**After:**
```python
def test_complete_dependency_graph(enabled_entity_names):
    """Test dependency relationships for all enabled entities."""
    registry = EntityRegistry()
    enabled = registry.get_enabled_entities()
    enabled_names = [e.config.name for e in enabled]

    # Verify we have all expected enabled entities
    assert set(enabled_names) == set(enabled_entity_names)

    # Validate specific dependency contracts (these are explicit)
    assert registry.get_entity("labels").get_dependencies() == []
    assert registry.get_entity("issues").get_dependencies() == ["milestones"]
    # ... etc ...
```

### Pattern 5: Topological Sort Validation

**Before:**
```python
def test_complete_topological_sort():
    registry = EntityRegistry()
    enabled = registry.get_enabled_entities()
    enabled_names = [e.config.name for e in enabled]

    def idx(name):
        return enabled_names.index(name)

    # Verify dependency order constraints
    assert idx("milestones") < idx("issues")
    # ... etc ...
```

**After:**
```python
def test_complete_topological_sort(enabled_entity_names):
    """Test topological sort produces valid execution order."""
    registry = EntityRegistry()
    enabled = registry.get_enabled_entities()
    enabled_names = [e.config.name for e in enabled]

    # Verify count matches discovery
    assert set(enabled_names) == set(enabled_entity_names)

    def idx(name):
        return enabled_names.index(name)

    # Verify dependency order constraints (these are explicit contracts)
    assert idx("milestones") < idx("issues")
    assert idx("milestones") < idx("pull_requests")
    assert idx("issues") < idx("comments")
    assert idx("issues") < idx("sub_issues")
    assert idx("pull_requests") < idx("pr_reviews")
    assert idx("pull_requests") < idx("pr_comments")
    assert idx("pr_reviews") < idx("pr_review_comments")
```

## Implementation Plan

### Files to Create

1. `tests/shared/fixtures/entity_fixtures.py` - Core fixtures

### Files to Modify

1. `tests/conftest.py` - Add fixture plugin
2. `tests/integration/operations/test_strategy_factory_integration.py` - Update 3 tests
3. `tests/unit/operations/test_strategy_factory_registry.py` - Update 2 tests
4. `tests/integration/test_complete_dependency_graph.py` - Update 2 tests
5. `docs/testing/test-infrastructure.md` - Add Entity Discovery Fixtures section
6. `docs/testing/writing-tests.md` - Add Testing with Entity Discovery section

### Implementation Checklist

```
☐ Create tests/shared/fixtures/entity_fixtures.py with 5 fixtures
☐ Update tests/conftest.py to load entity_fixtures plugin
☐ Update test_strategy_factory_integration.py:
  ☐ test_create_save_strategies_all_entities
  ☐ test_create_save_strategies_with_git_repository
  ☐ test_create_restore_strategies_all_entities
☐ Update test_strategy_factory_registry.py:
  ☐ test_strategy_factory_creates_all_entities (formerly test_strategy_factory_creates_all_10_entities)
  ☐ test_strategy_factory_create_save_strategies_from_registry
☐ Update test_complete_dependency_graph.py:
  ☐ test_no_circular_dependencies
  ☐ test_complete_topological_sort
☐ Update testing documentation:
  ☐ docs/testing/test-infrastructure.md - Add entity fixtures section
  ☐ docs/testing/writing-tests.md - Add usage examples
☐ Run make test-fast to verify all changes
☐ Verify tests pass without modification when adding test entity
```

### Test Strategy

1. **Phase 1**: Create fixtures and add to conftest
   - Verify fixtures are available in test environment

2. **Phase 2**: Update one test file at a time
   - Run `make test-fast` after each file
   - Ensure no regressions

3. **Phase 3**: Validation
   - Create dummy entity to verify zero maintenance
   - Remove dummy entity
   - Confirm no test updates needed

## Benefits

### Maintenance Reduction

**Before:**
- 5+ files need manual updates per entity
- Hardcoded counts in 7+ locations
- Easy to forget a file

**After:**
- 0 files need updates per entity
- All counts computed dynamically
- Impossible to forget (automatic)

### Test Quality Improvements

1. **Focused tests** - Tests validate behavior, not counts
2. **Discovery validation** - Tests verify EntityRegistry works
3. **Future-proof** - Tests adapt to system growth automatically
4. **Clear failures** - Set comparison shows exactly what's missing

### Developer Experience

1. **Add entity** → All tests automatically include it
2. **Remove entity** → All tests automatically exclude it
3. **No "forgot to update test" bugs**
4. **Clear error messages** when discovery fails

## Success Metrics

### Before Implementation (Baseline)

Adding releases entity required updates to:
- `test_strategy_factory_integration.py` (2 locations)
- `test_strategy_factory_registry.py` (3 locations)
- `test_complete_dependency_graph.py` (2 locations)

**Total: 7 manual updates across 3 files**

### After Implementation (Target)

Adding new entity requires:
- **0 test file updates**
- Tests automatically discover and validate new entity
- Only entity implementation files needed

**Reduction: 100% elimination of test maintenance**

## Risk Analysis

### Low Risk: Discovery Failures

**Scenario**: EntityRegistry fails to discover entity

**Mitigation**: Tests fail immediately with clear error (desired behavior)

### Low Risk: Test Isolation

**Scenario**: Tests share EntityRegistry state

**Mitigation**: Function-scoped fixtures create fresh instance per test

### Low Risk: Accidental Entity Addition

**Scenario**: Developer accidentally creates entity structure

**Mitigation**: Code review process catches unexpected entities

### Low Risk: Test Performance

**Scenario**: EntityRegistry creation in every test is slow

**Mitigation**: Can optimize to session-scope if needed (simple config change)

## Alternatives Considered

### Alternative 1: Documented List as Source

```python
ALL_ENTITIES = ["labels", "milestones", ..., "releases"]

@pytest.fixture
def all_entity_names():
    return ALL_ENTITIES
```

**Rejected**: Still requires 1 file update per entity (not zero maintenance)

### Alternative 2: Discovery with Validation

```python
EXPECTED_ENTITIES = ["labels", ..., "releases"]

@pytest.fixture
def all_entity_names():
    discovered = EntityRegistry().get_all_entity_names()
    if set(discovered) != set(EXPECTED_ENTITIES):
        pytest.fail("Update EXPECTED_ENTITIES")
    return discovered
```

**Rejected**: Adds complexity without benefit, still requires updates

### Alternative 3: Safety Test with Entity Count Range

```python
def test_entity_discovery_is_reasonable():
    discovered = EntityRegistry().get_all_entity_names()
    assert 11 <= len(discovered) <= 15
```

**Rejected**: Provides no real value, arbitrary thresholds, still needs updates

## Documentation Updates

### Overview

The entity fixture system requires documentation updates to ensure developers know about and correctly use the new fixtures. These updates integrate the fixtures into existing testing documentation.

### Files to Update

#### 1. docs/testing/test-infrastructure.md

**Section**: Shared Fixture System (after line ~480)

**Add New Subsection**: "Entity Discovery Fixtures"

```markdown
### Entity Discovery Fixtures

The project provides entity discovery fixtures in `tests.shared.fixtures.entity_fixtures` that dynamically discover all registered entities. These fixtures eliminate the need to hardcode entity counts or lists in tests.

**Available Fixtures:**

```python
from tests.shared import (
    entity_registry,                    # Fresh EntityRegistry instance
    all_entity_names,                   # All registered entity names
    enabled_entity_names,               # Default-enabled entity names
    entity_names_by_dependency_order,   # Entities in topological order
    independent_entity_names,           # Entities with no dependencies
)
```

**When to Use:**

- **all_entity_names**: When validating all entities are handled (factory tests, registry tests)
- **enabled_entity_names**: When testing default configuration behavior
- **entity_names_by_dependency_order**: When validating execution order
- **independent_entity_names**: When testing root entities without dependencies
- **entity_registry**: When tests need full registry access for custom queries

**Key Benefits:**

- Zero maintenance when adding/removing entities
- Tests automatically adapt to system changes
- Validates EntityRegistry discovery mechanism
- Eliminates hardcoded entity counts and lists

**Example: Factory Test with Entity Discovery**

```python
@pytest.mark.integration
def test_factory_creates_all_entities(all_entity_names):
    """Test factory creates strategies for all discovered entities."""
    factory = StrategyFactory(registry=EntityRegistry())
    strategies = factory.create_save_strategies(git_service=Mock())

    strategy_names = [s.get_entity_name() for s in strategies]

    # Verify all discovered entities have strategies
    assert set(strategy_names) == set(all_entity_names)
```

**Example: Dependency Order Test**

```python
@pytest.mark.integration
def test_entities_in_dependency_order(entity_names_by_dependency_order):
    """Test entities are processed in correct dependency order."""
    registry = EntityRegistry()
    enabled = registry.get_enabled_entities()
    enabled_names = [e.config.name for e in enabled]

    # Verify matches discovered order
    assert enabled_names == entity_names_by_dependency_order

    # Verify specific dependency contracts
    def idx(name):
        return enabled_names.index(name)

    assert idx("milestones") < idx("issues")
    assert idx("issues") < idx("comments")
```

**Example: Testing Conditional Entity Inclusion**

```python
@pytest.mark.integration
def test_strategy_without_git_service(all_entity_names):
    """Test git_repository excluded when git_service not provided."""
    registry = EntityRegistry()
    registry.get_entity("git_repository").enabled = False
    factory = StrategyFactory(registry)

    strategies = factory.create_save_strategies()
    strategy_names = [s.get_entity_name() for s in strategies]

    # Verify all entities except git_repository
    expected = set(all_entity_names) - {"git_repository"}
    assert set(strategy_names) == expected
```

**Anti-Patterns to Avoid:**

❌ **Don't hardcode entity names in fixtures:**
```python
# BAD - creates coupling
def test_with_hardcoded_list():
    expected = ["labels", "issues", "releases"]  # Manual list
    assert actual == expected
```

✅ **Do use discovery fixtures:**
```python
# GOOD - uses discovery
def test_with_discovery(all_entity_names):
    assert set(actual) == set(all_entity_names)
```

❌ **Don't check specific entities unless testing that entity:**
```python
# BAD - unnecessary coupling
def test_factory(all_entity_names):
    strategies = create_strategies()
    assert "labels" in strategies  # Only needed if testing labels specifically
    assert "issues" in strategies  # Creates brittle test
```

✅ **Do use set equality for completeness:**
```python
# GOOD - validates behavior without coupling
def test_factory(all_entity_names):
    strategies = create_strategies()
    strategy_names = [s.get_entity_name() for s in strategies]
    assert set(strategy_names) == set(all_entity_names)
```
```

#### 2. docs/testing/writing-tests.md

**Section**: Basic Test Structure (after line ~152)

**Add New Subsection**: "Testing with Entity Discovery"

```markdown
### Testing with Entity Discovery

When writing tests that validate entity-related behavior (factories, registries, workflows), use entity discovery fixtures instead of hardcoding entity names or counts.

**Pattern: Registry and Factory Tests**

```python
import pytest
from tests.shared import all_entity_names
from github_data.entities.registry import EntityRegistry
from github_data.operations.strategy_factory import StrategyFactory

@pytest.mark.unit
@pytest.mark.fast
def test_factory_completeness(all_entity_names):
    """Test factory creates strategies for all entities."""
    factory = StrategyFactory(registry=EntityRegistry())
    strategies = factory.create_strategies()

    strategy_names = [s.get_entity_name() for s in strategies]
    assert set(strategy_names) == set(all_entity_names)
```

**Pattern: Dependency Validation**

```python
@pytest.mark.integration
def test_dependency_order(enabled_entity_names):
    """Test enabled entities respect dependencies."""
    registry = EntityRegistry()
    enabled = registry.get_enabled_entities()

    # Verify count matches discovery
    assert len(enabled) == len(enabled_entity_names)

    # Verify specific dependency contracts
    # (These are explicit requirements that shouldn't change)
    for entity in enabled:
        for dep in entity.get_dependencies():
            dep_entity = registry.get_entity(dep)
            assert dep_entity.is_enabled()
```

**Pattern: Conditional Entity Handling**

```python
@pytest.mark.integration
def test_conditional_entity(all_entity_names):
    """Test entity included only when condition met."""
    registry = EntityRegistry()

    # Test without condition
    factory = StrategyFactory(registry)
    strategies_without = factory.create_strategies()
    names_without = [s.get_entity_name() for s in strategies_without]

    # Test with condition
    strategies_with = factory.create_strategies(git_service=Mock())
    names_with = [s.get_entity_name() for s in strategies_with]

    # Verify all entities included when condition met
    assert set(names_with) == set(all_entity_names)
```

**When NOT to Use Entity Discovery:**

Entity discovery fixtures are for testing **system-wide entity behavior**. Don't use them when:

- Testing a specific entity (just test that entity directly)
- Entity names are part of the test's explicit contract
- Testing exact dependency relationships (hardcode those - they're requirements)

**Example of Appropriate Hardcoding:**

```python
def test_issues_depend_on_milestones():
    """Test explicit dependency contract."""
    registry = EntityRegistry()
    issues_entity = registry.get_entity("issues")

    # This is a requirement, not a discovery - hardcode it
    assert "milestones" in issues_entity.get_dependencies()
```
```

### Documentation Update Rationale

**Why These Sections:**

1. **test-infrastructure.md** - Comprehensive reference for the fixture system
   - Documents all 5 fixtures with their purposes
   - Provides complete usage examples
   - Shows anti-patterns to avoid
   - Integrated with existing fixture documentation

2. **writing-tests.md** - Practical guidance for test authors
   - Shows common patterns for new tests
   - Explains when to use vs. not use fixtures
   - Provides copy-paste examples
   - Guides decision-making

**What's NOT Updated:**

- `docs/testing/README.md` - Hub file, no detail changes needed
- `docs/testing/getting-started.md` - Introductory guide, too advanced
- `docs/testing/specialized-testing.md` - Focuses on container/error/performance
- `docs/testing/reference/*` - Reference docs, not changed by new fixtures

### Documentation Benefits

1. **Discoverability** - Developers find fixtures through normal documentation flow
2. **Clear usage** - Examples show correct patterns
3. **Anti-patterns** - Explicitly show what NOT to do
4. **Integration** - Fits naturally into existing documentation structure
5. **Maintenance** - Updates concentrated in 2 high-traffic files

## Conclusion

This design achieves zero-maintenance test infrastructure through Pure Discovery. The EntityRegistry becomes the single source of truth for entity information, and all tests automatically adapt to system changes.

**Implementation Effort**: 4-6 hours (including documentation)
**Maintenance Savings**: 5+ file updates per entity → 0 updates
**Risk Level**: Low (leverages existing production code paths)

The design is ready for immediate implementation as part of Phase 1 Quick Wins in the architectural improvements roadmap.

---

## Appendix: Complete Fixture API

### entity_registry
**Type**: pytest.fixture
**Scope**: function
**Returns**: EntityRegistry
**Use**: When test needs full registry access

### all_entity_names
**Type**: pytest.fixture
**Scope**: function
**Returns**: List[str]
**Use**: When test needs complete entity list

### enabled_entity_names
**Type**: pytest.fixture
**Scope**: function
**Returns**: List[str]
**Use**: When test validates default-enabled entities

### entity_names_by_dependency_order
**Type**: pytest.fixture
**Scope**: function
**Returns**: List[str] (sorted)
**Use**: When test validates execution order

### independent_entity_names
**Type**: pytest.fixture
**Scope**: function
**Returns**: List[str]
**Use**: When test focuses on root entities

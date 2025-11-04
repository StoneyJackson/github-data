# Dynamic Entity Count Validation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement dynamic entity discovery fixtures to eliminate hardcoded entity counts in tests

**Architecture:** Create pytest fixtures that use EntityRegistry auto-discovery to provide entity information dynamically. Update 7 test functions across 3 test files to use discovery instead of hardcoded counts. Add documentation for the new fixture system.

**Tech Stack:** Python 3, pytest fixtures, EntityRegistry auto-discovery

---

## Task 1: Create Entity Discovery Fixtures

**Files:**
- Create: `tests/shared/fixtures/entity_fixtures.py`
- Test: `tests/unit/shared/fixtures/test_entity_fixtures.py` (new)

**Step 1: Write the failing test for entity_registry fixture**

Create `tests/unit/shared/fixtures/test_entity_fixtures.py`:

```python
"""Tests for entity discovery fixtures."""

import pytest
from github_data.entities.registry import EntityRegistry


def test_entity_registry_fixture_provides_fresh_instance(entity_registry):
    """Test entity_registry fixture provides a fresh EntityRegistry."""
    assert isinstance(entity_registry, EntityRegistry)
    assert entity_registry is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/shared/fixtures/test_entity_fixtures.py::test_entity_registry_fixture_provides_fresh_instance -v`
Expected: FAIL with "fixture 'entity_registry' not found"

**Step 3: Create entity_fixtures.py with entity_registry fixture**

Create `tests/shared/fixtures/entity_fixtures.py`:

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
```

**Step 4: Update conftest.py to load entity_fixtures plugin**

Edit `tests/conftest.py` to add to pytest_plugins list:

```python
pytest_plugins = [
    # ... existing plugins ...
    # Entity Discovery Fixtures
    "tests.shared.fixtures.entity_fixtures",
]
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/unit/shared/fixtures/test_entity_fixtures.py::test_entity_registry_fixture_provides_fresh_instance -v`
Expected: PASS

**Step 6: Commit entity_registry fixture**

```bash
git add tests/shared/fixtures/entity_fixtures.py tests/unit/shared/fixtures/test_entity_fixtures.py tests/conftest.py
git commit -s -m "feat: add entity_registry fixture for dynamic entity discovery"
```

---

## Task 2: Add all_entity_names Fixture

**Files:**
- Modify: `tests/shared/fixtures/entity_fixtures.py`
- Modify: `tests/unit/shared/fixtures/test_entity_fixtures.py`

**Step 1: Write the failing test for all_entity_names fixture**

Add to `tests/unit/shared/fixtures/test_entity_fixtures.py`:

```python
def test_all_entity_names_fixture_returns_list(all_entity_names):
    """Test all_entity_names fixture returns list of entity names."""
    assert isinstance(all_entity_names, list)
    assert len(all_entity_names) > 0
    assert all(isinstance(name, str) for name in all_entity_names)


def test_all_entity_names_includes_known_entities(all_entity_names):
    """Test all_entity_names includes expected entities."""
    # Check for a few known entities that should always exist
    assert "labels" in all_entity_names
    assert "issues" in all_entity_names
    assert "milestones" in all_entity_names
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/shared/fixtures/test_entity_fixtures.py::test_all_entity_names_fixture_returns_list -v`
Expected: FAIL with "fixture 'all_entity_names' not found"

**Step 3: Add all_entity_names fixture**

Add to `tests/shared/fixtures/entity_fixtures.py`:

```python
@pytest.fixture
def all_entity_names(entity_registry):
    """Get all registered entity names dynamically.

    Uses EntityRegistry auto-discovery to find all entities.
    No manual updates needed when adding new entities.

    Returns:
        List[str]: All discovered entity names
    """
    return entity_registry.get_all_entity_names()
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/shared/fixtures/test_entity_fixtures.py -v`
Expected: All tests PASS

**Step 5: Commit all_entity_names fixture**

```bash
git add tests/shared/fixtures/entity_fixtures.py tests/unit/shared/fixtures/test_entity_fixtures.py
git commit -s -m "feat: add all_entity_names fixture for dynamic entity list"
```

---

## Task 3: Add enabled_entity_names Fixture

**Files:**
- Modify: `tests/shared/fixtures/entity_fixtures.py`
- Modify: `tests/unit/shared/fixtures/test_entity_fixtures.py`

**Step 1: Write the failing test for enabled_entity_names fixture**

Add to `tests/unit/shared/fixtures/test_entity_fixtures.py`:

```python
def test_enabled_entity_names_returns_enabled_only(enabled_entity_names, entity_registry):
    """Test enabled_entity_names returns only enabled entities."""
    assert isinstance(enabled_entity_names, list)

    # Verify all returned entities are actually enabled
    for name in enabled_entity_names:
        entity = entity_registry.get_entity(name)
        assert entity.is_enabled(), f"{name} should be enabled"


def test_enabled_entity_names_subset_of_all(enabled_entity_names, all_entity_names):
    """Test enabled entities are subset of all entities."""
    assert set(enabled_entity_names).issubset(set(all_entity_names))
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/shared/fixtures/test_entity_fixtures.py::test_enabled_entity_names_returns_enabled_only -v`
Expected: FAIL with "fixture 'enabled_entity_names' not found"

**Step 3: Add enabled_entity_names fixture**

Add to `tests/shared/fixtures/entity_fixtures.py`:

```python
@pytest.fixture
def enabled_entity_names(entity_registry):
    """Get all enabled entity names by default configuration.

    Returns:
        List[str]: Names of entities enabled by default
    """
    enabled = entity_registry.get_enabled_entities()
    return [e.config.name for e in enabled]
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/shared/fixtures/test_entity_fixtures.py -v`
Expected: All tests PASS

**Step 5: Commit enabled_entity_names fixture**

```bash
git add tests/shared/fixtures/entity_fixtures.py tests/unit/shared/fixtures/test_entity_fixtures.py
git commit -s -m "feat: add enabled_entity_names fixture for default-enabled entities"
```

---

## Task 4: Add entity_names_by_dependency_order and independent_entity_names Fixtures

**Files:**
- Modify: `tests/shared/fixtures/entity_fixtures.py`
- Modify: `tests/unit/shared/fixtures/test_entity_fixtures.py`

**Step 1: Write the failing tests**

Add to `tests/unit/shared/fixtures/test_entity_fixtures.py`:

```python
def test_entity_names_by_dependency_order_respects_dependencies(
    entity_names_by_dependency_order, entity_registry
):
    """Test dependency order fixture returns valid topological sort."""
    names = entity_names_by_dependency_order

    # Create position lookup
    positions = {name: idx for idx, name in enumerate(names)}

    # Verify each entity comes after its dependencies
    for name in names:
        entity = entity_registry.get_entity(name)
        for dep in entity.get_dependencies():
            assert positions[dep] < positions[name], \
                f"{name} depends on {dep}, but {dep} comes after {name}"


def test_independent_entity_names_have_no_dependencies(
    independent_entity_names, entity_registry
):
    """Test independent entities have empty dependency lists."""
    for name in independent_entity_names:
        entity = entity_registry.get_entity(name)
        deps = entity.get_dependencies()
        assert len(deps) == 0, f"{name} should have no dependencies, has {deps}"
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/shared/fixtures/test_entity_fixtures.py::test_entity_names_by_dependency_order_respects_dependencies -v`
Expected: FAIL with "fixture 'entity_names_by_dependency_order' not found"

**Step 3: Add both fixtures**

Add to `tests/shared/fixtures/entity_fixtures.py`:

```python
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

**Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/shared/fixtures/test_entity_fixtures.py -v`
Expected: All tests PASS

**Step 5: Commit remaining fixtures**

```bash
git add tests/shared/fixtures/entity_fixtures.py tests/unit/shared/fixtures/test_entity_fixtures.py
git commit -s -m "feat: add dependency order and independent entity fixtures"
```

---

## Task 5: Update test_strategy_factory_integration.py - Part 1

**Files:**
- Modify: `tests/integration/operations/test_strategy_factory_integration.py:42-57`

**Step 1: Identify current test implementation**

Read the current test:
```bash
grep -A 20 "def test_create_save_strategies_all_entities" tests/integration/operations/test_strategy_factory_integration.py
```

**Step 2: Update test_create_save_strategies_all_entities**

Replace the test in `tests/integration/operations/test_strategy_factory_integration.py`:

```python
@pytest.mark.integration
@pytest.mark.medium
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

**Step 3: Run test to verify it passes**

Run: `pytest tests/integration/operations/test_strategy_factory_integration.py::test_create_save_strategies_all_entities -v`
Expected: PASS

**Step 4: Commit the change**

```bash
git add tests/integration/operations/test_strategy_factory_integration.py
git commit -s -m "refactor: use all_entity_names fixture in test_create_save_strategies_all_entities"
```

---

## Task 6: Update test_strategy_factory_integration.py - Part 2

**Files:**
- Modify: `tests/integration/operations/test_strategy_factory_integration.py` (test_create_save_strategies_with_git_repository)

**Step 1: Update test_create_save_strategies_with_git_repository**

Replace the test in `tests/integration/operations/test_strategy_factory_integration.py`:

```python
@pytest.mark.integration
@pytest.mark.medium
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

**Step 2: Run test to verify it passes**

Run: `pytest tests/integration/operations/test_strategy_factory_integration.py::test_create_save_strategies_with_git_repository -v`
Expected: PASS

**Step 3: Commit the change**

```bash
git add tests/integration/operations/test_strategy_factory_integration.py
git commit -s -m "refactor: use all_entity_names in test_create_save_strategies_with_git_repository"
```

---

## Task 7: Update test_strategy_factory_integration.py - Part 3

**Files:**
- Modify: `tests/integration/operations/test_strategy_factory_integration.py` (test_create_restore_strategies_all_entities)

**Step 1: Update test_create_restore_strategies_all_entities**

Replace the test in `tests/integration/operations/test_strategy_factory_integration.py`:

```python
@pytest.mark.integration
@pytest.mark.medium
def test_create_restore_strategies_all_entities(all_entity_names):
    """Test creating restore strategies for all enabled entities except git_repository."""
    registry = EntityRegistry()
    registry.get_entity("git_repository").enabled = False
    factory = StrategyFactory(registry)
    strategies = factory.create_restore_strategies()

    strategy_names = [s.get_entity_name() for s in strategies]

    # Verify we got all enabled entities
    expected = set(all_entity_names) - {"git_repository"}
    assert set(strategy_names) == expected
```

**Step 2: Run test to verify it passes**

Run: `pytest tests/integration/operations/test_strategy_factory_integration.py::test_create_restore_strategies_all_entities -v`
Expected: PASS

**Step 3: Run all tests in file to verify no regressions**

Run: `pytest tests/integration/operations/test_strategy_factory_integration.py -v`
Expected: All tests PASS

**Step 4: Commit the change**

```bash
git add tests/integration/operations/test_strategy_factory_integration.py
git commit -s -m "refactor: use all_entity_names in test_create_restore_strategies_all_entities"
```

---

## Task 8: Update test_strategy_factory_registry.py - Part 1

**Files:**
- Modify: `tests/unit/operations/test_strategy_factory_registry.py` (test_strategy_factory_creates_all_10_entities)

**Step 1: Locate and update test_strategy_factory_creates_all_10_entities**

Replace and rename the test in `tests/unit/operations/test_strategy_factory_registry.py`:

```python
@pytest.mark.unit
@pytest.mark.fast
def test_strategy_factory_creates_all_entities(all_entity_names):
    """Test StrategyFactory creates strategies for all discovered entities."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry)
    mock_git_service = Mock()

    strategies = factory.create_save_strategies(git_service=mock_git_service)
    strategy_names = [s.get_entity_name() for s in strategies]

    # Verify all discovered entities have strategies
    assert set(strategy_names) == set(all_entity_names)
```

**Step 2: Run test to verify it passes**

Run: `pytest tests/unit/operations/test_strategy_factory_registry.py::test_strategy_factory_creates_all_entities -v`
Expected: PASS

**Step 3: Commit the change**

```bash
git add tests/unit/operations/test_strategy_factory_registry.py
git commit -s -m "refactor: rename and use all_entity_names in test_strategy_factory_creates_all_entities"
```

---

## Task 9: Update test_strategy_factory_registry.py - Part 2

**Files:**
- Modify: `tests/unit/operations/test_strategy_factory_registry.py` (test_strategy_factory_create_save_strategies_from_registry)

**Step 1: Locate current test**

Find test_strategy_factory_create_save_strategies_from_registry and examine its structure.

**Step 2: Update test to use discovery fixture**

Replace the test in `tests/unit/operations/test_strategy_factory_registry.py`:

```python
@pytest.mark.unit
@pytest.mark.fast
def test_strategy_factory_create_save_strategies_from_registry(all_entity_names):
    """Test save strategies created from registry match all entities."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry)
    mock_git_service = Mock()

    strategies = factory.create_save_strategies(git_service=mock_git_service)
    strategy_names = [s.get_entity_name() for s in strategies]

    # Verify strategies for all entities
    assert set(strategy_names) == set(all_entity_names)
```

**Step 3: Run test to verify it passes**

Run: `pytest tests/unit/operations/test_strategy_factory_registry.py::test_strategy_factory_create_save_strategies_from_registry -v`
Expected: PASS

**Step 4: Run all tests in file to verify no regressions**

Run: `pytest tests/unit/operations/test_strategy_factory_registry.py -v`
Expected: All tests PASS

**Step 5: Commit the change**

```bash
git add tests/unit/operations/test_strategy_factory_registry.py
git commit -s -m "refactor: use all_entity_names in test_strategy_factory_create_save_strategies_from_registry"
```

---

## Task 10: Update test_complete_dependency_graph.py - Part 1

**Files:**
- Modify: `tests/integration/test_complete_dependency_graph.py` (test_no_circular_dependencies)

**Step 1: Locate and update test_no_circular_dependencies**

Find the test and update to use enabled_entity_names fixture:

```python
@pytest.mark.integration
@pytest.mark.fast
def test_no_circular_dependencies(enabled_entity_names):
    """Test that there are no circular dependencies in the entity graph."""
    registry = EntityRegistry()
    enabled = registry.get_enabled_entities()
    enabled_names = [e.config.name for e in enabled]

    # Verify we have all expected enabled entities
    assert set(enabled_names) == set(enabled_entity_names)

    # Build dependency graph
    graph = {}
    for entity in enabled:
        graph[entity.config.name] = entity.get_dependencies()

    # Check for cycles using DFS
    def has_cycle(node, visited, rec_stack):
        visited.add(node)
        rec_stack.add(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                return True

        rec_stack.remove(node)
        return False

    visited = set()
    for node in graph:
        if node not in visited:
            assert not has_cycle(node, visited, set()), \
                f"Circular dependency detected involving {node}"
```

**Step 2: Run test to verify it passes**

Run: `pytest tests/integration/test_complete_dependency_graph.py::test_no_circular_dependencies -v`
Expected: PASS

**Step 3: Commit the change**

```bash
git add tests/integration/test_complete_dependency_graph.py
git commit -s -m "refactor: use enabled_entity_names in test_no_circular_dependencies"
```

---

## Task 11: Update test_complete_dependency_graph.py - Part 2

**Files:**
- Modify: `tests/integration/test_complete_dependency_graph.py` (test_complete_topological_sort)

**Step 1: Update test_complete_topological_sort**

Replace the test in `tests/integration/test_complete_dependency_graph.py`:

```python
@pytest.mark.integration
@pytest.mark.fast
def test_complete_topological_sort(enabled_entity_names):
    """Test topological sort produces valid execution order."""
    registry = EntityRegistry()
    enabled = registry.get_enabled_entities()
    enabled_names = [e.config.name for e in enabled]

    # Verify count matches discovery
    assert set(enabled_names) == set(enabled_entity_names)

    def idx(name):
        return enabled_names.index(name)

    # Verify dependency order constraints (explicit contracts)
    assert idx("milestones") < idx("issues")
    assert idx("milestones") < idx("pull_requests")
    assert idx("issues") < idx("comments")
    assert idx("issues") < idx("sub_issues")
    assert idx("pull_requests") < idx("pr_reviews")
    assert idx("pull_requests") < idx("pr_comments")
    assert idx("pr_reviews") < idx("pr_review_comments")
```

**Step 2: Run test to verify it passes**

Run: `pytest tests/integration/test_complete_dependency_graph.py::test_complete_topological_sort -v`
Expected: PASS

**Step 3: Run all tests in file to verify no regressions**

Run: `pytest tests/integration/test_complete_dependency_graph.py -v`
Expected: All tests PASS

**Step 4: Commit the change**

```bash
git add tests/integration/test_complete_dependency_graph.py
git commit -s -m "refactor: use enabled_entity_names in test_complete_topological_sort"
```

---

## Task 12: Run Full Test Suite

**Files:** None (verification only)

**Step 1: Run make test-fast to verify all changes**

Run: `make test-fast`
Expected: All tests PASS with no failures

**Step 2: Check for any test warnings or issues**

Review output for:
- Deprecation warnings
- Fixture not found errors
- Import errors
- Any other test infrastructure issues

**Step 3: If any issues found, fix them before proceeding**

Address any problems discovered in the test run.

---

## Task 13: Update Documentation - test-infrastructure.md

**Files:**
- Modify: `docs/testing/test-infrastructure.md` (after line ~480)

**Step 1: Locate the Shared Fixture System section**

Find the appropriate location to add the new section (after existing fixture documentation).

**Step 2: Add Entity Discovery Fixtures section**

Add this section to `docs/testing/test-infrastructure.md`:

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

**Step 3: Run doc linter if available**

```bash
# Check if there's a doc linter
make lint-docs || echo "No doc linter configured"
```

**Step 4: Commit documentation update**

```bash
git add docs/testing/test-infrastructure.md
git commit -s -m "docs: add entity discovery fixtures to test infrastructure guide"
```

---

## Task 14: Update Documentation - writing-tests.md

**Files:**
- Modify: `docs/testing/writing-tests.md` (after line ~152)

**Step 1: Locate the Basic Test Structure section**

Find the appropriate location after basic test examples.

**Step 2: Add Testing with Entity Discovery section**

Add this section to `docs/testing/writing-tests.md`:

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

**Step 3: Run doc linter if available**

```bash
# Check if there's a doc linter
make lint-docs || echo "No doc linter configured"
```

**Step 4: Commit documentation update**

```bash
git add docs/testing/writing-tests.md
git commit -s -m "docs: add entity discovery patterns to writing tests guide"
```

---

## Task 15: Final Verification and Validation

**Files:** None (verification only)

**Step 1: Run complete test suite**

Run: `make test-fast`
Expected: All tests PASS

**Step 2: Run full quality checks**

Run: `make check`
Expected: No linting, formatting, or type errors

**Step 3: Verify commit messages follow conventions**

```bash
git log --oneline -15
```

Expected: All commits follow Conventional Commits format with sign-off

**Step 4: Create summary of changes**

List all modified files and test improvements:
```bash
git diff --stat main...HEAD
```

**Step 5: Verify design goals achieved**

Check that:
- All 7 tests updated to use discovery fixtures
- No hardcoded entity counts remain in modified tests
- Documentation updated
- All tests pass

---

## Validation Test: Add Dummy Entity

**Files:** None (validation only)

**Purpose:** Verify that adding a new entity requires zero test updates

**Step 1: Note current test count**

```bash
pytest tests/integration/operations/test_strategy_factory_integration.py -v --tb=no | grep -c PASSED
```

**Step 2: Temporarily add a dummy entity**

This is just for validation - will be removed immediately:

Create minimal entity at `src/github_data/entities/dummy_entity.py`:
```python
"""Dummy entity for validation testing only."""
from github_data.entities.base_entity import BaseEntity


class DummyEntity(BaseEntity):
    """Dummy entity to validate zero-maintenance fixtures."""

    def get_dependencies(self):
        return []
```

**Step 3: Run tests without modifications**

Run: `make test-fast`
Expected: All tests PASS without ANY modifications

**Step 4: Remove dummy entity**

```bash
rm src/github_data/entities/dummy_entity.py
```

**Step 5: Verify tests still pass**

Run: `make test-fast`
Expected: All tests PASS

**Step 6: Confirm zero-maintenance achieved**

Document that adding/removing entity required zero test changes.

---

## Summary

**Files Created:**
- `tests/shared/fixtures/entity_fixtures.py` - 5 discovery fixtures
- `tests/unit/shared/fixtures/test_entity_fixtures.py` - Fixture validation tests

**Files Modified:**
- `tests/conftest.py` - Added entity_fixtures plugin
- `tests/integration/operations/test_strategy_factory_integration.py` - 3 tests updated
- `tests/unit/operations/test_strategy_factory_registry.py` - 2 tests updated (1 renamed)
- `tests/integration/test_complete_dependency_graph.py` - 2 tests updated
- `docs/testing/test-infrastructure.md` - Added entity discovery section
- `docs/testing/writing-tests.md` - Added testing patterns

**Commits:** 15 commits (one per task)

**Testing Strategy:**
- TDD approach - write failing tests first
- Run tests after each change
- Verify no regressions with `make test-fast`
- Final validation with dummy entity test

**Success Metrics:**
- Zero test updates needed when adding entities
- All 7 target tests use discovery fixtures
- Complete documentation coverage
- 100% test pass rate

---

## Remember

- Use `make test-fast` for quick validation (excludes slow container tests)
- Follow TDD: failing test → minimal implementation → passing test → commit
- All commits must be signed off (`git commit -s`)
- Run `make check` before final completion
- Verify with dummy entity test to confirm zero-maintenance


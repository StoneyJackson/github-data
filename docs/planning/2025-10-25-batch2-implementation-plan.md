# Phase 3 Batch 2: Issues Domain Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate issues, comments, and sub_issues entities with dependency declarations to EntityRegistry system.

**Architecture:** Create entity_config.py with dependencies for each entity, move strategies, update StrategyFactory to handle dependencies, validate dependency enforcement.

**Tech Stack:** Python 3, pytest, EntityRegistry with dependency management, PDM

---

## Prerequisites

- Batch 1 must be complete (labels, milestones, git_repository migrated)
- StrategyFactory supports EntityRegistry
- EntityRegistry dependency validation is functional

---

## Task 1: Migrate issues entity

**Files:**
- Create: `src/entities/issues/entity_config.py`
- Move: `src/operations/save/strategies/issues_strategy.py` → `src/entities/issues/save_strategy.py`
- Move: `src/operations/restore/strategies/issues_strategy.py` → `src/entities/issues/restore_strategy.py`
- Create: `tests/unit/entities/issues/test_entity_config.py`

### Step 1: Write failing test for issues entity with dependencies

```python
# tests/unit/entities/issues/test_entity_config.py
"""Tests for issues entity configuration."""

import pytest
from src.entities.registry import EntityRegistry
from typing import Union, Set


@pytest.mark.unit
def test_issues_entity_discovered():
    """Test that issues entity is discovered by registry."""
    registry = EntityRegistry()
    entity = registry.get_entity("issues")

    assert entity.config.name == "issues"
    assert entity.config.env_var == "INCLUDE_ISSUES"
    assert entity.config.default_value is True
    assert entity.config.value_type == Union[bool, Set[int]]
    assert entity.config.dependencies == ["milestones"]
    assert entity.config.description != ""


@pytest.mark.unit
def test_issues_depends_on_milestones():
    """Test that issues entity depends on milestones."""
    registry = EntityRegistry()
    entity = registry.get_entity("issues")

    assert "milestones" in entity.get_dependencies()
```

### Step 2: Run test to verify it fails

**Command:**
```bash
pdm run pytest tests/unit/entities/issues/test_entity_config.py -v
```

**Expected:** FAILED - Unknown entity: issues

### Step 3: Create issues entity_config.py

```python
# src/entities/issues/entity_config.py
"""Issues entity configuration for EntityRegistry."""

from typing import Union, Set


class IssuesEntityConfig:
    """Configuration for issues entity.

    Issues depend on milestones (can reference milestones).
    Supports selective issue numbers via Set[int].
    """

    name = "issues"
    env_var = "INCLUDE_ISSUES"
    default_value = True
    value_type = Union[bool, Set[int]]
    dependencies = ["milestones"]  # Issues can reference milestones
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Repository issues with milestone references"
```

### Step 4: Run test to verify entity config

**Command:**
```bash
pdm run pytest tests/unit/entities/issues/test_entity_config.py::test_issues_entity_discovered -v
```

**Expected:** PASSED

### Step 5: Move issues strategies and update imports

**Commands:**
```bash
mv src/operations/save/strategies/issues_strategy.py src/entities/issues/save_strategy.py
mv src/operations/restore/strategies/issues_strategy.py src/entities/issues/restore_strategy.py
```

Update imports in both files to use:
```python
from src.operations.save.strategy import SaveEntityStrategy  # save_strategy.py
from src.operations.restore.strategy import RestoreEntityStrategy  # restore_strategy.py
from src.entities.issues.models import Issue
```

### Step 6: Test dependency validation

Add test:

```python
@pytest.mark.unit
def test_issues_disabled_when_milestones_disabled():
    """Test that issues auto-disable when milestones disabled (non-strict mode)."""
    import os

    # Set environment to disable milestones
    os.environ["INCLUDE_MILESTONES"] = "false"
    os.environ["INCLUDE_ISSUES"] = "true"

    registry = EntityRegistry.from_environment(strict=False)
    issues_entity = registry.get_entity("issues")

    # Issues should be auto-disabled with warning
    assert issues_entity.is_enabled() is False

    # Cleanup
    del os.environ["INCLUDE_MILESTONES"]
    del os.environ["INCLUDE_ISSUES"]
```

### Step 7: Run all issues tests

**Command:**
```bash
pdm run pytest tests/unit/entities/issues/ -v
```

**Expected:** All PASSED

### Step 8: Commit issues migration

**Command:**
```bash
git add src/entities/issues/entity_config.py src/entities/issues/save_strategy.py src/entities/issues/restore_strategy.py tests/unit/entities/issues/test_entity_config.py
git commit -s -m "feat: migrate issues entity with milestone dependency

Add IssuesEntityConfig with milestone dependency and move strategies.
Supports Union[bool, Set[int]] for selective issue numbers.

Part of Phase 3 Batch 2 migration.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 2: Migrate comments entity

**Files:**
- Create: `src/entities/comments/entity_config.py`
- Move strategies to `src/entities/comments/`
- Create: `tests/unit/entities/comments/test_entity_config.py`

### Step 1: Write failing test

```python
# tests/unit/entities/comments/test_entity_config.py
"""Tests for comments entity configuration."""

import pytest
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_comments_entity_discovered():
    """Test that comments entity is discovered by registry."""
    registry = EntityRegistry()
    entity = registry.get_entity("comments")

    assert entity.config.name == "comments"
    assert entity.config.env_var == "INCLUDE_ISSUE_COMMENTS"
    assert entity.config.default_value is True
    assert entity.config.dependencies == ["issues"]


@pytest.mark.unit
def test_comments_depends_on_issues():
    """Test that comments depend on issues."""
    registry = EntityRegistry()
    entity = registry.get_entity("comments")

    assert "issues" in entity.get_dependencies()
```

### Step 2: Run test to verify it fails

**Command:**
```bash
pdm run pytest tests/unit/entities/comments/test_entity_config.py -v
```

**Expected:** FAILED - Unknown entity: comments

### Step 3: Create comments entity_config.py

```python
# src/entities/comments/entity_config.py
"""Comments entity configuration for EntityRegistry."""


class CommentsEntityConfig:
    """Configuration for comments entity.

    Comments depend on issues (belong to issues).
    """

    name = "comments"
    env_var = "INCLUDE_ISSUE_COMMENTS"
    default_value = True
    value_type = bool
    dependencies = ["issues"]  # Comments belong to issues
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Issue comments and discussions"
```

### Step 4: Run test to verify

**Command:**
```bash
pdm run pytest tests/unit/entities/comments/test_entity_config.py::test_comments_entity_discovered -v
```

**Expected:** PASSED

### Step 5: Move strategies and update imports

**Commands:**
```bash
mv src/operations/save/strategies/comments_strategy.py src/entities/comments/save_strategy.py
mv src/operations/restore/strategies/comments_strategy.py src/entities/comments/restore_strategy.py
```

Update imports as needed.

### Step 6: Test dependency chain validation

```python
@pytest.mark.unit
def test_comments_disabled_when_issues_disabled():
    """Test comments auto-disable when issues disabled."""
    import os

    os.environ["INCLUDE_ISSUES"] = "false"
    os.environ["INCLUDE_ISSUE_COMMENTS"] = "true"

    registry = EntityRegistry.from_environment(strict=False)
    comments = registry.get_entity("comments")

    assert comments.is_enabled() is False

    del os.environ["INCLUDE_ISSUES"]
    del os.environ["INCLUDE_ISSUE_COMMENTS"]
```

### Step 7: Run all comments tests

**Command:**
```bash
pdm run pytest tests/unit/entities/comments/ -v
```

**Expected:** All PASSED

### Step 8: Commit comments migration

**Command:**
```bash
git add src/entities/comments/ tests/unit/entities/comments/
git commit -s -m "feat: migrate comments entity with issues dependency

Add CommentsEntityConfig with issues dependency and move strategies.

Part of Phase 3 Batch 2 migration.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 3: Migrate sub_issues entity

**Files:**
- Create: `src/entities/sub_issues/entity_config.py`
- Move strategies to `src/entities/sub_issues/`
- Create: `tests/unit/entities/sub_issues/test_entity_config.py`

### Step 1: Write failing test

```python
# tests/unit/entities/sub_issues/test_entity_config.py
"""Tests for sub_issues entity configuration."""

import pytest
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_sub_issues_entity_discovered():
    """Test that sub_issues entity is discovered."""
    registry = EntityRegistry()
    entity = registry.get_entity("sub_issues")

    assert entity.config.name == "sub_issues"
    assert entity.config.env_var == "INCLUDE_SUB_ISSUES"
    assert entity.config.dependencies == ["issues"]


@pytest.mark.unit
def test_sub_issues_depends_on_issues():
    """Test that sub_issues depend on issues."""
    registry = EntityRegistry()
    entity = registry.get_entity("sub_issues")

    assert "issues" in entity.get_dependencies()
```

### Step 2: Run test to verify failure

**Command:**
```bash
pdm run pytest tests/unit/entities/sub_issues/test_entity_config.py -v
```

**Expected:** FAILED - Unknown entity: sub_issues

### Step 3: Create sub_issues entity_config.py

```python
# src/entities/sub_issues/entity_config.py
"""Sub-issues entity configuration for EntityRegistry."""


class SubIssuesEntityConfig:
    """Configuration for sub_issues entity.

    Sub-issues depend on issues (hierarchical relationships).
    """

    name = "sub_issues"
    env_var = "INCLUDE_SUB_ISSUES"
    default_value = True
    value_type = bool
    dependencies = ["issues"]  # Sub-issues are hierarchical issues
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Hierarchical sub-issue relationships"
```

### Step 4: Verify test passes

**Command:**
```bash
pdm run pytest tests/unit/entities/sub_issues/test_entity_config.py::test_sub_issues_entity_discovered -v
```

**Expected:** PASSED

### Step 5: Move strategies and update imports

**Commands:**
```bash
mv src/operations/save/strategies/sub_issues_strategy.py src/entities/sub_issues/save_strategy.py
mv src/operations/restore/strategies/sub_issues_strategy.py src/entities/sub_issues/restore_strategy.py
```

### Step 6: Run all sub_issues tests

**Command:**
```bash
pdm run pytest tests/unit/entities/sub_issues/ -v
```

**Expected:** All PASSED

### Step 7: Commit sub_issues migration

**Command:**
```bash
git add src/entities/sub_issues/ tests/unit/entities/sub_issues/
git commit -s -m "feat: migrate sub_issues entity with issues dependency

Add SubIssuesEntityConfig with issues dependency and move strategies.

Part of Phase 3 Batch 2 migration.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 4: Verify Batch 2 dependency graph

**Files:**
- Create: `tests/integration/test_batch2_dependencies.py`

### Step 1: Write dependency graph integration test

```python
# tests/integration/test_batch2_dependencies.py
"""Integration tests for Batch 2 dependency validation."""

import pytest
import os
from src.entities.registry import EntityRegistry


@pytest.mark.integration
def test_batch2_entities_discovered():
    """Test all Batch 2 entities discovered."""
    registry = EntityRegistry()
    names = registry.get_all_entity_names()

    assert "issues" in names
    assert "comments" in names
    assert "sub_issues" in names


@pytest.mark.integration
def test_batch2_dependency_graph():
    """Test Batch 2 dependency relationships."""
    registry = EntityRegistry()

    issues = registry.get_entity("issues")
    comments = registry.get_entity("comments")
    sub_issues = registry.get_entity("sub_issues")

    # Verify dependencies
    assert issues.get_dependencies() == ["milestones"]
    assert comments.get_dependencies() == ["issues"]
    assert sub_issues.get_dependencies() == ["issues"]


@pytest.mark.integration
def test_batch2_topological_sort():
    """Test Batch 1 + 2 entities sort correctly."""
    registry = EntityRegistry()
    enabled = registry.get_enabled_entities()
    enabled_names = [e.config.name for e in enabled]

    # Verify dependency order
    milestone_idx = enabled_names.index("milestones")
    issues_idx = enabled_names.index("issues")
    comments_idx = enabled_names.index("comments")
    sub_issues_idx = enabled_names.index("sub_issues")

    # Milestones must come before issues
    assert milestone_idx < issues_idx
    # Issues must come before comments and sub_issues
    assert issues_idx < comments_idx
    assert issues_idx < sub_issues_idx


@pytest.mark.integration
def test_batch2_auto_disable_on_missing_dependency():
    """Test auto-disable when dependency is disabled."""
    os.environ["INCLUDE_ISSUES"] = "false"
    os.environ["INCLUDE_ISSUE_COMMENTS"] = "true"
    os.environ["INCLUDE_SUB_ISSUES"] = "true"

    registry = EntityRegistry.from_environment(strict=False)
    enabled_names = [e.config.name for e in registry.get_enabled_entities()]

    # Comments and sub_issues should be auto-disabled
    assert "comments" not in enabled_names
    assert "sub_issues" not in enabled_names

    # Cleanup
    del os.environ["INCLUDE_ISSUES"]
    del os.environ["INCLUDE_ISSUE_COMMENTS"]
    del os.environ["INCLUDE_SUB_ISSUES"]


@pytest.mark.integration
def test_batch2_strict_mode_raises_on_violation():
    """Test strict mode raises error on dependency violation."""
    os.environ["INCLUDE_ISSUES"] = "false"
    os.environ["INCLUDE_ISSUE_COMMENTS"] = "true"

    with pytest.raises(ValueError, match="requires.*INCLUDE_ISSUES"):
        EntityRegistry.from_environment(strict=True)

    # Cleanup
    del os.environ["INCLUDE_ISSUES"]
    del os.environ["INCLUDE_ISSUE_COMMENTS"]
```

### Step 2: Run integration tests

**Command:**
```bash
pdm run pytest tests/integration/test_batch2_dependencies.py -v
```

**Expected:** All PASSED

### Step 3: Run full fast test suite

**Command:**
```bash
make test-fast
```

**Expected:** All unit and integration tests pass

### Step 4: Commit integration tests

**Command:**
```bash
git add tests/integration/test_batch2_dependencies.py
git commit -s -m "test: add Batch 2 dependency validation tests

Add comprehensive dependency graph tests for Batch 2 including:
- Entity discovery
- Dependency relationships
- Topological sort validation
- Auto-disable behavior
- Strict mode enforcement

All tests passing.

Part of Phase 3 Batch 2 migration.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 5: Update StrategyFactory for complete Batch 1+2 support

### Step 1: Test StrategyFactory loads all Batch 1+2 entities

```python
# tests/unit/operations/test_strategy_factory_registry.py

@pytest.mark.unit
def test_strategy_factory_loads_all_batch1_and_batch2():
    """Test StrategyFactory loads strategies for all Batch 1+2 entities."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry, config=None)

    batch1_and_2 = ["labels", "milestones", "git_repository", "issues", "comments", "sub_issues"]

    for entity_name in batch1_and_2:
        strategy = factory.load_save_strategy(entity_name)
        assert strategy is not None, f"Failed to load {entity_name}"
        assert strategy.get_entity_name() == entity_name
```

### Step 2: Run test

**Command:**
```bash
pdm run pytest tests/unit/operations/test_strategy_factory_registry.py::test_strategy_factory_loads_all_batch1_and_batch2 -v
```

**Expected:** PASSED

### Step 3: Commit factory test update

**Command:**
```bash
git add tests/unit/operations/test_strategy_factory_registry.py
git commit -s -m "test: verify StrategyFactory supports Batch 1+2 entities

Add test to ensure all 6 migrated entities load correctly.

Part of Phase 3 Batch 2 migration.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 6: Final Batch 2 validation

### Step 1: Run complete quality checks

**Command:**
```bash
make check
```

**Expected:** All checks pass (excluding container tests)

### Step 2: Tag Batch 2 completion

**Command:**
```bash
git tag -a phase3-batch2-complete -m "Phase 3 Batch 2 Complete: Issues domain entities migrated"
```

### Step 3: Push branch and tags

**Command:**
```bash
git push origin feature/entity-registry-system && git push origin --tags
```

---

## Success Criteria

Batch 2 is complete when:
- ✅ Issues entity migrated with milestone dependency
- ✅ Comments entity migrated with issues dependency
- ✅ Sub_issues entity migrated with issues dependency
- ✅ Dependency graph validated (milestones → issues → [comments, sub_issues])
- ✅ Topological sort produces correct execution order
- ✅ Auto-disable works for missing dependencies (non-strict)
- ✅ Strict mode raises errors on explicit violations
- ✅ All unit tests passing
- ✅ All integration tests passing
- ✅ StrategyFactory loads all 6 entities correctly

## Dependency Graph After Batch 2

```
milestones (Batch 1)
    ↓
issues (Batch 2)
    ↓
    ├─→ comments (Batch 2)
    └─→ sub_issues (Batch 2)

labels (Batch 1, independent)
git_repository (Batch 1, independent)
```

## Next Steps

After Batch 2 completion:
- Proceed to Batch 3 implementation plan (pull requests domain)
- Factory and orchestrator updates after Batch 3

# Phase 3 Batch 3: Pull Requests Domain Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate pull_requests, pr_reviews, pr_review_comments, and pr_comments entities to EntityRegistry with complete dependency graph.

**Architecture:** Create entity_config.py for all PR entities, establish dependency relationships (PR → reviews → review_comments, PR → pr_comments), complete the full dependency graph for all 10 entities.

**Tech Stack:** Python 3, pytest, EntityRegistry, complete dependency management

---

## Prerequisites

- Batch 1 complete (labels, milestones, git_repository)
- Batch 2 complete (issues, comments, sub_issues)
- Dependency validation working for existing entities

---

## Task 1: Migrate pull_requests entity

**Files:**
- Create: `src/entities/pull_requests/entity_config.py`
- Move strategies to `src/entities/pull_requests/`
- Create: `tests/unit/entities/pull_requests/test_entity_config.py`

### Step 1: Write failing test

```python
# tests/unit/entities/pull_requests/test_entity_config.py
"""Tests for pull_requests entity configuration."""

import pytest
from src.entities.registry import EntityRegistry
from typing import Union, Set


@pytest.mark.unit
def test_pull_requests_entity_discovered():
    """Test pull_requests entity discovered."""
    registry = EntityRegistry()
    entity = registry.get_entity("pull_requests")

    assert entity.config.name == "pull_requests"
    assert entity.config.env_var == "INCLUDE_PULL_REQUESTS"
    assert entity.config.default_value is True
    assert entity.config.value_type == Union[bool, Set[int]]
    assert entity.config.dependencies == ["milestones"]


@pytest.mark.unit
def test_pull_requests_depends_on_milestones():
    """Test pull_requests depend on milestones."""
    registry = EntityRegistry()
    entity = registry.get_entity("pull_requests")

    assert "milestones" in entity.get_dependencies()
```

### Step 2: Run test to verify failure

**Command:**
```bash
pdm run pytest tests/unit/entities/pull_requests/test_entity_config.py -v
```

**Expected:** FAILED - Unknown entity: pull_requests

### Step 3: Create pull_requests entity_config.py

```python
# src/entities/pull_requests/entity_config.py
"""Pull requests entity configuration for EntityRegistry."""

from typing import Union, Set


class PullRequestsEntityConfig:
    """Configuration for pull_requests entity.

    Pull requests depend on milestones (can reference milestones).
    Supports selective PR numbers via Set[int].
    """

    name = "pull_requests"
    env_var = "INCLUDE_PULL_REQUESTS"
    default_value = True
    value_type = Union[bool, Set[int]]
    dependencies = ["milestones"]  # PRs can reference milestones
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Pull requests with milestone references"
```

### Step 4: Verify test passes

**Command:**
```bash
pdm run pytest tests/unit/entities/pull_requests/test_entity_config.py::test_pull_requests_entity_discovered -v
```

**Expected:** PASSED

### Step 5: Move strategies and update imports

**Commands:**
```bash
mv src/operations/save/strategies/pull_requests_strategy.py src/entities/pull_requests/save_strategy.py
mv src/operations/restore/strategies/pull_requests_strategy.py src/entities/pull_requests/restore_strategy.py
```

Update imports:
```python
from src.operations.save.strategy import SaveEntityStrategy
from src.operations.restore.strategy import RestoreEntityStrategy
from src.entities.pull_requests.models import PullRequest
```

### Step 6: Run all pull_requests tests

**Command:**
```bash
pdm run pytest tests/unit/entities/pull_requests/ -v
```

**Expected:** All PASSED

### Step 7: Commit pull_requests migration

**Command:**
```bash
git add src/entities/pull_requests/ tests/unit/entities/pull_requests/
git commit -s -m "feat: migrate pull_requests entity with milestone dependency

Add PullRequestsEntityConfig with milestone dependency.
Supports Union[bool, Set[int]] for selective PR numbers.

Part of Phase 3 Batch 3 migration.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 2: Migrate pr_reviews entity

**Files:**
- Create: `src/entities/pr_reviews/entity_config.py`
- Move strategies to `src/entities/pr_reviews/`
- Create: `tests/unit/entities/pr_reviews/test_entity_config.py`

### Step 1: Write failing test

```python
# tests/unit/entities/pr_reviews/test_entity_config.py
"""Tests for pr_reviews entity configuration."""

import pytest
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_pr_reviews_entity_discovered():
    """Test pr_reviews entity discovered."""
    registry = EntityRegistry()
    entity = registry.get_entity("pr_reviews")

    assert entity.config.name == "pr_reviews"
    assert entity.config.env_var == "INCLUDE_PR_REVIEWS"
    assert entity.config.dependencies == ["pull_requests"]


@pytest.mark.unit
def test_pr_reviews_depends_on_pull_requests():
    """Test pr_reviews depend on pull_requests."""
    registry = EntityRegistry()
    entity = registry.get_entity("pr_reviews")

    assert "pull_requests" in entity.get_dependencies()
```

### Step 2: Run test to verify failure

**Command:**
```bash
pdm run pytest tests/unit/entities/pr_reviews/test_entity_config.py -v
```

**Expected:** FAILED - Unknown entity: pr_reviews

### Step 3: Create pr_reviews entity_config.py

```python
# src/entities/pr_reviews/entity_config.py
"""PR reviews entity configuration for EntityRegistry."""


class PrReviewsEntityConfig:
    """Configuration for pr_reviews entity.

    PR reviews depend on pull_requests (belong to PRs).
    """

    name = "pr_reviews"
    env_var = "INCLUDE_PR_REVIEWS"
    default_value = True
    value_type = bool
    dependencies = ["pull_requests"]  # Reviews belong to PRs
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Pull request code reviews"
```

### Step 4: Verify test passes

**Command:**
```bash
pdm run pytest tests/unit/entities/pr_reviews/test_entity_config.py::test_pr_reviews_entity_discovered -v
```

**Expected:** PASSED

### Step 5: Move strategies and update imports

**Commands:**
```bash
mv src/operations/save/strategies/pr_reviews_strategy.py src/entities/pr_reviews/save_strategy.py
mv src/operations/restore/strategies/pr_reviews_strategy.py src/entities/pr_reviews/restore_strategy.py
```

### Step 6: Run all pr_reviews tests

**Command:**
```bash
pdm run pytest tests/unit/entities/pr_reviews/ -v
```

**Expected:** All PASSED

### Step 7: Commit pr_reviews migration

**Command:**
```bash
git add src/entities/pr_reviews/ tests/unit/entities/pr_reviews/
git commit -s -m "feat: migrate pr_reviews entity with pull_requests dependency

Add PrReviewsEntityConfig with pull_requests dependency.

Part of Phase 3 Batch 3 migration.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 3: Migrate pr_review_comments entity

**Files:**
- Create: `src/entities/pr_review_comments/entity_config.py`
- Move strategies to `src/entities/pr_review_comments/`
- Create: `tests/unit/entities/pr_review_comments/test_entity_config.py`

### Step 1: Write failing test

```python
# tests/unit/entities/pr_review_comments/test_entity_config.py
"""Tests for pr_review_comments entity configuration."""

import pytest
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_pr_review_comments_entity_discovered():
    """Test pr_review_comments entity discovered."""
    registry = EntityRegistry()
    entity = registry.get_entity("pr_review_comments")

    assert entity.config.name == "pr_review_comments"
    assert entity.config.env_var == "INCLUDE_PR_REVIEW_COMMENTS"
    assert entity.config.dependencies == ["pr_reviews"]


@pytest.mark.unit
def test_pr_review_comments_depends_on_pr_reviews():
    """Test pr_review_comments depend on pr_reviews."""
    registry = EntityRegistry()
    entity = registry.get_entity("pr_review_comments")

    assert "pr_reviews" in entity.get_dependencies()
```

### Step 2: Run test to verify failure

**Command:**
```bash
pdm run pytest tests/unit/entities/pr_review_comments/test_entity_config.py -v
```

**Expected:** FAILED - Unknown entity: pr_review_comments

### Step 3: Create pr_review_comments entity_config.py

```python
# src/entities/pr_review_comments/entity_config.py
"""PR review comments entity configuration for EntityRegistry."""


class PrReviewCommentsEntityConfig:
    """Configuration for pr_review_comments entity.

    PR review comments depend on pr_reviews (inline code comments).
    """

    name = "pr_review_comments"
    env_var = "INCLUDE_PR_REVIEW_COMMENTS"
    default_value = True
    value_type = bool
    dependencies = ["pr_reviews"]  # Review comments belong to reviews
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Code review inline comments"
```

### Step 4: Verify test passes

**Command:**
```bash
pdm run pytest tests/unit/entities/pr_review_comments/test_entity_config.py::test_pr_review_comments_entity_discovered -v
```

**Expected:** PASSED

### Step 5: Move strategies and update imports

**Commands:**
```bash
mv src/operations/save/strategies/pr_review_comments_strategy.py src/entities/pr_review_comments/save_strategy.py
mv src/operations/restore/strategies/pr_review_comments_strategy.py src/entities/pr_review_comments/restore_strategy.py
```

### Step 6: Run all pr_review_comments tests

**Command:**
```bash
pdm run pytest tests/unit/entities/pr_review_comments/ -v
```

**Expected:** All PASSED

### Step 7: Commit pr_review_comments migration

**Command:**
```bash
git add src/entities/pr_review_comments/ tests/unit/entities/pr_review_comments/
git commit -s -m "feat: migrate pr_review_comments entity with pr_reviews dependency

Add PrReviewCommentsEntityConfig with pr_reviews dependency.

Part of Phase 3 Batch 3 migration.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 4: Migrate pr_comments entity

**Files:**
- Create: `src/entities/pr_comments/entity_config.py`
- Move strategies to `src/entities/pr_comments/`
- Create: `tests/unit/entities/pr_comments/test_entity_config.py`

### Step 1: Write failing test

```python
# tests/unit/entities/pr_comments/test_entity_config.py
"""Tests for pr_comments entity configuration."""

import pytest
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_pr_comments_entity_discovered():
    """Test pr_comments entity discovered."""
    registry = EntityRegistry()
    entity = registry.get_entity("pr_comments")

    assert entity.config.name == "pr_comments"
    assert entity.config.env_var == "INCLUDE_PULL_REQUEST_COMMENTS"
    assert entity.config.dependencies == ["pull_requests"]


@pytest.mark.unit
def test_pr_comments_depends_on_pull_requests():
    """Test pr_comments depend on pull_requests."""
    registry = EntityRegistry()
    entity = registry.get_entity("pr_comments")

    assert "pull_requests" in entity.get_dependencies()
```

### Step 2: Run test to verify failure

**Command:**
```bash
pdm run pytest tests/unit/entities/pr_comments/test_entity_config.py -v
```

**Expected:** FAILED - Unknown entity: pr_comments

### Step 3: Create pr_comments entity_config.py

```python
# src/entities/pr_comments/entity_config.py
"""PR comments entity configuration for EntityRegistry."""


class PrCommentsEntityConfig:
    """Configuration for pr_comments entity.

    PR comments depend on pull_requests (conversation comments).
    """

    name = "pr_comments"
    env_var = "INCLUDE_PULL_REQUEST_COMMENTS"
    default_value = True
    value_type = bool
    dependencies = ["pull_requests"]  # PR comments belong to PRs
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Pull request conversation comments"
```

### Step 4: Verify test passes

**Command:**
```bash
pdm run pytest tests/unit/entities/pr_comments/test_entity_config.py::test_pr_comments_entity_discovered -v
```

**Expected:** PASSED

### Step 5: Move strategies and update imports

**Commands:**
```bash
mv src/operations/save/strategies/pr_comments_strategy.py src/entities/pr_comments/save_strategy.py
mv src/operations/restore/strategies/pr_comments_strategy.py src/entities/pr_comments/restore_strategy.py
```

### Step 6: Run all pr_comments tests

**Command:**
```bash
pdm run pytest tests/unit/entities/pr_comments/ -v
```

**Expected:** All PASSED

### Step 7: Commit pr_comments migration

**Command:**
```bash
git add src/entities/pr_comments/ tests/unit/entities/pr_comments/
git commit -s -m "feat: migrate pr_comments entity with pull_requests dependency

Add PrCommentsEntityConfig with pull_requests dependency.

Part of Phase 3 Batch 3 migration.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 5: Verify complete dependency graph

**Files:**
- Create: `tests/integration/test_complete_dependency_graph.py`

### Step 1: Write comprehensive dependency graph test

```python
# tests/integration/test_complete_dependency_graph.py
"""Integration tests for complete 10-entity dependency graph."""

import pytest
from src.entities.registry import EntityRegistry


@pytest.mark.integration
def test_all_10_entities_discovered():
    """Test all 10 entities discovered by registry."""
    registry = EntityRegistry()
    names = registry.get_all_entity_names()

    # Batch 1
    assert "labels" in names
    assert "milestones" in names
    assert "git_repository" in names

    # Batch 2
    assert "issues" in names
    assert "comments" in names
    assert "sub_issues" in names

    # Batch 3
    assert "pull_requests" in names
    assert "pr_reviews" in names
    assert "pr_review_comments" in names
    assert "pr_comments" in names


@pytest.mark.integration
def test_complete_dependency_graph():
    """Test complete dependency relationships for all entities."""
    registry = EntityRegistry()

    # Verify each entity's dependencies
    assert registry.get_entity("labels").get_dependencies() == []
    assert registry.get_entity("milestones").get_dependencies() == []
    assert registry.get_entity("git_repository").get_dependencies() == []

    assert registry.get_entity("issues").get_dependencies() == ["milestones"]
    assert registry.get_entity("comments").get_dependencies() == ["issues"]
    assert registry.get_entity("sub_issues").get_dependencies() == ["issues"]

    assert registry.get_entity("pull_requests").get_dependencies() == ["milestones"]
    assert registry.get_entity("pr_reviews").get_dependencies() == ["pull_requests"]
    assert registry.get_entity("pr_review_comments").get_dependencies() == ["pr_reviews"]
    assert registry.get_entity("pr_comments").get_dependencies() == ["pull_requests"]


@pytest.mark.integration
def test_complete_topological_sort():
    """Test topological sort produces valid execution order for all 10 entities."""
    registry = EntityRegistry()
    enabled = registry.get_enabled_entities()
    enabled_names = [e.config.name for e in enabled]

    # Get indices
    def idx(name):
        return enabled_names.index(name)

    # Verify dependency order constraints
    # Independent entities can appear anywhere, but:
    assert idx("milestones") < idx("issues")
    assert idx("milestones") < idx("pull_requests")
    assert idx("issues") < idx("comments")
    assert idx("issues") < idx("sub_issues")
    assert idx("pull_requests") < idx("pr_reviews")
    assert idx("pull_requests") < idx("pr_comments")
    assert idx("pr_reviews") < idx("pr_review_comments")


@pytest.mark.integration
def test_cascading_dependency_disable():
    """Test cascading disable when root dependency disabled."""
    import os

    # Disable milestones - should cascade to issues and PRs
    os.environ["INCLUDE_MILESTONES"] = "false"

    registry = EntityRegistry.from_environment(is_strict=False)
    enabled_names = [e.config.name for e in registry.get_enabled_entities()]

    # These should all be disabled due to cascade
    assert "milestones" not in enabled_names
    assert "issues" not in enabled_names
    assert "comments" not in enabled_names
    assert "sub_issues" not in enabled_names
    assert "pull_requests" not in enabled_names
    assert "pr_reviews" not in enabled_names
    assert "pr_review_comments" not in enabled_names
    assert "pr_comments" not in enabled_names

    # These should still be enabled (independent)
    assert "labels" in enabled_names
    assert "git_repository" in enabled_names

    # Cleanup
    del os.environ["INCLUDE_MILESTONES"]


@pytest.mark.integration
def test_pr_branch_independence():
    """Test PR review comments and PR comments are independent branches."""
    import os

    # Disable pr_reviews - should only affect pr_review_comments, not pr_comments
    os.environ["INCLUDE_PR_REVIEWS"] = "false"

    registry = EntityRegistry.from_environment(is_strict=False)
    enabled_names = [e.config.name for e in registry.get_enabled_entities()]

    # pr_review_comments should be disabled
    assert "pr_review_comments" not in enabled_names

    # pr_comments should still be enabled (different branch)
    assert "pr_comments" in enabled_names
    assert "pull_requests" in enabled_names

    # Cleanup
    del os.environ["INCLUDE_PR_REVIEWS"]


@pytest.mark.integration
def test_no_circular_dependencies():
    """Test no circular dependencies in complete graph."""
    registry = EntityRegistry()

    # get_enabled_entities performs topological sort
    # If there are circular deps, this raises ValueError
    enabled = registry.get_enabled_entities()

    # Should succeed with all 10 entities
    assert len(enabled) == 10
```

### Step 2: Run complete dependency graph tests

**Command:**
```bash
pdm run pytest tests/integration/test_complete_dependency_graph.py -v
```

**Expected:** All PASSED

### Step 3: Run full fast test suite

**Command:**
```bash
make test-fast
```

**Expected:** All tests pass

### Step 4: Commit comprehensive tests

**Command:**
```bash
git add tests/integration/test_complete_dependency_graph.py
git commit -s -m "test: add complete 10-entity dependency graph validation

Add comprehensive tests for complete dependency graph including:
- All 10 entities discovered
- Complete dependency relationships
- Topological sort validation
- Cascading disable behavior
- Branch independence (PR reviews vs PR comments)
- No circular dependencies

All integration tests passing.

Part of Phase 3 Batch 3 migration.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 6: Update StrategyFactory for all 10 entities

### Step 1: Test StrategyFactory loads all entities

```python
# tests/unit/operations/test_strategy_factory_registry.py

@pytest.mark.unit
def test_strategy_factory_loads_all_10_entities():
    """Test StrategyFactory loads all 10 migrated entities."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry, config=None)

    all_entities = [
        "labels", "milestones", "git_repository",
        "issues", "comments", "sub_issues",
        "pull_requests", "pr_reviews", "pr_review_comments", "pr_comments"
    ]

    for entity_name in all_entities:
        strategy = factory.load_save_strategy(entity_name)
        assert strategy is not None, f"Failed to load {entity_name}"
        assert strategy.get_entity_name() == entity_name
```

### Step 2: Run test

**Command:**
```bash
pdm run pytest tests/unit/operations/test_strategy_factory_registry.py::test_strategy_factory_loads_all_10_entities -v
```

**Expected:** PASSED

### Step 3: Commit factory test

**Command:**
```bash
git add tests/unit/operations/test_strategy_factory_registry.py
git commit -s -m "test: verify StrategyFactory supports all 10 entities

Add test ensuring all 10 migrated entities load via registry.

Part of Phase 3 Batch 3 migration.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 7: Final Batch 3 validation

### Step 1: Run complete quality checks

**Command:**
```bash
make check
```

**Expected:** All checks pass

### Step 2: Create summary commit

**Command:**
```bash
git commit --allow-empty -s -m "$(cat <<'EOF'
feat: complete Phase 3 Batch 3 - all 10 entities migrated

Complete migration of pull request domain entities to EntityRegistry.
All 10 entities now managed by EntityRegistry with full dependency graph.

Batch 3 entities:
- pull_requests (depends on milestones)
- pr_reviews (depends on pull_requests)
- pr_review_comments (depends on pr_reviews)
- pr_comments (depends on pull_requests)

Complete dependency graph:
  milestones → issues → [comments, sub_issues]
  milestones → pull_requests → [pr_reviews → pr_review_comments, pr_comments]
  labels (independent)
  git_repository (independent)

All 10 entities discovered, all tests passing.

Part of Phase 3 entity migration.

Signed-off-by: Claude <noreply@anthropic.com>
EOF
)"
```

### Step 3: Tag Batch 3 completion

**Command:**
```bash
git tag -a phase3-batch3-complete -m "Phase 3 Batch 3 Complete: All 10 entities migrated to EntityRegistry"
```

### Step 4: Push branch and tags

**Command:**
```bash
git push origin feature/entity-registry-system && git push origin --tags
```

---

## Success Criteria

Batch 3 is complete when:
- ✅ Pull_requests entity migrated with milestone dependency
- ✅ Pr_reviews entity migrated with pull_requests dependency
- ✅ Pr_review_comments entity migrated with pr_reviews dependency
- ✅ Pr_comments entity migrated with pull_requests dependency
- ✅ Complete dependency graph validated for all 10 entities
- ✅ Topological sort produces valid execution order
- ✅ Cascading disable behavior works correctly
- ✅ Branch independence verified (PR reviews vs comments)
- ✅ No circular dependencies
- ✅ All unit tests passing
- ✅ All integration tests passing
- ✅ StrategyFactory loads all 10 entities

## Complete Dependency Graph

```
Independent:
  - labels
  - git_repository

Milestone branch:
  milestones
    ├─→ issues
    │   ├─→ comments
    │   └─→ sub_issues
    └─→ pull_requests
        ├─→ pr_reviews
        │   └─→ pr_review_comments
        └─→ pr_comments
```

## Next Steps

After Batch 3 completion:
- Proceed to Factory and Orchestrator update implementation plan
- Complete StrategyFactory migration (remove ApplicationConfig)
- Update save and restore orchestrators to use EntityRegistry

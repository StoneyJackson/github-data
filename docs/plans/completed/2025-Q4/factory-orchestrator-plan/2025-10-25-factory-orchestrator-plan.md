# Phase 3: Factory and Orchestrator Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete StrategyFactory migration and update save/restore orchestrators to use EntityRegistry exclusively, removing ApplicationConfig dependencies.

**Architecture:** Remove ApplicationConfig from StrategyFactory, update orchestrators to use EntityRegistry for entity management and execution order, maintain existing functionality with new system.

**Tech Stack:** Python 3, pytest, EntityRegistry, StrategyFactory, orchestrators

---

## Prerequisites

- All 3 batches complete (10 entities migrated)
- StrategyFactory supports EntityRegistry (from Batch 1)
- EntityRegistry dependency validation working

---

## Task 1: Complete StrategyFactory migration

**Files:**
- Modify: `src/operations/strategy_factory.py`
- Modify: `tests/unit/operations/test_strategy_factory_registry.py`

### Step 1: Write test for ApplicationConfig removal

```python
# tests/unit/operations/test_strategy_factory_registry.py

@pytest.mark.unit
def test_strategy_factory_works_without_config():
    """Test StrategyFactory works with only EntityRegistry."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry)

    # Should work without config parameter
    assert factory.registry == registry


@pytest.mark.unit
def test_strategy_factory_create_save_strategies_from_registry():
    """Test factory creates save strategies for enabled entities."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry)

    strategies = factory.create_save_strategies()

    # Should return strategies for all enabled entities
    strategy_names = [s.get_entity_name() for s in strategies]
    assert "labels" in strategy_names
    assert "milestones" in strategy_names
    assert len(strategy_names) == 10  # All entities enabled by default


@pytest.mark.unit
def test_strategy_factory_respects_disabled_entities():
    """Test factory skips disabled entities."""
    import os

    os.environ["INCLUDE_LABELS"] = "false"
    registry = EntityRegistry.from_environment()
    factory = StrategyFactory(registry=registry)

    strategies = factory.create_save_strategies()
    strategy_names = [s.get_entity_name() for s in strategies]

    assert "labels" not in strategy_names

    del os.environ["INCLUDE_LABELS"]
```

### Step 2: Run tests to verify they fail

**Command:**
```bash
pdm run pytest tests/unit/operations/test_strategy_factory_registry.py::test_strategy_factory_works_without_config -v
```

**Expected:** FAILED - missing required parameter

### Step 3: Update StrategyFactory to make config optional

Edit `src/operations/strategy_factory.py`:

```python
class StrategyFactory:
    """Factory for creating entity strategies from EntityRegistry."""

    def __init__(self, registry: "EntityRegistry"):
        """Initialize strategy factory.

        Args:
            registry: EntityRegistry for entity management
        """
        self.registry = registry

    def create_save_strategies(
        self, git_service: Optional[Any] = None
    ) -> List["SaveEntityStrategy"]:
        """Create save strategies for all enabled entities.

        Args:
            git_service: Optional git service for git_repository entity

        Returns:
            List of save strategy instances in dependency order
        """
        strategies = []

        # Get enabled entities in dependency order
        enabled_entities = self.registry.get_enabled_entities()

        for entity in enabled_entities:
            strategy = self.load_save_strategy(entity.config.name, git_service=git_service)
            if strategy:
                strategies.append(strategy)

        return strategies

    def create_restore_strategies(
        self, **kwargs
    ) -> List["RestoreEntityStrategy"]:
        """Create restore strategies for all enabled entities.

        Args:
            **kwargs: Additional arguments for strategy instantiation

        Returns:
            List of restore strategy instances in dependency order
        """
        strategies = []

        # Get enabled entities in dependency order
        enabled_entities = self.registry.get_enabled_entities()

        for entity in enabled_entities:
            strategy = self.load_restore_strategy(entity.config.name, **kwargs)
            if strategy:
                strategies.append(strategy)

        return strategies

    def load_save_strategy(
        self, entity_name: str, git_service: Optional[Any] = None
    ) -> Optional["SaveEntityStrategy"]:
        """Load save strategy for entity by name.

        Args:
            entity_name: Name of entity
            git_service: Optional git service for git_repository

        Returns:
            Save strategy instance or None
        """
        try:
            entity = self.registry.get_entity(entity_name)
        except ValueError:
            logger.warning(f"Entity not found: {entity_name}")
            return None

        # Check for override
        if entity.config.save_strategy_class:
            if entity_name == "git_repository" and git_service:
                return entity.config.save_strategy_class(git_service)
            return entity.config.save_strategy_class()

        # Use convention
        entity_name_normalized = entity.config.name
        module_name = f"src.entities.{entity_name_normalized}.save_strategy"
        class_name = self._to_class_name(entity_name_normalized) + "SaveStrategy"

        try:
            module = importlib.import_module(module_name)
            strategy_class = getattr(module, class_name)

            # Special handling for git_repository
            if entity_name == "git_repository" and git_service:
                return strategy_class(git_service)

            return strategy_class()
        except (ImportError, AttributeError) as e:
            logger.warning(f"Could not load save strategy for {entity_name}: {e}")
            return None

    def _to_class_name(self, entity_name: str) -> str:
        """Convert snake_case entity name to PascalCase.

        Args:
            entity_name: Snake case name (e.g., "pr_review_comments")

        Returns:
            PascalCase name (e.g., "PrReviewComments")
        """
        parts = entity_name.split("_")
        return "".join(word.capitalize() for word in parts)
```

### Step 4: Run tests to verify changes

**Command:**
```bash
pdm run pytest tests/unit/operations/test_strategy_factory_registry.py -v
```

**Expected:** All PASSED

### Step 5: Remove legacy ApplicationConfig methods

Remove any remaining `_load_save_strategy_from_config` and `_load_restore_strategy_from_config` methods.

### Step 6: Run all StrategyFactory tests

**Command:**
```bash
pdm run pytest tests/unit/operations/ -k strategy_factory -v
```

**Expected:** All PASSED

### Step 7: Commit StrategyFactory completion

**Command:**
```bash
git add src/operations/strategy_factory.py tests/unit/operations/test_strategy_factory_registry.py
git commit -s -m "feat: complete StrategyFactory migration to EntityRegistry

Remove ApplicationConfig dependency from StrategyFactory. Factory now
exclusively uses EntityRegistry for entity management and strategy loading.

- Make config parameter optional (removed)
- Add create_save_strategies method
- Add create_restore_strategies method
- Remove ApplicationConfig fallback methods
- Update all strategy loading to use EntityRegistry
- Add tests for registry-only operation

Part of Phase 3 factory/orchestrator updates.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 2: Update SaveOrchestrator to use EntityRegistry

**Files:**
- Modify: `src/operations/save/orchestrator.py`
- Create: `tests/unit/operations/save/test_orchestrator_registry.py`

### Step 1: Write failing test for SaveOrchestrator with EntityRegistry

```python
# tests/unit/operations/save/test_orchestrator_registry.py
"""Tests for SaveOrchestrator with EntityRegistry."""

import pytest
from unittest.mock import Mock
from src.operations.save.orchestrator import StrategyBasedSaveOrchestrator
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_save_orchestrator_accepts_registry():
    """Test SaveOrchestrator accepts EntityRegistry."""
    registry = EntityRegistry()
    github_service = Mock()
    storage_service = Mock()

    orchestrator = StrategyBasedSaveOrchestrator(
        registry=registry,
        github_service=github_service,
        storage_service=storage_service
    )

    assert orchestrator._registry == registry


@pytest.mark.unit
def test_save_orchestrator_uses_registry_for_execution_order():
    """Test orchestrator uses registry for dependency-ordered execution."""
    registry = EntityRegistry()
    github_service = Mock()
    storage_service = Mock()

    orchestrator = StrategyBasedSaveOrchestrator(
        registry=registry,
        github_service=github_service,
        storage_service=storage_service
    )

    # Get execution order
    enabled = registry.get_enabled_entities()
    entity_names = [e.config.name for e in enabled]

    # Should respect dependency order
    milestone_idx = entity_names.index("milestones")
    issues_idx = entity_names.index("issues")
    assert milestone_idx < issues_idx
```

### Step 2: Run test to verify failure

**Command:**
```bash
pdm run pytest tests/unit/operations/save/test_orchestrator_registry.py::test_save_orchestrator_accepts_registry -v
```

**Expected:** FAILED - unexpected keyword argument 'registry'

### Step 3: Update SaveOrchestrator __init__

Edit `src/operations/save/orchestrator.py`:

```python
class StrategyBasedSaveOrchestrator:
    """Orchestrator that executes save operations using EntityRegistry."""

    def __init__(
        self,
        registry: "EntityRegistry",
        github_service: "RepositoryService",
        storage_service: "StorageService",
        git_service: Optional["GitRepositoryService"] = None,
    ) -> None:
        """Initialize save orchestrator.

        Args:
            registry: EntityRegistry for entity management
            github_service: GitHub API service
            storage_service: Storage service for writing data
            git_service: Optional git service for repository cloning
        """
        self._registry = registry
        self._github_service = github_service
        self._storage_service = storage_service
        self._git_service = git_service
        self._context: Dict[str, Any] = {}

        # Create strategy factory
        self._factory = StrategyFactory(registry=registry)

        # Load strategies for enabled entities
        self._strategies = self._factory.create_save_strategies(git_service=git_service)
```

### Step 4: Update execute_save method

```python
    def execute_save(
        self,
        repo_name: str,
        output_path: str,
    ) -> List[Dict[str, Any]]:
        """Execute save operation using registered strategies.

        Args:
            repo_name: Repository name (owner/repo)
            output_path: Output directory path

        Returns:
            List of result dictionaries for each entity
        """
        results = []

        # Execute strategies in dependency order (already sorted by registry)
        for strategy in self._strategies:
            entity_name = strategy.get_entity_name()
            result = self._execute_strategy(strategy, repo_name, output_path)
            results.append(result)
            print(f"Saved {entity_name}: {result['count']} items")

        return results
```

### Step 5: Update _is_selective_mode method

```python
    def _is_selective_mode(self, entity_name: str) -> bool:
        """Check if entity is in selective mode (Set[int] instead of bool).

        Args:
            entity_name: Entity name to check

        Returns:
            True if entity has Set[int] value (selective mode)
        """
        try:
            entity = self._registry.get_entity(entity_name)
            return isinstance(entity.enabled, set)
        except ValueError:
            return False
```

### Step 6: Run tests to verify changes

**Command:**
```bash
pdm run pytest tests/unit/operations/save/test_orchestrator_registry.py -v
```

**Expected:** All PASSED

### Step 7: Remove ApplicationConfig references

Search and remove all `self._config` references, replacing with `self._registry` calls.

### Step 8: Run all save orchestrator tests

**Command:**
```bash
pdm run pytest tests/unit/operations/save/ -v
```

**Expected:** All PASSED (some may need updates)

### Step 9: Commit SaveOrchestrator updates

**Command:**
```bash
git add src/operations/save/orchestrator.py tests/unit/operations/save/test_orchestrator_registry.py
git commit -s -m "feat: migrate SaveOrchestrator to EntityRegistry

Replace ApplicationConfig with EntityRegistry in save orchestrator.
Orchestrator now uses registry for entity management and execution order.

- Replace config parameter with registry
- Use StrategyFactory with EntityRegistry
- Remove DependencyResolver (registry handles order)
- Update selective mode detection to use registry
- Remove all ApplicationConfig references

Part of Phase 3 factory/orchestrator updates.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 3: Update RestoreOrchestrator to use EntityRegistry

**Files:**
- Modify: `src/operations/restore/orchestrator.py`
- Create: `tests/unit/operations/restore/test_orchestrator_registry.py`

### Step 1: Write failing test

```python
# tests/unit/operations/restore/test_orchestrator_registry.py
"""Tests for RestoreOrchestrator with EntityRegistry."""

import pytest
from unittest.mock import Mock
from src.operations.restore.orchestrator import StrategyBasedRestoreOrchestrator
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_restore_orchestrator_accepts_registry():
    """Test RestoreOrchestrator accepts EntityRegistry."""
    registry = EntityRegistry()
    github_service = Mock()
    storage_service = Mock()

    orchestrator = StrategyBasedRestoreOrchestrator(
        registry=registry,
        github_service=github_service,
        storage_service=storage_service
    )

    assert orchestrator._registry == registry
```

### Step 2: Run test to verify failure

**Command:**
```bash
pdm run pytest tests/unit/operations/restore/test_orchestrator_registry.py -v
```

**Expected:** FAILED - unexpected keyword argument

### Step 3: Update RestoreOrchestrator

Similar changes to SaveOrchestrator:
- Replace `config` with `registry` parameter
- Use `StrategyFactory` with registry
- Remove DependencyResolver usage
- Update selective mode detection

### Step 4: Run tests

**Command:**
```bash
pdm run pytest tests/unit/operations/restore/ -v
```

**Expected:** All PASSED

### Step 5: Commit RestoreOrchestrator updates

**Command:**
```bash
git add src/operations/restore/orchestrator.py tests/unit/operations/restore/test_orchestrator_registry.py
git commit -s -m "feat: migrate RestoreOrchestrator to EntityRegistry

Replace ApplicationConfig with EntityRegistry in restore orchestrator.

- Replace config parameter with registry
- Use StrategyFactory with EntityRegistry
- Remove DependencyResolver (registry handles order)
- Update selective mode detection
- Remove all ApplicationConfig references

Part of Phase 3 factory/orchestrator updates.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 4: Update DependencyResolver (deprecate or remove)

**Files:**
- Modify or remove: `src/operations/dependency_resolver.py`

### Step 1: Check if DependencyResolver is still used

**Command:**
```bash
grep -r "DependencyResolver" src/ --exclude-dir=__pycache__
```

### Step 2: If still used, mark as deprecated

Add deprecation warning:

```python
# src/operations/dependency_resolver.py
"""DEPRECATED: Use EntityRegistry.get_enabled_entities() instead.

This module is deprecated as of Phase 3. EntityRegistry now handles
dependency resolution and topological sorting.
"""

import warnings


class DependencyResolver:
    """DEPRECATED: Use EntityRegistry instead."""

    def __init__(self):
        warnings.warn(
            "DependencyResolver is deprecated. Use EntityRegistry.get_enabled_entities() instead.",
            DeprecationWarning,
            stacklevel=2
        )
```

### Step 3: If not used, remove file

**Command:**
```bash
git rm src/operations/dependency_resolver.py
```

### Step 4: Commit changes

**Command:**
```bash
git add src/operations/dependency_resolver.py  # or git rm
git commit -s -m "refactor: deprecate/remove DependencyResolver

EntityRegistry now handles dependency resolution and topological sorting.
DependencyResolver is no longer needed.

Part of Phase 3 factory/orchestrator updates.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 5: Integration testing for factory/orchestrator updates

**Files:**
- Create: `tests/integration/test_orchestrator_end_to_end.py`

### Step 1: Write end-to-end integration test

```python
# tests/integration/test_orchestrator_end_to_end.py
"""End-to-end integration tests for orchestrators with EntityRegistry."""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock
from src.entities.registry import EntityRegistry
from src.operations.save.orchestrator import StrategyBasedSaveOrchestrator


@pytest.mark.integration
def test_save_orchestrator_end_to_end():
    """Test save orchestrator executes all enabled entities in order."""
    registry = EntityRegistry()
    github_service = Mock()
    storage_service = Mock()

    # Mock GitHub service responses
    github_service.get_repository_labels.return_value = []
    github_service.get_repository_milestones.return_value = []
    # ... mock other methods

    orchestrator = StrategyBasedSaveOrchestrator(
        registry=registry,
        github_service=github_service,
        storage_service=storage_service
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        results = orchestrator.execute_save("owner/repo", tmpdir)

    # Should have results for all 10 entities
    assert len(results) == 10

    # Verify execution order
    result_names = [r["entity_name"] for r in results]
    milestone_idx = result_names.index("milestones")
    issues_idx = result_names.index("issues")
    assert milestone_idx < issues_idx


@pytest.mark.integration
def test_orchestrator_respects_disabled_entities():
    """Test orchestrator skips disabled entities."""
    os.environ["INCLUDE_LABELS"] = "false"
    os.environ["INCLUDE_MILESTONES"] = "false"

    registry = EntityRegistry.from_environment()
    github_service = Mock()
    storage_service = Mock()

    orchestrator = StrategyBasedSaveOrchestrator(
        registry=registry,
        github_service=github_service,
        storage_service=storage_service
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        results = orchestrator.execute_save("owner/repo", tmpdir)

    result_names = [r["entity_name"] for r in results]

    # Labels and milestones should be skipped
    assert "labels" not in result_names
    assert "milestones" not in result_names

    # Dependent entities should also be skipped
    assert "issues" not in result_names

    # Cleanup
    del os.environ["INCLUDE_LABELS"]
    del os.environ["INCLUDE_MILESTONES"]
```

### Step 2: Run integration tests

**Command:**
```bash
pdm run pytest tests/integration/test_orchestrator_end_to_end.py -v
```

**Expected:** All PASSED

### Step 3: Commit integration tests

**Command:**
```bash
git add tests/integration/test_orchestrator_end_to_end.py
git commit -s -m "test: add end-to-end orchestrator integration tests

Add comprehensive tests for orchestrators with EntityRegistry including
execution order, disabled entity handling, and full workflow validation.

Part of Phase 3 factory/orchestrator updates.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 6: Final validation

### Step 1: Run complete test suite

**Command:**
```bash
make test-fast
```

**Expected:** All tests pass

### Step 2: Run quality checks

**Command:**
```bash
make check
```

**Expected:** All checks pass

### Step 3: Create summary commit

**Command:**
```bash
git commit --allow-empty -s -m "$(cat <<'EOF'
feat: complete factory and orchestrator migration to EntityRegistry

Complete migration of StrategyFactory and both orchestrators to use
EntityRegistry exclusively. ApplicationConfig no longer used for entity
management.

Changes:
- StrategyFactory: Remove ApplicationConfig, use EntityRegistry only
- SaveOrchestrator: Replace config with registry parameter
- RestoreOrchestrator: Replace config with registry parameter
- DependencyResolver: Deprecated (registry handles dependencies)

All strategy loading, entity management, and dependency resolution now
handled by EntityRegistry system.

All tests passing.

Part of Phase 3 entity migration.

Signed-off-by: Claude <noreply@anthropic.com>
EOF
)"
```

### Step 4: Tag completion

**Command:**
```bash
git tag -a phase3-factory-orchestrator-complete -m "Phase 3 Factory/Orchestrator Complete: EntityRegistry fully integrated"
```

---

## Success Criteria

Factory/Orchestrator updates complete when:
- ✅ StrategyFactory works with EntityRegistry only (no ApplicationConfig)
- ✅ StrategyFactory creates strategies for all enabled entities
- ✅ SaveOrchestrator uses EntityRegistry for entity management
- ✅ RestoreOrchestrator uses EntityRegistry for entity management
- ✅ Execution order determined by EntityRegistry topological sort
- ✅ Selective mode detection uses registry
- ✅ DependencyResolver deprecated or removed
- ✅ All unit tests passing
- ✅ All integration tests passing
- ✅ End-to-end workflow validated

## Next Steps

After factory/orchestrator updates:
- Proceed to ApplicationConfig removal implementation plan
- Update main entry point to use EntityRegistry
- Remove ApplicationConfig class completely

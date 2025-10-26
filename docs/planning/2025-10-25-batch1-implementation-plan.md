# Phase 3 Batch 1: Independent Entities Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate labels, milestones, and git_repository entities to the EntityRegistry system.

**Architecture:** Create entity_config.py for each entity, move save/restore strategies into entity directories, and update StrategyFactory to load from EntityRegistry while maintaining ApplicationConfig fallback for unmigrated entities.

**Tech Stack:** Python 3, pytest, EntityRegistry, PDM package management

---

## Task 1: Migrate labels entity

**Files:**
- Create: `src/entities/labels/entity_config.py`
- Move: `src/operations/save/strategies/labels_strategy.py` → `src/entities/labels/save_strategy.py`
- Move: `src/operations/restore/strategies/labels_strategy.py` → `src/entities/labels/restore_strategy.py`
- Create: `tests/unit/entities/labels/test_entity_config.py`

### Step 1: Write failing test for labels entity config discovery

Create test file:

```python
# tests/unit/entities/labels/test_entity_config.py
"""Tests for labels entity configuration."""

import pytest
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_labels_entity_discovered():
    """Test that labels entity is discovered by registry."""
    registry = EntityRegistry()
    entity = registry.get_entity("labels")

    assert entity.config.name == "labels"
    assert entity.config.env_var == "INCLUDE_LABELS"
    assert entity.config.default_value is True
    assert entity.config.value_type == bool
    assert entity.config.dependencies == []
    assert entity.config.description != ""


@pytest.mark.unit
def test_labels_entity_no_dependencies():
    """Test that labels entity has no dependencies."""
    registry = EntityRegistry()
    entity = registry.get_entity("labels")

    assert entity.get_dependencies() == []


@pytest.mark.unit
def test_labels_entity_enabled_by_default():
    """Test that labels entity is enabled by default."""
    registry = EntityRegistry()
    entity = registry.get_entity("labels")

    assert entity.is_enabled() is True
```

### Step 2: Run test to verify it fails

**Command:**
```bash
pdm run pytest tests/unit/entities/labels/test_entity_config.py -v
```

**Expected Output:**
```
FAILED tests/unit/entities/labels/test_entity_config.py::test_labels_entity_discovered - ValueError: Unknown entity: labels
```

### Step 3: Create labels entity_config.py

```python
# src/entities/labels/entity_config.py
"""Labels entity configuration for EntityRegistry."""


class LabelsEntityConfig:
    """Configuration for labels entity.

    Labels have no dependencies and are enabled by default.
    Uses convention-based strategy loading.
    """

    name = "labels"
    env_var = "INCLUDE_LABELS"
    default_value = True
    value_type = bool
    dependencies = []
    save_strategy_class = None  # Use convention
    restore_strategy_class = None  # Use convention
    storage_filename = None  # Use convention (labels.json)
    description = "Repository labels for issue/PR categorization"
```

### Step 4: Run test to verify entity config works

**Command:**
```bash
pdm run pytest tests/unit/entities/labels/test_entity_config.py -v
```

**Expected Output:**
```
PASSED tests/unit/entities/labels/test_entity_config.py::test_labels_entity_discovered
PASSED tests/unit/entities/labels/test_entity_config.py::test_labels_entity_no_dependencies
PASSED tests/unit/entities/labels/test_entity_config.py::test_labels_entity_enabled_by_default
```

### Step 5: Move labels save strategy

**Command:**
```bash
mkdir -p src/entities/labels && mv src/operations/save/strategies/labels_strategy.py src/entities/labels/save_strategy.py
```

**Expected Output:**
```
(file moved successfully)
```

### Step 6: Update imports in labels save_strategy.py

Edit the moved file to fix relative imports:

```python
# src/entities/labels/save_strategy.py
"""Labels save strategy implementation."""

from typing import List, Dict, Any

from src.operations.save.strategy import SaveEntityStrategy


class LabelsSaveStrategy(SaveEntityStrategy):
    """Strategy for saving repository labels."""

    def get_entity_name(self) -> str:
        """Return the entity type name."""
        return "labels"

    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        return []  # Labels have no dependencies

    def get_converter_name(self) -> str:
        """Return the converter function name for this entity type."""
        return "convert_to_label"

    def get_service_method(self) -> str:
        """Return the GitHub service method name for this entity type."""
        return "get_repository_labels"

    def transform(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Transform labels data."""
        # Labels don't require any processing
        return entities
```

### Step 7: Move labels restore strategy

**Command:**
```bash
mv src/operations/restore/strategies/labels_strategy.py src/entities/labels/restore_strategy.py
```

**Expected Output:**
```
(file moved successfully)
```

### Step 8: Update imports in labels restore_strategy.py

Edit the moved file to fix relative imports:

```python
# src/entities/labels/restore_strategy.py
"""Labels restore strategy implementation."""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path

from src.operations.restore.strategy import (
    RestoreEntityStrategy,
    RestoreConflictStrategy,
)
from src.entities.labels.models import Label
from src.conflict_strategies import (
    LabelConflictStrategy,
    parse_conflict_strategy,
    detect_label_conflicts,
)

if TYPE_CHECKING:
    from src.storage.protocols import StorageService
    from src.github.protocols import RepositoryService

# ... rest of file unchanged ...
```

### Step 9: Write test for strategy discovery by convention

Add to test file:

```python
# tests/unit/entities/labels/test_entity_config.py
import importlib


@pytest.mark.unit
def test_labels_save_strategy_exists():
    """Test that labels save strategy exists at expected location."""
    module = importlib.import_module("src.entities.labels.save_strategy")
    strategy_class = getattr(module, "LabelsSaveStrategy")
    assert strategy_class is not None


@pytest.mark.unit
def test_labels_restore_strategy_exists():
    """Test that labels restore strategy exists at expected location."""
    module = importlib.import_module("src.entities.labels.restore_strategy")
    strategy_class = getattr(module, "LabelsRestoreStrategy")
    assert strategy_class is not None
```

### Step 10: Run tests to verify strategy discovery

**Command:**
```bash
pdm run pytest tests/unit/entities/labels/test_entity_config.py -v
```

**Expected Output:**
```
PASSED tests/unit/entities/labels/test_entity_config.py::test_labels_entity_discovered
PASSED tests/unit/entities/labels/test_entity_config.py::test_labels_entity_no_dependencies
PASSED tests/unit/entities/labels/test_entity_config.py::test_labels_entity_enabled_by_default
PASSED tests/unit/entities/labels/test_entity_config.py::test_labels_save_strategy_exists
PASSED tests/unit/entities/labels/test_entity_config.py::test_labels_restore_strategy_exists
```

### Step 11: Run all tests to ensure no breakage

**Command:**
```bash
pdm run pytest tests/ -v --tb=short
```

**Expected Output:**
```
(some tests may fail due to import paths - we'll fix in StrategyFactory updates)
```

### Step 12: Commit labels entity migration

**Command:**
```bash
git add src/entities/labels/entity_config.py
git add src/entities/labels/save_strategy.py
git add src/entities/labels/restore_strategy.py
git add tests/unit/entities/labels/test_entity_config.py
git commit -s -m "$(cat <<'EOF'
feat: migrate labels entity to EntityRegistry

Add entity_config.py for labels entity with metadata and move save/restore
strategies to entity directory following convention-based structure.

- Add LabelsEntityConfig with no dependencies
- Move LabelsSaveStrategy to src/entities/labels/save_strategy.py
- Move LabelsRestoreStrategy to src/entities/labels/restore_strategy.py
- Update imports to use absolute paths
- Add tests for entity config discovery and strategy location

Part of Phase 3 Batch 1 migration.

Signed-off-by: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Migrate milestones entity

**Files:**
- Create: `src/entities/milestones/entity_config.py`
- Move: `src/operations/save/strategies/milestones_strategy.py` → `src/entities/milestones/save_strategy.py`
- Move: `src/operations/restore/strategies/milestones_strategy.py` → `src/entities/milestones/restore_strategy.py`
- Create: `tests/unit/entities/milestones/test_entity_config.py`

### Step 1: Write failing test for milestones entity config

```python
# tests/unit/entities/milestones/test_entity_config.py
"""Tests for milestones entity configuration."""

import pytest
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_milestones_entity_discovered():
    """Test that milestones entity is discovered by registry."""
    registry = EntityRegistry()
    entity = registry.get_entity("milestones")

    assert entity.config.name == "milestones"
    assert entity.config.env_var == "INCLUDE_MILESTONES"
    assert entity.config.default_value is True
    assert entity.config.value_type == bool
    assert entity.config.dependencies == []
    assert entity.config.description != ""


@pytest.mark.unit
def test_milestones_entity_no_dependencies():
    """Test that milestones entity has no dependencies."""
    registry = EntityRegistry()
    entity = registry.get_entity("milestones")

    assert entity.get_dependencies() == []


@pytest.mark.unit
def test_milestones_entity_enabled_by_default():
    """Test that milestones entity is enabled by default."""
    registry = EntityRegistry()
    entity = registry.get_entity("milestones")

    assert entity.is_enabled() is True
```

### Step 2: Run test to verify it fails

**Command:**
```bash
pdm run pytest tests/unit/entities/milestones/test_entity_config.py -v
```

**Expected Output:**
```
FAILED tests/unit/entities/milestones/test_entity_config.py::test_milestones_entity_discovered - ValueError: Unknown entity: milestones
```

### Step 3: Create milestones entity_config.py

```python
# src/entities/milestones/entity_config.py
"""Milestones entity configuration for EntityRegistry."""


class MilestonesEntityConfig:
    """Configuration for milestones entity.

    Milestones have no dependencies and are enabled by default.
    Uses convention-based strategy loading.
    """

    name = "milestones"
    env_var = "INCLUDE_MILESTONES"
    default_value = True
    value_type = bool
    dependencies = []
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Project milestones for issue/PR organization"
```

### Step 4: Run test to verify entity config works

**Command:**
```bash
pdm run pytest tests/unit/entities/milestones/test_entity_config.py::test_milestones_entity_discovered -v
```

**Expected Output:**
```
PASSED tests/unit/entities/milestones/test_entity_config.py::test_milestones_entity_discovered
```

### Step 5: Move milestones strategies

**Command:**
```bash
mv src/operations/save/strategies/milestones_strategy.py src/entities/milestones/save_strategy.py && mv src/operations/restore/strategies/milestones_strategy.py src/entities/milestones/restore_strategy.py
```

### Step 6: Update imports in milestones save_strategy.py

Edit file to fix imports:

```python
# src/entities/milestones/save_strategy.py
"""Milestones save strategy implementation."""

from typing import List, Dict, Any

from src.operations.save.strategy import SaveEntityStrategy

# ... rest of file with updated imports ...
```

### Step 7: Update imports in milestones restore_strategy.py

Edit file to fix imports:

```python
# src/entities/milestones/restore_strategy.py
"""Milestones restore strategy implementation."""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path

from src.operations.restore.strategy import RestoreEntityStrategy
from src.entities.milestones.models import Milestone

# ... rest of file with updated imports ...
```

### Step 8: Add strategy existence tests

```python
# tests/unit/entities/milestones/test_entity_config.py
import importlib


@pytest.mark.unit
def test_milestones_save_strategy_exists():
    """Test that milestones save strategy exists at expected location."""
    module = importlib.import_module("src.entities.milestones.save_strategy")
    strategy_class = getattr(module, "MilestonesSaveStrategy")
    assert strategy_class is not None


@pytest.mark.unit
def test_milestones_restore_strategy_exists():
    """Test that milestones restore strategy exists at expected location."""
    module = importlib.import_module("src.entities.milestones.restore_strategy")
    strategy_class = getattr(module, "MilestonesRestoreStrategy")
    assert strategy_class is not None
```

### Step 9: Run all milestones tests

**Command:**
```bash
pdm run pytest tests/unit/entities/milestones/test_entity_config.py -v
```

**Expected Output:**
```
PASSED tests/unit/entities/milestones/test_entity_config.py::test_milestones_entity_discovered
PASSED tests/unit/entities/milestones/test_entity_config.py::test_milestones_entity_no_dependencies
PASSED tests/unit/entities/milestones/test_entity_config.py::test_milestones_entity_enabled_by_default
PASSED tests/unit/entities/milestones/test_entity_config.py::test_milestones_save_strategy_exists
PASSED tests/unit/entities/milestones/test_entity_config.py::test_milestones_restore_strategy_exists
```

### Step 10: Commit milestones entity migration

**Command:**
```bash
git add src/entities/milestones/entity_config.py
git add src/entities/milestones/save_strategy.py
git add src/entities/milestones/restore_strategy.py
git add tests/unit/entities/milestones/test_entity_config.py
git commit -s -m "$(cat <<'EOF'
feat: migrate milestones entity to EntityRegistry

Add entity_config.py for milestones entity and move strategies to entity
directory following convention-based structure.

- Add MilestonesEntityConfig with no dependencies
- Move MilestonesSaveStrategy to src/entities/milestones/save_strategy.py
- Move MilestonesRestoreStrategy to src/entities/milestones/restore_strategy.py
- Update imports to use absolute paths
- Add tests for entity config discovery and strategy location

Part of Phase 3 Batch 1 migration.

Signed-off-by: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Migrate git_repository entity

**Files:**
- Create: `src/entities/git_repositories/entity_config.py`
- Move: `src/operations/save/strategies/git_repository_strategy.py` → `src/entities/git_repositories/save_strategy.py`
- Move: `src/operations/restore/strategies/git_repository_strategy.py` → `src/entities/git_repositories/restore_strategy.py`
- Create: `tests/unit/entities/git_repositories/test_entity_config.py`

**Note:** The directory is `git_repositories` (plural), not `git_repository`.

### Step 1: Write failing test for git_repository entity config

```python
# tests/unit/entities/git_repositories/test_entity_config.py
"""Tests for git_repository entity configuration."""

import pytest
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_git_repository_entity_discovered():
    """Test that git_repository entity is discovered by registry."""
    registry = EntityRegistry()
    entity = registry.get_entity("git_repository")

    assert entity.config.name == "git_repository"
    assert entity.config.env_var == "INCLUDE_GIT_REPO"
    assert entity.config.default_value is True
    assert entity.config.value_type == bool
    assert entity.config.dependencies == []
    assert entity.config.description != ""


@pytest.mark.unit
def test_git_repository_entity_no_dependencies():
    """Test that git_repository entity has no dependencies."""
    registry = EntityRegistry()
    entity = registry.get_entity("git_repository")

    assert entity.get_dependencies() == []


@pytest.mark.unit
def test_git_repository_entity_enabled_by_default():
    """Test that git_repository entity is enabled by default."""
    registry = EntityRegistry()
    entity = registry.get_entity("git_repository")

    assert entity.is_enabled() is True
```

### Step 2: Run test to verify it fails

**Command:**
```bash
pdm run pytest tests/unit/entities/git_repositories/test_entity_config.py -v
```

**Expected Output:**
```
FAILED tests/unit/entities/git_repositories/test_entity_config.py::test_git_repository_entity_discovered - ValueError: Unknown entity: git_repository
```

### Step 3: Create git_repository entity_config.py

```python
# src/entities/git_repositories/entity_config.py
"""Git repository entity configuration for EntityRegistry."""


class GitRepositoryEntityConfig:
    """Configuration for git_repository entity.

    Git repository backup has no dependencies and is enabled by default.
    Uses convention-based strategy loading.
    """

    name = "git_repository"
    env_var = "INCLUDE_GIT_REPO"
    default_value = True
    value_type = bool
    dependencies = []
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Git repository clone for full backup"
```

### Step 4: Run test to verify entity config works

**Command:**
```bash
pdm run pytest tests/unit/entities/git_repositories/test_entity_config.py::test_git_repository_entity_discovered -v
```

**Expected Output:**
```
PASSED tests/unit/entities/git_repositories/test_entity_config.py::test_git_repository_entity_discovered
```

### Step 5: Move git_repository strategies

**Command:**
```bash
mv src/operations/save/strategies/git_repository_strategy.py src/entities/git_repositories/save_strategy.py && mv src/operations/restore/strategies/git_repository_strategy.py src/entities/git_repositories/restore_strategy.py
```

### Step 6: Update imports in git_repository save_strategy.py

Edit file to fix imports:

```python
# src/entities/git_repositories/save_strategy.py
"""Git repository save strategy implementation."""

from typing import List, Dict, Any

from src.operations.save.strategy import SaveEntityStrategy

# ... rest of file with updated imports ...
```

### Step 7: Update imports in git_repository restore_strategy.py

Edit file to fix imports:

```python
# src/entities/git_repositories/restore_strategy.py
"""Git repository restore strategy implementation."""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path

from src.operations.restore.strategy import RestoreEntityStrategy

# ... rest of file with updated imports ...
```

### Step 8: Add strategy existence tests

```python
# tests/unit/entities/git_repositories/test_entity_config.py
import importlib


@pytest.mark.unit
def test_git_repository_save_strategy_exists():
    """Test that git_repository save strategy exists at expected location."""
    module = importlib.import_module("src.entities.git_repositories.save_strategy")
    strategy_class = getattr(module, "GitRepositorySaveStrategy")
    assert strategy_class is not None


@pytest.mark.unit
def test_git_repository_restore_strategy_exists():
    """Test that git_repository restore strategy exists at expected location."""
    module = importlib.import_module("src.entities.git_repositories.restore_strategy")
    strategy_class = getattr(module, "GitRepositoryRestoreStrategy")
    assert strategy_class is not None
```

### Step 9: Run all git_repository tests

**Command:**
```bash
pdm run pytest tests/unit/entities/git_repositories/test_entity_config.py -v
```

**Expected Output:**
```
PASSED tests/unit/entities/git_repositories/test_entity_config.py::test_git_repository_entity_discovered
PASSED tests/unit/entities/git_repositories/test_entity_config.py::test_git_repository_entity_no_dependencies
PASSED tests/unit/entities/git_repositories/test_entity_config.py::test_git_repository_entity_enabled_by_default
PASSED tests/unit/entities/git_repositories/test_entity_config.py::test_git_repository_save_strategy_exists
PASSED tests/unit/entities/git_repositories/test_entity_config.py::test_git_repository_restore_strategy_exists
```

### Step 10: Commit git_repository entity migration

**Command:**
```bash
git add src/entities/git_repositories/entity_config.py
git add src/entities/git_repositories/save_strategy.py
git add src/entities/git_repositories/restore_strategy.py
git add tests/unit/entities/git_repositories/test_entity_config.py
git commit -s -m "$(cat <<'EOF'
feat: migrate git_repository entity to EntityRegistry

Add entity_config.py for git_repository entity and move strategies to entity
directory following convention-based structure.

- Add GitRepositoryEntityConfig with no dependencies
- Move GitRepositorySaveStrategy to src/entities/git_repositories/save_strategy.py
- Move GitRepositoryRestoreStrategy to src/entities/git_repositories/restore_strategy.py
- Update imports to use absolute paths
- Add tests for entity config discovery and strategy location

Part of Phase 3 Batch 1 migration.

Signed-off-by: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Update StrategyFactory for Batch 1

**Files:**
- Modify: `src/operations/strategy_factory.py`
- Create: `tests/unit/operations/test_strategy_factory_registry.py`

### Step 1: Write failing test for StrategyFactory with EntityRegistry

```python
# tests/unit/operations/test_strategy_factory_registry.py
"""Tests for StrategyFactory with EntityRegistry integration."""

import pytest
from unittest.mock import Mock
from src.operations.strategy_factory import StrategyFactory
from src.entities.registry import EntityRegistry


@pytest.mark.unit
def test_strategy_factory_accepts_registry():
    """Test that StrategyFactory accepts EntityRegistry parameter."""
    registry = EntityRegistry()
    config = Mock()  # ApplicationConfig for unmigrated entities

    factory = StrategyFactory(registry=registry, config=config)

    assert factory.registry == registry
    assert factory.config == config


@pytest.mark.unit
def test_strategy_factory_loads_labels_from_registry():
    """Test that StrategyFactory loads labels strategy from registry."""
    registry = EntityRegistry()
    config = Mock()
    factory = StrategyFactory(registry=registry, config=config)

    strategy = factory.load_save_strategy("labels")

    assert strategy is not None
    assert strategy.get_entity_name() == "labels"


@pytest.mark.unit
def test_strategy_factory_loads_milestones_from_registry():
    """Test that StrategyFactory loads milestones strategy from registry."""
    registry = EntityRegistry()
    config = Mock()
    factory = StrategyFactory(registry=registry, config=config)

    strategy = factory.load_save_strategy("milestones")

    assert strategy is not None
    assert strategy.get_entity_name() == "milestones"


@pytest.mark.unit
def test_strategy_factory_loads_git_repository_from_registry():
    """Test that StrategyFactory loads git_repository strategy from registry."""
    registry = EntityRegistry()
    config = Mock()
    factory = StrategyFactory(registry=registry, config=config)

    strategy = factory.load_save_strategy("git_repository")

    assert strategy is not None
    assert strategy.get_entity_name() == "git_repository"
```

### Step 2: Run test to verify it fails

**Command:**
```bash
pdm run pytest tests/unit/operations/test_strategy_factory_registry.py::test_strategy_factory_accepts_registry -v
```

**Expected Output:**
```
FAILED tests/unit/operations/test_strategy_factory_registry.py::test_strategy_factory_accepts_registry - TypeError: __init__() got an unexpected keyword argument 'registry'
```

### Step 3: Read current StrategyFactory implementation

**Command:**
```bash
cat src/operations/strategy_factory.py | head -50
```

### Step 4: Update StrategyFactory __init__ to accept registry

Edit `src/operations/strategy_factory.py`:

```python
# src/operations/strategy_factory.py
"""Factory for creating save and restore strategies."""

import importlib
import logging
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.config.settings import ApplicationConfig
    from src.entities.registry import EntityRegistry
    from src.operations.save.strategy import SaveEntityStrategy
    from src.operations.restore.strategy import RestoreEntityStrategy

logger = logging.getLogger(__name__)


class StrategyFactory:
    """Factory for creating entity strategies.

    Supports loading strategies from both EntityRegistry (new system)
    and ApplicationConfig (legacy system for unmigrated entities).
    """

    def __init__(
        self,
        registry: Optional["EntityRegistry"] = None,
        config: Optional["ApplicationConfig"] = None
    ):
        """Initialize strategy factory.

        Args:
            registry: EntityRegistry for migrated entities
            config: ApplicationConfig for unmigrated entities (legacy)
        """
        self.registry = registry
        self.config = config

    def load_save_strategy(self, entity_name: str) -> Optional["SaveEntityStrategy"]:
        """Load save strategy for entity by name.

        Args:
            entity_name: Name of entity (e.g., "labels", "issues")

        Returns:
            Save strategy instance or None if not found
        """
        # Try loading from registry first (migrated entities)
        if self.registry:
            try:
                entity = self.registry.get_entity(entity_name)
                return self._load_save_strategy_from_registry(entity)
            except ValueError:
                # Entity not in registry, try ApplicationConfig
                pass

        # Fall back to ApplicationConfig (unmigrated entities)
        if self.config:
            return self._load_save_strategy_from_config(entity_name)

        return None

    def _load_save_strategy_from_registry(self, entity) -> Optional["SaveEntityStrategy"]:
        """Load save strategy from registry entity using convention.

        Args:
            entity: RegisteredEntity instance

        Returns:
            Save strategy instance or None
        """
        # Check for override in entity config
        if entity.config.save_strategy_class:
            return entity.config.save_strategy_class()

        # Use convention: src.entities.{name}.save_strategy.{Name}SaveStrategy
        entity_name = entity.config.name
        module_name = f"src.entities.{entity_name}.save_strategy"
        class_name = self._to_class_name(entity_name) + "SaveStrategy"

        try:
            module = importlib.import_module(module_name)
            strategy_class = getattr(module, class_name)
            return strategy_class()
        except (ImportError, AttributeError) as e:
            logger.warning(
                f"Could not load save strategy for {entity_name}: {e}"
            )
            return None

    def _load_save_strategy_from_config(self, entity_name: str) -> Optional["SaveEntityStrategy"]:
        """Load save strategy from ApplicationConfig (legacy).

        Args:
            entity_name: Entity name

        Returns:
            Save strategy instance or None
        """
        # TODO: Implement ApplicationConfig loading for unmigrated entities
        logger.warning(f"ApplicationConfig loading not yet implemented for {entity_name}")
        return None

    def _to_class_name(self, entity_name: str) -> str:
        """Convert entity name to class name.

        Args:
            entity_name: Snake case name (e.g., "pr_review_comments")

        Returns:
            PascalCase name (e.g., "PrReviewComments")
        """
        # Handle special case: git_repository -> GitRepository
        parts = entity_name.split("_")
        return "".join(word.capitalize() for word in parts)
```

### Step 5: Run test to verify StrategyFactory accepts registry

**Command:**
```bash
pdm run pytest tests/unit/operations/test_strategy_factory_registry.py::test_strategy_factory_accepts_registry -v
```

**Expected Output:**
```
PASSED tests/unit/operations/test_strategy_factory_registry.py::test_strategy_factory_accepts_registry
```

### Step 6: Run tests to verify strategy loading

**Command:**
```bash
pdm run pytest tests/unit/operations/test_strategy_factory_registry.py -v
```

**Expected Output:**
```
PASSED tests/unit/operations/test_strategy_factory_registry.py::test_strategy_factory_accepts_registry
PASSED tests/unit/operations/test_strategy_factory_registry.py::test_strategy_factory_loads_labels_from_registry
PASSED tests/unit/operations/test_strategy_factory_registry.py::test_strategy_factory_loads_milestones_from_registry
PASSED tests/unit/operations/test_strategy_factory_registry.py::test_strategy_factory_loads_git_repository_from_registry
```

### Step 7: Add test for restore strategy loading

```python
# tests/unit/operations/test_strategy_factory_registry.py

@pytest.mark.unit
def test_strategy_factory_loads_restore_strategy():
    """Test that StrategyFactory loads restore strategies from registry."""
    registry = EntityRegistry()
    config = Mock()
    factory = StrategyFactory(registry=registry, config=config)

    strategy = factory.load_restore_strategy("labels")

    assert strategy is not None
    # Note: restore strategy requires conflict_strategy parameter
```

### Step 8: Implement load_restore_strategy method

Add to `src/operations/strategy_factory.py`:

```python
    def load_restore_strategy(self, entity_name: str, **kwargs) -> Optional["RestoreEntityStrategy"]:
        """Load restore strategy for entity by name.

        Args:
            entity_name: Name of entity (e.g., "labels", "issues")
            **kwargs: Additional arguments for strategy instantiation

        Returns:
            Restore strategy instance or None if not found
        """
        # Try loading from registry first (migrated entities)
        if self.registry:
            try:
                entity = self.registry.get_entity(entity_name)
                return self._load_restore_strategy_from_registry(entity, **kwargs)
            except ValueError:
                # Entity not in registry, try ApplicationConfig
                pass

        # Fall back to ApplicationConfig (unmigrated entities)
        if self.config:
            return self._load_restore_strategy_from_config(entity_name, **kwargs)

        return None

    def _load_restore_strategy_from_registry(self, entity, **kwargs) -> Optional["RestoreEntityStrategy"]:
        """Load restore strategy from registry entity using convention.

        Args:
            entity: RegisteredEntity instance
            **kwargs: Additional arguments for strategy instantiation

        Returns:
            Restore strategy instance or None
        """
        # Check for override in entity config
        if entity.config.restore_strategy_class:
            return entity.config.restore_strategy_class(**kwargs)

        # Use convention: src.entities.{name}.restore_strategy.{Name}RestoreStrategy
        entity_name = entity.config.name
        module_name = f"src.entities.{entity_name}.restore_strategy"
        class_name = self._to_class_name(entity_name) + "RestoreStrategy"

        try:
            module = importlib.import_module(module_name)
            strategy_class = getattr(module, class_name)
            return strategy_class(**kwargs)
        except (ImportError, AttributeError) as e:
            logger.warning(
                f"Could not load restore strategy for {entity_name}: {e}"
            )
            return None

    def _load_restore_strategy_from_config(self, entity_name: str, **kwargs) -> Optional["RestoreEntityStrategy"]:
        """Load restore strategy from ApplicationConfig (legacy).

        Args:
            entity_name: Entity name
            **kwargs: Additional arguments for strategy instantiation

        Returns:
            Restore strategy instance or None
        """
        # TODO: Implement ApplicationConfig loading for unmigrated entities
        logger.warning(f"ApplicationConfig loading not yet implemented for {entity_name}")
        return None
```

### Step 9: Run all StrategyFactory tests

**Command:**
```bash
pdm run pytest tests/unit/operations/test_strategy_factory_registry.py -v
```

**Expected Output:**
```
PASSED (all tests)
```

### Step 10: Run full test suite to check for regressions

**Command:**
```bash
pdm run pytest tests/unit/ -v --tb=short
```

**Expected Output:**
```
(tests pass, some integration tests may fail - that's expected until orchestrators are updated)
```

### Step 11: Commit StrategyFactory updates

**Command:**
```bash
git add src/operations/strategy_factory.py
git add tests/unit/operations/test_strategy_factory_registry.py
git commit -s -m "$(cat <<'EOF'
feat: update StrategyFactory to support EntityRegistry

Add EntityRegistry support to StrategyFactory with convention-based strategy
loading. Maintains ApplicationConfig fallback for unmigrated entities.

- Add registry parameter to StrategyFactory constructor
- Implement load_save_strategy with registry support
- Implement load_restore_strategy with registry support
- Add convention-based strategy discovery (_to_class_name helper)
- Add comprehensive tests for registry-based strategy loading

StrategyFactory now tries EntityRegistry first, then falls back to
ApplicationConfig for entities not yet migrated.

Part of Phase 3 Batch 1 migration.

Signed-off-by: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Verify Batch 1 integration

**Files:**
- Create: `tests/integration/test_batch1_integration.py`

### Step 1: Write integration test for Batch 1 entities

```python
# tests/integration/test_batch1_integration.py
"""Integration tests for Batch 1 entity migration."""

import pytest
from src.entities.registry import EntityRegistry
from src.operations.strategy_factory import StrategyFactory


@pytest.mark.integration
def test_batch1_entities_discovered():
    """Test that all Batch 1 entities are discovered."""
    registry = EntityRegistry()

    entity_names = registry.get_all_entity_names()

    assert "labels" in entity_names
    assert "milestones" in entity_names
    assert "git_repository" in entity_names


@pytest.mark.integration
def test_batch1_entities_enabled_by_default():
    """Test that Batch 1 entities are enabled by default."""
    registry = EntityRegistry()

    enabled_entities = registry.get_enabled_entities()
    enabled_names = [e.config.name for e in enabled_entities]

    assert "labels" in enabled_names
    assert "milestones" in enabled_names
    assert "git_repository" in enabled_names


@pytest.mark.integration
def test_batch1_entities_no_dependencies():
    """Test that Batch 1 entities have no dependencies."""
    registry = EntityRegistry()

    for entity_name in ["labels", "milestones", "git_repository"]:
        entity = registry.get_entity(entity_name)
        assert entity.get_dependencies() == []


@pytest.mark.integration
def test_batch1_save_strategies_load():
    """Test that save strategies load for Batch 1 entities."""
    registry = EntityRegistry()
    factory = StrategyFactory(registry=registry, config=None)

    for entity_name in ["labels", "milestones", "git_repository"]:
        strategy = factory.load_save_strategy(entity_name)
        assert strategy is not None
        assert strategy.get_entity_name() == entity_name


@pytest.mark.integration
def test_batch1_execution_order():
    """Test that Batch 1 entities can be sorted (no circular deps)."""
    registry = EntityRegistry()

    enabled_entities = registry.get_enabled_entities()

    # Should not raise ValueError for circular dependency
    assert len(enabled_entities) >= 3
```

### Step 2: Run integration tests

**Command:**
```bash
pdm run pytest tests/integration/test_batch1_integration.py -v
```

**Expected Output:**
```
PASSED tests/integration/test_batch1_integration.py::test_batch1_entities_discovered
PASSED tests/integration/test_batch1_integration.py::test_batch1_entities_enabled_by_default
PASSED tests/integration/test_batch1_integration.py::test_batch1_entities_no_dependencies
PASSED tests/integration/test_batch1_integration.py::test_batch1_save_strategies_load
PASSED tests/integration/test_batch1_integration.py::test_batch1_execution_order
```

### Step 3: Run all fast tests

**Command:**
```bash
make test-fast
```

**Expected Output:**
```
(all unit and integration tests pass)
```

### Step 4: Commit integration tests

**Command:**
```bash
git add tests/integration/test_batch1_integration.py
git commit -s -m "$(cat <<'EOF'
test: add Batch 1 integration tests

Add comprehensive integration tests for Batch 1 entity migration including
entity discovery, default state, dependency validation, and strategy loading.

- Test all 3 entities discovered
- Test enabled by default
- Test no dependencies
- Test save strategies load correctly
- Test execution order (topological sort)

All integration tests passing for Batch 1.

Part of Phase 3 Batch 1 migration.

Signed-off-by: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Final Batch 1 commit

### Step 1: Run complete test suite

**Command:**
```bash
make check
```

**Expected Output:**
```
(all quality checks pass except possibly container tests)
```

### Step 2: Review git log

**Command:**
```bash
git log --oneline -10
```

**Expected Output:**
```
<hash> test: add Batch 1 integration tests
<hash> feat: update StrategyFactory to support EntityRegistry
<hash> feat: migrate git_repository entity to EntityRegistry
<hash> feat: migrate milestones entity to EntityRegistry
<hash> feat: migrate labels entity to EntityRegistry
```

### Step 3: Create final Batch 1 summary commit tag

**Command:**
```bash
git tag -a phase3-batch1-complete -m "Phase 3 Batch 1 Complete: Independent entities migrated to EntityRegistry"
```

### Step 4: Push branch and tags

**Command:**
```bash
git push origin feature/entity-registry-system && git push origin --tags
```

---

## Success Criteria

Batch 1 is complete when:
- ✅ Labels entity migrated with entity_config.py and moved strategies
- ✅ Milestones entity migrated with entity_config.py and moved strategies
- ✅ Git_repository entity migrated with entity_config.py and moved strategies
- ✅ StrategyFactory accepts EntityRegistry parameter
- ✅ StrategyFactory loads strategies from registry by convention
- ✅ All unit tests passing
- ✅ All integration tests passing
- ✅ No circular dependencies detected
- ✅ All 3 entities discovered and enabled by default

## Next Steps

After Batch 1 completion:
- Proceed to Batch 2 implementation plan (issues domain entities)
- Update orchestrators will happen after all 3 batches complete

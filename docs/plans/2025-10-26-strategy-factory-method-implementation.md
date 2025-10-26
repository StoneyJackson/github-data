# Strategy Factory Method Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement factory methods in EntityConfig protocol and all entities to eliminate TypeError workaround in StrategyFactory and enable explicit dependency injection.

**Architecture:** Add `create_save_strategy()` and `create_restore_strategy()` static methods to EntityConfig protocol. Update entity generator to create default zero-arg factory implementations. Migrate all 10 entities to use factory methods. Refactor StrategyFactory to delegate instantiation to entity configs.

**Tech Stack:** Python 3.10+, Jinja2 templates, pytest, mypy

---

## Phase 1: Core Infrastructure

### Task 1: Update EntityConfig Protocol

**Files:**
- Modify: `src/entities/base.py:7-22`
- Test: `tests/unit/entities/test_base.py` (create if needed)

**Step 1: Write the failing test**

Create test file if it doesn't exist:

```python
"""Tests for entity base protocols."""

import pytest
from typing import Optional
from src.entities.base import EntityConfig


def test_entity_config_has_factory_methods():
    """Verify EntityConfig protocol defines factory methods."""
    # This test validates protocol structure
    assert hasattr(EntityConfig, 'create_save_strategy')
    assert hasattr(EntityConfig, 'create_restore_strategy')


class MinimalTestConfig:
    """Minimal config for testing protocol compliance."""
    name = "test"
    env_var = "INCLUDE_TEST"
    default_value = True
    value_type = bool
    dependencies = []
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Test config"

    @staticmethod
    def create_save_strategy(**context):
        return None

    @staticmethod
    def create_restore_strategy(**context):
        return None


def test_config_implements_protocol():
    """Test that minimal config satisfies protocol."""
    config = MinimalTestConfig()
    assert config.name == "test"

    # Factory methods should be callable
    result = config.create_save_strategy()
    assert result is None

    result = config.create_restore_strategy()
    assert result is None


def test_factory_methods_accept_context():
    """Verify factory methods accept **context kwargs."""
    config = MinimalTestConfig()

    # Should accept arbitrary context
    result = config.create_save_strategy(git_service="test")
    assert result is None

    result = config.create_restore_strategy(
        git_service="test",
        conflict_strategy="skip",
        include_original_metadata=True
    )
    assert result is None
```

**Step 2: Run test to verify it fails**

Run: `pdm run pytest tests/unit/entities/test_base.py::test_entity_config_has_factory_methods -v`

Expected: FAIL - AttributeError or protocol validation error

**Step 3: Update EntityConfig protocol**

```python
# src/entities/base.py (lines 7-22, expand to add factory methods)
class EntityConfig(Protocol):
    """Protocol for entity configuration metadata.

    All entity configs must define these attributes to be discovered.
    """

    name: str  # Entity identifier (e.g., "comment_attachments")
    env_var: str  # Environment variable name
    default_value: Union[bool, Set[int]]  # Default enabled state
    value_type: Type  # bool or Union[bool, Set[int]]
    dependencies: List[str] = []  # List of entity names this depends on
    save_strategy_class: Optional[Type] = None  # Override auto-discovery
    restore_strategy_class: Optional[Type] = None  # Override auto-discovery
    storage_filename: Optional[str] = None  # Override convention
    description: str = ""  # Documentation

    @staticmethod
    def create_save_strategy(**context: Any) -> Optional["BaseSaveStrategy"]:
        """Factory method for creating save strategy instances.

        Args:
            **context: Available dependencies (git_service, etc.)

        Returns:
            Configured save strategy instance, or None if not applicable
        """
        ...

    @staticmethod
    def create_restore_strategy(**context: Any) -> Optional["BaseRestoreStrategy"]:
        """Factory method for creating restore strategy instances.

        Args:
            **context: Available dependencies (git_service, conflict_strategy, etc.)

        Returns:
            Configured restore strategy instance, or None if not applicable
        """
        ...
```

**Step 4: Run test to verify it passes**

Run: `pdm run pytest tests/unit/entities/test_base.py -v`

Expected: All tests PASS

**Step 5: Run type check**

Run: `pdm run mypy src/entities/base.py`

Expected: No errors

**Step 6: Commit**

```bash
git add src/entities/base.py tests/unit/entities/test_base.py
git commit -s -m "feat: add factory methods to EntityConfig protocol

Add create_save_strategy() and create_restore_strategy() static methods
to EntityConfig protocol. These methods enable each entity to control
its own instantiation logic and dependency injection.

This eliminates the need for TypeError workarounds in StrategyFactory.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 2: Update Entity Generator Template

**Files:**
- Modify: `src/tools/templates/entity_config_template.py.j2`
- Test: Generate test entity to verify template changes

**Step 1: Update template to include factory methods**

Add factory methods to the template after the description line:

```jinja2
"""Entity configuration for {{ entity_name }}.

This file was auto-generated by src/tools/generate_entity.py
"""
from typing import Union, Set, Optional, Any
from src.entities.base import EntityConfig


class {{ class_name }}(EntityConfig):
    """{{ description }}

    Auto-discovered by naming convention: *EntityConfig
    """

    name = "{{ entity_name }}"
    env_var = "{{ env_var }}"
    default_value = {{ default_value }}
    value_type = {{ value_type }}
    {% if dependencies %}
    dependencies = {{ dependencies }}
    {% else %}
    dependencies = []
    {% endif %}
    description = "{{ description }}"

    @staticmethod
    def create_save_strategy(**context: Any) -> Optional[Any]:
        """Create save strategy instance.

        Default implementation: instantiate with no arguments.
        Override this method if your strategy requires dependencies from context.

        Available context keys:
            - git_service: GitRepositoryService instance

        Args:
            **context: Available dependencies

        Returns:
            Strategy instance or None if not applicable
        """
        from src.entities.{{ entity_name }}.save_strategy import {{ save_strategy_class }}
        return {{ save_strategy_class }}()

    @staticmethod
    def create_restore_strategy(**context: Any) -> Optional[Any]:
        """Create restore strategy instance.

        Default implementation: instantiate with no arguments.
        Override this method if your strategy requires dependencies from context.

        Available context keys:
            - git_service: GitRepositoryService instance
            - conflict_strategy: Strategy for handling conflicts
            - include_original_metadata: Whether to preserve original metadata

        Args:
            **context: Available dependencies

        Returns:
            Strategy instance or None if not applicable
        """
        from src.entities.{{ entity_name }}.restore_strategy import {{ restore_strategy_class }}
        include_original_metadata = context.get('include_original_metadata', True)
        return {{ restore_strategy_class }}(include_original_metadata=include_original_metadata)
```

**Step 2: Generate test entity to verify template**

Run: `pdm run python -m src.tools.generate_entity --name cli_test_entity --type bool --default true --description "Test entity for CLI validation" --force`

Expected: Entity generated successfully

**Step 3: Verify generated files have factory methods**

Run: `cat src/entities/cli_test_entity/entity_config.py`

Expected: File contains both `create_save_strategy()` and `create_restore_strategy()` methods

**Step 4: Run basic import test**

Run: `pdm run python -c "from src.entities.cli_test_entity.entity_config import CliTestEntityEntityConfig; print('Import successful')"`

Expected: "Import successful"

**Step 5: Clean up test entity**

Run: `rm -rf src/entities/cli_test_entity`

**Step 6: Commit**

```bash
git add src/tools/templates/entity_config_template.py.j2
git commit -s -m "feat: update entity generator template with factory methods

Update entity_config_template.py.j2 to include create_save_strategy()
and create_restore_strategy() factory methods with default zero-arg
implementations.

Generated entities will have working factory methods that can be
overridden for custom dependency injection.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 2: Simple Entities Migration (7 entities)

These entities have zero-arg or `include_original_metadata` constructors and need only the standard factory methods.

### Task 3: Migrate Comments Entity

**Files:**
- Modify: `src/entities/comments/entity_config.py`
- Test: Verify factory methods work

**Step 1: Write test for factory methods**

Create/update: `tests/unit/entities/comments/test_entity_config.py`

```python
"""Tests for comments entity configuration."""

import pytest
from src.entities.comments.entity_config import CommentsEntityConfig


def test_comments_create_save_strategy():
    """Test save strategy factory method."""
    strategy = CommentsEntityConfig.create_save_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "comments"


def test_comments_create_restore_strategy_default():
    """Test restore strategy factory with defaults."""
    strategy = CommentsEntityConfig.create_restore_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "comments"
    # Default: include_original_metadata=True
    assert strategy._include_original_metadata is True


def test_comments_create_restore_strategy_custom():
    """Test restore strategy factory with custom metadata flag."""
    strategy = CommentsEntityConfig.create_restore_strategy(
        include_original_metadata=False
    )
    assert strategy is not None
    assert strategy._include_original_metadata is False


def test_comments_factory_ignores_unknown_context():
    """Test that factory methods ignore unknown context keys."""
    strategy = CommentsEntityConfig.create_restore_strategy(
        unknown_key="should_be_ignored",
        include_original_metadata=False
    )
    assert strategy is not None
```

**Step 2: Run test to verify it fails**

Run: `pdm run pytest tests/unit/entities/comments/test_entity_config.py -v`

Expected: FAIL - Method not found

**Step 3: Add factory methods to CommentsEntityConfig**

```python
"""Comments entity configuration for EntityRegistry."""

from typing import Optional, Any


class CommentsEntityConfig:
    """Configuration for comments entity.

    Comments depend on issues and are enabled by default.
    """

    name = "comments"
    env_var = "INCLUDE_COMMENTS"
    default_value = True
    value_type = bool
    dependencies = ["issues"]
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Issue comments and discussions"

    @staticmethod
    def create_save_strategy(**context: Any) -> Optional[Any]:
        """Create save strategy instance.

        Args:
            **context: Available dependencies (unused for comments)

        Returns:
            CommentsSaveStrategy instance
        """
        from src.entities.comments.save_strategy import CommentsSaveStrategy
        return CommentsSaveStrategy()

    @staticmethod
    def create_restore_strategy(**context: Any) -> Optional[Any]:
        """Create restore strategy instance.

        Args:
            **context: Available dependencies
                - include_original_metadata: Preserve original metadata (default: True)

        Returns:
            CommentsRestoreStrategy instance
        """
        from src.entities.comments.restore_strategy import CommentsRestoreStrategy
        include_original_metadata = context.get('include_original_metadata', True)
        return CommentsRestoreStrategy(include_original_metadata=include_original_metadata)
```

**Step 4: Run test to verify it passes**

Run: `pdm run pytest tests/unit/entities/comments/test_entity_config.py -v`

Expected: All tests PASS

**Step 5: Run type check**

Run: `pdm run mypy src/entities/comments/entity_config.py`

Expected: No errors

**Step 6: Commit**

```bash
git add src/entities/comments/entity_config.py tests/unit/entities/comments/test_entity_config.py
git commit -s -m "feat: add factory methods to comments entity

Add create_save_strategy() and create_restore_strategy() to
CommentsEntityConfig. Factory methods handle include_original_metadata
parameter with sensible default.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: Migrate Issues Entity

**Files:**
- Modify: `src/entities/issues/entity_config.py`
- Test: `tests/unit/entities/issues/test_entity_config.py`

**Step 1: Write test for factory methods**

```python
"""Tests for issues entity configuration."""

import pytest
from src.entities.issues.entity_config import IssuesEntityConfig


def test_issues_create_save_strategy():
    """Test save strategy factory method."""
    strategy = IssuesEntityConfig.create_save_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "issues"


def test_issues_create_restore_strategy_default():
    """Test restore strategy factory with defaults."""
    strategy = IssuesEntityConfig.create_restore_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "issues"
    assert strategy._include_original_metadata is True


def test_issues_create_restore_strategy_custom():
    """Test restore strategy factory with custom metadata flag."""
    strategy = IssuesEntityConfig.create_restore_strategy(
        include_original_metadata=False
    )
    assert strategy is not None
    assert strategy._include_original_metadata is False
```

**Step 2: Run test to verify it fails**

Run: `pdm run pytest tests/unit/entities/issues/test_entity_config.py -v`

Expected: FAIL

**Step 3: Add factory methods to IssuesEntityConfig**

```python
"""Issues entity configuration for EntityRegistry."""

from typing import Optional, Any


class IssuesEntityConfig:
    """Configuration for issues entity.

    Issues depend on labels and milestones, enabled by default.
    """

    name = "issues"
    env_var = "INCLUDE_ISSUES"
    default_value = True
    value_type = bool
    dependencies = ["labels", "milestones"]
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Repository issues and metadata"

    @staticmethod
    def create_save_strategy(**context: Any) -> Optional[Any]:
        """Create save strategy instance.

        Args:
            **context: Available dependencies (unused)

        Returns:
            IssuesSaveStrategy instance
        """
        from src.entities.issues.save_strategy import IssuesSaveStrategy
        return IssuesSaveStrategy()

    @staticmethod
    def create_restore_strategy(**context: Any) -> Optional[Any]:
        """Create restore strategy instance.

        Args:
            **context: Available dependencies
                - include_original_metadata: Preserve original metadata (default: True)

        Returns:
            IssuesRestoreStrategy instance
        """
        from src.entities.issues.restore_strategy import IssuesRestoreStrategy
        include_original_metadata = context.get('include_original_metadata', True)
        return IssuesRestoreStrategy(include_original_metadata=include_original_metadata)
```

**Step 4: Run test to verify it passes**

Run: `pdm run pytest tests/unit/entities/issues/test_entity_config.py -v`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/entities/issues/entity_config.py tests/unit/entities/issues/test_entity_config.py
git commit -s -m "feat: add factory methods to issues entity

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 5: Migrate Milestones Entity

**Files:**
- Modify: `src/entities/milestones/entity_config.py`
- Test: `tests/unit/entities/milestones/test_entity_config.py`

**Step 1: Check current milestone strategy constructor**

Run: `grep -n "def __init__" src/entities/milestones/restore_strategy.py`

Expected: Shows constructor signature

**Step 2: Write and run test**

Follow same pattern as Task 4:
- Write test for factory methods
- Run test (should fail)
- Add factory methods with appropriate constructor params
- Run test (should pass)
- Commit

**Step 3: Commit**

```bash
git add src/entities/milestones/entity_config.py tests/unit/entities/milestones/test_entity_config.py
git commit -s -m "feat: add factory methods to milestones entity

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 6: Migrate Pull Requests Entity

**Files:**
- Modify: `src/entities/pull_requests/entity_config.py`
- Test: `tests/unit/entities/pull_requests/test_entity_config.py`

Follow same TDD pattern as Task 4-5.

**Commit:**

```bash
git add src/entities/pull_requests/entity_config.py tests/unit/entities/pull_requests/test_entity_config.py
git commit -s -m "feat: add factory methods to pull_requests entity

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 7: Migrate PR Reviews Entity

**Files:**
- Modify: `src/entities/pr_reviews/entity_config.py`
- Test: `tests/unit/entities/pr_reviews/test_entity_config.py`

Follow same TDD pattern.

**Commit:**

```bash
git add src/entities/pr_reviews/entity_config.py tests/unit/entities/pr_reviews/test_entity_config.py
git commit -s -m "feat: add factory methods to pr_reviews entity

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 8: Migrate PR Comments Entity

**Files:**
- Modify: `src/entities/pr_comments/entity_config.py`
- Test: `tests/unit/entities/pr_comments/test_entity_config.py`

Follow same TDD pattern.

**Commit:**

```bash
git add src/entities/pr_comments/entity_config.py tests/unit/entities/pr_comments/test_entity_config.py
git commit -s -m "feat: add factory methods to pr_comments entity

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 9: Migrate PR Review Comments Entity

**Files:**
- Modify: `src/entities/pr_review_comments/entity_config.py`
- Test: `tests/unit/entities/pr_review_comments/test_entity_config.py`

Follow same TDD pattern.

**Commit:**

```bash
git add src/entities/pr_review_comments/entity_config.py tests/unit/entities/pr_review_comments/test_entity_config.py
git commit -s -m "feat: add factory methods to pr_review_comments entity

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 3: Complex Entities Migration

### Task 10: Migrate Labels Entity (Optional Dependency)

**Files:**
- Modify: `src/entities/labels/entity_config.py`
- Test: `tests/unit/entities/labels/test_entity_config.py`

**Step 1: Write test for conflict_strategy handling**

```python
"""Tests for labels entity configuration."""

import pytest
from src.entities.labels.entity_config import LabelsEntityConfig
from src.entities.labels.conflict_strategies import LabelConflictStrategy


def test_labels_create_save_strategy():
    """Test save strategy factory method."""
    strategy = LabelsEntityConfig.create_save_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "labels"


def test_labels_create_restore_strategy_default():
    """Test restore strategy factory with default conflict strategy."""
    strategy = LabelsEntityConfig.create_restore_strategy()
    assert strategy is not None
    assert strategy.get_entity_name() == "labels"
    # Default should be SKIP
    assert strategy._conflict_strategy == LabelConflictStrategy.SKIP


def test_labels_create_restore_strategy_custom():
    """Test restore strategy factory with custom conflict strategy."""
    strategy = LabelsEntityConfig.create_restore_strategy(
        conflict_strategy=LabelConflictStrategy.REPLACE
    )
    assert strategy is not None
    assert strategy._conflict_strategy == LabelConflictStrategy.REPLACE


def test_labels_create_restore_strategy_ignores_metadata():
    """Test that labels factory ignores include_original_metadata."""
    # Labels don't use this parameter
    strategy = LabelsEntityConfig.create_restore_strategy(
        include_original_metadata=False,
        conflict_strategy=LabelConflictStrategy.SKIP
    )
    assert strategy is not None
```

**Step 2: Run test to verify it fails**

Run: `pdm run pytest tests/unit/entities/labels/test_entity_config.py -v`

Expected: FAIL

**Step 3: Add factory methods to LabelsEntityConfig**

```python
"""Labels entity configuration for EntityRegistry."""

from typing import Optional, Any


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
    save_strategy_class = None
    restore_strategy_class = None
    storage_filename = None
    description = "Repository labels for issue/PR categorization"

    @staticmethod
    def create_save_strategy(**context: Any) -> Optional[Any]:
        """Create save strategy instance.

        Args:
            **context: Available dependencies (unused)

        Returns:
            LabelsSaveStrategy instance
        """
        from src.entities.labels.save_strategy import LabelsSaveStrategy
        return LabelsSaveStrategy()

    @staticmethod
    def create_restore_strategy(**context: Any) -> Optional[Any]:
        """Create restore strategy instance.

        Args:
            **context: Available dependencies
                - conflict_strategy: How to handle label conflicts (default: SKIP)

        Returns:
            LabelsRestoreStrategy instance
        """
        from src.entities.labels.restore_strategy import LabelsRestoreStrategy
        from src.entities.labels.conflict_strategies import LabelConflictStrategy

        conflict_strategy = context.get('conflict_strategy', LabelConflictStrategy.SKIP)
        return LabelsRestoreStrategy(conflict_strategy=conflict_strategy)
```

**Step 4: Run test to verify it passes**

Run: `pdm run pytest tests/unit/entities/labels/test_entity_config.py -v`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/entities/labels/entity_config.py tests/unit/entities/labels/test_entity_config.py
git commit -s -m "feat: add factory methods to labels entity

Add factory methods with conflict_strategy parameter handling.
Default conflict strategy is SKIP, can be overridden via context.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 11: Migrate Git Repository Entity (Required Dependency)

**Files:**
- Modify: `src/entities/git_repositories/entity_config.py`
- Test: `tests/unit/entities/git_repositories/test_entity_config.py`

**Step 1: Write test for required git_service**

```python
"""Tests for git_repositories entity configuration."""

import pytest
from unittest.mock import Mock
from src.entities.git_repositories.entity_config import GitRepositoryEntityConfig


def test_git_repository_create_save_strategy_requires_git_service():
    """Test that save strategy requires git_service."""
    with pytest.raises(ValueError, match="git_service"):
        GitRepositoryEntityConfig.create_save_strategy()


def test_git_repository_create_save_strategy_with_service():
    """Test save strategy creation with git_service."""
    mock_service = Mock()
    strategy = GitRepositoryEntityConfig.create_save_strategy(git_service=mock_service)
    assert strategy is not None
    assert strategy._git_service is mock_service


def test_git_repository_create_restore_strategy_requires_git_service():
    """Test that restore strategy requires git_service."""
    with pytest.raises(ValueError, match="git_service"):
        GitRepositoryEntityConfig.create_restore_strategy()


def test_git_repository_create_restore_strategy_with_service():
    """Test restore strategy creation with git_service."""
    mock_service = Mock()
    strategy = GitRepositoryEntityConfig.create_restore_strategy(git_service=mock_service)
    assert strategy is not None
    assert strategy._git_service is mock_service


def test_git_repository_factory_ignores_other_context():
    """Test that factory ignores irrelevant context keys."""
    mock_service = Mock()
    strategy = GitRepositoryEntityConfig.create_restore_strategy(
        git_service=mock_service,
        include_original_metadata=True,  # Should be ignored
        conflict_strategy="skip"  # Should be ignored
    )
    assert strategy is not None
```

**Step 2: Run test to verify it fails**

Run: `pdm run pytest tests/unit/entities/git_repositories/test_entity_config.py -v`

Expected: FAIL

**Step 3: Add factory methods to GitRepositoryEntityConfig**

```python
"""Git repository entity configuration for EntityRegistry."""

from typing import Optional, Any


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

    @staticmethod
    def create_save_strategy(**context: Any) -> Optional[Any]:
        """Create save strategy instance.

        Args:
            **context: Available dependencies
                - git_service: GitRepositoryService instance (REQUIRED)

        Returns:
            GitRepositorySaveStrategy instance

        Raises:
            ValueError: If git_service not provided
        """
        from src.entities.git_repositories.save_strategy import GitRepositorySaveStrategy

        git_service = context.get('git_service')
        if git_service is None:
            raise ValueError(
                "git_repository save strategy requires 'git_service' in context"
            )
        return GitRepositorySaveStrategy(git_service)

    @staticmethod
    def create_restore_strategy(**context: Any) -> Optional[Any]:
        """Create restore strategy instance.

        Args:
            **context: Available dependencies
                - git_service: GitRepositoryService instance (REQUIRED)

        Returns:
            GitRepositoryRestoreStrategy instance

        Raises:
            ValueError: If git_service not provided
        """
        from src.entities.git_repositories.restore_strategy import GitRepositoryRestoreStrategy

        git_service = context.get('git_service')
        if git_service is None:
            raise ValueError(
                "git_repository restore strategy requires 'git_service' in context"
            )
        return GitRepositoryRestoreStrategy(git_service)
```

**Step 4: Run test to verify it passes**

Run: `pdm run pytest tests/unit/entities/git_repositories/test_entity_config.py -v`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/entities/git_repositories/entity_config.py tests/unit/entities/git_repositories/test_entity_config.py
git commit -s -m "feat: add factory methods to git_repository entity

Add factory methods that require git_service dependency. Methods
raise ValueError if git_service is not provided in context.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 12: Migrate Sub-Issues Entity

**Files:**
- Modify: `src/entities/sub_issues/entity_config.py`
- Test: `tests/unit/entities/sub_issues/test_entity_config.py`

**Step 1: Check sub-issues constructor signature**

Run: `grep -n "def __init__" src/entities/sub_issues/restore_strategy.py`

Expected: Shows constructor parameters

**Step 2: Write and run test**

Follow TDD pattern based on actual constructor signature.

**Step 3: Add factory methods**

Based on constructor, add appropriate factory methods.

**Step 4: Commit**

```bash
git add src/entities/sub_issues/entity_config.py tests/unit/entities/sub_issues/test_entity_config.py
git commit -s -m "feat: add factory methods to sub_issues entity

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 4: StrategyFactory Refactoring

### Task 13: Refactor create_save_strategies()

**Files:**
- Modify: `src/operations/strategy_factory.py:26-51`
- Test: `tests/unit/operations/test_strategy_factory.py`

**Step 1: Write test for new factory method delegation**

```python
"""Tests for StrategyFactory."""

import pytest
from unittest.mock import Mock, MagicMock
from src.operations.strategy_factory import StrategyFactory


def test_create_save_strategies_uses_factory_methods(mock_registry):
    """Test that create_save_strategies delegates to entity factory methods."""
    # Setup mock entity with factory method
    mock_entity = Mock()
    mock_entity.config.name = "test_entity"
    mock_entity.config.save_strategy_class = Mock()
    mock_strategy = Mock()
    mock_entity.config.create_save_strategy = Mock(return_value=mock_strategy)

    mock_registry.get_enabled_entities.return_value = [mock_entity]

    factory = StrategyFactory(mock_registry)
    mock_git_service = Mock()

    strategies = factory.create_save_strategies(git_service=mock_git_service)

    # Verify factory method was called with context
    mock_entity.config.create_save_strategy.assert_called_once()
    call_kwargs = mock_entity.config.create_save_strategy.call_args[1]
    assert call_kwargs['git_service'] is mock_git_service

    # Verify strategy was added to list
    assert mock_strategy in strategies


def test_create_save_strategies_skips_none_results(mock_registry):
    """Test that None results from factory are skipped."""
    mock_entity = Mock()
    mock_entity.config.name = "test_entity"
    mock_entity.config.save_strategy_class = Mock()
    mock_entity.config.create_save_strategy = Mock(return_value=None)

    mock_registry.get_enabled_entities.return_value = [mock_entity]

    factory = StrategyFactory(mock_registry)
    strategies = factory.create_save_strategies()

    assert len(strategies) == 0


def test_create_save_strategies_raises_on_factory_error(mock_registry):
    """Test that factory errors are re-raised as RuntimeError."""
    mock_entity = Mock()
    mock_entity.config.name = "failing_entity"
    mock_entity.config.save_strategy_class = Mock()
    mock_entity.config.create_save_strategy = Mock(
        side_effect=ValueError("Missing dependency")
    )

    mock_registry.get_enabled_entities.return_value = [mock_entity]

    factory = StrategyFactory(mock_registry)

    with pytest.raises(RuntimeError, match="Failed to create save strategy"):
        factory.create_save_strategies()


@pytest.fixture
def mock_registry():
    """Provide mock EntityRegistry."""
    return Mock()
```

**Step 2: Run test to verify it fails**

Run: `pdm run pytest tests/unit/operations/test_strategy_factory.py::test_create_save_strategies_uses_factory_methods -v`

Expected: FAIL - Old implementation doesn't delegate to factory methods

**Step 3: Refactor create_save_strategies() method**

```python
def create_save_strategies(
    self,
    git_service: Optional[Any] = None,
    **additional_context: Any
) -> List["SaveEntityStrategy"]:
    """Create save strategies for all enabled entities.

    Args:
        git_service: Optional git service for entities that need it
        **additional_context: Additional context for strategy creation

    Returns:
        List of save strategy instances in dependency order

    Raises:
        RuntimeError: If any strategy factory method fails
    """
    context = {
        'git_service': git_service,
        **additional_context
    }

    strategies = []
    enabled_entities = self.registry.get_enabled_entities()

    for entity in enabled_entities:
        if entity.config.save_strategy_class is None:
            continue  # No save strategy - expected

        try:
            strategy = entity.config.create_save_strategy(**context)
            if strategy is not None:
                strategies.append(strategy)
        except Exception as e:
            raise RuntimeError(
                f"Failed to create save strategy for '{entity.config.name}': {e}. "
                f"Cannot proceed with save operation."
            ) from e

    return strategies
```

**Step 4: Run test to verify it passes**

Run: `pdm run pytest tests/unit/operations/test_strategy_factory.py::test_create_save_strategies_uses_factory_methods -v`

Expected: PASS

**Step 5: Run all strategy factory tests**

Run: `pdm run pytest tests/unit/operations/test_strategy_factory.py -v`

Expected: All PASS

**Step 6: Commit**

```bash
git add src/operations/strategy_factory.py tests/unit/operations/test_strategy_factory.py
git commit -s -m "refactor: delegate save strategy creation to entity factories

Replace direct instantiation with delegation to entity config factory
methods. Fail-fast on errors with clear RuntimeError messages.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 14: Refactor create_restore_strategies()

**Files:**
- Modify: `src/operations/strategy_factory.py:53-85`
- Test: `tests/unit/operations/test_strategy_factory.py`

**Step 1: Write test for restore factory delegation**

```python
def test_create_restore_strategies_uses_factory_methods(mock_registry):
    """Test that create_restore_strategies delegates to entity factory methods."""
    mock_entity = Mock()
    mock_entity.config.name = "test_entity"
    mock_entity.config.restore_strategy_class = Mock()
    mock_strategy = Mock()
    mock_entity.config.create_restore_strategy = Mock(return_value=mock_strategy)

    mock_registry.get_enabled_entities.return_value = [mock_entity]

    factory = StrategyFactory(mock_registry)
    mock_git_service = Mock()
    mock_conflict_strategy = Mock()

    strategies = factory.create_restore_strategies(
        git_service=mock_git_service,
        conflict_strategy=mock_conflict_strategy,
        include_original_metadata=False
    )

    # Verify factory method was called with all context
    mock_entity.config.create_restore_strategy.assert_called_once()
    call_kwargs = mock_entity.config.create_restore_strategy.call_args[1]
    assert call_kwargs['git_service'] is mock_git_service
    assert call_kwargs['conflict_strategy'] is mock_conflict_strategy
    assert call_kwargs['include_original_metadata'] is False

    assert mock_strategy in strategies


def test_create_restore_strategies_raises_on_factory_error(mock_registry):
    """Test that factory errors are re-raised as RuntimeError."""
    mock_entity = Mock()
    mock_entity.config.name = "failing_entity"
    mock_entity.config.restore_strategy_class = Mock()
    mock_entity.config.create_restore_strategy = Mock(
        side_effect=ValueError("Missing dependency")
    )

    mock_registry.get_enabled_entities.return_value = [mock_entity]

    factory = StrategyFactory(mock_registry)

    with pytest.raises(RuntimeError, match="Failed to create restore strategy"):
        factory.create_restore_strategies()
```

**Step 2: Run test to verify it fails**

Run: `pdm run pytest tests/unit/operations/test_strategy_factory.py::test_create_restore_strategies_uses_factory_methods -v`

Expected: FAIL

**Step 3: Refactor create_restore_strategies() method**

```python
def create_restore_strategies(
    self,
    git_service: Optional[Any] = None,
    conflict_strategy: Optional[Any] = None,
    include_original_metadata: bool = True,
    **additional_context: Any
) -> List["RestoreEntityStrategy"]:
    """Create restore strategies for all enabled entities.

    Args:
        git_service: Optional git service for entities that need it
        conflict_strategy: Optional conflict resolution strategy
        include_original_metadata: Whether to preserve original metadata
        **additional_context: Additional context for strategy creation

    Returns:
        List of restore strategy instances in dependency order

    Raises:
        RuntimeError: If any strategy factory method fails
    """
    context = {
        'git_service': git_service,
        'conflict_strategy': conflict_strategy,
        'include_original_metadata': include_original_metadata,
        **additional_context
    }

    strategies = []
    enabled_entities = self.registry.get_enabled_entities()

    for entity in enabled_entities:
        if entity.config.restore_strategy_class is None:
            continue  # No restore strategy - expected

        try:
            strategy = entity.config.create_restore_strategy(**context)
            if strategy is not None:
                strategies.append(strategy)
        except Exception as e:
            raise RuntimeError(
                f"Failed to create restore strategy for '{entity.config.name}': {e}. "
                f"Cannot proceed with restore operation."
            ) from e

    return strategies
```

**Step 4: Run test to verify it passes**

Run: `pdm run pytest tests/unit/operations/test_strategy_factory.py -v`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/operations/strategy_factory.py tests/unit/operations/test_strategy_factory.py
git commit -s -m "refactor: delegate restore strategy creation to entity factories

Replace direct instantiation and special-case logic with delegation
to entity config factory methods. Unified error handling.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 15: Remove Legacy Helper Methods

**Files:**
- Modify: `src/operations/strategy_factory.py:87-206`
- Test: Verify no imports reference removed methods

**Step 1: Search for references to helper methods**

Run: `grep -r "load_save_strategy\|load_restore_strategy" src/ tests/ --include="*.py"`

Expected: Only references in strategy_factory.py itself

**Step 2: Remove helper methods and conversion utilities**

Delete these methods from `src/operations/strategy_factory.py`:
- `load_save_strategy()` (lines ~87-132)
- `load_restore_strategy()` (lines ~134-178)
- `_to_directory_name()` (lines ~180-193)
- `_to_class_name()` (lines ~195-206)

Also remove the `import importlib` statement (line 3) as it's no longer needed.

**Step 3: Run all tests to verify nothing broke**

Run: `pdm run pytest tests/ -v -k strategy_factory`

Expected: All tests PASS

**Step 4: Run type check**

Run: `pdm run mypy src/operations/strategy_factory.py`

Expected: No errors

**Step 5: Verify final file is clean**

Run: `cat src/operations/strategy_factory.py`

Expected: File contains only:
- Imports (logging, typing, no importlib)
- StrategyFactory class with:
  - `__init__()`
  - `create_save_strategies()`
  - `create_restore_strategies()`

**Step 6: Commit**

```bash
git add src/operations/strategy_factory.py
git commit -s -m "refactor: remove legacy strategy loading methods

Remove load_save_strategy(), load_restore_strategy(), and helper
methods. All instantiation now delegated to entity factory methods.

Removes importlib dependency and TypeError workaround.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 5: Integration Testing and Verification

### Task 16: Integration Test - End-to-End Strategy Creation

**Files:**
- Test: `tests/integration/operations/test_strategy_factory_integration.py`

**Step 1: Write integration test**

```python
"""Integration tests for StrategyFactory with real entities."""

import pytest
from unittest.mock import Mock
from src.operations.strategy_factory import StrategyFactory
from src.entities.registry import EntityRegistry


@pytest.mark.integration
def test_create_save_strategies_all_entities():
    """Test creating save strategies for all real entities."""
    registry = EntityRegistry()

    # Enable all entities
    for entity_name in ["labels", "milestones", "issues", "comments",
                        "pull_requests", "pr_reviews", "pr_comments",
                        "pr_review_comments", "sub_issues"]:
        registry.enable_entity(entity_name)

    factory = StrategyFactory(registry)
    strategies = factory.create_save_strategies()

    # Should get strategies for all enabled entities
    assert len(strategies) == 9
    entity_names = [s.get_entity_name() for s in strategies]
    assert "labels" in entity_names
    assert "issues" in entity_names


@pytest.mark.integration
def test_create_save_strategies_with_git_repository():
    """Test creating save strategies including git_repository."""
    registry = EntityRegistry()
    registry.enable_entity("git_repository")

    factory = StrategyFactory(registry)
    mock_git_service = Mock()

    strategies = factory.create_save_strategies(git_service=mock_git_service)

    assert len(strategies) == 1
    assert strategies[0].get_entity_name() == "git_repository"
    assert strategies[0]._git_service is mock_git_service


@pytest.mark.integration
def test_create_restore_strategies_all_entities():
    """Test creating restore strategies for all real entities."""
    registry = EntityRegistry()

    for entity_name in ["labels", "milestones", "issues", "comments",
                        "pull_requests", "pr_reviews", "pr_comments",
                        "pr_review_comments", "sub_issues"]:
        registry.enable_entity(entity_name)

    factory = StrategyFactory(registry)
    strategies = factory.create_restore_strategies(
        include_original_metadata=False
    )

    assert len(strategies) == 9

    # Verify metadata flag was passed
    for strategy in strategies:
        if hasattr(strategy, '_include_original_metadata'):
            assert strategy._include_original_metadata is False


@pytest.mark.integration
def test_create_restore_strategies_labels_with_conflict_strategy():
    """Test labels restore with custom conflict strategy."""
    from src.entities.labels.conflict_strategies import LabelConflictStrategy

    registry = EntityRegistry()
    registry.enable_entity("labels")

    factory = StrategyFactory(registry)
    strategies = factory.create_restore_strategies(
        conflict_strategy=LabelConflictStrategy.REPLACE
    )

    assert len(strategies) == 1
    labels_strategy = strategies[0]
    assert labels_strategy._conflict_strategy == LabelConflictStrategy.REPLACE


@pytest.mark.integration
def test_git_repository_requires_git_service():
    """Test that git_repository raises clear error without git_service."""
    registry = EntityRegistry()
    registry.enable_entity("git_repository")

    factory = StrategyFactory(registry)

    with pytest.raises(RuntimeError, match="git_repository.*git_service"):
        factory.create_save_strategies()  # No git_service provided

    with pytest.raises(RuntimeError, match="git_repository.*git_service"):
        factory.create_restore_strategies()  # No git_service provided
```

**Step 2: Run integration tests**

Run: `pdm run pytest tests/integration/operations/test_strategy_factory_integration.py -v`

Expected: All tests PASS

**Step 3: Commit**

```bash
git add tests/integration/operations/test_strategy_factory_integration.py
git commit -s -m "test: add integration tests for strategy factory pattern

Verify end-to-end strategy creation with real entities, dependency
injection, and error handling.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 17: Run Full Test Suite

**Files:**
- Test: All tests

**Step 1: Run fast tests**

Run: `make test-fast`

Expected: All tests PASS

**Step 2: Run type checking**

Run: `make type-check`

Expected: No errors

**Step 3: Run linting**

Run: `make lint`

Expected: No errors

**Step 4: Run all quality checks**

Run: `make check`

Expected: All checks PASS

**Step 5: Document success**

If all checks pass, create success marker:

```bash
echo "✅ Strategy factory method implementation complete" > /tmp/implementation_success.txt
cat /tmp/implementation_success.txt
```

---

### Task 18: Update Documentation

**Files:**
- Modify: `docs/plans/2025-10-26-strategy-factory-method-design.md`

**Step 1: Mark design as implemented**

Change status from "Approved" to "Implemented":

```markdown
**Date:** 2025-10-26
**Status:** Implemented
**Implementation Date:** 2025-10-26
**Replaces:** TypeError workaround in StrategyFactory
```

**Step 2: Add implementation notes section**

Add at end of document:

```markdown
## Implementation Notes

**Implementation completed:** 2025-10-26

**Summary:**
- All 10 entities successfully migrated to factory method pattern
- StrategyFactory refactored to delegate to entity factory methods
- TypeError workaround eliminated
- All tests passing with new pattern

**Key Learnings:**
- Factory methods provide clear dependency requirements
- Fail-fast errors improve debugging experience
- Pattern scales well across simple and complex entities

**Files Changed:**
- `src/entities/base.py` - EntityConfig protocol
- `src/tools/templates/entity_config_template.py.j2` - Generator template
- All 10 entity configs in `src/entities/*/entity_config.py`
- `src/operations/strategy_factory.py` - Factory refactoring
- Comprehensive test coverage added
```

**Step 3: Commit documentation update**

```bash
git add docs/plans/2025-10-26-strategy-factory-method-design.md
git commit -s -m "docs: mark strategy factory design as implemented

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Success Criteria Verification

After completing all tasks, verify these criteria:

1. ✅ All 10 entities successfully instantiate strategies
2. ✅ Labels restore works with conflict_strategy
3. ✅ Git repository save/restore works with git_service
4. ✅ Missing required dependencies cause clear RuntimeError
5. ✅ No silent failures or TypeError workarounds
6. ✅ Entity generator creates both factory methods
7. ✅ All tests pass with new pattern

**Verification command:**

```bash
pdm run pytest tests/ -v -m "not container" && \
pdm run mypy src/ && \
echo "✅ All success criteria met"
```

---

## Rollback Plan

If critical issues arise:

1. **Revert to design phase:**
   ```bash
   git reset --hard origin/main
   git checkout -b feature/entity-registry-system-v2
   ```

2. **Partial rollback (keep protocol, revert factory):**
   ```bash
   git revert <commit-hash-of-factory-refactor>
   ```

3. **Keep new code, restore TypeError handling temporarily:**
   - Add try/except TypeError in StrategyFactory as emergency fallback
   - File bug to track proper fix

---

## Notes

- **DRY:** Factory methods share identical structure via template
- **YAGNI:** Only add context parameters that entities actually use
- **TDD:** Write tests first for every entity migration
- **Frequent commits:** One commit per entity, per phase milestone
- **Clean Code:** Factory methods follow Single Responsibility (instantiation only)

**Estimated time:** 4-6 hours total
- Phase 1: 30 minutes
- Phase 2: 2 hours
- Phase 3: 1 hour
- Phase 4: 1 hour
- Phase 5: 30-60 minutes

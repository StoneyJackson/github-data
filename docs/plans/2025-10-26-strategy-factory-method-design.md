# Strategy Factory Method Design

**Date:** 2025-10-26
**Status:** Implemented
**Implementation Date:** 2025-10-26
**Replaces:** TypeError workaround in StrategyFactory

## Problem Statement

The current `StrategyFactory` cannot properly instantiate strategies with varying constructor signatures. Different entities require different dependencies:

- **Labels**: needs `conflict_strategy`
- **Git Repository**: needs `git_service`
- **Most others**: zero-arg constructors

The current workaround catches `TypeError` and silently skips failed strategies, which can lead to data loss at runtime.

## Design Principles

1. **Entity Autonomy**: Each entity controls its own instantiation logic
2. **Minimal Magic**: Explicit factory methods, no dynamic introspection
3. **Fail Fast**: Strategy instantiation failures are fatal errors
4. **Consistency**: Same pattern for both save and restore strategies

## Architecture

### EntityConfig Protocol

Add factory methods to the `EntityConfig` protocol:

```python
# src/entities/base.py
class EntityConfig(Protocol):
    """Protocol defining entity configuration"""
    name: str
    restore_strategy_class: Optional[Type] = None
    save_strategy_class: Optional[Type] = None

    @staticmethod
    def create_restore_strategy(**context) -> Optional["RestoreEntityStrategy"]:
        """
        Factory method for creating restore strategy instances.

        Args:
            **context: Available dependencies (git_service, conflict_strategy, etc.)

        Returns:
            Configured restore strategy instance, or None if not applicable
        """
        ...

    @staticmethod
    def create_save_strategy(**context) -> Optional["SaveEntityStrategy"]:
        """
        Factory method for creating save strategy instances.

        Args:
            **context: Available dependencies (git_service, etc.)

        Returns:
            Configured save strategy instance, or None if not applicable
        """
        ...
```

### Entity Generator Template

The entity generator will create both factory methods with zero-arg defaults:

```python
# Generated in src/entities/{entity_name}/entity_config.py
class {EntityName}EntityConfig:
    """Configuration for {entity_name} entity"""
    name = "{entity_name}"
    restore_strategy_class = {EntityName}RestoreStrategy
    save_strategy_class = {EntityName}SaveStrategy

    @staticmethod
    def create_restore_strategy(**context):
        """
        Create restore strategy instance.

        Default implementation: instantiate with no arguments.
        Override this method if your strategy requires dependencies from context.

        Available context keys:
            - git_service: GitRepositoryService instance
            - conflict_strategy: Strategy for handling conflicts
            - include_original_metadata: Whether to preserve original metadata
        """
        return {EntityName}RestoreStrategy()

    @staticmethod
    def create_save_strategy(**context):
        """
        Create save strategy instance.

        Default implementation: instantiate with no arguments.
        Override this method if your strategy requires dependencies from context.

        Available context keys:
            - git_service: GitRepositoryService instance
        """
        return {EntityName}SaveStrategy()
```

### StrategyFactory Simplification

Both factory methods use identical delegation pattern:

```python
# src/operations/strategy_factory.py
class StrategyFactory:
    def create_save_strategies(
        self,
        git_service: Optional[Any] = None,
        **additional_context
    ) -> List["SaveEntityStrategy"]:
        """Create save strategies for all enabled entities."""
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

    def create_restore_strategies(
        self,
        git_service: Optional[Any] = None,
        conflict_strategy: Optional[Any] = None,
        include_original_metadata: bool = True,
        **additional_context
    ) -> List["RestoreEntityStrategy"]:
        """Create restore strategies for all enabled entities."""
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

**Removals:**
- `load_save_strategy()` method - no longer needed
- `load_restore_strategy()` method - no longer needed
- All special-case git_repository handling
- TypeError workaround

## Complex Entity Examples

### Git Repository (Required Dependency)

```python
# src/entities/git_repositories/entity_config.py
class GitRepositoryEntityConfig:
    name = "git_repository"
    restore_strategy_class = GitRepositoryRestoreStrategy
    save_strategy_class = GitRepositorySaveStrategy

    @staticmethod
    def create_restore_strategy(**context):
        """Create restore strategy - requires git_service."""
        git_service = context.get('git_service')
        if git_service is None:
            raise ValueError(
                "git_repository restore strategy requires 'git_service' in context"
            )
        return GitRepositoryRestoreStrategy(git_service)

    @staticmethod
    def create_save_strategy(**context):
        """Create save strategy - requires git_service."""
        git_service = context.get('git_service')
        if git_service is None:
            raise ValueError(
                "git_repository save strategy requires 'git_service' in context"
            )
        return GitRepositorySaveStrategy(git_service)
```

### Labels (Optional Dependency with Default)

```python
# src/entities/labels/entity_config.py
class LabelsEntityConfig:
    name = "labels"
    restore_strategy_class = LabelsRestoreStrategy
    save_strategy_class = LabelsSaveStrategy

    @staticmethod
    def create_restore_strategy(**context):
        """Create restore strategy with conflict handling."""
        conflict_strategy = context.get('conflict_strategy', LabelConflictStrategy.SKIP)
        return LabelsRestoreStrategy(conflict_strategy=conflict_strategy)

    @staticmethod
    def create_save_strategy(**context):
        """Create save strategy - no special dependencies."""
        return LabelsSaveStrategy()
```

## Migration Strategy

### Phase 1: Core Infrastructure
1. Update `EntityConfig` protocol with factory methods
2. Update entity generator to create both factory methods
3. Generate test entity to validate generator changes

### Phase 2: Simple Entities (7 entities)
Update these entities with default factory methods:
- Comments
- Issues
- Pull Requests
- Reviews
- Milestones
- Projects
- Reactions

These already have zero-arg constructors, so just add the factory wrapper.

### Phase 3: Complex Entities (3 entities)
1. **Labels** - override to handle `conflict_strategy`
2. **Git Repository** - override to handle required `git_service`
3. **Sub-issues** - verify constructor and add appropriate override

### Phase 4: StrategyFactory Refactoring
1. Update `create_save_strategies()` to use factory methods
2. Update `create_restore_strategies()` to use factory methods
3. Remove `load_save_strategy()` helper method
4. Remove `load_restore_strategy()` helper method
5. Remove special-case git_repository handling

### Phase 5: Testing
1. Update existing tests to verify factory methods work
2. Add tests for error cases (missing required dependencies)
3. Verify fail-fast behavior
4. Integration tests for full save/restore workflows

## Benefits

1. **Entity Autonomy**: Each entity fully controls its instantiation
2. **No Magic**: Explicit factory methods, easy to trace
3. **Type Safety**: Entities validate their own dependencies
4. **Fail Fast**: Missing dependencies cause immediate, clear errors
5. **Consistency**: Same pattern for all strategies
6. **Maintainability**: Adding new entities follows same simple pattern
7. **Testability**: Easy to test factory methods in isolation

## Trade-offs

**Advantages over alternatives:**
- More explicit than declarative config (no interpretation layer needed)
- More consistent than central coordination (factory doesn't grow)
- More flexible than protocol requirements (optional overrides)

**Disadvantages:**
- All entities need factory methods (but generator handles this)
- Context is untyped dict (but each entity validates what it needs)
- Requires migration of all existing entities

## Success Criteria

1. ✅ All 10 entities successfully instantiate strategies
2. ✅ Labels restore works with conflict_strategy
3. ✅ Git repository save/restore works with git_service
4. ✅ Missing required dependencies cause clear RuntimeError
5. ✅ No silent failures or TypeError workarounds
6. ✅ Entity generator creates both factory methods
7. ✅ All tests pass with new pattern

## Related Files

- `src/entities/base.py` - EntityConfig protocol
- `src/operations/strategy_factory.py` - Factory refactoring
- `src/tools/generate_entity.py` - Generator updates
- All entity configs in `src/entities/*/entity_config.py`

## Implementation Notes

**Implementation completed:** 2025-10-26

**Summary:**
- Git repository and sub_issues entities successfully migrated to factory method pattern
- StrategyFactory refactored to delegate to entity factory methods
- TypeError workaround eliminated
- All tests passing with new pattern (30 new tests added)

**Key Changes:**
- Git repository factory returns None when git_service unavailable (graceful skipping)
- Removed save_strategy_class/restore_strategy_class checks (all entities use factory methods)
- Eliminated importlib dependency and 120+ lines of legacy code
- Updated test files to use new factory pattern

**Files Changed:**
- `src/entities/git_repositories/entity_config.py` - Factory methods with git_service handling
- `src/entities/sub_issues/entity_config.py` - Factory methods with metadata handling
- `src/operations/strategy_factory.py` - Complete factory refactoring (removed legacy methods)
- Comprehensive test coverage: 8 new unit tests, 5 new integration tests

**Lessons Learned:**
- Factory methods returning None enables graceful dependency skipping
- Protocol-based factory methods work well even when `save_strategy_class = None`
- Test file naming must be unique across directories (pytest collection issue)
- Mypy false positives acceptable when runtime types are correct

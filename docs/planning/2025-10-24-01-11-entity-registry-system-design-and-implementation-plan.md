# Entity Registry System - Design and Implementation Plan

**Date:** 2025-10-24
**Session:** Brainstorming and Design
**Status:** Design Complete - Ready for Implementation

## Executive Summary

This document outlines the design and implementation plan for a convention-based entity registry system that will replace the current static configuration approach. The goal is to make adding new entities (like `INCLUDE_COMMENT_ATTACHMENTS`) dramatically easier by eliminating boilerplate and preventing test breakage.

### Current Pain Points

1. **Test Explosion**: Adding a new entity breaks many existing tests
2. **Scattered Changes**: Each new entity requires changes across 6+ files
3. **Boilerplate Duplication**: Same patterns repeated for parsing, validation, strategy creation
4. **Maintenance Burden**: ConfigBuilder must be manually updated for each entity

### Proposed Solution

A convention-based entity registry system where:
- New entities are declared in a single location
- Auto-discovery eliminates boilerplate changes
- Tests are isolated and don't break when entities are added
- CLI tool generates entity scaffolding
- Shared behavior is auto-tested

## Design Decisions

### 1. Entity Discovery
**Decision:** Convention-based folder structure + naming
**Rationale:** Zero boilerplate changes to shared files

### 2. Configuration Access
**Decision:** `config.get_entity('name').is_enabled()` (explicit methods)
**Rationale:** Clear, explicit, and greppable

### 3. Migration Strategy
**Decision:** Big Bang refactor of all existing entities
**Rationale:** Clean slate, no legacy technical debt

### 4. CLI Tool
**Decision:** Both command-line args and interactive prompts
**Rationale:** Automation (args) + user-friendliness (prompts)

### 5. Test Fixtures
**Decision:** Direct registry construction with factory methods (hybrid approach)
**Rationale:** Single unified API with convenience helpers

```python
# Simple cases
config = EntityRegistry.for_testing(issues=True, comments=False)

# Factory methods for common scenarios
config = EntityRegistry.for_testing_minimal()
config = EntityRegistry.for_testing_full()

# Override from template
config = EntityRegistry.for_testing_full(comment_attachments=False)
```

### 6. Dependency Validation
**Decision:** Context-aware validation with two behaviors:

**Scenario A - Implicit disable (warn and auto-correct):**
```bash
INCLUDE_ISSUES=false
INCLUDE_COMMENTS=true  # Depends on issues, not explicitly set by user defaults
```
**Result:** ⚠️ Warning logged, comments auto-disabled

**Scenario B - Explicit conflict (fail fast):**
```bash
INCLUDE_ISSUES=false
INCLUDE_COMMENTS=false
INCLUDE_COMMENT_ATTACHMENTS=true  # User EXPLICITLY enabled despite missing deps
```
**Result:** 💥 Fail with clear error message

**Detection Rule:** If user explicitly sets `dependent=true` while `ancestor=false`, fail fast. If dependent uses default value while ancestor is disabled, auto-disable with warning.

### 7. Execution Order
**Decision:** Dependency-based topological sort
**Rationale:** Order is self-documenting through dependency declarations

## Architecture

### Directory Structure

```
src/
  entities/
    __init__.py              # Auto-discovery engine
    base.py                  # BaseEntity, EntityConfig protocols
    registry.py              # EntityRegistry (replaces ApplicationConfig)

    labels/
      entity_config.py       # LabelEntityConfig
      models.py              # Data models (unchanged)
      save_strategy.py       # BaseSaveStrategy subclass
      restore_strategy.py    # BaseRestoreStrategy subclass

    issues/
      entity_config.py       # IssuesEntityConfig
      models.py
      save_strategy.py
      restore_strategy.py

    comment_attachments/     # NEW ENTITY EXAMPLE
      entity_config.py       # Declare metadata here
      models.py              # Data models
      save_strategy.py       # Auto-discovered by convention
      restore_strategy.py    # Auto-discovered by convention

  tools/
    generate_entity.py       # CLI tool for boilerplate generation

  config/
    number_parser.py         # KEPT (still needed for number specs)
    settings.py              # DELETED (replaced by EntityRegistry)

  operations/
    strategy_factory.py      # UPDATED (reads from EntityRegistry)
    save/
      orchestrator.py        # UPDATED (uses EntityRegistry)
    restore/
      orchestrator.py        # UPDATED (uses EntityRegistry)

tests/
  shared/
    builders/
      config_builder.py      # DELETED (replaced by EntityRegistry.for_testing)
      config_factory.py      # DELETED (replaced by factory methods)
```

### Core Components

#### 1. EntityConfig Protocol (base.py)

```python
from typing import Protocol, Optional, List, Union, Set, Type

class EntityConfig(Protocol):
    """Protocol for entity configuration metadata."""

    # Required attributes
    name: str                    # e.g., "comment_attachments"
    env_var: str                 # e.g., "INCLUDE_COMMENT_ATTACHMENTS"
    default_value: Union[bool, Set[int]]
    value_type: type             # bool or Union[bool, Set[int]]

    # Optional attributes with conventions
    dependencies: List[str] = []         # e.g., ["issues", "comments"]
    save_strategy_class: Optional[Type] = None    # None = auto-discover
    restore_strategy_class: Optional[Type] = None # None = auto-discover
    storage_filename: Optional[str] = None        # None = f"{name}.json"
    description: str = ""                         # For documentation
```

#### 2. EntityRegistry (registry.py)

```python
class EntityRegistry:
    """Central registry for all entities (replaces ApplicationConfig)."""

    def __init__(self):
        self._entities: Dict[str, RegisteredEntity] = {}
        self._discover_entities()

    @classmethod
    def from_environment(cls, strict: bool = False) -> "EntityRegistry":
        """Create registry from environment variables."""
        registry = cls()
        registry._load_from_environment(strict)
        return registry

    def get_entity(self, name: str) -> RegisteredEntity:
        """Get entity by name."""
        if name not in self._entities:
            raise ValueError(f"Unknown entity: {name}")
        return self._entities[name]

    def get_enabled_entities(self) -> List[RegisteredEntity]:
        """Get all enabled entities in dependency order."""
        enabled = [e for e in self._entities.values() if e.is_enabled()]
        return self._topological_sort(enabled)

    # Factory methods for testing
    @classmethod
    def for_testing(cls, **entity_overrides) -> "EntityRegistry":
        """Create registry for testing with entity overrides."""
        pass

    @classmethod
    def for_testing_minimal(cls) -> "EntityRegistry":
        """All optional entities disabled."""
        pass

    @classmethod
    def for_testing_full(cls) -> "EntityRegistry":
        """All entities enabled."""
        pass

    def _discover_entities(self):
        """Auto-discover entities by scanning entities/ directory."""
        pass

    def _load_from_environment(self, strict: bool):
        """Load entity values from environment variables."""
        pass

    def _validate_dependencies(self, strict: bool):
        """Validate dependency requirements."""
        pass

    def _topological_sort(self, entities: List[RegisteredEntity]) -> List[RegisteredEntity]:
        """Sort entities by dependency order."""
        pass
```

#### 3. RegisteredEntity

```python
@dataclass
class RegisteredEntity:
    """Represents a registered entity with its configuration and runtime state."""

    config: EntityConfig
    enabled: Union[bool, Set[int]]
    save_strategy: Optional[BaseSaveStrategy] = None
    restore_strategy: Optional[BaseRestoreStrategy] = None

    def is_enabled(self) -> bool:
        """Check if entity is enabled."""
        if isinstance(self.enabled, bool):
            return self.enabled
        else:  # Set[int]
            return len(self.enabled) > 0

    def get_dependencies(self) -> List[str]:
        """Get list of dependency names."""
        return self.config.dependencies

    def get_save_strategy(self) -> BaseSaveStrategy:
        """Get save strategy (lazy load if needed)."""
        if self.save_strategy is None:
            self.save_strategy = self._load_save_strategy()
        return self.save_strategy

    def get_restore_strategy(self) -> BaseRestoreStrategy:
        """Get restore strategy (lazy load if needed)."""
        if self.restore_strategy is None:
            self.restore_strategy = self._load_restore_strategy()
        return self.restore_strategy
```

#### 4. Entity Declaration Example

```python
# src/entities/comment_attachments/entity_config.py
from src.entities.base import EntityConfig

class CommentAttachmentsEntityConfig(EntityConfig):
    """Entity configuration for comment attachments.

    Auto-discovered by naming convention: *EntityConfig
    """

    name = "comment_attachments"
    env_var = "INCLUDE_COMMENT_ATTACHMENTS"
    default_value = True
    value_type = bool

    dependencies = ["issues", "comments"]
    description = "Save and restore issue comment attachments (images, files)"

    # Optional - override conventions if needed
    # save_strategy_class = CustomSaveStrategy
    # restore_strategy_class = CustomRestoreStrategy
    # storage_filename = "custom_name.json"
```

#### 5. CLI Generator Tool

```bash
# Interactive mode
$ python -m src.tools.generate_entity
Entity name: comment_attachments
Environment variable [INCLUDE_COMMENT_ATTACHMENTS]: ✓
Default value (true/false) [true]: ✓
Value type (bool/set) [bool]: ✓
Dependencies (comma-separated) []: issues,comments
Description: Save and restore issue comment attachments
✓ Generated src/entities/comment_attachments/
  ✓ entity_config.py
  ✓ models.py (template)
  ✓ save_strategy.py (template)
  ✓ restore_strategy.py (template)
  ✓ __init__.py

# Command-line args (for automation)
$ python -m src.tools.generate_entity \
    --name comment_attachments \
    --type bool \
    --default true \
    --deps issues,comments \
    --description "Save and restore issue comment attachments"

# Hybrid (args + prompts for missing)
$ python -m src.tools.generate_entity --name comment_attachments
# Prompts for other fields
```

## Implementation Plan

### Phase 1: Core Infrastructure (Foundation)

**Goal:** Build EntityRegistry system without breaking existing code

**Tasks:**
1. Create `src/entities/base.py` with protocols:
   - EntityConfig protocol
   - BaseSaveStrategy protocol
   - BaseRestoreStrategy protocol
   - RegisteredEntity dataclass

2. Create `src/entities/registry.py`:
   - EntityRegistry class
   - Auto-discovery mechanism
   - Environment variable parsing
   - Dependency validation (explicit vs implicit)
   - Topological sort algorithm

3. Create `src/entities/__init__.py`:
   - Export public API
   - Entity discovery on import

4. Write comprehensive unit tests:
   - Discovery mechanism
   - Dependency validation (both scenarios)
   - Topological sort
   - Environment parsing
   - Error cases

**Validation:** All new tests pass, existing tests unchanged

---

### Phase 2: CLI Generator Tool

**Goal:** Create tool to generate entity boilerplate

**Tasks:**
1. Create `src/tools/generate_entity.py`:
   - Command-line argument parser
   - Interactive prompt system
   - Template generation for:
     - entity_config.py
     - models.py (basic template)
     - save_strategy.py (basic template)
     - restore_strategy.py (basic template)
     - __init__.py
   - Validation of inputs
   - File conflict detection

2. Create templates in `src/tools/templates/`:
   - entity_config_template.py.j2
   - models_template.py.j2
   - save_strategy_template.py.j2
   - restore_strategy_template.py.j2

3. Write tests for generator:
   - Argument parsing
   - Template rendering
   - File generation
   - Conflict detection

4. Test manually by generating a test entity

**Validation:** Generator creates valid entity structure

---

### Phase 3: Big Bang Migration

**Goal:** Migrate all existing entities and update all code

#### Phase 3.1: Proof of Concept (Single Entity)

**Tasks:**
1. Migrate `labels` entity as proof-of-concept:
   - Create `src/entities/labels/entity_config.py`
   - Move models.py into entity folder (already exists)
   - Ensure save/restore strategies follow convention

2. Verify EntityRegistry can discover and load labels

3. Update one small usage (e.g., in tests) to use registry

**Validation:** Labels entity works through registry

#### Phase 3.2: Migrate All Entities

**Tasks:**
1. Migrate remaining entities:
   - issues
   - comments
   - pull_requests
   - pr_comments
   - pr_reviews
   - pr_review_comments
   - sub_issues
   - milestones
   - git_repository

2. For each entity:
   - Create entity_config.py
   - Reorganize into entity folder structure
   - Update strategy imports

**Validation:** All entities discovered by registry

#### Phase 3.3: Update Core Code

**Tasks:**
1. Update `src/operations/strategy_factory.py`:
   - Replace ApplicationConfig with EntityRegistry
   - Use `config.get_entity(name).is_enabled()`
   - Get strategies from registry
   - Use topological sort for execution order

2. Update `src/operations/save/orchestrator.py`:
   - Use EntityRegistry instead of ApplicationConfig
   - Access entity configuration through registry

3. Update `src/operations/restore/orchestrator.py`:
   - Use EntityRegistry instead of ApplicationConfig
   - Access entity configuration through registry

4. Update `src/main.py`:
   - Replace ApplicationConfig.from_environment()
   - Use EntityRegistry.from_environment()

5. Delete `src/config/settings.py`

6. Update all imports throughout codebase:
   - Find: `from src.config.settings import ApplicationConfig`
   - Replace: `from src.entities.registry import EntityRegistry`

**Validation:** Code compiles, runs without errors

---

### Phase 4: Test Infrastructure

**Goal:** Update all tests to use new registry-based system

#### Phase 4.1: Create Test Utilities

**Tasks:**
1. Add factory methods to EntityRegistry:
   - `for_testing(**overrides)`
   - `for_testing_minimal()`
   - `for_testing_full()`
   - `for_testing_issues_only()`
   - `for_testing_prs_only()`
   - Other common scenarios

2. Create test helpers in `tests/shared/registry_helpers.py`:
   - Common registry configurations
   - Assertion helpers
   - Mock entity configurations

**Validation:** Factory methods work correctly

#### Phase 4.2: Migrate Tests

**Tasks:**
1. Update `tests/shared/fixtures/config_fixtures.py`:
   - Replace ConfigBuilder usage
   - Use EntityRegistry.for_testing()

2. Update all unit tests:
   - Replace ApplicationConfig usage
   - Use registry-based access patterns
   - Update assertions for new API

3. Update all integration tests:
   - Replace config construction
   - Update entity access patterns

4. Update container tests:
   - Ensure environment variable parsing works
   - Test dependency validation

5. Delete obsolete files:
   - `tests/shared/builders/config_builder.py`
   - `tests/shared/builders/config_factory.py`

**Validation:** All 443 tests pass (or more)

#### Phase 4.3: Auto-Tested Shared Behavior

**Tasks:**
1. Create `tests/shared/entity_contract_tests.py`:
   - Parameterized tests that run for ALL entities
   - Test: Entity can be discovered
   - Test: Entity config is valid
   - Test: Entity strategies can be loaded
   - Test: Entity dependencies are satisfied
   - Test: Entity can be enabled/disabled
   - Test: Save strategy has required methods
   - Test: Restore strategy has required methods

2. Hook into pytest to auto-run for all discovered entities

**Validation:** Contract tests run for all entities

---

### Phase 5: Documentation and Validation

**Goal:** Document new system and validate everything works

**Tasks:**
1. Update `CLAUDE.md`:
   - Remove ApplicationConfig references
   - Add EntityRegistry documentation
   - Add entity development guide
   - Document CLI generator tool usage
   - Update examples

2. Update `CONTRIBUTING.md`:
   - Add "Adding a New Entity" section
   - Document entity conventions
   - Show CLI generator usage
   - Explain testing requirements

3. Create `docs/entity-development-guide.md`:
   - Comprehensive guide for entity development
   - Convention documentation
   - Examples and best practices
   - Troubleshooting

4. Update `README.md`:
   - Update environment variables section
   - Link to entity guide

5. Final validation:
   - Run `make check-all`
   - Run container integration tests
   - Test CLI generator end-to-end
   - Verify all documentation is accurate

**Validation:** All checks pass, documentation complete

---

## Success Criteria

### Before (Current State)

**Adding `INCLUDE_COMMENT_ATTACHMENTS` requires:**
1. ✏️ Update ApplicationConfig (4 locations: field, from_environment, validate, docstring)
2. ✏️ Update StrategyFactory (3 methods: create_save_strategies, create_restore_strategies, get_enabled_entities)
3. ✏️ Update ConfigBuilder (5 locations: __init__, with_comment_attachments, with_minimal, with_all, as_env_dict)
4. ✏️ Update ConfigFactory (similar changes)
5. ✏️ Fix ~50-100 broken tests that now fail
6. ✏️ Write entity-specific tests
7. ⏱️ **Total time: 4-8 hours**

### After (Target State)

**Adding `INCLUDE_COMMENT_ATTACHMENTS` requires:**
1. 🤖 Run: `python -m src.tools.generate_entity --name comment_attachments --deps issues,comments`
2. ✏️ Implement save_strategy.py logic
3. ✏️ Implement restore_strategy.py logic
4. ✏️ Write entity-specific tests (only test unique behavior)
5. ✅ All existing tests continue to pass
6. ✅ Auto-tested contract tests validate entity
7. ⏱️ **Total time: 1-2 hours**

### Quantifiable Improvements

- **Boilerplate reduction:** 90% (6+ files → 1 command + custom logic)
- **Test breakage:** 100% reduction (0 existing tests break)
- **Development time:** 75% reduction (4-8 hours → 1-2 hours)
- **Error prevention:** CLI generator eliminates typos and forgotten steps
- **Maintenance burden:** Significantly reduced (no central config files to maintain)

## Risks and Mitigations

### Risk 1: Big Bang Migration Complexity
**Impact:** High
**Probability:** Medium
**Mitigation:**
- Proof-of-concept with single entity first
- Comprehensive test coverage before migration
- Run tests after each sub-phase
- Can roll back if needed (Git)

### Risk 2: Performance Overhead (Auto-Discovery)
**Impact:** Low
**Probability:** Low
**Mitigation:**
- Discovery only happens once at startup
- Cache discovered entities
- Lazy-load strategies only when needed
- Benchmark before/after

### Risk 3: Breaking Production Workflows
**Impact:** High
**Probability:** Low
**Mitigation:**
- Environment variables unchanged (backward compatible)
- Comprehensive container tests
- Test all documented use cases
- Maintain changelog

### Risk 4: Test Migration Errors
**Impact:** Medium
**Probability:** Medium
**Mitigation:**
- Migrate tests incrementally
- Run test suite continuously
- Use git bisect if regressions found
- Pair review test changes

## Timeline Estimate

| Phase | Estimated Time | Cumulative |
|-------|---------------|------------|
| Phase 1: Core Infrastructure | 6-8 hours | 6-8 hours |
| Phase 2: CLI Generator | 3-4 hours | 9-12 hours |
| Phase 3: Big Bang Migration | 12-16 hours | 21-28 hours |
| Phase 4: Test Infrastructure | 8-10 hours | 29-38 hours |
| Phase 5: Documentation | 3-4 hours | 32-42 hours |

**Total: 32-42 hours** (4-5 working days)

## Next Steps

1. **Get approval** on this design and implementation plan
2. **Begin Phase 1** - Core Infrastructure
3. **Iterate** with feedback after each phase
4. **Validate** continuously with test suite

## Appendix A: Example Usage Comparison

### Current System (Before)

```python
# ApplicationConfig creation
config = ApplicationConfig(
    operation="save",
    github_token="token",
    github_repo="owner/repo",
    data_path="/data",
    label_conflict_strategy="skip",
    include_git_repo=True,
    include_issues=True,
    include_issue_comments=True,
    include_pull_requests=True,
    include_pull_request_comments=True,
    include_pr_reviews=True,
    include_pr_review_comments=True,
    include_sub_issues=True,
    include_milestones=True,
    git_auth_method="token"
)

# Access
if config.include_issues:
    # Process issues
    pass

# Strategy factory
strategies = StrategyFactory.create_save_strategies(config)
```

### New System (After)

```python
# EntityRegistry creation
registry = EntityRegistry.from_environment()

# Or for testing
registry = EntityRegistry.for_testing(
    issues=True,
    comments=False,
    comment_attachments=True
)

# Access
if registry.get_entity('issues').is_enabled():
    # Process issues
    pass

# Get strategies (auto-sorted by dependencies)
enabled_entities = registry.get_enabled_entities()
for entity in enabled_entities:
    strategy = entity.get_save_strategy()
    strategy.execute()
```

## Appendix B: Entity Conventions Reference

### Naming Conventions

| Item | Convention | Example |
|------|-----------|---------|
| Entity folder | `snake_case` | `comment_attachments/` |
| Config class | `{Name}EntityConfig` | `CommentAttachmentsEntityConfig` |
| Save strategy file | `save_strategy.py` | `save_strategy.py` |
| Save strategy class | `{Name}SaveStrategy` | `CommentAttachmentsSaveStrategy` |
| Restore strategy file | `restore_strategy.py` | `restore_strategy.py` |
| Restore strategy class | `{Name}RestoreStrategy` | `CommentAttachmentsRestoreStrategy` |
| Storage file | `{entity_name}.json` | `comment_attachments.json` |
| Environment var | `INCLUDE_{UPPER_SNAKE}` | `INCLUDE_COMMENT_ATTACHMENTS` |

### File Structure Template

```
src/entities/comment_attachments/
├── __init__.py                    # Export public API
├── entity_config.py               # CommentAttachmentsEntityConfig
├── models.py                      # Pydantic data models
├── save_strategy.py               # CommentAttachmentsSaveStrategy
└── restore_strategy.py            # CommentAttachmentsRestoreStrategy
```

### Minimal entity_config.py

```python
from src.entities.base import EntityConfig

class CommentAttachmentsEntityConfig(EntityConfig):
    name = "comment_attachments"
    env_var = "INCLUDE_COMMENT_ATTACHMENTS"
    default_value = True
    value_type = bool
    dependencies = ["issues", "comments"]
    description = "Brief description"
```

## Appendix C: Dependency Validation Examples

### Example 1: Auto-Disable (Warning)

```python
# Environment
INCLUDE_ISSUES=false
# INCLUDE_COMMENTS not set (uses default=true)

# Result
# WARNING: INCLUDE_COMMENTS requires INCLUDE_ISSUES. Disabling comments.
registry.get_entity('issues').is_enabled()   # False
registry.get_entity('comments').is_enabled() # False (auto-disabled)
```

### Example 2: Explicit Conflict (Fail Fast)

```python
# Environment
INCLUDE_ISSUES=false
INCLUDE_COMMENTS=false
INCLUDE_COMMENT_ATTACHMENTS=true  # Explicitly enabled!

# Result
# ERROR: INCLUDE_COMMENT_ATTACHMENTS=true requires INCLUDE_COMMENTS=true
# Raises ValueError with clear message
```

### Example 3: Valid Configuration

```python
# Environment
INCLUDE_ISSUES=true
INCLUDE_COMMENTS=true
INCLUDE_COMMENT_ATTACHMENTS=true

# Result
registry.get_entity('issues').is_enabled()              # True
registry.get_entity('comments').is_enabled()            # True
registry.get_entity('comment_attachments').is_enabled() # True
```

### Example 4: Selective Issues

```python
# Environment
INCLUDE_ISSUES="1,5,10-20"
INCLUDE_COMMENTS=true
INCLUDE_COMMENT_ATTACHMENTS=true

# Result
registry.get_entity('issues').enabled                    # {1, 5, 10, 11, ..., 20}
registry.get_entity('comments').is_enabled()             # True
registry.get_entity('comment_attachments').is_enabled()  # True
# Comments and attachments filtered to selected issues
```

---

**End of Implementation Plan**

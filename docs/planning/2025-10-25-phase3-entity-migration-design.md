# Phase 3: Entity Migration to EntityRegistry System

**Date:** 2025-10-25
**Status:** Design Complete
**Related:** [2025-10-24-entity-registry-system.md](2025-10-24-entity-registry-system.md)

## Overview

Phase 3 migrates all 10 existing entities from the static `ApplicationConfig` system to the convention-based `EntityRegistry` system. This migration eliminates boilerplate, enables automatic dependency management, and prevents test breakage when adding new entities.

## Design Decisions

### Migration Strategy
- **Grouped migration in 3 batches** based on dependency hierarchy
- **Direct replacement per batch** - no feature flags or compatibility layers
- **Dependency inference and validation** - analyze code, write tests, then document

### Batch Grouping by Dependencies
- **Batch 1 (Independent)**: labels, milestones, git_repository
- **Batch 2 (Issues domain)**: issues, comments, sub_issues
- **Batch 3 (PRs domain)**: pull_requests, pr_reviews, pr_review_comments, pr_comments

### File Organization
**Flat structure** - Add new files to existing entity directories:
```
src/entities/{entity_name}/
├── __init__.py              # Existing - exports data models
├── models.py                # Existing - Pydantic data models
├── entity_config.py         # NEW - EntityRegistry metadata
├── save_strategy.py         # MOVED - from src/operations/save/strategies/
└── restore_strategy.py      # MOVED - from src/operations/restore/strategies/
```

**Purpose separation:**
- `models.py`: Defines **what the data looks like** (Pydantic models)
- `entity_config.py`: Defines **how the entity is managed** (registry metadata)
- Strategies use models for data processing

## Naming Conventions

### Directory and Class Names
- Directory: `{entity_name}` (snake_case, e.g., `pr_review_comments`)
- Config class: `{EntityName}EntityConfig` (e.g., `PrReviewCommentsEntityConfig`)
- Save strategy: `{EntityName}SaveStrategy` (e.g., `PrReviewCommentsSaveStrategy`)
- Restore strategy: `{EntityName}RestoreStrategy` (e.g., `PrReviewCommentsRestoreStrategy`)

### Discovery Process
1. EntityRegistry scans `src/entities/` for subdirectories
2. Looks for `entity_config.py` in each directory
3. Imports and finds classes ending with `EntityConfig`
4. Registers entity with default enabled state
5. Optionally loads strategies by convention

## Dependency Analysis

### Expected Dependencies (to be validated)

**Independent entities (no dependencies):**
- labels
- milestones
- git_repository

**Issues domain dependencies:**
- issues → [milestones] (issues can reference milestones)
- comments → [issues] (comments belong to issues)
- sub_issues → [issues] (sub-issues are hierarchical issues)

**Pull requests domain dependencies:**
- pull_requests → [milestones] (PRs can reference milestones)
- pr_reviews → [pull_requests] (reviews belong to PRs)
- pr_review_comments → [pr_reviews] (review comments belong to reviews)
- pr_comments → [pull_requests] (PR comments belong to PRs)

### Dependency Inference Process

For each entity:
1. **Examine strategy dependencies**: Check `get_dependencies()` methods
2. **Review orchestrator execution order**: Current sequencing
3. **Analyze data relationships**: Foreign key relationships
4. **Check API call sequencing**: Restoration requirements

### Validation Testing Strategy

For each entity:
- Test entities fail when parent dependency disabled
- Test execution order respects dependencies (topological sort)
- Test registry auto-disables dependents when parent disabled (non-strict)
- Test strict mode raises errors for explicit violations

## Batch 1: Independent Entities

**Entities:** labels, milestones, git_repository

### Task 13: Migrate labels entity

**Directory:** `src/entities/labels/` (existing)

**Steps:**
1. Write failing dependency validation test
2. Create `entity_config.py`:
   ```python
   class LabelsEntityConfig:
       name = "labels"
       env_var = "INCLUDE_LABELS"  # NEW environment variable
       default_value = True
       value_type = bool
       dependencies = []
       save_strategy_class = None  # Use convention
       restore_strategy_class = None  # Use convention
       storage_filename = None  # Use convention (labels.json)
       description = "Repository labels for issue/PR categorization"
   ```
3. Move `LabelsSaveStrategy`:
   - From: `src/operations/save/strategies/labels_strategy.py`
   - To: `src/entities/labels/save_strategy.py`
4. Move `LabelsRestoreStrategy`:
   - From: `src/operations/restore/strategies/labels_strategy.py`
   - To: `src/entities/labels/restore_strategy.py`
5. Update imports in moved files
6. Run tests - expect pass

**Commit:** (individual task commit)

### Task 14: Migrate milestones entity

**Directory:** `src/entities/milestones/` (existing)

**Steps:**
1. Write failing dependency validation test
2. Create `entity_config.py`:
   ```python
   class MilestonesEntityConfig:
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
3. Move strategies from `src/operations/{save,restore}/strategies/milestones_strategy.py`
4. Update imports
5. Run tests - expect pass

**Commit:** (individual task commit)

### Task 15: Migrate git_repository entity

**Directory:** `src/entities/git_repository/` (existing as `git_repositories`)

**Note:** Check if directory name is `git_repository` or `git_repositories` and use existing name.

**Steps:**
1. Write failing dependency validation test
2. Create `entity_config.py`:
   ```python
   class GitRepositoryEntityConfig:
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
3. Move strategies from `src/operations/{save,restore}/strategies/git_repository_strategy.py`
4. Update imports
5. Run tests - expect pass

**Commit:** (individual task commit)

### Task 16: Update StrategyFactory for Batch 1

**File:** `src/operations/strategy_factory.py` (or similar)

**Steps:**
1. Write tests for loading strategies from EntityRegistry
2. Add EntityRegistry parameter to StrategyFactory constructor:
   ```python
   def __init__(self, registry: EntityRegistry, config: ApplicationConfig):
       self.registry = registry
       self.config = config  # Keep for unmigrated entities
   ```
3. Update strategy loading logic:
   ```python
   def get_save_strategies(self):
       strategies = []

       # Load from registry for migrated entities
       for entity in self.registry.get_enabled_entities():
           strategy = self._load_save_strategy(entity)
           if strategy:
               strategies.append(strategy)

       # Load from ApplicationConfig for unmigrated entities (Batch 2 & 3)
       # ... existing logic for unmigrated entities

       return strategies
   ```
4. Implement convention-based strategy loading:
   ```python
   def _load_save_strategy(self, entity: RegisteredEntity):
       # Use override if specified
       if entity.config.save_strategy_class:
           return entity.config.save_strategy_class(...)

       # Use convention
       module_name = f"src.entities.{entity.config.name}.save_strategy"
       class_name = f"{self._to_class_name(entity.config.name)}SaveStrategy"
       # Import and instantiate
   ```
5. Run tests - Batch 1 entities work through registry

**Commit:** (individual task commit)

### Task 17: Commit Batch 1

**Commit message:**
```
feat: migrate independent entities to EntityRegistry (Batch 1)

Migrate labels, milestones, and git_repository to the new EntityRegistry
system. These entities have no dependencies and serve as the foundation
for dependent entities in Batches 2 and 3.

- Add entity_config.py for each entity with metadata
- Move save/restore strategies to entity directories
- Update StrategyFactory to load from registry (with ApplicationConfig fallback)
- Add dependency validation tests

All tests passing for Batch 1 entities.
```

## Batch 2: Issues Domain

**Entities:** issues, comments, sub_issues

### Task 18: Migrate issues entity

**Directory:** `src/entities/issues/` (existing)

**Steps:**
1. Write dependency validation tests (issues depends on milestones)
2. Create `entity_config.py`:
   ```python
   from typing import Union, Set

   class IssuesEntityConfig:
       name = "issues"
       env_var = "INCLUDE_ISSUES"
       default_value = True
       value_type = Union[bool, Set[int]]  # Supports selective issue numbers
       dependencies = ["milestones"]  # Issues can reference milestones
       save_strategy_class = None
       restore_strategy_class = None
       storage_filename = None
       description = "Repository issues with milestone references"
   ```
3. Move strategies from `src/operations/{save,restore}/strategies/issues_strategy.py`
4. Update imports
5. Run tests - verify dependency validation works

**Commit:** (individual task commit)

### Task 19: Migrate comments entity

**Directory:** `src/entities/comments/` (existing)

**Steps:**
1. Write dependency validation tests (comments depends on issues)
2. Create `entity_config.py`:
   ```python
   class CommentsEntityConfig:
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
3. Move strategies from `src/operations/{save,restore}/strategies/comments_strategy.py`
4. Update imports
5. Run tests - verify dependency validation

**Commit:** (individual task commit)

### Task 20: Migrate sub_issues entity

**Directory:** `src/entities/sub_issues/` (existing)

**Steps:**
1. Write dependency validation tests (sub_issues depends on issues)
2. Create `entity_config.py`:
   ```python
   class SubIssuesEntityConfig:
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
3. Move strategies from `src/operations/{save,restore}/strategies/sub_issues_strategy.py`
4. Update imports
5. Run tests - verify dependency validation

**Commit:** (individual task commit)

### Task 21: Update StrategyFactory for Batch 2

**Steps:**
1. Update tests to cover Batch 1 + 2 entities
2. Verify factory loads strategies from registry for all migrated entities
3. Keep ApplicationConfig support for unmigrated PR entities (Batch 3)
4. Run full test suite - Batches 1 & 2 working through registry
5. Test dependency order in execution

**Commit:** (individual task commit)

### Task 22: Commit Batch 2

**Commit message:**
```
feat: migrate issues domain entities to EntityRegistry (Batch 2)

Migrate issues, comments, and sub_issues to EntityRegistry with proper
dependency declarations. These entities depend on Batch 1 entities.

- Add entity_config.py with dependency metadata
- Move save/restore strategies to entity directories
- Update StrategyFactory to support Batch 1 + 2
- Add comprehensive dependency validation tests

All tests passing. Dependency graph validated:
- issues → milestones
- comments → issues
- sub_issues → issues
```

## Batch 3: Pull Requests Domain

**Entities:** pull_requests, pr_reviews, pr_review_comments, pr_comments

### Task 23: Migrate pull_requests entity

**Directory:** `src/entities/pull_requests/` (existing)

**Steps:**
1. Write dependency validation tests (PRs depend on milestones)
2. Create `entity_config.py`:
   ```python
   from typing import Union, Set

   class PullRequestsEntityConfig:
       name = "pull_requests"
       env_var = "INCLUDE_PULL_REQUESTS"
       default_value = True
       value_type = Union[bool, Set[int]]  # Supports selective PR numbers
       dependencies = ["milestones"]  # PRs can reference milestones
       save_strategy_class = None
       restore_strategy_class = None
       storage_filename = None
       description = "Pull requests with milestone references"
   ```
3. Move strategies from `src/operations/{save,restore}/strategies/pull_requests_strategy.py`
4. Update imports
5. Run tests - verify dependency validation

**Commit:** (individual task commit)

### Task 24: Migrate pr_reviews entity

**Directory:** `src/entities/pr_reviews/` (existing)

**Steps:**
1. Write dependency validation tests (reviews depend on pull_requests)
2. Create `entity_config.py`:
   ```python
   class PrReviewsEntityConfig:
       name = "pr_reviews"
       env_var = "INCLUDE_PR_REVIEWS"
       default_value = True
       value_type = bool
       dependencies = ["pull_requests"]
       save_strategy_class = None
       restore_strategy_class = None
       storage_filename = None
       description = "Pull request code reviews"
   ```
3. Move strategies from `src/operations/{save,restore}/strategies/pr_reviews_strategy.py`
4. Update imports
5. Run tests - verify dependency validation

**Commit:** (individual task commit)

### Task 25: Migrate pr_review_comments entity

**Directory:** `src/entities/pr_review_comments/` (existing)

**Steps:**
1. Write dependency validation tests (review comments depend on pr_reviews)
2. Create `entity_config.py`:
   ```python
   class PrReviewCommentsEntityConfig:
       name = "pr_review_comments"
       env_var = "INCLUDE_PR_REVIEW_COMMENTS"
       default_value = True
       value_type = bool
       dependencies = ["pr_reviews"]
       save_strategy_class = None
       restore_strategy_class = None
       storage_filename = None
       description = "Code review inline comments"
   ```
3. Move strategies from `src/operations/{save,restore}/strategies/pr_review_comments_strategy.py`
4. Update imports
5. Run tests - verify dependency validation

**Commit:** (individual task commit)

### Task 26: Migrate pr_comments entity

**Directory:** Check if `src/entities/pr_comments/` exists, create if needed

**Note:** Verify environment variable name - likely `INCLUDE_PULL_REQUEST_COMMENTS`

**Steps:**
1. Write dependency validation tests (PR comments depend on pull_requests)
2. Create `entity_config.py`:
   ```python
   class PrCommentsEntityConfig:
       name = "pr_comments"
       env_var = "INCLUDE_PULL_REQUEST_COMMENTS"
       default_value = True
       value_type = bool
       dependencies = ["pull_requests"]
       save_strategy_class = None
       restore_strategy_class = None
       storage_filename = None
       description = "Pull request conversation comments"
   ```
3. Move strategies from `src/operations/{save,restore}/strategies/pr_comments_strategy.py`
4. Update imports
5. Run tests - verify dependency validation

**Commit:** (individual task commit)

### Task 27: Commit Batch 3

**Commit message:**
```
feat: migrate PR domain entities to EntityRegistry (Batch 3)

Migrate all pull request related entities to EntityRegistry with complete
dependency graph. This completes the entity migration phase.

- Add entity_config.py for all PR entities
- Move save/restore strategies to entity directories
- Complete dependency graph for all 10 entities
- Full dependency validation test coverage

All tests passing. Complete dependency graph validated:
- pull_requests → milestones
- pr_reviews → pull_requests
- pr_review_comments → pr_reviews
- pr_comments → pull_requests
```

## Factory and Orchestrator Updates

### Task 28: Complete StrategyFactory Migration

**File:** `src/operations/strategy_factory.py` (or similar)

Now that all entities are migrated, fully convert to EntityRegistry.

**Steps:**

1. **Remove ApplicationConfig dependency:**
   ```python
   class StrategyFactory:
       def __init__(self, registry: EntityRegistry):
           self.registry = registry
           # ApplicationConfig removed
   ```

2. **Strategy loading by convention:**
   ```python
   def get_save_strategies(self) -> List[SaveEntityStrategy]:
       strategies = []
       for entity in self.registry.get_enabled_entities():
           strategy = self._load_save_strategy(entity)
           if strategy:
               strategies.append(strategy)
       return strategies

   def _load_save_strategy(self, entity: RegisteredEntity) -> Optional[SaveEntityStrategy]:
       # Check for override in entity_config
       if entity.config.save_strategy_class:
           return entity.config.save_strategy_class(...)

       # Use convention: src.entities.{name}.save_strategy.{Name}SaveStrategy
       try:
           module_name = f"src.entities.{entity.config.name}.save_strategy"
           class_name = self._to_class_name(entity.config.name) + "SaveStrategy"
           module = importlib.import_module(module_name)
           strategy_class = getattr(module, class_name)
           return strategy_class(...)
       except (ImportError, AttributeError) as e:
           logger.warning(f"Could not load save strategy for {entity.config.name}: {e}")
           return None
   ```

3. **Update tests:**
   - Test strategy loading for all 10 entities
   - Test disabled entities don't load strategies
   - Test dependency-based execution order
   - Test strategy loading errors are handled gracefully

**Commit:** (individual task commit)

### Task 29: Update Save Orchestrator

**File:** `src/operations/save/orchestrator.py`

**Steps:**

1. **Replace ApplicationConfig with EntityRegistry:**
   ```python
   class SaveOrchestrator:
       def __init__(
           self,
           github_service: GitHubService,
           storage_service: StorageService,
           registry: EntityRegistry  # Replaced ApplicationConfig
       ):
           self.github_service = github_service
           self.storage_service = storage_service
           self.registry = registry
           self.factory = StrategyFactory(registry)
   ```

2. **Use registry for execution order:**
   ```python
   def save(self) -> Dict[str, int]:
       results = {}

       # Get enabled entities in dependency order (topologically sorted)
       enabled_entities = self.registry.get_enabled_entities()

       for entity in enabled_entities:
           strategy = self.factory.get_save_strategy(entity.config.name)
           if strategy:
               count = self._execute_save(strategy)
               results[entity.config.name] = count

       return results
   ```

3. **Update tests:**
   - Test orchestrator with various entity configurations
   - Test dependency order respected during save
   - Test disabled entities are skipped
   - Test partial configurations work correctly

**Commit:** (individual task commit)

### Task 30: Update Restore Orchestrator

**File:** `src/operations/restore/orchestrator.py`

**Steps:**

1. **Replace ApplicationConfig with EntityRegistry:**
   ```python
   class RestoreOrchestrator:
       def __init__(
           self,
           github_service: GitHubService,
           storage_service: StorageService,
           registry: EntityRegistry  # Replaced ApplicationConfig
       ):
           self.github_service = github_service
           self.storage_service = storage_service
           self.registry = registry
           self.factory = StrategyFactory(registry)
   ```

2. **Use registry for execution order:**
   ```python
   def restore(self) -> Dict[str, int]:
       results = {}

       # Get enabled entities in dependency order
       enabled_entities = self.registry.get_enabled_entities()

       for entity in enabled_entities:
           strategy = self.factory.get_restore_strategy(entity.config.name)
           if strategy:
               count = self._execute_restore(strategy)
               results[entity.config.name] = count

       return results
   ```

3. **Update tests:**
   - Test orchestrator with various configurations
   - Test dependency order during restore
   - Test disabled entities are skipped
   - Test dependency violations are caught

**Commit:** (individual task commit)

### Task 31: Commit Factory and Orchestrator Updates

**Commit message:**
```
feat: complete StrategyFactory and orchestrator migration to EntityRegistry

Replace ApplicationConfig with EntityRegistry in StrategyFactory and both
orchestrators. Strategy loading now uses convention-based discovery.

- Remove ApplicationConfig from StrategyFactory constructor
- Implement convention-based strategy loading
- Update save/restore orchestrators to use registry
- Use topological sort for execution order
- Remove all ApplicationConfig references

All integration tests passing. Execution order validated.
```

## ApplicationConfig Removal

### Task 32: Remove ApplicationConfig

**Files:**
- `src/config/settings.py` (contains ApplicationConfig)
- `src/main.py` (entry point)
- Any CLI modules

**Steps:**

1. **Update main entry point:**
   ```python
   # OLD:
   config = ApplicationConfig.from_environment()
   orchestrator = SaveOrchestrator(..., config)

   # NEW:
   registry = EntityRegistry.from_environment()
   orchestrator = SaveOrchestrator(..., registry)
   ```

2. **Delete ApplicationConfig class:**
   - Remove from `src/config/settings.py`
   - Keep `NumberSpecificationParser` (still used by EntityRegistry)

3. **Update CLI interface:**
   - Replace ApplicationConfig references with EntityRegistry
   - Ensure all command-line arguments still work
   - Update help text if needed

4. **Search for remaining references:**
   ```bash
   grep -r "ApplicationConfig" src/ tests/
   ```
   - Remove or update all remaining references
   - Check imports, type hints, docstrings

**Commit:** (individual task commit)

### Task 33: Update Integration Tests

**Directories:**
- `tests/integration/`
- `tests/container/`

**Steps:**

1. **Find all tests using ApplicationConfig:**
   ```bash
   grep -r "ApplicationConfig" tests/
   ```

2. **Update to use EntityRegistry:**
   ```python
   # OLD:
   config = ApplicationConfig(
       operation="save",
       include_issues=True,
       include_comments=False,
       ...
   )

   # NEW:
   # Set environment variables
   os.environ["INCLUDE_ISSUES"] = "true"
   os.environ["INCLUDE_ISSUE_COMMENTS"] = "false"
   registry = EntityRegistry.from_environment()
   ```

3. **Test all environment variables:**
   - Test INCLUDE_LABELS (new)
   - Test INCLUDE_MILESTONES
   - Test INCLUDE_ISSUES (with bool and Set[int])
   - Test INCLUDE_ISSUE_COMMENTS
   - Test INCLUDE_PULL_REQUESTS (with bool and Set[int])
   - Test INCLUDE_PULL_REQUEST_COMMENTS
   - Test INCLUDE_PR_REVIEWS
   - Test INCLUDE_PR_REVIEW_COMMENTS
   - Test INCLUDE_SUB_ISSUES
   - Test INCLUDE_GIT_REPO

4. **End-to-end workflow tests:**
   - Test full save workflow with various entity combinations
   - Test full restore workflow with dependencies
   - Test dependency validation in real scenarios
   - Test number specifications work correctly

**Commit:** (individual task commit)

### Task 34: Commit ApplicationConfig Removal

**Commit message:**
```
feat: remove ApplicationConfig, complete EntityRegistry migration

Remove ApplicationConfig class and all references. EntityRegistry is now
the sole configuration system for entity management.

- Delete ApplicationConfig from src/config/settings.py
- Update main.py and CLI to use EntityRegistry
- Migrate all integration tests to EntityRegistry
- Remove all ApplicationConfig imports and references

All tests (unit + integration + container) passing.
No ApplicationConfig references remain in codebase.

BREAKING CHANGE: ApplicationConfig class removed. Use EntityRegistry instead.
```

## Final Validation

### Task 35: Comprehensive System Testing

**Manual Validation Scenarios:**

1. **All entities enabled (default):**
   ```bash
   # No environment variables set - all entities should be enabled
   make test-container
   ```

2. **Selective entities disabled:**
   ```bash
   INCLUDE_ISSUE_COMMENTS=false
   INCLUDE_PR_REVIEWS=false
   make test-container
   ```

3. **Number specifications:**
   ```bash
   INCLUDE_ISSUES=1,5-10
   INCLUDE_PULL_REQUESTS=1-3,7
   make test-container
   ```

4. **Dependency validation (non-strict):**
   ```bash
   INCLUDE_ISSUES=false
   INCLUDE_ISSUE_COMMENTS=true  # Should auto-disable with warning
   make test-container
   ```

5. **Invalid configurations:**
   ```bash
   INCLUDE_ISSUES=invalid  # Should fail with clear error
   make test-container
   ```

**Error Message Quality:**

Verify helpful error messages for:
- Unknown entity names
- Circular dependencies
- Missing required dependencies
- Invalid environment variable values
- Entity config discovery failures

Ensure errors point to:
- Specific entity_config.py file
- Environment variable name
- Suggested fixes

**Backward Compatibility:**

- Verify all existing environment variables work
- Test default behaviors match previous system
- Ensure no breaking changes for users (except ApplicationConfig removal)

### Task 36: Performance and Discovery Validation

**Discovery Performance:**
1. Add timing logs to entity discovery
2. Measure discovery time with all 10 entities
3. Verify discovery happens once at initialization
4. Confirm discovery time is negligible (< 100ms)

**Memory Footprint:**
1. Verify EntityRegistry doesn't load unnecessary data
2. Confirm strategies are lazy-loaded only for enabled entities
3. Test memory usage with all entities vs selective entities

**Logging Validation:**
1. Test entity discovery logs useful information:
   ```
   INFO: Discovered entity: labels
   INFO: Discovered entity: issues
   ...
   ```

2. Verify dependency warnings are clear:
   ```
   WARNING: INCLUDE_ISSUE_COMMENTS requires INCLUDE_ISSUES. Disabling comments.
   ```

3. Ensure debug logs help troubleshoot:
   ```
   DEBUG: Loading save strategy for labels: LabelsSaveStrategy
   DEBUG: Executing entities in order: ['labels', 'milestones', 'issues', ...]
   ```

### Task 37: Final Commit and Phase 3 Completion

**Quality Checks:**
```bash
make check-all  # Run all quality checks including container tests
```

Verify:
- All unit tests pass
- All integration tests pass
- All container tests pass
- Linting passes (flake8)
- Formatting passes (black)
- Type checking passes (mypy)

**Commit message:**
```
test: comprehensive validation of EntityRegistry migration

Add comprehensive system tests for EntityRegistry migration including
manual validation scenarios, error handling, and performance checks.

- Test all entity combinations and configurations
- Validate dependency enforcement in real scenarios
- Verify error messages are helpful and actionable
- Confirm performance and memory footprint acceptable
- Test backward compatibility of environment variables

All quality checks passing: unit, integration, container, lint, format, types.

Phase 3 (Entity Migration) complete. All 10 entities migrated to EntityRegistry.
```

**Documentation:**
- Update Phase 3 status in main plan document
- Tag completion: `git tag phase3-complete`
- Document any issues or deviations from plan

## Task Summary

Phase 3 consists of 37 tasks organized into 9 sections:

**Batch 1 (Tasks 13-17):** Migrate independent entities
- Task 13: Migrate labels
- Task 14: Migrate milestones
- Task 15: Migrate git_repository
- Task 16: Update StrategyFactory for Batch 1
- Task 17: Commit Batch 1

**Batch 2 (Tasks 18-22):** Migrate issues domain
- Task 18: Migrate issues
- Task 19: Migrate comments
- Task 20: Migrate sub_issues
- Task 21: Update StrategyFactory for Batch 2
- Task 22: Commit Batch 2

**Batch 3 (Tasks 23-27):** Migrate PR domain
- Task 23: Migrate pull_requests
- Task 24: Migrate pr_reviews
- Task 25: Migrate pr_review_comments
- Task 26: Migrate pr_comments
- Task 27: Commit Batch 3

**Infrastructure (Tasks 28-31):** Update factory and orchestrators
- Task 28: Complete StrategyFactory migration
- Task 29: Update save orchestrator
- Task 30: Update restore orchestrator
- Task 31: Commit factory/orchestrator updates

**Cleanup (Tasks 32-34):** Remove ApplicationConfig
- Task 32: Remove ApplicationConfig class
- Task 33: Update integration tests
- Task 34: Commit ApplicationConfig removal

**Validation (Tasks 35-37):** Final testing
- Task 35: Comprehensive system testing
- Task 36: Performance and discovery validation
- Task 37: Final commit and phase completion

## Success Criteria

Phase 3 is complete when:
- ✅ All 10 entities migrated to EntityRegistry
- ✅ ApplicationConfig class removed from codebase
- ✅ All strategies moved to entity directories
- ✅ Dependency graph fully validated and documented
- ✅ All tests passing (unit, integration, container)
- ✅ All quality checks passing (lint, format, types)
- ✅ No ApplicationConfig references remain
- ✅ Backward compatibility maintained for environment variables
- ✅ Error messages are clear and helpful
- ✅ Documentation updated

## Risk Mitigation

**Risk:** Breaking existing workflows during migration

**Mitigation:**
- Comprehensive test coverage before starting
- Grouped batches allow incremental validation
- Each task has explicit commit point
- Can rollback individual batches if needed

**Risk:** Missing or incorrect dependencies

**Mitigation:**
- Dependency inference process analyzes multiple sources
- Validation tests required before documenting dependencies
- Non-strict mode provides warnings for investigation
- Can iterate on dependencies after initial migration

**Risk:** Performance degradation from discovery

**Mitigation:**
- Discovery happens once at initialization
- Performance validation in Task 36
- Lazy-loading of strategies
- Can optimize if issues found

## Next Steps

After Phase 3 completion:
- **Phase 4:** Test infrastructure improvements
- **Phase 5:** Documentation and developer guides
- **Phase 6:** CLI generator tool (if not completed in Phase 2)

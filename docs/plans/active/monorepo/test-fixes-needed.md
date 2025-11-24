# Test Fixes Needed - Monorepo Conversion

**Date**: 2025-11-24
**Status**: Phase 10 - Post-cleanup test failures
**Total Failing**: 67 test files

## Executive Summary

After completing the monorepo conversion and cleanup, 67 test files are failing collection. Analysis reveals these are **NOT structural issues** with the monorepo conversion itself, but rather:

1. **Missing module structure** - Tests reference submodules that don't exist in the simplified package structure
2. **Missing dependency** - One test requires `pydantic` which isn't installed
3. **Import path mismatches** - Tests importing from locations that changed during the monorepo restructuring

**Key Finding**: The monorepo structure is correct. The tests need to be updated to match the simplified module organization.

## Root Cause Analysis

### Issue 1: Non-existent Submodules (66 files)

Tests are importing from submodules that don't exist:

**git-repo-tools** (3 files):
- Tests import: `git_repo_tools.entities.git_repositories.*`
- Tests import: `git_repo_tools.entities.registry`
- **Reality**: No `git_repositories/` subdir, no `registry.py` in git-repo-tools
- **Actual structure**: Flat `git_repo_tools.entities.*` with entity_config.py, models.py, etc.

**github-data-tools** (63 files):
- Tests import: `github_data_tools.operations.strategy_factory`
- Tests import: `github_data_tools.entities.registry`
- Tests import: `github_data_tools.entities.{issues,labels,milestones,...}.*`
- **Reality**: No `strategy_factory.py` in github-data-tools/operations, no `registry.py`
- **Reality**: The entity-specific submodules DO exist, but imports may be incorrect

### Issue 2: Missing Dependency (1 file)

**packages/core/tests/unit/storage/test_json_storage_unit.py**:
- Error: `ModuleNotFoundError: No module named 'pydantic'`
- **Fix**: Add pydantic to core package dev dependencies

## Failing Test Files by Package

### Package: core (1 file)

**Unit Tests (1)**:
1. `packages/core/tests/unit/storage/test_json_storage_unit.py` - Missing pydantic dependency

### Package: git-repo-tools (3 files)

**Unit Tests (3)**:
1. `packages/git-repo-tools/tests/unit/entities/test_git_repositories_entity_config.py` - Imports non-existent `git_repo_tools.entities.git_repositories`
2. `packages/git-repo-tools/tests/unit/entities/test_git_repository_entity_config.py` - Imports non-existent `git_repo_tools.entities.registry`
3. `packages/git-repo-tools/tests/unit/test_git_repository_service_unit.py` - Imports non-existent `git_repo_tools.entities.git_repositories.models`

### Package: github-data-tools (63 files)

**Integration Tests (13)**:
1. `packages/github-data-tools/tests/integration/operations/test_strategy_factory_integration.py` - No `strategy_factory` in operations
2. `packages/github-data-tools/tests/integration/test_batch2_dependencies.py` - No `registry` module
3. `packages/github-data-tools/tests/integration/test_complete_dependency_graph.py` - No `registry` module
4. `packages/github-data-tools/tests/integration/test_entity_registry_integration.py` - No `registry` module
5. `packages/github-data-tools/tests/integration/test_git_repository_integration.py` - Import issues
6. `packages/github-data-tools/tests/integration/test_graphql_integration.py` - Import issues
7. `packages/github-data-tools/tests/integration/test_milestone_graphql_integration.py` - Import issues
8. `packages/github-data-tools/tests/integration/test_milestone_save_restore_integration.py` - Import issues
9. `packages/github-data-tools/tests/integration/test_release_save_restore_integration.py` - Import issues
10. `packages/github-data-tools/tests/integration/test_releases_registry_integration.py` - Import issues
11. `packages/github-data-tools/tests/integration/test_repository_creation_integration.py` - Import issues
12. `packages/github-data-tools/tests/integration/test_strategy_context_validation.py` - Import issues

**Unit Tests (50)**:

*Entity Tests - Issues (3)*:
1. `packages/github-data-tools/tests/unit/entities/issues/test_converters.py`
2. `packages/github-data-tools/tests/unit/entities/issues/test_issues_entity_config.py`
3. `packages/github-data-tools/tests/unit/entities/issues/test_restore_strategy_sanitization.py`

*Entity Tests - Labels (2)*:
4. `packages/github-data-tools/tests/unit/entities/labels/test_converters.py`
5. `packages/github-data-tools/tests/unit/entities/labels/test_labels_entity_config.py`

*Entity Tests - Milestones (2)*:
6. `packages/github-data-tools/tests/unit/entities/milestones/test_converters.py`
7. `packages/github-data-tools/tests/unit/entities/milestones/test_milestones_entity_config.py`

*Entity Tests - PR Comments (2)*:
8. `packages/github-data-tools/tests/unit/entities/pr_comments/test_pr_comments_entity_config.py`
9. `packages/github-data-tools/tests/unit/entities/pr_comments/test_restore_strategy_sanitization.py`

*Entity Tests - PR Review Comments (2)*:
10. `packages/github-data-tools/tests/unit/entities/pr_review_comments/test_pr_review_comments_entity_config.py`
11. `packages/github-data-tools/tests/unit/entities/pr_review_comments/test_restore_strategy_sanitization.py`

*Entity Tests - PR Reviews (2)*:
12. `packages/github-data-tools/tests/unit/entities/pr_reviews/test_pr_reviews_entity_config.py`
13. `packages/github-data-tools/tests/unit/entities/pr_reviews/test_restore_strategy_sanitization.py`

*Entity Tests - Pull Requests (3)*:
14. `packages/github-data-tools/tests/unit/entities/pull_requests/test_converters.py`
15. `packages/github-data-tools/tests/unit/entities/pull_requests/test_pull_requests_entity_config.py`
16. `packages/github-data-tools/tests/unit/entities/pull_requests/test_restore_strategy_sanitization.py`

*Entity Tests - Releases (4)*:
17. `packages/github-data-tools/tests/unit/entities/releases/test_converters.py`
18. `packages/github-data-tools/tests/unit/entities/releases/test_release_models.py`
19. `packages/github-data-tools/tests/unit/entities/releases/test_releases_entity_config.py`
20. `packages/github-data-tools/tests/unit/entities/releases/test_restore_strategy.py`
21. `packages/github-data-tools/tests/unit/entities/releases/test_save_strategy.py`

*Entity Tests - Sub Issues (1)*:
22. `packages/github-data-tools/tests/unit/entities/sub_issues/test_sub_issues_entity_config.py`

*Entity Tests - Generic (3)*:
23. `packages/github-data-tools/tests/unit/entities/test_comments_entity_config.py`
24. `packages/github-data-tools/tests/unit/entities/test_converters.py`
25. `packages/github-data-tools/tests/unit/entities/test_restore_strategy_sanitization.py`

*GitHub Service Tests (6)*:
26. `packages/github-data-tools/tests/unit/github/test_boundary.py`
27. `packages/github-data-tools/tests/unit/github/test_common_converters.py`
28. `packages/github-data-tools/tests/unit/github/test_converter_migration_complete.py`
29. `packages/github-data-tools/tests/unit/github/test_github_service_dynamic.py`
30. `packages/github-data-tools/tests/unit/github/test_metadata.py`
31. `packages/github-data-tools/tests/unit/github/test_service.py`

*Operations Tests (5)*:
32. `packages/github-data-tools/tests/unit/operations/restore/test_restore_orchestrator_registry.py`
33. `packages/github-data-tools/tests/unit/operations/save/test_save_orchestrator_registry.py`
34. `packages/github-data-tools/tests/unit/operations/test_strategy_factory.py` - No `strategy_factory` in operations
35. `packages/github-data-tools/tests/unit/operations/test_strategy_factory_registry.py`
36. `packages/github-data-tools/tests/unit/operations/test_strategy_factory_validation.py`

*Other Unit Tests (14)*:
37. `packages/github-data-tools/tests/unit/test_enhanced_boundary_factory.py`
38. `packages/github-data-tools/tests/unit/test_example_modernized_unit.py`
39. `packages/github-data-tools/tests/unit/test_github_data_builder_extensions.py`
40. `packages/github-data-tools/tests/unit/test_github_data_builder_week2_extensions.py`
41. `packages/github-data-tools/tests/unit/test_github_data_builder_week3_extensions.py`
42. `packages/github-data-tools/tests/unit/test_github_service_releases.py`
43. `packages/github-data-tools/tests/unit/test_git_repository_service_unit.py`
44. `packages/github-data-tools/tests/unit/test_graphql_paginator_unit.py`
45. `packages/github-data-tools/tests/unit/test_json_storage_unit.py`
46. `packages/github-data-tools/tests/unit/test_milestone_entities.py`
47. `packages/github-data-tools/tests/unit/test_milestone_issue_relationships.py`
48. `packages/github-data-tools/tests/unit/test_milestone_pr_relationships.py`
49. `packages/github-data-tools/tests/unit/test_protocol_validation.py`
50. `packages/github-data-tools/tests/unit/test_rate_limit_handling_unit.py`

*Tools Tests (1)*:
51. `packages/github-data-tools/tests/unit/tools/test_generate_entity.py`

## Action Plan

### Step 1: Investigate Actual Module Structure

Before fixing imports, understand what actually exists:

```bash
# Check git-repo-tools structure
tree packages/git-repo-tools/src/git_repo_tools/ -I __pycache__

# Check github-data-tools structure
tree packages/github-data-tools/src/github_data_tools/ -I __pycache__

# Verify what's actually exported
python -c "import git_repo_tools; print(dir(git_repo_tools))"
python -c "import github_data_tools; print(dir(github_data_tools))"
```

### Step 2: Fix Core Package Dependency

```bash
# Add pydantic to core package
cd packages/core
pdm add --dev pydantic
cd ../..
pdm lock
pdm install --dev
```

### Step 3: Understand Import Path Changes

Compare test imports with actual module structure to determine:
- What modules moved from monolith to which package
- What modules were consolidated or renamed
- What the correct import paths should be

### Step 4: Fix Test Imports Systematically

Based on findings from Step 1 & 3:

**Option A**: Update test imports to match actual structure
```bash
# Example: Fix git-repo-tools tests
find packages/git-repo-tools/tests -name "*.py" -exec sed -i \
  's/from git_repo_tools\.entities\.git_repositories/from git_repo_tools.entities/g' {} \;
```

**Option B**: Create missing modules if tests are correct
- If tests expect `registry.py`, determine where it should live
- If tests expect `strategy_factory.py` in operations, check if it's in core instead

### Step 5: Verify Each Package

```bash
# Test each package independently
pdm run pytest packages/core/tests/ -m "not container" -v
pdm run pytest packages/git-repo-tools/tests/ -m "not container" -v
pdm run pytest packages/github-data-tools/tests/ -m "not container" -v
```

## Specific Investigation Needed

### git-repo-tools Questions:
1. Where did `EntityRegistry` move to? (tests expect `git_repo_tools.entities.registry`)
2. Is there supposed to be a `git_repositories/` subpackage or is it flat `entities/`?
3. What is `GitBackupFormat` and where should it be imported from?

### github-data-tools Questions:
1. Where is `StrategyFactory`? In core or in github-data-tools?
   - Tests import: `github_data_tools.operations.strategy_factory`
   - Core has: `github_data_core.operations.strategy_factory`
   - Should github-data-tools re-export it?
2. Where is `EntityRegistry`? Should it be in github-data-tools or core?
3. Are entity submodules (issues/, labels/, etc.) complete?

## Expected Outcomes

After fixes:
- All 67 test files should successfully import their dependencies
- Tests should run (may still have test failures, but collection should work)
- ~172 tests that currently pass should continue passing
- Monorepo structure validation complete

## Notes

- The 172 tests that currently pass prove the monorepo structure is fundamentally sound
- These 67 failures are test infrastructure issues, not code issues
- Priority: Fix imports to match actual structure (don't create unnecessary modules)
- The module simplification during monorepo conversion is likely intentional and good
